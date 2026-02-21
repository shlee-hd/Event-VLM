# CERA Experiment Workspace

This folder is the execution handoff package for external-server runs.
It is designed so measured numbers can replace projected paper tables with minimal manual work.

## Quick map

- Protocol lock: `cera/experiments/PROTOCOL_LOCK.md`
- Server runbook: `cera/experiments/SERVER_RUNBOOK.md`
- Result schema: `cera/experiments/RESULT_SCHEMA.md`
- D-0 checklist: `cera/experiments/D0_CHECKLIST.md`
- Scripts: `cera/experiments/scripts/`

## Config files

- `configs/base.yaml`: CERA baseline defaults
- `configs/base_detr.yaml`: DETR-based detector override seed
- `configs/ucf_crime.yaml`: UCF-Crime focused override seed
- `configs/xd_violence.yaml`: XD-Violence focused override seed

## Script entrypoints

Run from repository root:

```bash
# 1) Main profile runs (YOLO/DETR x datasets x seeds)
bash cera/experiments/scripts/run_main.sh

# 2) Ablation runs (supported + pending manifest)
bash cera/experiments/scripts/run_ablation.sh

# 2-1) Plan-only ablation manifest (no runtime deps required)
bash cera/experiments/scripts/run_ablation.sh --execute-supported 0

# 3) Statistics and paper-table stubs
bash cera/experiments/scripts/run_stats.sh
```

Optional dry-run validation without GPU/data:

```bash
python3 cera/experiments/scripts/make_dummy_results.py \
  --output-root cera/experiments/results/main_dummy
python3 cera/experiments/scripts/collect_metrics.py \
  --root cera/experiments/results/main_dummy \
  --kind main \
  --out-dir cera/experiments/results/main_dummy/summary
python3 cera/experiments/scripts/render_paper_tables.py \
  --main-summary cera/experiments/results/main_dummy/summary/main_summary.csv \
  --out-dir cera/experiments/results/main_dummy/paper_tables
```

Note: runtime dependencies (e.g., `omegaconf`, model/runtime packages) must be installed on the execution server.
