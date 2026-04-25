"""
KV-cache adapter boundary for evidence-aware sparse decoding.

The FC selector operates in visual-token coordinates. This adapter maps those
visual indices into mixed text/visual KV-cache positions and applies the keep
set to mockable HuggingFace-style ``past_key_values`` tensors. It is designed
to fail closed: uncertain mappings or unsafe selector outputs become dense
decisions instead of silently dropping evidence.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Sequence, Set, Tuple, Union

import torch

from src.decoding.fc_sparse import FCSparseSelection


SparseSelectionLike = Union[FCSparseSelection, Dict[str, Any]]


@dataclass(frozen=True)
class KVAdapterConfig:
    """Configuration for mapping selector outputs onto KV-cache positions."""

    sink_tokens: int = 4
    recent_tokens: int = 32
    min_keep: int = 1
    preserve_text_tokens: bool = True
    dense_fallback: bool = True


@dataclass(frozen=True)
class KVAdapterDecision:
    """Decision returned by the KV adapter before cache mutation."""

    keep_indices: torch.Tensor
    visual_keep_indices: torch.Tensor
    evidence_kv_indices: torch.Tensor
    anchor_kv_indices: torch.Tensor
    dropped_indices: torch.Tensor
    sequence_length: int
    visual_token_start: int
    visual_token_count: int
    used_dense_fallback: bool
    fallback_reason: Optional[str] = None

    @property
    def kv_keep_ratio(self) -> float:
        if self.sequence_length <= 0:
            return 0.0
        return float(self.keep_indices.numel()) / float(self.sequence_length)

    @property
    def evidence_retention(self) -> float:
        if self.evidence_kv_indices.numel() == 0:
            return 1.0
        keep = {int(i) for i in self.keep_indices.tolist()}
        evidence = {int(i) for i in self.evidence_kv_indices.tolist()}
        return len(keep & evidence) / max(len(evidence), 1)

    @property
    def adapter_status(self) -> str:
        return "dense_fallback" if self.used_dense_fallback else "sparse"

    def to_dict(self) -> Dict[str, Any]:
        """Return JSON-serializable diagnostics for traces and appendix logs."""
        return {
            "adapter_status": self.adapter_status,
            "fallback_reason": self.fallback_reason,
            "sequence_length": self.sequence_length,
            "visual_token_start": self.visual_token_start,
            "visual_token_count": self.visual_token_count,
            "kv_keep_ratio": self.kv_keep_ratio,
            "kv_evidence_retention": self.evidence_retention,
            "kv_keep_indices": [int(i) for i in self.keep_indices.tolist()],
            "kv_anchor_indices": [int(i) for i in self.anchor_kv_indices.tolist()],
            "kv_evidence_indices": [int(i) for i in self.evidence_kv_indices.tolist()],
            "kv_dropped_indices": [int(i) for i in self.dropped_indices.tolist()],
        }


class SparseKVAdapter:
    """Map visual-token sparse selections onto KV-cache tensors."""

    def __init__(self, config: Optional[KVAdapterConfig] = None):
        self.config = config or KVAdapterConfig()

    def plan(
        self,
        selection: SparseSelectionLike,
        *,
        sequence_length: int,
        visual_token_start: int,
        visual_token_count: Optional[int] = None,
    ) -> KVAdapterDecision:
        """
        Build a KV keep plan from a visual-token selection.

        Args:
            selection: ``FCSparseSelection`` or equivalent dict in visual-token
                coordinates.
            sequence_length: Total mixed text/visual KV sequence length.
            visual_token_start: First KV position occupied by visual tokens.
            visual_token_count: Number of visual tokens in the KV sequence.
        """
        payload = self._selection_payload(selection)
        num_visual = int(
            visual_token_count
            if visual_token_count is not None
            else payload.get("num_total", 0)
        )
        seq_len = int(sequence_length)
        visual_start = int(visual_token_start)

        mapping_error = self._mapping_error(
            seq_len=seq_len,
            visual_start=visual_start,
            visual_count=num_visual,
            selection_total=int(payload.get("num_total", num_visual)),
        )
        if mapping_error:
            return self._dense_decision(
                seq_len=max(seq_len, 0),
                visual_start=max(visual_start, 0),
                visual_count=max(num_visual, 0),
                selection=payload,
                reason=mapping_error,
            )

        if bool(payload.get("used_dense_fallback", False)):
            return self._dense_decision(
                seq_len=seq_len,
                visual_start=visual_start,
                visual_count=num_visual,
                selection=payload,
                reason="selector_dense_fallback",
            )

        visual_keep = self._indices_from_payload(payload, "keep_indices", num_visual)
        visual_evidence = self._indices_from_payload(payload, "evidence_indices", num_visual)
        visual_anchors = self._indices_from_payload(payload, "anchor_indices", num_visual)

        mapped_visual_keep = {visual_start + idx for idx in visual_keep}
        mapped_evidence = {visual_start + idx for idx in visual_evidence}
        mapped_anchors = {visual_start + idx for idx in visual_anchors}

        anchors = set(mapped_anchors)
        anchors.update(mapped_evidence)
        anchors.update(range(min(seq_len, max(0, int(self.config.sink_tokens)))))
        recent_count = max(0, int(self.config.recent_tokens))
        anchors.update(range(max(0, seq_len - recent_count), seq_len))

        keep = set(mapped_visual_keep)
        keep.update(anchors)
        if self.config.preserve_text_tokens:
            keep.update(range(0, visual_start))
            keep.update(range(visual_start + num_visual, seq_len))

        reason = self._safety_error(keep, anchors, mapped_evidence, seq_len)
        if reason:
            return self._dense_decision(
                seq_len=seq_len,
                visual_start=visual_start,
                visual_count=num_visual,
                selection=payload,
                reason=reason,
            )

        keep_tensor = torch.tensor(sorted(keep), dtype=torch.long)
        dropped = sorted(set(range(seq_len)) - keep)
        return KVAdapterDecision(
            keep_indices=keep_tensor,
            visual_keep_indices=torch.tensor(sorted(visual_keep), dtype=torch.long),
            evidence_kv_indices=torch.tensor(sorted(mapped_evidence), dtype=torch.long),
            anchor_kv_indices=torch.tensor(sorted(anchors), dtype=torch.long),
            dropped_indices=torch.tensor(dropped, dtype=torch.long),
            sequence_length=seq_len,
            visual_token_start=visual_start,
            visual_token_count=num_visual,
            used_dense_fallback=False,
            fallback_reason=None,
        )

    def apply(self, past_key_values: Any, decision: KVAdapterDecision) -> Any:
        """
        Apply a sparse KV decision to HuggingFace-style cache tensors.

        The method supports nested tuples/lists containing tensors whose sequence
        dimension equals ``decision.sequence_length``. If the decision fell back
        dense, the original object is returned unchanged.
        """
        if decision.used_dense_fallback:
            return past_key_values

        keep = decision.keep_indices
        return self._apply_recursive(past_key_values, keep, decision.sequence_length)

    def _apply_recursive(self, value: Any, keep: torch.Tensor, sequence_length: int) -> Any:
        if torch.is_tensor(value):
            seq_dim = self._find_sequence_dim(value, sequence_length)
            if seq_dim is None:
                return value
            return value.index_select(seq_dim, keep.to(value.device))

        if isinstance(value, tuple):
            return tuple(self._apply_recursive(v, keep, sequence_length) for v in value)

        if isinstance(value, list):
            return [self._apply_recursive(v, keep, sequence_length) for v in value]

        return value

    @staticmethod
    def _find_sequence_dim(tensor: torch.Tensor, sequence_length: int) -> Optional[int]:
        matches = [idx for idx, size in enumerate(tensor.shape) if int(size) == sequence_length]
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]
        # HuggingFace KV tensors are commonly [B, H, L, D].
        if tensor.dim() >= 3 and int(tensor.shape[-2]) == sequence_length:
            return tensor.dim() - 2
        return matches[-1]

    def _dense_decision(
        self,
        *,
        seq_len: int,
        visual_start: int,
        visual_count: int,
        selection: Dict[str, Any],
        reason: str,
    ) -> KVAdapterDecision:
        keep = torch.arange(max(seq_len, 0), dtype=torch.long)
        visual_keep = self._indices_from_payload(selection, "keep_indices", max(visual_count, 0))
        visual_evidence = self._indices_from_payload(
            selection,
            "evidence_indices",
            max(visual_count, 0),
        )
        evidence = {
            visual_start + idx
            for idx in visual_evidence
            if 0 <= visual_start + idx < max(seq_len, 0)
        }
        return KVAdapterDecision(
            keep_indices=keep,
            visual_keep_indices=torch.tensor(sorted(visual_keep), dtype=torch.long),
            evidence_kv_indices=torch.tensor(sorted(evidence), dtype=torch.long),
            anchor_kv_indices=torch.tensor(sorted(evidence), dtype=torch.long),
            dropped_indices=torch.empty(0, dtype=torch.long),
            sequence_length=max(seq_len, 0),
            visual_token_start=max(visual_start, 0),
            visual_token_count=max(visual_count, 0),
            used_dense_fallback=True,
            fallback_reason=reason,
        )

    @staticmethod
    def _selection_payload(selection: SparseSelectionLike) -> Dict[str, Any]:
        if isinstance(selection, FCSparseSelection):
            return selection.to_dict()
        if isinstance(selection, dict):
            return dict(selection)
        raise TypeError("selection must be FCSparseSelection or dict")

    @staticmethod
    def _indices_from_payload(
        payload: Dict[str, Any],
        field_name: str,
        upper_bound: int,
    ) -> Set[int]:
        values = payload.get(field_name, ())
        if torch.is_tensor(values):
            raw: Iterable[Any] = values.detach().cpu().tolist()
        else:
            raw = values or ()
        return {
            int(idx)
            for idx in raw
            if 0 <= int(idx) < max(upper_bound, 0)
        }

    @staticmethod
    def _mapping_error(
        *,
        seq_len: int,
        visual_start: int,
        visual_count: int,
        selection_total: int,
    ) -> Optional[str]:
        if seq_len <= 0:
            return "invalid_sequence_length"
        if visual_start < 0:
            return "invalid_visual_token_start"
        if visual_count < 0:
            return "invalid_visual_token_count"
        if selection_total != visual_count:
            return "selection_visual_count_mismatch"
        if visual_start + visual_count > seq_len:
            return "visual_span_out_of_bounds"
        return None

    def _safety_error(
        self,
        keep: Set[int],
        anchors: Set[int],
        evidence: Set[int],
        seq_len: int,
    ) -> Optional[str]:
        if len(keep) < max(0, int(self.config.min_keep)):
            return "below_min_keep"
        if not evidence.issubset(keep):
            return "evidence_anchor_dropped"
        if not anchors.issubset(keep):
            return "hard_anchor_dropped"
        if any(idx < 0 or idx >= seq_len for idx in keep):
            return "keep_index_out_of_bounds"
        return None
