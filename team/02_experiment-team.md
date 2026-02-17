# Experiment Team

## Mission
- Produce reproducible, trustworthy evidence under constrained and heterogeneous environments:
  - local Ubuntu server
  - secure internal VM

## Scope
- execute canonical runs, multi-seed runs, stress tests.
- maintain parity settings across datasets and variants.
- publish machine-readable outputs and human-readable summaries.

## Mandatory Artifacts
- `outputs/.../summary.json`
- `outputs/.../summary.md`
- run-specific `metrics.json` and `predictions.json`
- updates to:
  - `experiments/coordination/EXPERIMENT_REQUEST_QUEUE.md`
  - `experiments/coordination/RUN_LOG.md`
  - `experiments/coordination/ARTIFACT_REGISTRY.md`
  - `experiments/coordination/LOCAL_UBUNTU_SYNC_BOARD.md` (when Ubuntu execution is used)

## Environment Modes
1. Local Ubuntu mode
- all progress and requests are synchronized through `LOCAL_UBUNTU_SYNC_BOARD.md`.
- every run must include:
  - command
  - commit hash
  - config files
  - seeds
  - output path
  - short finding summary

2. Secure VM mode
- follow `SECURE_VM_SYNC_PROTOCOL.md`.
- if direct git push is blocked, export sanitized artifacts and mirror them into `experiments/coordination/`.

## Execution Readiness
- one-click command path is prewired:
  - `bash scripts/server_ready_one_click.sh`
- multi-seed orchestration:
  - `python experiments/multi_seed_eval.py ...`

## Quality Bar
- no manual copy of numbers into paper without artifact trace.
- no mixed protocol metrics in a single comparison table unless explicitly labeled.
- failed runs must still be logged with failure reason.
