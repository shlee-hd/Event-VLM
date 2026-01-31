"""
Adaptive Dilation for amorphous objects.
Expands bounding boxes based on class-specific shape variance.
"""

from typing import Dict, Optional


class AdaptiveDilation:
    """
    Adaptive dilation strategy based on intraclass shape variance.
    
    α_k = α_base * (1 + β * σ_shape(c_k))
    
    where σ_shape is the normalized shape variance computed from training data.
    """
    
    # Default shape variance values (precomputed from training data)
    DEFAULT_SHAPE_VARIANCE = {
        # Amorphous objects (high variance)
        "fire": 0.42,
        "smoke": 0.38,
        "explosion": 0.45,
        "dust": 0.35,
        
        # Semi-rigid objects (medium variance)
        "collapse": 0.28,
        "debris": 0.25,
        "crane": 0.20,
        "forklift": 0.15,
        
        # Rigid objects (low variance)
        "person": 0.12,
        "vehicle": 0.08,
        "car": 0.08,
        "truck": 0.10,
        "helmet": 0.06,
        "vest": 0.08,
        
        # Default for unknown classes
        "default": 0.15
    }
    
    def __init__(
        self,
        alpha_base: float = 1.2,
        beta: float = 0.5,
        shape_variance: Optional[Dict[str, float]] = None
    ):
        """
        Args:
            alpha_base: Base dilation factor (minimum expansion)
            beta: Coefficient for adaptive component
            shape_variance: Dict of class name to shape variance
        """
        self.alpha_base = alpha_base
        self.beta = beta
        
        # Merge with defaults
        self.shape_variance = self.DEFAULT_SHAPE_VARIANCE.copy()
        if shape_variance:
            self.shape_variance.update(shape_variance)
    
    def get_shape_variance(self, class_name: str) -> float:
        """Get shape variance for a class."""
        return self.shape_variance.get(
            class_name.lower(),
            self.shape_variance["default"]
        )
    
    def get_dilation(self, class_name: str) -> float:
        """
        Compute adaptive dilation factor for a class.
        
        α_k = α_base * (1 + β * σ_shape(c_k))
        """
        sigma = self.get_shape_variance(class_name)
        return self.alpha_base * (1 + self.beta * sigma)
    
    def get_dilation_by_hazard_level(self, hazard_level: str) -> float:
        """
        Get dilation factor by hazard level (for fallback).
        
        Critical hazards get highest dilation (often amorphous).
        """
        level_variance = {
            "critical": 0.40,  # Fire, smoke, explosion
            "high": 0.20,      # Forklift, machinery
            "standard": 0.10,  # Person, vehicle
            "none": 0.15
        }
        sigma = level_variance.get(hazard_level, 0.15)
        return self.alpha_base * (1 + self.beta * sigma)
    
    def __repr__(self) -> str:
        return (
            f"AdaptiveDilation(alpha_base={self.alpha_base}, "
            f"beta={self.beta})"
        )


class FixedDilation:
    """Fixed dilation strategy (baseline for comparison)."""
    
    def __init__(self, dilation: float = 1.2):
        self.dilation = dilation
    
    def get_dilation(self, class_name: str) -> float:
        return self.dilation
    
    def get_dilation_by_hazard_level(self, hazard_level: str) -> float:
        return self.dilation
