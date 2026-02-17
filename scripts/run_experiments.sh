#!/usr/bin/env bash
# Run Event-VLM experiments under a unified runtime protocol.

set -euo pipefail

echo "========================================"
echo "Event-VLM Experiment Runner"
echo "========================================"

QUICK=""
TUNING=""
MULTI_SEED=""
SEEDS="41,42,43"
DETECTOR="detr-l"
VARIANTS="core,full"
CONFIGS_CSV="experiments/configs/ucf_crime.yaml,experiments/configs/xd_violence.yaml"
SIGNIFICANCE=""
SIGNIFICANCE_BASELINE="none"
SIGNIFICANCE_CANDIDATES="core,full"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --quick) QUICK="--quick" ;;
    --tuning) TUNING="true" ;;
    --multi-seed) MULTI_SEED="true" ;;
    --seeds) SEEDS="$2"; shift ;;
    --detector) DETECTOR="$2"; shift ;;
    --variants) VARIANTS="$2"; shift ;;
    --configs) CONFIGS_CSV="$2"; shift ;;
    --significance) SIGNIFICANCE="true" ;;
    --significance-baseline) SIGNIFICANCE_BASELINE="$2"; shift ;;
    --significance-candidates) SIGNIFICANCE_CANDIDATES="$2"; shift ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

IFS=',' read -r -a CONFIGS <<< "$CONFIGS_CSV"
IFS=',' read -r -a SIG_CANDIDATES <<< "$SIGNIFICANCE_CANDIDATES"
if [[ "${#CONFIGS[@]}" -eq 0 ]]; then
  echo "ERROR: No configs provided."
  exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="outputs/run_$TIMESTAMP"
mkdir -p "$OUTPUT_DIR"

echo "Output directory: $OUTPUT_DIR"
echo "Detector: $DETECTOR"
echo "Variants: $VARIANTS"
echo "Configs: $CONFIGS_CSV"
if [[ "$SIGNIFICANCE" == "true" ]]; then
  echo "Significance: enabled (baseline=$SIGNIFICANCE_BASELINE, candidates=$SIGNIFICANCE_CANDIDATES)"
fi
if [[ "$MULTI_SEED" == "true" ]]; then
  echo "Multi-seed: enabled (seeds=$SEEDS)"
fi
echo ""

echo "========================================"
echo "Running unit tests..."
echo "========================================"
pytest tests/ -v || echo "Some tests failed, continuing..."

for cfg in "${CONFIGS[@]}"; do
  dataset="$(basename "$cfg" .yaml)"
  echo ""
  echo "========================================"
  echo "Evaluating on $dataset..."
  echo "========================================"

  python experiments/evaluate.py \
    --config "$cfg" \
    --detector "$DETECTOR" \
    --output-dir "$OUTPUT_DIR/$dataset" \
    $QUICK
done

if [[ "$TUNING" == "true" ]]; then
  echo ""
  echo "========================================"
  echo "Running auto-tuning..."
  echo "========================================"
  python experiments/auto_tune.py \
    --config experiments/configs/base.yaml \
    --n-trials 50 \
    --output-dir "$OUTPUT_DIR/tuning" \
    --visualize \
    $QUICK
fi

if [[ "$MULTI_SEED" == "true" ]]; then
  echo ""
  echo "========================================"
  echo "Running multi-seed evaluation..."
  echo "========================================"

  python experiments/multi_seed_eval.py \
    --configs "${CONFIGS[@]}" \
    --seeds "$SEEDS" \
    --variants "$VARIANTS" \
    --detector "$DETECTOR" \
    --output-dir "$OUTPUT_DIR/multi_seed" \
    $QUICK

  if [[ "$SIGNIFICANCE" == "true" ]]; then
    for cfg in "${CONFIGS[@]}"; do
      dataset="$(basename "$cfg" .yaml)"
      for candidate in "${SIG_CANDIDATES[@]}"; do
        if [[ "$candidate" == "$SIGNIFICANCE_BASELINE" ]]; then
          continue
        fi
        python experiments/paired_significance.py \
          --multi-seed-root "$OUTPUT_DIR/multi_seed" \
          --dataset "$dataset" \
          --baseline-variant "$SIGNIFICANCE_BASELINE" \
          --candidate-variant "$candidate" \
          --seeds "$SEEDS"
      done
    done
  fi
fi

echo ""
echo "========================================"
echo "Experiment Summary"
echo "========================================"

for cfg in "${CONFIGS[@]}"; do
  dataset="$(basename "$cfg" .yaml)"
  echo "$dataset results:"
  cat "$OUTPUT_DIR/$dataset/metrics.json" 2>/dev/null || echo "No $dataset results"
  echo ""
done

echo "========================================"
echo "Experiments complete!"
echo "Results saved to: $OUTPUT_DIR"
echo "========================================"
