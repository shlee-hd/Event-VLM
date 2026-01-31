"""
Risk-Sensitive Detection Loss for Stage 1.
Prioritizes high-risk hazard categories during detector training.
"""

from typing import Dict, List, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class RiskSensitiveLoss(nn.Module):
    """
    Risk-Sensitive Detection Loss that assigns higher weights to critical hazards.
    
    L_detect = Σ w(c_k) * L_focal(p_k, y_k)
    
    where w(c_k) = λ_crit if c_k ∈ C_critical
                   λ_high if c_k ∈ C_high
                   1.0    otherwise
    """
    
    def __init__(
        self,
        lambda_crit: float = 3.0,
        lambda_high: float = 2.0,
        lambda_standard: float = 1.0,
        focal_alpha: float = 0.25,
        focal_gamma: float = 2.0,
        hazard_classes: Optional[Dict[str, List[int]]] = None
    ):
        """
        Args:
            lambda_crit: Weight for critical hazards (fire, smoke, collapse)
            lambda_high: Weight for high-risk hazards (forklift, machinery)
            lambda_standard: Weight for standard detections
            focal_alpha: Focal loss alpha parameter
            focal_gamma: Focal loss gamma parameter
            hazard_classes: Dict mapping hazard level to class indices
        """
        super().__init__()
        self.lambda_crit = lambda_crit
        self.lambda_high = lambda_high
        self.lambda_standard = lambda_standard
        self.focal_alpha = focal_alpha
        self.focal_gamma = focal_gamma
        
        # Default hazard class indices (will be overridden by config)
        self.hazard_classes = hazard_classes or {
            "critical": [],  # fire, smoke indices
            "high": [],      # forklift, machinery indices
            "standard": []   # person, vehicle indices
        }
        
        # Build class to weight mapping
        self._build_weight_mapping()
    
    def _build_weight_mapping(self) -> None:
        """Build class index to weight mapping."""
        self.class_weights = {}
        
        for cls_idx in self.hazard_classes.get("critical", []):
            self.class_weights[cls_idx] = self.lambda_crit
        
        for cls_idx in self.hazard_classes.get("high", []):
            self.class_weights[cls_idx] = self.lambda_high
        
        for cls_idx in self.hazard_classes.get("standard", []):
            self.class_weights[cls_idx] = self.lambda_standard
    
    def get_weight(self, class_idx: int) -> float:
        """Get risk weight for a class index."""
        return self.class_weights.get(class_idx, 1.0)
    
    def focal_loss(
        self,
        pred: torch.Tensor,
        target: torch.Tensor,
        alpha: float,
        gamma: float
    ) -> torch.Tensor:
        """
        Compute focal loss for binary classification.
        
        FL(p_t) = -α_t * (1 - p_t)^γ * log(p_t)
        """
        p = torch.sigmoid(pred)
        ce_loss = F.binary_cross_entropy_with_logits(pred, target, reduction='none')
        p_t = p * target + (1 - p) * (1 - target)
        focal_weight = (1 - p_t) ** gamma
        alpha_t = alpha * target + (1 - alpha) * (1 - target)
        loss = alpha_t * focal_weight * ce_loss
        return loss
    
    def forward(
        self,
        pred_logits: torch.Tensor,
        target_classes: torch.Tensor,
        pred_boxes: Optional[torch.Tensor] = None,
        target_boxes: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Compute risk-sensitive detection loss.
        
        Args:
            pred_logits: Predicted class logits [B, N, C]
            target_classes: Target class indices [B, N]
            pred_boxes: Predicted boxes [B, N, 4] (optional)
            target_boxes: Target boxes [B, N, 4] (optional)
            
        Returns:
            Dict with loss components
        """
        batch_size, num_queries, num_classes = pred_logits.shape
        
        # Create one-hot targets
        target_onehot = F.one_hot(target_classes, num_classes).float()
        
        # Compute focal loss for each class
        focal_losses = self.focal_loss(
            pred_logits.view(-1, num_classes),
            target_onehot.view(-1, num_classes),
            self.focal_alpha,
            self.focal_gamma
        )  # [B*N, C]
        
        # Apply risk-sensitive weights
        weights = torch.ones(num_classes, device=pred_logits.device)
        for cls_idx, weight in self.class_weights.items():
            if cls_idx < num_classes:
                weights[cls_idx] = weight
        
        # Weighted loss per class
        weighted_focal = focal_losses * weights.unsqueeze(0)
        
        # Sum over classes, mean over queries and batch
        cls_loss = weighted_focal.sum(dim=-1).view(batch_size, num_queries).mean()
        
        losses = {"loss_cls": cls_loss}
        
        # Optional: box regression loss (L1 + GIoU)
        if pred_boxes is not None and target_boxes is not None:
            # Mask for non-background targets
            mask = target_classes > 0  # Assuming 0 is background
            
            if mask.any():
                l1_loss = F.l1_loss(
                    pred_boxes[mask],
                    target_boxes[mask],
                    reduction='mean'
                )
                
                giou_loss = self._giou_loss(
                    pred_boxes[mask],
                    target_boxes[mask]
                )
                
                losses["loss_bbox"] = l1_loss
                losses["loss_giou"] = giou_loss
        
        # Total loss
        losses["loss_total"] = sum(losses.values())
        
        return losses
    
    def _giou_loss(
        self,
        pred_boxes: torch.Tensor,
        target_boxes: torch.Tensor
    ) -> torch.Tensor:
        """Compute Generalized IoU loss."""
        # Convert to x1y1x2y2 format if needed
        pred_x1, pred_y1, pred_x2, pred_y2 = pred_boxes.unbind(-1)
        tgt_x1, tgt_y1, tgt_x2, tgt_y2 = target_boxes.unbind(-1)
        
        # Intersection
        inter_x1 = torch.max(pred_x1, tgt_x1)
        inter_y1 = torch.max(pred_y1, tgt_y1)
        inter_x2 = torch.min(pred_x2, tgt_x2)
        inter_y2 = torch.min(pred_y2, tgt_y2)
        
        inter_area = (inter_x2 - inter_x1).clamp(min=0) * (inter_y2 - inter_y1).clamp(min=0)
        
        # Union
        pred_area = (pred_x2 - pred_x1) * (pred_y2 - pred_y1)
        tgt_area = (tgt_x2 - tgt_x1) * (tgt_y2 - tgt_y1)
        union_area = pred_area + tgt_area - inter_area
        
        # IoU
        iou = inter_area / (union_area + 1e-8)
        
        # Enclosing box
        enc_x1 = torch.min(pred_x1, tgt_x1)
        enc_y1 = torch.min(pred_y1, tgt_y1)
        enc_x2 = torch.max(pred_x2, tgt_x2)
        enc_y2 = torch.max(pred_y2, tgt_y2)
        enc_area = (enc_x2 - enc_x1) * (enc_y2 - enc_y1)
        
        # GIoU
        giou = iou - (enc_area - union_area) / (enc_area + 1e-8)
        
        return (1 - giou).mean()


class FocalLoss(nn.Module):
    """Standalone Focal Loss for classification."""
    
    def __init__(
        self,
        alpha: float = 0.25,
        gamma: float = 2.0,
        reduction: str = "mean"
    ):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(
        self,
        pred: torch.Tensor,
        target: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            pred: Predictions [B, C] or [B, N, C]
            target: Target indices [B] or [B, N]
        """
        ce_loss = F.cross_entropy(pred, target, reduction='none')
        p_t = torch.exp(-ce_loss)
        focal_weight = (1 - p_t) ** self.gamma
        loss = self.alpha * focal_weight * ce_loss
        
        if self.reduction == "mean":
            return loss.mean()
        elif self.reduction == "sum":
            return loss.sum()
        return loss
