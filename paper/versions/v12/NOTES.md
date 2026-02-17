# v12 Notes

Date: 2026-02-18

## What changed
- Prepared benchmark/statistical expansion pipeline for immediate server execution.
- Added third-benchmark config template:
  - `experiments/configs/shanghaitech.yaml`
- Extended experiment execution scripts to support configurable benchmark lists and significance analysis:
  - `scripts/run_experiments.sh`
  - `scripts/server_ready_one_click.sh`
- Added paired significance runner for anomaly metrics (AUC/AP):
  - `experiments/paired_significance.py`
- Updated evaluation outputs to preserve per-video labels/captions for paired analysis:
  - `experiments/evaluate.py`
- Updated coordination/reviewer docs with concrete REQ items and execution plan for benchmark expansion.
- Updated manuscript text to explicitly scope final statistical release with additional benchmark extension.

## Build status
- PASS: `bash scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`

## Ready commands (server)
- Multi-seed + 3 benchmarks + significance:
  - `BENCHMARK_CONFIGS=experiments/configs/ucf_crime.yaml,experiments/configs/xd_violence.yaml,experiments/configs/shanghaitech.yaml VARIANTS=none,core,full SIGNIFICANCE=1 SIGNIFICANCE_BASELINE=none SIGNIFICANCE_CANDIDATES=core,full bash scripts/server_ready_one_click.sh`
