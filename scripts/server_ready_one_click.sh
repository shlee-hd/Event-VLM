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
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/outputs/multi_seed_eval_$(date +%Y%m%d_%H%M%S)}"
MAX_VIDEOS="${MAX_VIDEOS:-}"
QUICK_MODE="${QUICK_MODE:-0}"

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
  --configs experiments/configs/ucf_crime.yaml experiments/configs/xd_violence.yaml
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

echo "Done. Outputs:"
echo "- $OUTPUT_DIR/summary.json"
echo "- $OUTPUT_DIR/summary.md"
