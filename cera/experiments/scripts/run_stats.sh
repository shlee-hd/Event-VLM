#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

MAIN_ROOT="${REPO_ROOT}/cera/experiments/results/main"
ABLATION_ROOT="${REPO_ROOT}/cera/experiments/results/ablation"
OUT_ROOT="${REPO_ROOT}/cera/experiments/results/stats"
SEEDS="41,42,43"

usage() {
  cat <<'EOF'
Usage: run_stats.sh [options]

Options:
  --main-root <path>      Main run root
  --ablation-root <path>  Ablation run root
  --out-root <path>       Stats output root
  --seeds <csv>           Comma-separated seeds (default: 41,42,43)
  -h, --help              Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --main-root) MAIN_ROOT="$2"; shift 2 ;;
    --ablation-root) ABLATION_ROOT="$2"; shift 2 ;;
    --out-root) OUT_ROOT="$2"; shift 2 ;;
    --seeds) SEEDS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

mkdir -p "${OUT_ROOT}"

if [[ -d "${MAIN_ROOT}" ]]; then
  python3 "${REPO_ROOT}/cera/experiments/scripts/collect_metrics.py" \
    --root "${MAIN_ROOT}" \
    --kind main \
    --out-dir "${MAIN_ROOT}/summary"
fi

if [[ -d "${ABLATION_ROOT}" ]]; then
  python3 "${REPO_ROOT}/cera/experiments/scripts/collect_metrics.py" \
    --root "${ABLATION_ROOT}" \
    --kind ablation \
    --out-dir "${ABLATION_ROOT}/summary"
fi

for dataset in ucf_crime xd_violence; do
  if [[ -f "${MAIN_ROOT}/${dataset}/yolo/seed_41/predictions.json" && -f "${MAIN_ROOT}/${dataset}/detr/seed_41/predictions.json" ]]; then
    if python3 -c "import sklearn" >/dev/null 2>&1; then
      python3 "${REPO_ROOT}/experiments/paired_significance.py" \
        --multi-seed-root "${MAIN_ROOT}" \
        --dataset "${dataset}" \
        --baseline-variant yolo \
        --candidate-variant detr \
        --seeds "${SEEDS}" \
        --output-dir "${OUT_ROOT}/significance/${dataset}/detr_vs_yolo"
    else
      echo "[run_stats] Skip significance for ${dataset}: sklearn not installed"
    fi
  fi
done

MAIN_SUMMARY="${MAIN_ROOT}/summary/main_summary.csv"
ABL_SUMMARY="${ABLATION_ROOT}/summary/ablation_summary.csv"

if [[ -f "${MAIN_SUMMARY}" ]]; then
  CMD=(
    python3 "${REPO_ROOT}/cera/experiments/scripts/render_paper_tables.py"
    --main-summary "${MAIN_SUMMARY}"
    --out-dir "${OUT_ROOT}/paper_tables"
  )
  if [[ -f "${ABL_SUMMARY}" ]]; then
    CMD+=(--ablation-summary "${ABL_SUMMARY}")
  fi
  "${CMD[@]}"
fi

echo "[run_stats] done"
