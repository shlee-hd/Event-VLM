"""
Visualization utilities for Event-VLM.
"""

from typing import List, Optional, Tuple
import numpy as np
import cv2
from PIL import Image

from src.detector.detr_wrapper import Detection


# Color palette for hazard levels
HAZARD_COLORS = {
    "critical": (0, 0, 255),    # Red
    "high": (0, 165, 255),      # Orange
    "standard": (0, 255, 0),    # Green
    "none": (128, 128, 128)     # Gray
}


def visualize_detections(
    image: np.ndarray,
    detections: List[Detection],
    show_labels: bool = True,
    thickness: int = 2
) -> np.ndarray:
    """
    Visualize detections on image.
    
    Args:
        image: Input image (BGR)
        detections: List of Detection objects
        show_labels: Whether to show class labels
        thickness: Line thickness
        
    Returns:
        Annotated image
    """
    vis = image.copy()
    h, w = vis.shape[:2]
    
    for det in detections:
        # Get bbox in pixel coordinates
        x1, y1, x2, y2 = det.bbox
        x1, y1, x2, y2 = int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)
        
        # Get color based on hazard level
        color = HAZARD_COLORS.get(det.hazard_level, HAZARD_COLORS["none"])
        
        # Draw rectangle
        cv2.rectangle(vis, (x1, y1), (x2, y2), color, thickness)
        
        # Draw label
        if show_labels:
            label = f"{det.class_name}: {det.confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            # Label background
            cv2.rectangle(
                vis,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0] + 10, y1),
                color,
                -1
            )
            
            # Label text
            cv2.putText(
                vis,
                label,
                (x1 + 5, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
    
    return vis


def visualize_pruning(
    image: np.ndarray,
    mask: np.ndarray,
    image_size: int = 336,
    patch_size: int = 14,
    alpha: float = 0.4
) -> np.ndarray:
    """
    Visualize token pruning mask overlaid on image.
    
    Args:
        image: Input image
        mask: Binary mask [L] where L = num_patches
        image_size: Target image size
        patch_size: ViT patch size
        alpha: Overlay transparency
        
    Returns:
        Visualization image
    """
    num_patches_side = image_size // patch_size
    
    # Resize image
    vis = cv2.resize(image, (image_size, image_size))
    
    # Reshape mask to 2D
    if isinstance(mask, np.ndarray):
        mask_2d = mask.reshape(num_patches_side, num_patches_side)
    else:
        mask_2d = mask.cpu().numpy().reshape(num_patches_side, num_patches_side)
    
    # Create overlay
    overlay = np.zeros_like(vis)
    
    for py in range(num_patches_side):
        for px in range(num_patches_side):
            y1 = py * patch_size
            y2 = (py + 1) * patch_size
            x1 = px * patch_size
            x2 = (px + 1) * patch_size
            
            if mask_2d[py, px]:
                overlay[y1:y2, x1:x2] = [0, 255, 0]  # Green for kept
            else:
                overlay[y1:y2, x1:x2] = [255, 0, 0]  # Red for pruned
    
    # Blend
    vis = cv2.addWeighted(vis, 1 - alpha, overlay, alpha, 0)
    
    return vis


def create_comparison_figure(
    image: np.ndarray,
    detections: List[Detection],
    mask_fixed: np.ndarray,
    mask_adaptive: np.ndarray,
    image_size: int = 336
) -> np.ndarray:
    """
    Create a comparison figure showing fixed vs adaptive dilation.
    
    Args:
        image: Original image
        detections: List of detections
        mask_fixed: Mask from fixed dilation
        mask_adaptive: Mask from adaptive dilation
        image_size: Target size
        
    Returns:
        2x2 comparison figure
    """
    # Resize original
    img_resized = cv2.resize(image, (image_size, image_size))
    
    # Create panels
    detection_vis = visualize_detections(img_resized, detections)
    fixed_vis = visualize_pruning(img_resized, mask_fixed, image_size)
    adaptive_vis = visualize_pruning(img_resized, mask_adaptive, image_size)
    
    # Add panel labels
    def add_label(img, text):
        cv2.putText(
            img, text, (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
        )
        return img
    
    img_resized = add_label(img_resized.copy(), "Original")
    detection_vis = add_label(detection_vis, "Detections")
    fixed_vis = add_label(fixed_vis, "Fixed Dilation")
    adaptive_vis = add_label(adaptive_vis, "Adaptive Dilation")
    
    # Combine into 2x2 grid
    top_row = np.hstack([img_resized, detection_vis])
    bottom_row = np.hstack([fixed_vis, adaptive_vis])
    combined = np.vstack([top_row, bottom_row])
    
    return combined


def save_visualization(
    output_path: str,
    image: np.ndarray,
    detections: Optional[List[Detection]] = None,
    mask: Optional[np.ndarray] = None,
    caption: Optional[str] = None
) -> None:
    """
    Save visualization to file.
    
    Args:
        output_path: Output file path
        image: Image to visualize
        detections: Optional detections to overlay
        mask: Optional pruning mask
        caption: Optional caption to display
    """
    vis = image.copy()
    
    if detections:
        vis = visualize_detections(vis, detections)
    
    if mask is not None:
        vis = visualize_pruning(vis, mask)
    
    if caption:
        # Add caption at bottom
        h, w = vis.shape[:2]
        caption_height = 60
        
        # Create caption bar
        caption_bar = np.zeros((caption_height, w, 3), dtype=np.uint8)
        
        # Wrap text
        max_chars = w // 8
        lines = [caption[i:i+max_chars] for i in range(0, len(caption), max_chars)]
        
        for i, line in enumerate(lines[:2]):  # Max 2 lines
            cv2.putText(
                caption_bar,
                line,
                (10, 20 + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
        
        vis = np.vstack([vis, caption_bar])
    
    cv2.imwrite(output_path, vis)
