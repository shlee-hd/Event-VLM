# Non-Experiment Command Board (2026-02-18, v13)

Status: IN_PROGRESS  
Commander: Codex Reviewer Lead  
Scope: 서버 실험 실행 제외, 그 외 제출 준비 선행작업 전부 완료

## Operating Constraints
- Experiment server is unavailable today.
- No untraceable manual number edits are allowed.
- Every fix must map to a file path and acceptance check.

## Already Pre-Handled (this round)
- `paper/main.tex` compile blocker fixed (double-subscript equation crash removed).
- Figure/table claim linkage strengthened with explicit `\ref` calls in main narrative.
- Method notation gaps closed for `\sigma_shape`, `TopKIdx`, and prompt threshold relation.
- Draft limitation scope explicitly added to prevent overclaim while server results are pending.

## Team Orders
| Team | Priority | Orders | Deliverable | Deadline |
|---|---|---|---|---|
| Reviewer Team | P0 | Re-run full adversarial audit on latest `paper/main.tex`; verify claim-method-evidence alignment after new references and notation fixes; refresh open risk list only (no duplicate closed items). | `paper/reviews/2026-02-18_reviewer-full-audit-v13.md` | 2026-02-18 |
| Writing & Figure Team | P0 | Remove remaining readability blockers in log (`Overfull/Underfull` hotspots), tighten long appendix command line rendering, and keep all projected-scope caveats consistent across abstract/experiments/conclusion. | `paper/reviews/2026-02-18_writing-figure-polish-v13.md` | 2026-02-18 |
| Model & Method Team | P1 | Validate equation semantics and complexity wording against implementation assumptions; produce final symbol glossary and edge-case notes for camera-ready appendix migration. | `paper/reviews/2026-02-18_method-consistency-v13.md` | 2026-02-18 |
| Data & Benchmark Team | P1 | Freeze benchmark-expansion spec (dataset choice + baseline choice + fairness constraints) and produce final insertion-ready paragraph/table deltas for main text and appendix. | `paper/reviews/2026-02-18_benchmark-expansion-freeze-v13.md` | 2026-02-19 |
| MLE & Infra Team | P0 | Prepare server re-entry packet only: exact command, expected artifact paths, validation checklist, and failure triage protocol. No run execution. | `experiments/coordination/READY_TO_RUN_PACKET_2026-02-18.md` | 2026-02-18 |
| Experiment Team | P0 (BLOCKED) | Keep queue status synchronized as `BLOCKED`; once server is restored, execute pre-approved packet without changing protocol knobs. | `experiments/coordination/EXPERIMENT_REQUEST_QUEUE.md`, `experiments/coordination/RUN_LOG.md` | on server restore |
| Release & Risk Team | P0 | Update gate with current truth: compile now passes, projected-number dependency remains open; publish explicit Go/No-Go conditions for server-unblock day. | `paper/reviews/2026-02-18_release-risk-gate.md` | 2026-02-18 |

## Cross-Team Dependency Rules
1. Writing changes that alter claims require Reviewer re-signoff.
2. Method notation changes require Reviewer + Release dual signoff.
3. Any table cell change must reference artifact source path or be marked `PROJECTED`.
4. Release Team can promote version only when all P0 entries are `CLOSED` or `BLOCKED(with owner/date)`.

## Acceptance Gate (Server-Unavailable Mode)
1. `bash scripts/build_paper.sh` passes without fatal errors.
2. No unresolved P0 item in `paper/reviews/`.
3. Experiment queue is fully staged and marked `BLOCKED` with reason.
4. Draft clearly distinguishes projected numbers from measured outputs.
