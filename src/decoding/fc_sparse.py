"""
Evidence-aware frequency-chunk sparse decoding.

This module implements the cache-entry selection policy used by the paper
framing. It intentionally keeps the model-specific KV-cache mutation outside
the selector so the invariant can be tested without loading a VLM.
"""

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Set, Tuple

import torch


@dataclass(frozen=True)
class FCSparseConfig:
    """Configuration for evidence-aware sparse cache selection."""

    enabled: bool = False
    budget: Optional[int] = None
    min_keep: int = 64
    sink_tokens: int = 4
    recent_tokens: int = 32
    preserve_evidence: bool = True
    dense_fallback: bool = True
    chunk_count: int = 8
    dominant_chunks: Tuple[int, ...] = (0, 1)


@dataclass(frozen=True)
class FCSparseSelection:
    """Result of selecting KV-cache entries for sparse decoding."""

    keep_indices: torch.Tensor
    anchor_indices: torch.Tensor
    frequency_indices: torch.Tensor
    dropped_indices: torch.Tensor
    evidence_indices: torch.Tensor
    num_total: int
    requested_budget: int
    effective_budget: int
    used_dense_fallback: bool

    @property
    def keep_ratio(self) -> float:
        if self.num_total == 0:
            return 0.0
        return float(self.keep_indices.numel()) / float(self.num_total)

    @property
    def evidence_retention(self) -> float:
        if self.evidence_indices.numel() == 0:
            return 1.0
        keep = set(int(i) for i in self.keep_indices.tolist())
        evidence = set(int(i) for i in self.evidence_indices.tolist())
        return len(keep & evidence) / max(len(evidence), 1)

    def to_dict(self) -> dict:
        """Return JSON-serializable diagnostics."""
        return {
            "num_total": self.num_total,
            "requested_budget": self.requested_budget,
            "effective_budget": self.effective_budget,
            "keep_ratio": self.keep_ratio,
            "evidence_retention": self.evidence_retention,
            "used_dense_fallback": self.used_dense_fallback,
            "num_anchors": int(self.anchor_indices.numel()),
            "num_frequency_ranked": int(self.frequency_indices.numel()),
            "num_dropped": int(self.dropped_indices.numel()),
            "selection_space": "visual",
            "keep_indices": [int(i) for i in self.keep_indices.tolist()],
            "anchor_indices": [int(i) for i in self.anchor_indices.tolist()],
            "frequency_indices": [int(i) for i in self.frequency_indices.tolist()],
            "dropped_indices": [int(i) for i in self.dropped_indices.tolist()],
            "evidence_indices": [int(i) for i in self.evidence_indices.tolist()],
        }


class EvidenceAwareFCSparseSelector:
    """
    Select cache entries using hard evidence anchors plus FC-ranked entries.

    The policy is:

    K_keep = K_sink U K_recent U K_evidence U TopK(S_FC, K)

    Evidence, sink, and recent entries are hard anchors. Frequency scores only
    rank the remaining entries.
    """

    def __init__(self, config: Optional[FCSparseConfig] = None):
        self.config = config or FCSparseConfig()

    def estimate_frequency_scores(self, token_states: torch.Tensor) -> torch.Tensor:
        """
        Estimate per-token dominant frequency-chunk scores from hidden states.

        Args:
            token_states: Tensor shaped [L, D] or [B, L, D].

        Returns:
            Tensor [L] where larger means more energy in configured dominant
            frequency chunks.
        """
        if token_states.dim() == 3:
            if token_states.shape[0] != 1:
                token_states = token_states.mean(dim=0)
            else:
                token_states = token_states.squeeze(0)
        if token_states.dim() != 2:
            raise ValueError("token_states must have shape [L, D] or [B, L, D]")

        states = token_states.float()
        spectrum = torch.fft.rfft(states, dim=-1).abs().pow(2)
        chunks = torch.chunk(
            spectrum,
            max(1, min(self.config.chunk_count, spectrum.shape[-1])),
            dim=-1,
        )
        valid_chunks = [
            chunks[i].mean(dim=-1)
            for i in self.config.dominant_chunks
            if 0 <= i < len(chunks)
        ]
        if not valid_chunks:
            return spectrum.mean(dim=-1)
        return torch.stack(valid_chunks, dim=0).sum(dim=0)

    def select(
        self,
        *,
        num_entries: Optional[int] = None,
        frequency_scores: Optional[torch.Tensor] = None,
        token_states: Optional[torch.Tensor] = None,
        evidence_indices: Optional[Iterable[int]] = None,
    ) -> FCSparseSelection:
        """
        Select cache entries under the configured budget and invariants.

        Args:
            num_entries: Number of cache entries when scores are unavailable.
            frequency_scores: Optional tensor [L] with per-entry scores.
            token_states: Optional hidden states used to estimate scores.
            evidence_indices: Cache indices linked to detector/token evidence.
        """
        if frequency_scores is None and token_states is not None:
            frequency_scores = self.estimate_frequency_scores(token_states)

        if frequency_scores is not None:
            if frequency_scores.dim() != 1:
                raise ValueError("frequency_scores must be a 1D tensor")
            total = int(frequency_scores.numel())
            scores = frequency_scores.detach().float().cpu()
        elif num_entries is not None:
            total = int(num_entries)
            scores = torch.zeros(total, dtype=torch.float32)
        else:
            raise ValueError("Provide num_entries, frequency_scores, or token_states")

        if total < 0:
            raise ValueError("num_entries must be non-negative")

        requested_budget = total if self.config.budget is None else int(self.config.budget)
        requested_budget = max(0, requested_budget)

        if total == 0:
            empty = torch.empty(0, dtype=torch.long)
            return FCSparseSelection(
                keep_indices=empty,
                anchor_indices=empty,
                frequency_indices=empty,
                dropped_indices=empty,
                evidence_indices=empty,
                num_total=0,
                requested_budget=requested_budget,
                effective_budget=0,
                used_dense_fallback=False,
            )

        evidence = self._normalize_indices(evidence_indices, total)
        anchors = self._anchor_indices(total, evidence)

        if not self.config.enabled:
            return self._dense_selection(
                total,
                evidence,
                requested_budget,
                anchors=anchors,
                used_fallback=False,
            )

        effective_budget = min(total, requested_budget)
        min_keep = max(0, min(total, int(self.config.min_keep)))
        required = max(min_keep, len(anchors))

        if self.config.dense_fallback and effective_budget < required:
            return self._dense_selection(
                total,
                evidence,
                requested_budget,
                anchors=anchors,
                used_fallback=True,
            )

        keep = set(anchors)
        remaining_budget = max(0, effective_budget - len(keep))
        ranked = self._rank_by_frequency(scores, keep)
        frequency_keep = ranked[:remaining_budget]
        keep.update(frequency_keep)

        keep_indices = torch.tensor(sorted(keep), dtype=torch.long)
        anchor_indices = torch.tensor(sorted(anchors), dtype=torch.long)
        frequency_indices = torch.tensor(sorted(frequency_keep), dtype=torch.long)
        evidence_tensor = torch.tensor(sorted(evidence), dtype=torch.long)
        dropped = sorted(set(range(total)) - keep)
        dropped_indices = torch.tensor(dropped, dtype=torch.long)

        return FCSparseSelection(
            keep_indices=keep_indices,
            anchor_indices=anchor_indices,
            frequency_indices=frequency_indices,
            dropped_indices=dropped_indices,
            evidence_indices=evidence_tensor,
            num_total=total,
            requested_budget=requested_budget,
            effective_budget=int(keep_indices.numel()),
            used_dense_fallback=False,
        )

    def _dense_selection(
        self,
        total: int,
        evidence: Set[int],
        requested_budget: int,
        *,
        anchors: Optional[Set[int]] = None,
        used_fallback: bool,
    ) -> FCSparseSelection:
        indices = torch.arange(total, dtype=torch.long)
        anchor_tensor = torch.tensor(sorted(anchors or set()), dtype=torch.long)
        evidence_tensor = torch.tensor(sorted(evidence), dtype=torch.long)
        empty = torch.empty(0, dtype=torch.long)
        return FCSparseSelection(
            keep_indices=indices,
            anchor_indices=anchor_tensor,
            frequency_indices=empty,
            dropped_indices=empty,
            evidence_indices=evidence_tensor,
            num_total=total,
            requested_budget=requested_budget,
            effective_budget=total,
            used_dense_fallback=used_fallback,
        )

    def _anchor_indices(self, total: int, evidence: Set[int]) -> Set[int]:
        sink_end = min(total, max(0, int(self.config.sink_tokens)))
        recent_start = max(0, total - max(0, int(self.config.recent_tokens)))
        anchors = set(range(sink_end))
        anchors.update(range(recent_start, total))
        if self.config.preserve_evidence:
            anchors.update(evidence)
        return anchors

    @staticmethod
    def _normalize_indices(indices: Optional[Iterable[int]], total: int) -> Set[int]:
        if indices is None:
            return set()
        return {int(i) for i in indices if 0 <= int(i) < total}

    @staticmethod
    def _rank_by_frequency(scores: torch.Tensor, excluded: Set[int]) -> Sequence[int]:
        candidates = [i for i in range(int(scores.numel())) if i not in excluded]
        return sorted(candidates, key=lambda i: (-float(scores[i]), i))
