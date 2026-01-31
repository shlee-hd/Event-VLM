"""
Unit tests for Event-VLM modules.
"""

import pytest
import numpy as np
import torch
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestTokenPruner:
    """Tests for TokenPruner module."""
    
    def test_bbox_to_patch_indices(self):
        """Test bbox to patch index conversion."""
        from src.pruning import TokenPruner
        
        pruner = TokenPruner(image_size=336, patch_size=14)
        
        # Test center box
        indices = pruner.bbox_to_patch_indices((0.4, 0.4, 0.6, 0.6), dilation=1.0)
        assert len(indices) > 0
        assert all(0 <= idx < pruner.num_patches for idx in indices)
        
        # Test full image box
        indices = pruner.bbox_to_patch_indices((0.0, 0.0, 1.0, 1.0), dilation=1.0)
        assert len(indices) == pruner.num_patches
    
    def test_dilation(self):
        """Test dilation increases patch count."""
        from src.pruning import TokenPruner
        
        pruner = TokenPruner(image_size=336, patch_size=14)
        bbox = (0.4, 0.4, 0.6, 0.6)
        
        indices_no_dilation = pruner.bbox_to_patch_indices(bbox, dilation=1.0)
        indices_with_dilation = pruner.bbox_to_patch_indices(bbox, dilation=1.5)
        
        assert len(indices_with_dilation) >= len(indices_no_dilation)
    
    def test_create_mask(self):
        """Test mask creation from detections."""
        from src.pruning import TokenPruner
        from src.detector.detr_wrapper import Detection
        
        pruner = TokenPruner(image_size=336, patch_size=14)
        
        detections = [
            Detection(
                bbox=(0.3, 0.3, 0.5, 0.5),
                class_id=0,
                class_name="person",
                confidence=0.9,
                hazard_level="standard"
            )
        ]
        
        mask = pruner.create_mask(detections)
        
        assert mask.shape[0] == pruner.num_patches
        assert mask.dtype == torch.bool
        assert mask.sum() > 0  # Some patches should be kept
    
    def test_prune_tokens(self):
        """Test token pruning."""
        from src.pruning import TokenPruner
        from src.detector.detr_wrapper import Detection
        
        pruner = TokenPruner(image_size=336, patch_size=14)
        
        # Create dummy tokens [1, 576, 768]
        tokens = torch.randn(1, 576, 768)
        
        detections = [
            Detection(
                bbox=(0.4, 0.4, 0.6, 0.6),
                class_id=0,
                class_name="fire",
                confidence=0.95,
                hazard_level="critical"
            )
        ]
        
        pruned_tokens, result = pruner.prune(tokens, detections, return_mask=True)
        
        assert pruned_tokens.shape[0] == 1
        assert pruned_tokens.shape[1] < tokens.shape[1]
        assert pruned_tokens.shape[2] == tokens.shape[2]
        assert result.reduction_ratio > 0


class TestAdaptiveDilation:
    """Tests for AdaptiveDilation module."""
    
    def test_amorphous_vs_rigid(self):
        """Test that amorphous objects get higher dilation."""
        from src.pruning import AdaptiveDilation
        
        dilation = AdaptiveDilation(alpha_base=1.2, beta=0.5)
        
        fire_dilation = dilation.get_dilation("fire")
        person_dilation = dilation.get_dilation("person")
        
        # Fire (amorphous) should have higher dilation than person (rigid)
        assert fire_dilation > person_dilation
    
    def test_dilation_bounds(self):
        """Test dilation values are reasonable."""
        from src.pruning import AdaptiveDilation
        
        dilation = AdaptiveDilation(alpha_base=1.2, beta=0.5)
        
        for class_name in ["fire", "smoke", "person", "vehicle", "unknown"]:
            d = dilation.get_dilation(class_name)
            assert 1.0 <= d <= 2.0  # Reasonable bounds


class TestRiskSensitiveLoss:
    """Tests for RiskSensitiveLoss module."""
    
    def test_loss_computation(self):
        """Test basic loss computation."""
        from src.detector.risk_loss import RiskSensitiveLoss
        
        loss_fn = RiskSensitiveLoss(
            lambda_crit=3.0,
            lambda_high=2.0,
            hazard_classes={
                "critical": [0, 1],
                "high": [2, 3],
                "standard": [4, 5]
            }
        )
        
        # Dummy predictions [B, N, C]
        pred_logits = torch.randn(2, 10, 6)
        target_classes = torch.randint(0, 6, (2, 10))
        
        losses = loss_fn(pred_logits, target_classes)
        
        assert "loss_cls" in losses
        assert "loss_total" in losses
        assert losses["loss_total"] > 0
    
    def test_weights_applied(self):
        """Test that class weights are correctly applied."""
        from src.detector.risk_loss import RiskSensitiveLoss
        
        loss_fn = RiskSensitiveLoss(
            lambda_crit=3.0,
            lambda_high=2.0,
            hazard_classes={
                "critical": [0],
                "high": [1],
                "standard": [2]
            }
        )
        
        assert loss_fn.get_weight(0) == 3.0
        assert loss_fn.get_weight(1) == 2.0
        assert loss_fn.get_weight(2) == 1.0
        assert loss_fn.get_weight(99) == 1.0  # Default


class TestHazardPriorityPrompting:
    """Tests for HazardPriorityPrompting module."""
    
    def test_prompt_selection(self):
        """Test prompt selection by hazard level."""
        from src.vlm import HazardPriorityPrompting
        
        prompting = HazardPriorityPrompting()
        
        critical_prompt = prompting.select_prompt("critical")
        standard_prompt = prompting.select_prompt("standard")
        
        assert "CRITICAL" in critical_prompt or "critical" in critical_prompt.lower()
        assert len(critical_prompt) > len(standard_prompt)  # Critical prompts are more detailed
    
    def test_weight_based_selection(self):
        """Test prompt selection by risk weight."""
        from src.vlm import HazardPriorityPrompting
        
        prompting = HazardPriorityPrompting(
            threshold_critical=2.5,
            threshold_high=1.5
        )
        
        critical_prompt = prompting.select_prompt_by_weight(3.0)
        high_prompt = prompting.select_prompt_by_weight(2.0)
        standard_prompt = prompting.select_prompt_by_weight(1.0)
        
        assert critical_prompt != high_prompt
        assert high_prompt != standard_prompt


class TestMetrics:
    """Tests for evaluation metrics."""
    
    def test_auc_meter(self):
        """Test AUC meter computation."""
        from src.utils.metrics import AUCMeter
        
        meter = AUCMeter()
        
        # Perfect predictions
        meter.update(np.array([0.9, 0.1]), np.array([1, 0]))
        metrics = meter.compute()
        
        assert "auc" in metrics
        assert metrics["auc"] == 1.0
    
    def test_trigger_reliability_meter(self):
        """Test trigger reliability meter."""
        from src.utils.metrics import TriggerReliabilityMeter
        
        meter = TriggerReliabilityMeter()
        
        # All correct triggers
        meter.update(True, True)
        meter.update(False, False)
        
        metrics = meter.compute()
        
        assert metrics["recall@trigger"] == 1.0
        assert metrics["precision@trigger"] == 1.0


class TestIntegration:
    """Integration tests."""
    
    def test_config_loading(self):
        """Test configuration loading."""
        from src.config import EventVLMConfig
        
        config = EventVLMConfig()
        
        assert config.detector.model == "detr-l"
        assert config.pruning.alpha_base == 1.2
        assert config.vlm.quantization == "4bit"
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_mock_pipeline(self):
        """Test pipeline with mock VLM."""
        from src.config import EventVLMConfig
        from src.pipeline import EventVLM
        from src.vlm.llava_wrapper import MockLLaVAWrapper
        
        config = EventVLMConfig()
        config.device = "cpu"
        
        # Would test with mock here
        # pipeline = EventVLM(config=config)
        # ...
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
