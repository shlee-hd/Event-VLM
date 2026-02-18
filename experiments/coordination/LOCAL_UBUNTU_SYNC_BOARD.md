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
| REQ-001 | 2026-02-17 | Experiment Team | P0 | Run multi-seed core/full on UCF + XD | TODO | `outputs/multi_seed_eval/summary.json` |
| REQ-002 | 2026-02-18 | Experiment Team | P0 | Run multi-seed none/core/full on UCF + XD + ShanghaiTech | TODO | `outputs/multi_seed_eval/summary.json` |
| REQ-003 | 2026-02-18 | Reviewer Team | P0 | Run paired significance (none vs core/full) for each dataset | TODO | `outputs/multi_seed_eval/significance/**/significance.json` |

## 3) Execution Status
| Run ID | Start | End | Command | Commit | Result | Notes |
|---|---|---|---|---|---|---|
| RUN-001 | - | - | - | - | PENDING | - |

## 4) Findings to Sync Back
- Finding 1:
- Finding 2:

## 5) Blockers
- Blocker:
- Mitigation:

## 6) Next Actions
- [ ] validate dataset mount paths for `data/ucf_crime`, `data/xd_violence`, `data/shanghaitech`
- [ ] execute one-click multi-seed run with `VARIANTS=none,core,full`
- [ ] execute significance phase and sync markdown summaries back to paper workspace
