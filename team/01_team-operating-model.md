# Team Operating Model

## Goal
- Build submission-grade evidence while preserving a strong and elegant claim narrative.

## Core Working Rules
- Claims first, evidence immediately after.
- No table/figure without reproducible generation path.
- No result promotion to abstract/conclusion before cross-check.

## Cadence
- Daily:
  - 15 min standup by team leads.
  - update sync documents in `experiments/coordination/`.
- Every experiment milestone:
  - update request queue, run log, artifact registry.
  - reviewer team performs immediate sanity audit.
- Weekly:
  - evidence gate review against submission checklist.

## Ownership Matrix
- Program Lead:
  - prioritization and conflict resolution.
  - final decision on what enters the main narrative.
- Experiment Team:
  - trusted metric generation and environment execution.
- Reviewer Team:
  - quality and correctness audit across content and presentation.
- Method Team:
  - algorithmic improvements, ablation design.
- Data/Benchmark Team:
  - benchmark expansion and SOTA parity definition.
- Writing/Figure Team:
  - argument flow, readability, and visual quality.
- MLE/Infra Team:
  - automation, scripts, reproducibility plumbing.
- Release/Risk Team:
  - final gatekeeper before external sharing/submission.

## Definition of Done (Per Iteration)
- updated markdown plans and logs.
- reproducible command and outputs recorded.
- reviewer audit completed for changed tables/figures/equations.
