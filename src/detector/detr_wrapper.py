"""
Detector wrappers for Stage 1: Event-Triggered Gating.
Supports both DETR-L and YOLOv8 variants.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import logging

import torch
import torch.nn as nn
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Single detection result."""
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2 (normalized)
    class_id: int
    class_name: str
    confidence: float
    hazard_level: str  # critical, high, standard


@dataclass
class DetectionResult:
    """Detection results for a single frame."""
    detections: List[Detection]
    is_event: bool  # Whether to trigger VLM
    max_hazard_level: str
    trigger_confidence: float
    
    @property
    def bboxes(self) -> List[Tuple[float, float, float, float]]:
        return [d.bbox for d in self.detections]
    
    @property
    def hazard_detections(self) -> List[Detection]:
        return [d for d in self.detections if d.hazard_level != "none"]


class BaseDetector(ABC):
    """Abstract base class for detectors."""
    
    # Class mapping to hazard levels
    HAZARD_MAPPING = {
        # COCO classes mapped to hazard levels
        "fire": "critical",
        "smoke": "critical",
        "explosion": "critical",
        "collapse": "critical",
        "forklift": "high",
        "truck": "high",
        "crane": "high",
        "person": "standard",
        "car": "standard",
        "motorcycle": "standard",
        "bicycle": "standard",
    }
    
    def __init__(
        self,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        hazard_classes: Optional[Dict[str, List[str]]] = None,
        device: str = "cuda"
    ):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        
        if hazard_classes:
            # Build reverse mapping from class name to hazard level
            self.HAZARD_MAPPING = {}
            for level, classes in hazard_classes.items():
                for cls in classes:
                    self.HAZARD_MAPPING[cls.lower()] = level
    
    @abstractmethod
    def load_model(self) -> None:
        """Load pretrained model."""
        pass
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> DetectionResult:
        """Run detection on a single image."""
        pass
    
    def get_hazard_level(self, class_name: str) -> str:
        """Get hazard level for a class."""
        return self.HAZARD_MAPPING.get(class_name.lower(), "none")
    
    def should_trigger(self, detections: List[Detection]) -> Tuple[bool, str, float]:
        """Determine if VLM should be triggered based on detections."""
        if not detections:
            return False, "none", 0.0
        
        # Find highest hazard level detection
        hazard_priority = {"critical": 3, "high": 2, "standard": 1, "none": 0}
        max_hazard = "none"
        max_conf = 0.0
        
        for det in detections:
            if hazard_priority.get(det.hazard_level, 0) > hazard_priority.get(max_hazard, 0):
                max_hazard = det.hazard_level
                max_conf = det.confidence
            elif det.hazard_level == max_hazard and det.confidence > max_conf:
                max_conf = det.confidence
        
        # Trigger on any hazard detection
        is_event = max_hazard in ["critical", "high", "standard"]
        return is_event, max_hazard, max_conf


class DETRDetector(BaseDetector):
    """
    RT-DETR detector wrapper using Ultralytics.
    
    Supports multiple variants:
    - detr-r18: ResNet-18 backbone (~20M params, comparable to YOLO-S)
    - detr-r50: ResNet-50 backbone (~42M params)
    - detr-l: Large model with HGNetV2 backbone (~32M params)
    - detr-x: Extra-large model (~67M params)
    
    For lightweight deployment, use detr-r18 which provides:
    - Similar FLOPs to YOLOv8-S
    - Better accuracy than YOLO-Nano on COCO
    - End-to-end transformer architecture (no NMS)
    """
    
    # Model variants with weight files and approximate parameters
    MODEL_VARIANTS = {
        "detr-r18": "rtdetr-r18.pt",    # ~20M params, lightweight
        "detr-r50": "rtdetr-r50.pt",    # ~42M params, balanced
        "detr-l": "rtdetr-l.pt",        # ~32M params, HGNetV2 backbone
        "detr-x": "rtdetr-x.pt",        # ~67M params, largest
    }
    
    def __init__(
        self,
        model_name: str = "detr-r18",  # Default to lightweight
        pretrained: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.pretrained = pretrained
        self.model = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load RT-DETR from Ultralytics."""
        try:
            from ultralytics import RTDETR
            
            if self.model_name not in self.MODEL_VARIANTS:
                raise ValueError(
                    f"Unknown DETR model: {self.model_name}. "
                    f"Available: {list(self.MODEL_VARIANTS.keys())}"
                )
            
            weight_file = self.MODEL_VARIANTS[self.model_name]
            self.model = RTDETR(weight_file)
            self.model.to(self.device)
            logger.info(f"Loaded {self.model_name} ({weight_file}) on {self.device}")
            
        except ImportError:
            logger.error("ultralytics not installed. Run: pip install ultralytics")
            raise
        except Exception as e:
            # Fallback for models not yet released by Ultralytics
            if "r18" in self.model_name or "r50" in self.model_name:
                logger.warning(
                    f"{self.model_name} weights not available in Ultralytics. "
                    "Falling back to detr-l. For R18/R50, train from scratch or "
                    "use weights from: https://github.com/lyuwenyu/RT-DETR"
                )
                from ultralytics import RTDETR
                self.model = RTDETR("rtdetr-l.pt")
                self.model.to(self.device)
            else:
                raise
    
    def detect(self, image: np.ndarray) -> DetectionResult:
        """Run DETR detection on image."""
        # Run inference
        results = self.model(
            image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False
        )[0]
        
        detections = []
        h, w = image.shape[:2]
        
        for box in results.boxes:
            # Get bounding box (normalized)
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            bbox = (x1/w, y1/h, x2/w, y2/h)
            
            # Get class info
            class_id = int(box.cls[0])
            class_name = results.names[class_id]
            confidence = float(box.conf[0])
            hazard_level = self.get_hazard_level(class_name)
            
            detections.append(Detection(
                bbox=bbox,
                class_id=class_id,
                class_name=class_name,
                confidence=confidence,
                hazard_level=hazard_level
            ))
        
        is_event, max_hazard, max_conf = self.should_trigger(detections)
        
        return DetectionResult(
            detections=detections,
            is_event=is_event,
            max_hazard_level=max_hazard,
            trigger_confidence=max_conf
        )


class YOLODetector(BaseDetector):
    """YOLOv8 detector wrapper using Ultralytics."""
    
    MODEL_VARIANTS = {
        "yolov8n": "yolov8n.pt",
        "yolov8s": "yolov8s.pt",
        "yolov8m": "yolov8m.pt",
        "yolov8l": "yolov8l.pt",
        "yolov8x": "yolov8x.pt",
    }
    
    def __init__(
        self,
        model_name: str = "yolov8s",
        pretrained: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.pretrained = pretrained
        self.model = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load YOLOv8 model."""
        try:
            from ultralytics import YOLO
            
            if self.model_name not in self.MODEL_VARIANTS:
                raise ValueError(f"Unknown YOLO model: {self.model_name}")
            
            weight_file = self.MODEL_VARIANTS[self.model_name]
            self.model = YOLO(weight_file)
            self.model.to(self.device)
            logger.info(f"Loaded {self.model_name} on {self.device}")
            
        except ImportError:
            logger.error("ultralytics not installed. Run: pip install ultralytics")
            raise
    
    def detect(self, image: np.ndarray) -> DetectionResult:
        """Run YOLO detection on image."""
        # Run inference
        results = self.model(
            image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False
        )[0]
        
        detections = []
        h, w = image.shape[:2]
        
        for box in results.boxes:
            # Get bounding box (normalized)
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            bbox = (x1/w, y1/h, x2/w, y2/h)
            
            # Get class info
            class_id = int(box.cls[0])
            class_name = results.names[class_id]
            confidence = float(box.conf[0])
            hazard_level = self.get_hazard_level(class_name)
            
            detections.append(Detection(
                bbox=bbox,
                class_id=class_id,
                class_name=class_name,
                confidence=confidence,
                hazard_level=hazard_level
            ))
        
        is_event, max_hazard, max_conf = self.should_trigger(detections)
        
        return DetectionResult(
            detections=detections,
            is_event=is_event,
            max_hazard_level=max_hazard,
            trigger_confidence=max_conf
        )


def get_detector(model_name: str, **kwargs) -> BaseDetector:
    """Factory function to get detector by name."""
    if model_name.startswith("detr"):
        return DETRDetector(model_name=model_name, **kwargs)
    elif model_name.startswith("yolo"):
        return YOLODetector(model_name=model_name, **kwargs)
    else:
        raise ValueError(f"Unknown detector: {model_name}")
