#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
SEEDS="${SEEDS:-41,42,43}"
VARIANTS="${VARIANTS:-core,full}"
DETECTOR="${DETECTOR:-detr-l}"
DEVICE="${DEVICE:-cuda}"
BENCHMARK_CONFIGS="${BENCHMARK_CONFIGS:-experiments/configs/ucf_crime.yaml,experiments/configs/xd_violence.yaml}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/outputs/multi_seed_eval_$(date +%Y%m%d_%H%M%S)}"
MAX_VIDEOS="${MAX_VIDEOS:-}"
QUICK_MODE="${QUICK_MODE:-0}"
SIGNIFICANCE="${SIGNIFICANCE:-0}"
SIGNIFICANCE_BASELINE="${SIGNIFICANCE_BASELINE:-none}"
SIGNIFICANCE_CANDIDATES="${SIGNIFICANCE_CANDIDATES:-core,full}"

IFS=',' read -r -a CONFIG_ARRAY <<< "$BENCHMARK_CONFIGS"
IFS=',' read -r -a SIGNIFICANCE_CANDIDATE_ARRAY <<< "$SIGNIFICANCE_CANDIDATES"
if [ "${#CONFIG_ARRAY[@]}" -eq 0 ]; then
  echo "ERROR: BENCHMARK_CONFIGS is empty."
  exit 1
fi

echo "=================================================="
echo "Event-VLM one-click server execution"
echo "=================================================="
echo "Root:       $ROOT_DIR"
echo "Python:     $PYTHON_BIN"
echo "Venv:       $VENV_DIR"
echo "Seeds:      $SEEDS"
echo "Variants:   $VARIANTS"
echo "Detector:   $DETECTOR"
echo "Device:     $DEVICE"
echo "Configs:    $BENCHMARK_CONFIGS"
echo "Signif.:    $SIGNIFICANCE (baseline=$SIGNIFICANCE_BASELINE, candidates=$SIGNIFICANCE_CANDIDATES)"
echo "Output:     $OUTPUT_DIR"
echo "=================================================="

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ERROR: python not found: $PYTHON_BIN"
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

CMD=(
  python experiments/multi_seed_eval.py
  --configs "${CONFIG_ARRAY[@]}"
  --seeds "$SEEDS"
  --variants "$VARIANTS"
  --detector "$DETECTOR"
  --device "$DEVICE"
  --output-dir "$OUTPUT_DIR"
)

if [ "$QUICK_MODE" = "1" ]; then
  CMD+=(--quick)
fi

if [ -n "$MAX_VIDEOS" ]; then
  CMD+=(--max-videos "$MAX_VIDEOS")
fi

echo "Running: ${CMD[*]}"
"${CMD[@]}"

if [ "$SIGNIFICANCE" = "1" ]; then
  for cfg in "${CONFIG_ARRAY[@]}"; do
    dataset="$(basename "$cfg" .yaml)"
    for candidate in "${SIGNIFICANCE_CANDIDATE_ARRAY[@]}"; do
      if [ "$candidate" = "$SIGNIFICANCE_BASELINE" ]; then
        continue
      fi
      SIG_CMD=(
        python experiments/paired_significance.py
        --multi-seed-root "$OUTPUT_DIR"
        --dataset "$dataset"
        --baseline-variant "$SIGNIFICANCE_BASELINE"
        --candidate-variant "$candidate"
        --seeds "$SEEDS"
      )
      echo "Running significance: ${SIG_CMD[*]}"
      "${SIG_CMD[@]}"
    done
  done
fi

echo "Done. Outputs:"
echo "- $OUTPUT_DIR/summary.json"
echo "- $OUTPUT_DIR/summary.md"
