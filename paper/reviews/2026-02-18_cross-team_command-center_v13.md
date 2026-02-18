# Cross-Team Command Center (2026-02-18, v13)

Status: ACTIVE  
Owner: Reviewer Lead  
Mode: Server unavailable (execution deferred, preparation mandatory)

## Objective
- Keep the manuscript submission-ready except for measured server outputs.
- Ensure immediate run-resume path once server access is restored.

## Current Source of Truth
- Main manuscript: `paper/main.tex`
- Build output: `paper/build/main.pdf`
- Run queue: `experiments/coordination/EXPERIMENT_REQUEST_QUEUE.md`
- Risk gate: `paper/reviews/2026-02-18_release-risk-gate.md`

## P0/P1 Command Items

### P0-1 (Closed): Compile blocker removed
- What: Fixed equation macro/subscript conflict in sparse decoding equation.
- Evidence: `paper/main.tex` now builds via `bash scripts/build_paper.sh`.
- Remaining: none.

### P0-2 (Open): Measured artifact integration pending
- What: Main numbers still marked projected until server runs finish.
- Owner: Experiment Team + Release & Risk Team.
- Required closure:
  - generate `outputs/.../summary.json` and significance files,
  - render `paper/generated/table_multiseed_overview.tex`,
  - render `paper/generated/table_significance_summary.tex`,
  - replace projected placeholders with measured values.

### P1-1 (Open): Layout/readability warnings cleanup
- What: Overfull/underfull lines remain in build log (non-fatal).
- Owner: Writing & Figure Team.
- Required closure:
  - reduce major overfull lines in related work and appendix command display,
  - keep all captions and references intact after reflow.

### P1-2 (Open): Benchmark and baseline expansion finalization
- What: Additional benchmark/baseline plan is defined but not measured.
- Owner: Data & Benchmark Team.
- Required closure:
  - finalize exact additions and protocol fairness text,
  - provide insertion-ready wording for main + appendix.

## Immediate Team Deliverables
| Team | Deliverable Path | Required Status |
|---|---|---|
| Reviewer Team | `paper/reviews/2026-02-18_reviewer-full-audit-v13.md` | DONE |
| Writing & Figure Team | `paper/reviews/2026-02-18_writing-figure-polish-v13.md` | DONE |
| Model & Method Team | `paper/reviews/2026-02-18_method-consistency-v13.md` | DONE |
| Data & Benchmark Team | `paper/reviews/2026-02-18_benchmark-expansion-freeze-v13.md` | DONE |
| MLE & Infra Team | `experiments/coordination/READY_TO_RUN_PACKET_2026-02-18.md` | DONE |
| Release & Risk Team | `paper/reviews/2026-02-18_release-risk-gate.md` | UPDATED |

## Promotion Rule
- No promotion to “submission candidate” while P0-2 is open.
- If server remains blocked, freeze manuscript as “text-complete projected draft”.
