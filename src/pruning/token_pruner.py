"""
Token Pruner for Stage 2: Knowledge-Guided Token Pruning.
Training-free spatial pruning using detector bounding boxes as priors.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import math

import torch
import torch.nn as nn
import numpy as np

from src.detector.detr_wrapper import Detection, DetectionResult
from src.pruning.adaptive_dilation import AdaptiveDilation


@dataclass
class PruningResult:
    """Result of token pruning operation."""
    mask: torch.Tensor           # [L] binary mask
    kept_indices: torch.Tensor   # Indices of kept tokens
    num_kept: int
    num_total: int
    reduction_ratio: float
    
    @property
    def num_pruned(self) -> int:
        return self.num_total - self.num_kept


class TokenPruner(nn.Module):
    """
    Knowledge-Guided Token Pruner.
    
    Uses bounding box priors from the detector to create binary masks
    for preserving only relevant visual tokens.
    """
    
    def __init__(
        self,
        image_size: int = 336,
        patch_size: int = 14,
        alpha_base: float = 1.2,
        beta: float = 0.5,
        min_tokens: int = 64,
        preserve_cls_token: bool = True,
        shape_variance: Optional[Dict[str, float]] = None
    ):
        """
        Args:
            image_size: Input image size
            patch_size: ViT patch size
            alpha_base: Base dilation factor
            beta: Adaptive dilation coefficient
            min_tokens: Minimum tokens to preserve
            preserve_cls_token: Whether to always preserve CLS token
            shape_variance: Dict of class name to shape variance
        """
        super().__init__()
        
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_patches_side = image_size // patch_size
        self.num_patches = self.num_patches_side ** 2
        self.min_tokens = min_tokens
        self.preserve_cls_token = preserve_cls_token
        
        # Adaptive dilation module
        self.adaptive_dilation = AdaptiveDilation(
            alpha_base=alpha_base,
            beta=beta,
            shape_variance=shape_variance
        )
    
    def bbox_to_patch_indices(
        self,
        bbox: Tuple[float, float, float, float],
        dilation: float = 1.0
    ) -> List[int]:
        """
        Convert normalized bounding box to patch indices.
        
        Args:
            bbox: (x1, y1, x2, y2) normalized coordinates
            dilation: Dilation factor for expanding bbox
            
        Returns:
            List of patch indices covered by the (dilated) bbox
        """
        x1, y1, x2, y2 = bbox
        
        # Calculate center and dimensions
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        w, h = x2 - x1, y2 - y1
        
        # Apply dilation
        w_dilated = w * dilation
        h_dilated = h * dilation
        
        # New bbox coordinates (clamped to [0, 1])
        x1_d = max(0, cx - w_dilated / 2)
        y1_d = max(0, cy - h_dilated / 2)
        x2_d = min(1, cx + w_dilated / 2)
        y2_d = min(1, cy + h_dilated / 2)
        
        # Convert to patch grid coordinates
        p1_x = int(x1_d * self.num_patches_side)
        p1_y = int(y1_d * self.num_patches_side)
        p2_x = min(int(x2_d * self.num_patches_side) + 1, self.num_patches_side)
        p2_y = min(int(y2_d * self.num_patches_side) + 1, self.num_patches_side)
        
        # Generate patch indices (row-major order)
        indices = []
        for py in range(p1_y, p2_y):
            for px in range(p1_x, p2_x):
                idx = py * self.num_patches_side + px
                indices.append(idx)
        
        return indices
    
    def create_mask(
        self,
        detections: List[Detection],
        device: torch.device = torch.device("cpu")
    ) -> torch.Tensor:
        """
        Create binary mask from detections.
        
        Args:
            detections: List of Detection objects
            device: Target device
            
        Returns:
            Binary mask [L] where L = num_patches
        """
        mask = torch.zeros(self.num_patches, dtype=torch.bool, device=device)
        
        for det in detections:
            # Get adaptive dilation factor
            dilation = self.adaptive_dilation.get_dilation(det.class_name)
            
            # Get patch indices for this detection
            indices = self.bbox_to_patch_indices(det.bbox, dilation)
            
            # Set mask
            for idx in indices:
                if 0 <= idx < self.num_patches:
                    mask[idx] = True
        
        return mask
    
    def prune(
        self,
        tokens: torch.Tensor,
        detections: List[Detection],
        return_mask: bool = False
    ) -> Tuple[torch.Tensor, Optional[PruningResult]]:
        """
        Prune visual tokens based on detector priors.
        
        Args:
            tokens: Visual tokens [B, L, D] or [L, D]
            detections: List of Detection objects
            return_mask: Whether to return pruning result
            
        Returns:
            Pruned tokens and optional PruningResult
        """
        # Handle batch dimension
        if tokens.dim() == 2:
            tokens = tokens.unsqueeze(0)
            squeeze_output = True
        else:
            squeeze_output = False
        
        B, L, D = tokens.shape
        device = tokens.device
        
        # Account for CLS token
        has_cls = L == self.num_patches + 1
        if has_cls:
            cls_token = tokens[:, :1, :]
            patch_tokens = tokens[:, 1:, :]
        else:
            cls_token = None
            patch_tokens = tokens
        
        # Create mask from detections
        mask = self.create_mask(detections, device)
        
        # Ensure minimum tokens
        if mask.sum() < self.min_tokens:
            # If not enough tokens, keep all (safety fallback)
            mask = torch.ones_like(mask)
        
        # Gather kept tokens
        kept_indices = mask.nonzero(as_tuple=True)[0]
        pruned_tokens = patch_tokens[:, kept_indices, :]
        
        # Add CLS token back
        if has_cls and self.preserve_cls_token:
            pruned_tokens = torch.cat([cls_token, pruned_tokens], dim=1)
        
        # Squeeze if needed
        if squeeze_output:
            pruned_tokens = pruned_tokens.squeeze(0)
        
        if return_mask:
            result = PruningResult(
                mask=mask,
                kept_indices=kept_indices,
                num_kept=len(kept_indices),
                num_total=self.num_patches,
                reduction_ratio=1.0 - len(kept_indices) / self.num_patches
            )
            return pruned_tokens, result
        
        return pruned_tokens, None
    
    def forward(
        self,
        tokens: torch.Tensor,
        detection_result: DetectionResult
    ) -> torch.Tensor:
        """
        Forward pass for nn.Module compatibility.
        
        Args:
            tokens: Visual tokens [B, L, D]
            detection_result: DetectionResult from detector
            
        Returns:
            Pruned tokens
        """
        pruned_tokens, _ = self.prune(
            tokens,
            detection_result.detections,
            return_mask=False
        )
        return pruned_tokens
    
    def visualize_mask(
        self,
        mask: torch.Tensor,
        image: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Visualize pruning mask as an image.
        
        Args:
            mask: Binary mask [L]
            image: Optional original image to overlay
            
        Returns:
            Visualization as numpy array
        """
        # Reshape mask to 2D
        mask_2d = mask.cpu().numpy().reshape(
            self.num_patches_side,
            self.num_patches_side
        )
        
        # Create visualization
        vis = np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)
        
        for py in range(self.num_patches_side):
            for px in range(self.num_patches_side):
                y1 = py * self.patch_size
                y2 = (py + 1) * self.patch_size
                x1 = px * self.patch_size
                x2 = (px + 1) * self.patch_size
                
                if mask_2d[py, px]:
                    vis[y1:y2, x1:x2] = [0, 255, 0]  # Green for kept
                else:
                    vis[y1:y2, x1:x2] = [255, 0, 0]  # Red for pruned
        
        # Overlay on image if provided
        if image is not None:
            import cv2
            image_resized = cv2.resize(image, (self.image_size, self.image_size))
            vis = cv2.addWeighted(image_resized, 0.6, vis, 0.4, 0)
        
        return vis
