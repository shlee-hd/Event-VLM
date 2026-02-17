#!/bin/bash
# Run all experiments for Event-VLM

set -e

echo "========================================"
echo "Event-VLM Experiment Runner"
echo "========================================"

# Parse arguments
QUICK=""
TUNING=""
MULTI_SEED=""
SEEDS="41,42,43"
DETECTOR="detr-l"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --quick) QUICK="--quick" ;;
        --tuning) TUNING="true" ;;
        --multi-seed) MULTI_SEED="true" ;;
        --seeds) SEEDS="$2"; shift ;;
        --detector) DETECTOR="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Create output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="outputs/run_$TIMESTAMP"
mkdir -p "$OUTPUT_DIR"

echo "Output directory: $OUTPUT_DIR"
echo "Detector: $DETECTOR"
if [ "$MULTI_SEED" = "true" ]; then
    echo "Multi-seed: enabled (seeds=$SEEDS)"
fi
echo ""

# Run unit tests first
echo "========================================"
echo "Running unit tests..."
echo "========================================"
pytest tests/ -v || echo "Some tests failed, continuing..."

# Run evaluation on UCF-Crime
echo ""
echo "========================================"
echo "Evaluating on UCF-Crime..."
echo "========================================"
python experiments/evaluate.py \
    --config experiments/configs/ucf_crime.yaml \
    --detector $DETECTOR \
    --output-dir "$OUTPUT_DIR/ucf_crime" \
    $QUICK

# Run evaluation on XD-Violence
echo ""
echo "========================================"
echo "Evaluating on XD-Violence..."
echo "========================================"
python experiments/evaluate.py \
    --config experiments/configs/xd_violence.yaml \
    --detector $DETECTOR \
    --output-dir "$OUTPUT_DIR/xd_violence" \
    $QUICK

# Run auto-tuning if requested
if [ "$TUNING" = "true" ]; then
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

# Run multi-seed aggregation if requested
if [ "$MULTI_SEED" = "true" ]; then
    echo ""
    echo "========================================"
    echo "Running multi-seed evaluation..."
    echo "========================================"
    python experiments/multi_seed_eval.py \
        --configs experiments/configs/ucf_crime.yaml experiments/configs/xd_violence.yaml \
        --seeds "$SEEDS" \
        --variants core,full \
        --detector "$DETECTOR" \
        --output-dir "$OUTPUT_DIR/multi_seed" \
        $QUICK
fi

# Generate summary
echo ""
echo "========================================"
echo "Experiment Summary"
echo "========================================"

# Collect metrics
echo "UCF-Crime results:"
cat "$OUTPUT_DIR/ucf_crime/metrics.json" 2>/dev/null || echo "No UCF-Crime results"

echo ""
echo "XD-Violence results:"
cat "$OUTPUT_DIR/xd_violence/metrics.json" 2>/dev/null || echo "No XD-Violence results"

echo ""
echo "========================================"
echo "Experiments complete!"
echo "Results saved to: $OUTPUT_DIR"
echo "========================================"
