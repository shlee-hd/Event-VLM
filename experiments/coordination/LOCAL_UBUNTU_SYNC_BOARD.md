# Local Ubuntu Sync Board

This is the primary synchronization document when experiments are executed on local Ubuntu.

## 1) Environment Fingerprint
- Date:
- Hostname:
- OS:
- GPU:
- CUDA:
- Python:
- Repo path:
- Commit hash:

## 2) Incoming Requests (from main workspace)
| Request ID | Date | Owner | Priority | Request | Status | Target Output |
|---|---|---|---|---|---|---|
| REQ-001 | 2026-02-17 | Experiment Team | P0 | Run multi-seed core/full on UCF + XD | BLOCKED | `outputs/multi_seed_eval/summary.json` |
| REQ-002 | 2026-02-18 | Experiment Team | P0 | Run multi-seed none/core/full on UCF + XD + ShanghaiTech | BLOCKED | `outputs/multi_seed_eval/summary.json` |
| REQ-003 | 2026-02-18 | Reviewer Team | P0 | Run paired significance (none vs core/full) for each dataset | BLOCKED | `outputs/multi_seed_eval/significance/**/significance.json` |
| REQ-004 | 2026-02-18 | Reviewer Lead | P0 | Use frozen packet and run one-click command as-is after server restoration | READY | `paper/generated/*.tex` + significance outputs |

## 3) Execution Status
| Run ID | Start | End | Command | Commit | Result | Notes |
|---|---|---|---|---|---|---|
| RUN-001 | - | - | `bash scripts/server_ready_one_click.sh` | - | BLOCKED | server unavailable |
| RUN-002 | - | - | `BENCHMARK_CONFIGS=... VARIANTS=none,core,full ... bash scripts/server_ready_one_click.sh` | - | BLOCKED | command frozen |
| RUN-003 | 2026-02-18 | 2026-02-18 | N/A (pre-staging only) | - | DONE | run packet prepared |

## 4) Findings to Sync Back
- Finding 1:
- Finding 2:

## 5) Blockers
- Blocker: experiment server unavailable.
- Mitigation: use `experiments/coordination/READY_TO_RUN_PACKET_2026-02-18.md` and execute immediately when server restores.

## 6) Next Actions
- [ ] validate dataset mount paths for `data/ucf_crime`, `data/xd_violence`, `data/shanghaitech` after server restore
- [ ] execute frozen one-click command from `READY_TO_RUN_PACKET_2026-02-18.md`
- [ ] sync generated `paper/generated/*.tex` and update artifact registry
