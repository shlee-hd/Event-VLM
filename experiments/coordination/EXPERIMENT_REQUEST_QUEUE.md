# Experiment Request Queue

Use this queue for all requested runs before execution.

| Request ID | Date | Requested By | Priority | Dataset | Variant | Seeds | Purpose | Status | Blocker |
|---|---|---|---|---|---|---|---|---|---|
| REQ-001 | 2026-02-17 | Main Team | P0 | UCF + XD | core, full | 41,42,43 | Multi-seed CI evidence hardening | BLOCKED | server unavailable |
| REQ-002 | 2026-02-18 | Main Team | P0 | UCF + XD + ShanghaiTech | none, core, full | 41,42,43 | Third-benchmark expansion with unified protocol | BLOCKED | server unavailable |
| REQ-003 | 2026-02-18 | Reviewer Team | P0 | UCF + XD + ShanghaiTech | none vs core/full | 41,42,43 | Paired significance report (AUC/AP bootstrap + permutation) | BLOCKED | server unavailable |
| REQ-004 | 2026-02-18 | Reviewer Lead | P0 | UCF + XD + ShanghaiTech | none, core, full | 41,42,43 | One-click execution packet prepared in advance (`READY_TO_RUN_PACKET_2026-02-18.md`) | READY | waiting for server restore |

## Status Definition
- `TODO`: request accepted, not started.
- `RUNNING`: currently executing.
- `DONE`: outputs validated and registered.
- `BLOCKED`: execution blocked, reason required.
- `READY`: fully pre-staged, can run immediately when blocker is removed.
