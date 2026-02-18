# Non-Experiment Team Action Board (2026-02-17)

Scope: execute next steps for all teams except Experiment Team.

## Exclusion
- Experiment Team is intentionally excluded in this round due to unavailable execution environments.

## Task Board
| Team | Priority | Immediate Actions | Deliverable | Due Date |
|---|---|---|---|---|
| Reviewer Team | P0 | exhaustive literature refresh; candidate benchmark/SOTA add-ons; full logic review; abstract/introduction/conclusion language audit; figure/table/layout overflow audit; equation/derivation correctness audit; impact significance review | `paper/reviews/2026-02-18_reviewer-full-audit.md` | 2026-02-18 |
| Model & Method Team | P0 | convert new claims into falsifiable hypotheses; define counterfactual ablations; specify acceptance/rejection criteria per hypothesis | `paper/reviews/2026-02-18_method-hypothesis-matrix.md` | 2026-02-18 |
| Data & Benchmark Team | P1 | propose additional benchmark datasets and stronger baselines; split reproduced-vs-native metrics policy; fairness constraints checklist update | `paper/reviews/2026-02-18_benchmark-expansion-plan.md` | 2026-02-19 |
| Writing & Figure Team | P0 | polish abstract/introduction beauty and precision; tighten claim-evidence mapping; improve caption readability and page aesthetics | `paper/reviews/2026-02-18_writing-figure-polish-plan.md` | 2026-02-18 |
| MLE & Infra Team | P1 | validate one-click server workflow and metadata schema; preflight scripts and log templates without launching unavailable experiments | `paper/reviews/2026-02-18_infra-readiness-report.md` | 2026-02-19 |
| Release & Risk Team | P0 | refresh release gate checklist; map open P0/P1 risks; define go/no-go conditions for next version promotion | `paper/reviews/2026-02-18_release-risk-gate.md` | 2026-02-18 |

## Coordination Rule
- Every team must submit deliverable markdown in `paper/reviews/` with explicit file path references and status (`DONE`, `PARTIAL`, `BLOCKED`).

## Quality Rule
- No claim text escalation to abstract/conclusion until Reviewer Team and Release & Risk Team both sign off.

## Progress Update (2026-02-18)
- Reviewer Team: `paper/reviews/2026-02-18_reviewer-full-audit.md` 제출 (PARTIAL, figure audit complete, benchmark expansion P1 open).
- Writing & Figure Team: `paper/reviews/2026-02-18_writing-figure-polish-plan.md` 업데이트 (PARTIAL, v9 figure/layout corrections 반영).
- Data & Benchmark Team: `paper/reviews/2026-02-18_benchmark-expansion-plan.md` 업데이트 (P0 open, 추가 benchmark 필요로 확정).
- Release & Risk Team: `paper/reviews/2026-02-18_release-risk-gate.md` 업데이트 (v8 figure risk closed in v9).
