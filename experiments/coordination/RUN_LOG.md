# Experiment Run Log

Append-only run history.

| Run ID | Date | Request ID | Environment | Commit | Command | Output Path | Outcome | Notes |
|---|---|---|---|---|---|---|---|---|
| RUN-001 | 2026-02-17 | REQ-001 | pending | - | `bash scripts/server_ready_one_click.sh` | `outputs/multi_seed_eval_*` | BLOCKED | server unavailable |
| RUN-002 | 2026-02-18 | REQ-002 | pending | - | `BENCHMARK_CONFIGS=experiments/configs/ucf_crime.yaml,experiments/configs/xd_violence.yaml,experiments/configs/shanghaitech.yaml VARIANTS=none,core,full SIGNIFICANCE=1 SIGNIFICANCE_BASELINE=none SIGNIFICANCE_CANDIDATES=core,full RENDER_PAPER_TABLES=1 bash scripts/server_ready_one_click.sh` | `outputs/multi_seed_eval_*` | BLOCKED | command frozen, waiting for server restore |
| RUN-003 | 2026-02-18 | REQ-004 | coordination-only | - | N/A (pre-staging only) | `experiments/coordination/READY_TO_RUN_PACKET_2026-02-18.md` | DONE | no experiment execution performed |
