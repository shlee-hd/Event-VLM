# CERA External Server Runbook

This runbook executes the frozen protocol and prepares measured outputs for paper replacement.

## 0) Preconditions

- Access to a CUDA-capable server with sufficient GPU memory.
- Dataset paths are available:
  - `data/ucf_crime`
  - `data/xd_violence`
- Runtime dependencies are installed (at least: `torch`, `omegaconf`, `tqdm`, `scikit-learn`).

## 1) Environment setup

```bash
git clone <repo_url> eccv2026
cd eccv2026
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Record:

- git commit hash
- GPU model / driver / CUDA version
- Python and package versions

## 2) Main runs

```bash
bash cera/experiments/scripts/run_main.sh \
  --output-root cera/experiments/results/main \
  --seeds 41,42,43 \
  --datasets ucf_crime,xd_violence \
  --profiles yolo,detr \
  --device cuda
```

Expected outputs:

- `cera/experiments/results/main/*/*/seed_*/metrics.json`
- `cera/experiments/results/main/*/*/seed_*/predictions.json`
- `cera/experiments/results/main/summary/main_summary.csv`

## 3) Ablation runs

```bash
bash cera/experiments/scripts/run_ablation.sh \
  --output-root cera/experiments/results/ablation \
  --seeds 41,42,43 \
  --datasets ucf_crime,xd_violence \
  --device cuda \
  --execute-supported 1
```

Expected outputs:

- `cera/experiments/results/ablation/ablation_manifest.csv`
- `cera/experiments/results/ablation/summary/ablation_summary.csv`

## 4) Statistics and paper stubs

```bash
bash cera/experiments/scripts/run_stats.sh \
  --main-root cera/experiments/results/main \
  --ablation-root cera/experiments/results/ablation \
  --out-root cera/experiments/results/stats \
  --seeds 41,42,43
```

Expected outputs:

- `cera/experiments/results/stats/significance/...`
- `cera/experiments/results/stats/paper_tables/paper_table_stub.tex`

## 5) Paper replacement

Replace projected blocks in `cera/paper/main.tex`:

- `MEASURED_SWAP_START/END:main_results`
- `MEASURED_SWAP_START/END:ablation_results`
- `MEASURED_SWAP_START/END:error_breakdown`

Then compile:

```bash
make -C cera/paper pdf
```

## 6) Failure handling

- If one seed fails, rerun only that seed path and keep others.
- Do not delete completed run directories.
- Keep failed run logs in place and annotate failure reason in manifest.

