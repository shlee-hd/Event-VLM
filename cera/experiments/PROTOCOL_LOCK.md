# CERA External Experiment Protocol Lock (v1)

- Lock date: 2026-02-21
- Lock ID: `CERA-EXP-LOCK-v1`
- Status: Pre-execution frozen (server run pending)

## Scope

This lock freezes the experiment protocol before external GPU execution so that:

1. runtime setup and reporting are reproducible,
2. projected paper tables can be replaced with measured values without rewriting the method narrative,
3. execution logs are auditable by other collaborators.

## Fixed runtime contract

- Repository commit at execution start must be recorded.
- Python entrypoint for per-run evaluation:
  - `experiments/evaluate.py`
- Aggregation/statistics entrypoints:
  - `cera/experiments/scripts/collect_metrics.py`
  - `experiments/paired_significance.py`

## Fixed run matrix

- Datasets:
  - `ucf_crime` -> `experiments/configs/ucf_crime.yaml`
  - `xd_violence` -> `experiments/configs/xd_violence.yaml`
- Profiles:
  - `yolo` -> detector override `yolov8n`
  - `detr` -> detector override `detr-l`
- Seeds:
  - `41,42,43`
- Device:
  - `cuda`

## Ablation policy (pre-server)

- Runnable in current runtime:
  - `full`
  - `no_event_gating` (proxy: detector threshold zero)
  - `no_token_compaction` (proxy: pruning disabled)
  - `no_budgeted_decoding` (proxy: longer dense decode setting)
- Pending in current runtime (manifest only):
  - `no_evidence_gate` (requires CERA evidence-gate runtime hooks)

## Output contract

All outputs are written under `cera/experiments/results/`:

- Main runs: `main/<dataset>/<profile>/seed_<seed>/`
- Ablation runs: `ablation/<dataset>/<ablation>/seed_<seed>/`
- Aggregation output: `*/summary/`
- Significance output: `stats/significance/`
- Paper-ready table stubs: `stats/paper_tables/`

## Non-negotiable checks

- Keep seeds and dataset/profile matrix unchanged.
- Keep output directory structure unchanged.
- Keep metric extraction script unchanged or version-bumped with explicit note.
- Keep paper replacement blocks aligned with `MEASURED_SWAP_START/END` markers.

