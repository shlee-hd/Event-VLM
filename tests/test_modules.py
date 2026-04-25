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


class TestFCSparseDecoding:
    """Tests for evidence-aware FC sparse decoding."""

    def test_preserves_evidence_sink_and_recent_anchors(self):
        from src.decoding import EvidenceAwareFCSparseSelector, FCSparseConfig

        scores = torch.tensor([0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6])
        selector = EvidenceAwareFCSparseSelector(
            FCSparseConfig(
                enabled=True,
                budget=5,
                min_keep=1,
                sink_tokens=1,
                recent_tokens=1,
            )
        )

        selection = selector.select(
            frequency_scores=scores,
            evidence_indices=[4]
        )

        kept = set(selection.keep_indices.tolist())
        assert {0, 4, 7}.issubset(kept)
        assert len(kept) == 5
        assert selection.evidence_retention == 1.0
        assert not selection.used_dense_fallback

    def test_dense_fallback_when_budget_breaks_min_keep(self):
        from src.decoding import EvidenceAwareFCSparseSelector, FCSparseConfig

        selector = EvidenceAwareFCSparseSelector(
            FCSparseConfig(
                enabled=True,
                budget=2,
                min_keep=4,
                sink_tokens=1,
                recent_tokens=1,
            )
        )

        selection = selector.select(
            num_entries=8,
            evidence_indices=[3]
        )

        assert selection.used_dense_fallback
        assert selection.keep_indices.tolist() == list(range(8))
        assert selection.evidence_retention == 1.0

    def test_estimates_frequency_scores_from_token_states(self):
        from src.decoding import EvidenceAwareFCSparseSelector, FCSparseConfig

        selector = EvidenceAwareFCSparseSelector(
            FCSparseConfig(enabled=True, budget=2, min_keep=1)
        )
        token_states = torch.randn(1, 4, 16)

        scores = selector.estimate_frequency_scores(token_states)

        assert scores.shape == (4,)
        assert torch.isfinite(scores).all()


class TestSparseKVAdapter:
    """Tests for visual-token to mixed-KV sparse mapping."""

    def test_maps_visual_evidence_into_mixed_kv_positions(self):
        from src.decoding import EvidenceAwareFCSparseSelector, FCSparseConfig
        from src.decoding import KVAdapterConfig, SparseKVAdapter

        selector = EvidenceAwareFCSparseSelector(
            FCSparseConfig(
                enabled=True,
                budget=4,
                min_keep=1,
                sink_tokens=0,
                recent_tokens=0,
            )
        )
        selection = selector.select(
            frequency_scores=torch.tensor([0.1, 0.9, 0.2, 0.8, 0.3, 0.7]),
            evidence_indices=[2],
        )

        adapter = SparseKVAdapter(
            KVAdapterConfig(
                sink_tokens=1,
                recent_tokens=1,
                preserve_text_tokens=True,
            )
        )
        decision = adapter.plan(
            selection,
            sequence_length=10,
            visual_token_start=2,
            visual_token_count=6,
        )

        kept = set(decision.keep_indices.tolist())
        assert 4 in kept  # visual evidence index 2 maps to KV index 4
        assert {0, 9}.issubset(kept)  # global sink/recent anchors
        assert {0, 1, 8, 9}.issubset(kept)  # text positions are preserved
        assert decision.evidence_retention == 1.0
        assert not decision.used_dense_fallback

    def test_applies_keep_indices_to_mock_past_key_values(self):
        from src.decoding import EvidenceAwareFCSparseSelector, FCSparseConfig
        from src.decoding import KVAdapterConfig, SparseKVAdapter

        selector = EvidenceAwareFCSparseSelector(
            FCSparseConfig(
                enabled=True,
                budget=2,
                min_keep=1,
                sink_tokens=0,
                recent_tokens=0,
            )
        )
        selection = selector.select(
            frequency_scores=torch.tensor([0.1, 0.9, 0.2, 0.8]),
            evidence_indices=[2],
        )
        adapter = SparseKVAdapter(
            KVAdapterConfig(
                sink_tokens=0,
                recent_tokens=0,
                preserve_text_tokens=False,
            )
        )
        decision = adapter.plan(
            selection,
            sequence_length=4,
            visual_token_start=0,
            visual_token_count=4,
        )
        values = torch.arange(4).view(1, 1, 4, 1)
        past = ((values, values + 10),)

        adapted = adapter.apply(past, decision)

        expected = decision.keep_indices.tolist()
        assert adapted[0][0].shape[2] == len(expected)
        assert adapted[0][0][0, 0, :, 0].tolist() == expected
        assert adapted[0][1][0, 0, :, 0].tolist() == [i + 10 for i in expected]

    def test_uncertain_mapping_falls_back_dense(self):
        from src.decoding import EvidenceAwareFCSparseSelector, FCSparseConfig
        from src.decoding import SparseKVAdapter

        selector = EvidenceAwareFCSparseSelector(
            FCSparseConfig(enabled=True, budget=2, min_keep=1)
        )
        selection = selector.select(num_entries=4, evidence_indices=[1])

        decision = SparseKVAdapter().plan(
            selection,
            sequence_length=5,
            visual_token_start=3,
            visual_token_count=4,
        )

        assert decision.used_dense_fallback
        assert decision.fallback_reason == "visual_span_out_of_bounds"
        assert decision.keep_indices.tolist() == list(range(5))


class TestLLaVASparseBoundary:
    """Tests for the public sparse_generation hook without loading LLaVA."""

    def test_sparse_hook_is_used_when_model_supports_adapter(self):
        from src.vlm.llava_wrapper import LLaVAWrapper

        class FakeTokenizer:
            def __call__(self, text, return_tensors):
                class Encoded:
                    input_ids = torch.tensor([[1, 2, 3]])

                return Encoded()

            def decode(self, output_ids, skip_special_tokens):
                return "USER: <image>\nPrompt\nASSISTANT: sparse response"

        class FakeModel:
            def __init__(self):
                self.used_sparse = False
                self.sparse_decoding = None

            def generate_with_sparse_cache(self, **kwargs):
                self.used_sparse = True
                self.sparse_decoding = kwargs["sparse_decoding"]
                return torch.tensor([[1, 2, 3, 4]])

            def generate(self, **kwargs):
                return torch.tensor([[1, 2, 3, 4]])

        wrapper = LLaVAWrapper(device="cpu")
        wrapper._loaded = True
        wrapper.tokenizer = FakeTokenizer()
        wrapper.model = FakeModel()

        output = wrapper.generate(
            image=np.zeros((16, 16, 3), dtype=np.uint8),
            prompt="Prompt",
            pruned_tokens=torch.randn(1, 6, 8),
            sparse_selection={
                "num_total": 6,
                "requested_budget": 3,
                "effective_budget": 3,
                "keep_ratio": 0.5,
                "evidence_retention": 1.0,
                "used_dense_fallback": False,
                "keep_indices": [1, 2, 5],
                "anchor_indices": [2],
                "frequency_indices": [1, 5],
                "dropped_indices": [0, 3, 4],
                "evidence_indices": [2],
                "kv_mapping": {
                    "sequence_length": 10,
                    "visual_token_start": 2,
                    "visual_token_count": 6,
                },
                "kv_config": {
                    "sink_tokens": 0,
                    "recent_tokens": 0,
                    "preserve_text_tokens": True,
                },
            },
        )

        assert wrapper.model.used_sparse
        assert output.decoding["adapter_status"] == "sparse"
        assert output.decoding["kv_evidence_indices"] == [4]

    def test_selector_dense_fallback_uses_regular_generate(self):
        from src.vlm.llava_wrapper import LLaVAWrapper

        class FakeTokenizer:
            def __call__(self, text, return_tensors):
                class Encoded:
                    input_ids = torch.tensor([[1, 2, 3]])

                return Encoded()

            def decode(self, output_ids, skip_special_tokens):
                return "USER: <image>\nPrompt\nASSISTANT: dense response"

        class FakeModel:
            def __init__(self):
                self.used_sparse = False
                self.used_dense = False

            def generate_with_sparse_cache(self, **kwargs):
                self.used_sparse = True
                return torch.tensor([[1, 2, 3, 4]])

            def generate(self, **kwargs):
                self.used_dense = True
                return torch.tensor([[1, 2, 3, 4]])

        wrapper = LLaVAWrapper(device="cpu")
        wrapper._loaded = True
        wrapper.tokenizer = FakeTokenizer()
        wrapper.model = FakeModel()

        output = wrapper.generate(
            image=np.zeros((16, 16, 3), dtype=np.uint8),
            prompt="Prompt",
            pruned_tokens=torch.randn(1, 6, 8),
            sparse_selection={
                "num_total": 6,
                "requested_budget": 2,
                "effective_budget": 6,
                "keep_ratio": 1.0,
                "evidence_retention": 1.0,
                "used_dense_fallback": True,
                "keep_indices": [0, 1, 2, 3, 4, 5],
                "anchor_indices": [2],
                "frequency_indices": [],
                "dropped_indices": [],
                "evidence_indices": [2],
                "kv_mapping": {
                    "sequence_length": 10,
                    "visual_token_start": 2,
                    "visual_token_count": 6,
                },
            },
        )

        assert wrapper.model.used_dense
        assert not wrapper.model.used_sparse
        assert output.decoding["adapter_status"] == "dense_fallback"
        assert output.decoding["fallback_reason"] == "selector_dense_fallback"


class TestReportingContract:
    """Tests for fail-closed evidence reporting."""

    def test_valid_report_requires_evidence(self):
        from src.reporting import EvidenceReport, ReportingContract

        contract = ReportingContract()
        report = EvidenceReport(
            event_statement="A person is near smoke.",
            status="valid",
            evidence=()
        )

        validation = contract.validate(report)

        assert validation.resolved_status == "insufficient_evidence"
        assert validation.unsafe_valid
        assert "insufficient_evidence_links" in validation.failures

    def test_valid_report_with_evidence_passes(self):
        from src.reporting import (
            AttributionTuple,
            EvidenceLink,
            EvidenceReport,
            ReportingContract,
        )

        contract = ReportingContract()
        evidence = EvidenceLink(
            evidence_id="f0:det0",
            frame_idx=0,
            timestamp=0.0,
            source="smoke",
            confidence=0.9,
        )
        attribution = AttributionTuple(
            subject="smoke",
            relation="precedes",
            object="evacuation",
            evidence_ids=("f0:det0",),
            subject_time=0.0,
            object_time=1.0,
        )
        report = EvidenceReport(
            event_statement="Smoke appears before evacuation.",
            status="valid",
            evidence=(evidence,),
            attributions=(attribution,),
        )

        validation = contract.validate(report)

        assert validation.resolved_status == "valid"
        assert validation.is_valid
        assert not validation.unsafe_valid

    def test_unsafe_valid_rate(self):
        from src.reporting import (
            ContractValidation,
            unsafe_valid_rate,
        )

        validations = [
            ContractValidation("valid", "valid", True),
            ContractValidation("valid", "insufficient_evidence", False),
            ContractValidation("abstain", "abstain", True),
        ]

        assert unsafe_valid_rate(validations) == 0.5


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

    def test_pipeline_emits_decoding_and_reporting_metadata(self):
        """Test the method diagnostics boundary without loading heavy models."""
        from src.config import EventVLMConfig
        from src.decoding import EvidenceAwareFCSparseSelector, FCSparseConfig
        from src.detector.detr_wrapper import Detection, DetectionResult
        from src.pipeline import EventVLM
        from src.pruning import TokenPruner
        from src.reporting import ReportingContract
        from src.vlm import HazardPriorityPrompting
        from src.vlm.llava_wrapper import MockLLaVAWrapper

        class MockDetector:
            def detect(self, frame):
                detection = Detection(
                    bbox=(0.4, 0.4, 0.6, 0.6),
                    class_id=0,
                    class_name="smoke",
                    confidence=0.9,
                    hazard_level="critical",
                )
                return DetectionResult(
                    detections=[detection],
                    is_event=True,
                    max_hazard_level="critical",
                    trigger_confidence=0.9,
                )

        config = EventVLMConfig()
        config.device = "cpu"
        config.decoding.enabled = True
        config.decoding.budget = 128
        config.decoding.min_keep = 64

        pipeline = EventVLM(config=config, device="cpu")
        pipeline._initialized = True
        pipeline.detector = MockDetector()
        pipeline.pruner = TokenPruner(
            image_size=config.data.image_size,
            patch_size=14,
            min_tokens=config.pruning.min_tokens,
        )
        pipeline.vlm = MockLLaVAWrapper(device="cpu")
        pipeline.prompting = HazardPriorityPrompting()
        pipeline.decoding_selector = EvidenceAwareFCSparseSelector(
            FCSparseConfig(
                enabled=config.decoding.enabled,
                budget=config.decoding.budget,
                min_keep=config.decoding.min_keep,
            )
        )
        pipeline.reporting_contract = ReportingContract()

        frame = np.zeros((336, 336, 3), dtype=np.uint8)
        result = pipeline.process_frame(frame, frame_idx=3, timestamp=1.5)

        assert result.caption
        assert result.decoding is not None
        assert result.decoding["evidence_retention"] == 1.0
        assert result.report_status == "valid"
        assert result.report is not None
        assert result.report["evidence"][0]["source"] == "smoke"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
