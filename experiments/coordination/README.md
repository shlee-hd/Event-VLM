# Experiment Coordination Hub

This directory is the canonical handoff and synchronization hub for external execution environments.

## Files
- `SERVER_READY_CHECKLIST.md`: access-day checklist for immediate execution.
- `LOCAL_UBUNTU_SYNC_BOARD.md`: primary sync board for local Ubuntu execution.
- `SECURE_VM_SYNC_PROTOCOL.md`: sync procedure for restricted VM environments.
- `EXPERIMENT_REQUEST_QUEUE.md`: prioritized incoming requests.
- `RUN_LOG.md`: immutable run records (success/failure).
- `ARTIFACT_REGISTRY.md`: canonical artifact inventory.

## One-Click Entry
- `bash scripts/server_ready_one_click.sh`
- Extended example (three benchmarks + significance):
  - `BENCHMARK_CONFIGS=experiments/configs/ucf_crime.yaml,experiments/configs/xd_violence.yaml,experiments/configs/shanghaitech.yaml VARIANTS=none,core,full SIGNIFICANCE=1 SIGNIFICANCE_BASELINE=none SIGNIFICANCE_CANDIDATES=core,full bash scripts/server_ready_one_click.sh`
  - This also renders paper-ready LaTeX blocks to `paper/generated/` by default (`RENDER_PAPER_TABLES=1`).

## Rules
- Every run must be logged.
- Every requested change must be queued before execution.
- Every promoted metric must point to an artifact in this registry.
