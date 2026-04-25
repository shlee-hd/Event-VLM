"""
Fail-closed reporting contract for evidence-grounded Event-VLM outputs.

The contract separates natural-language generation from whether a report is
safe to expose as `valid`. If validation fails, the resolved status is lowered
to `insufficient_evidence` instead of silently accepting an unsupported caption.
"""

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


VALID_STATUSES = {"valid", "insufficient_evidence", "abstain"}
VALID_RELATIONS = {"causes", "enables", "precedes", "co_occurs", "describes"}
TEMPORAL_RELATIONS = {"causes", "enables", "precedes"}


@dataclass(frozen=True)
class EvidenceLink:
    """Evidence item supporting a generated report."""

    evidence_id: str
    frame_idx: int
    timestamp: float
    source: str
    confidence: float = 1.0
    bbox: Optional[Tuple[float, float, float, float]] = None
    token_indices: Tuple[int, ...] = ()


@dataclass(frozen=True)
class AttributionTuple:
    """Causal or descriptive relation grounded by evidence links."""

    subject: str
    relation: str
    object: str
    evidence_ids: Tuple[str, ...] = ()
    subject_time: Optional[float] = None
    object_time: Optional[float] = None
    confidence: float = 1.0


@dataclass(frozen=True)
class EvidenceReport:
    """Structured report emitted by Event-VLM."""

    event_statement: str
    status: str
    evidence: Tuple[EvidenceLink, ...] = ()
    attributions: Tuple[AttributionTuple, ...] = ()
    latency_ms: Optional[float] = None
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ReportingPolicy:
    """Validation policy for evidence-grounded reports."""

    min_evidence_links: int = 1
    min_evidence_confidence: float = 0.0
    max_latency_ms: Optional[float] = None
    allow_descriptive_without_temporal_order: bool = True


@dataclass(frozen=True)
class ContractValidation:
    """Validation result for an evidence report."""

    requested_status: str
    resolved_status: str
    is_valid: bool
    failures: Tuple[str, ...] = ()

    @property
    def unsafe_valid(self) -> bool:
        return self.requested_status == "valid" and not self.is_valid


class ReportingContract:
    """Validate and downgrade generated reports according to evidence rules."""

    def __init__(self, policy: Optional[ReportingPolicy] = None):
        self.policy = policy or ReportingPolicy()

    def validate(self, report: EvidenceReport) -> ContractValidation:
        failures: List[str] = []

        if report.status not in VALID_STATUSES:
            failures.append(f"unknown_status:{report.status}")

        if report.status == "abstain":
            return ContractValidation(
                requested_status=report.status,
                resolved_status="abstain",
                is_valid=not failures,
                failures=tuple(failures),
            )

        if not report.event_statement.strip():
            failures.append("empty_event_statement")

        evidence_by_id = {item.evidence_id: item for item in report.evidence}
        confident_evidence = [
            item
            for item in report.evidence
            if item.confidence >= self.policy.min_evidence_confidence
        ]
        if len(confident_evidence) < self.policy.min_evidence_links:
            failures.append("insufficient_evidence_links")

        if self.policy.max_latency_ms is not None and report.latency_ms is not None:
            if report.latency_ms > self.policy.max_latency_ms:
                failures.append("latency_budget_exceeded")

        for attribution in report.attributions:
            if attribution.relation not in VALID_RELATIONS:
                failures.append(f"invalid_relation:{attribution.relation}")

            missing = [
                evidence_id
                for evidence_id in attribution.evidence_ids
                if evidence_id not in evidence_by_id
            ]
            if missing:
                failures.append(f"missing_attribution_evidence:{','.join(missing)}")

            if self._violates_temporal_order(attribution):
                failures.append(f"temporal_order_violation:{attribution.relation}")

        is_valid = not failures
        resolved_status = report.status
        if report.status == "valid" and not is_valid:
            resolved_status = "insufficient_evidence"

        return ContractValidation(
            requested_status=report.status,
            resolved_status=resolved_status,
            is_valid=is_valid,
            failures=tuple(failures),
        )

    def build_frame_report(
        self,
        *,
        caption: Optional[str],
        frame_idx: int,
        timestamp: float,
        detections: Sequence[object],
        latency_ms: Optional[float] = None,
        token_indices: Iterable[int] = (),
        status: str = "valid",
        metadata: Optional[Dict[str, object]] = None,
    ) -> EvidenceReport:
        """Build a conservative frame-level report from detector evidence."""
        evidence = []
        token_tuple = tuple(int(i) for i in token_indices)
        for idx, det in enumerate(detections):
            evidence.append(
                EvidenceLink(
                    evidence_id=f"f{frame_idx}:det{idx}",
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    source=getattr(det, "class_name", "detector"),
                    confidence=float(getattr(det, "confidence", 1.0)),
                    bbox=getattr(det, "bbox", None),
                    token_indices=token_tuple,
                )
            )

        event_statement = caption or ""
        if status == "valid" and not event_statement.strip():
            status = "insufficient_evidence"
        if status == "valid" and not evidence:
            status = "insufficient_evidence"

        return EvidenceReport(
            event_statement=event_statement,
            status=status,
            evidence=tuple(evidence),
            attributions=(),
            latency_ms=latency_ms,
            metadata=metadata or {},
        )

    def _violates_temporal_order(self, attribution: AttributionTuple) -> bool:
        if attribution.relation not in TEMPORAL_RELATIONS:
            return False
        if attribution.subject_time is None or attribution.object_time is None:
            return False
        return attribution.subject_time > attribution.object_time


def unsafe_valid_rate(validations: Iterable[ContractValidation]) -> float:
    """Compute unsafe-valid rate over validation results."""
    requested_valid = 0
    unsafe = 0
    for validation in validations:
        if validation.requested_status == "valid":
            requested_valid += 1
            if validation.unsafe_valid:
                unsafe += 1
    if requested_valid == 0:
        return 0.0
    return unsafe / requested_valid
