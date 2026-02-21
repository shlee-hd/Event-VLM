#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

OUTPUT_ROOT="${REPO_ROOT}/cera/experiments/results/main"
SEEDS="41,42,43"
DATASETS="ucf_crime,xd_violence"
PROFILES="yolo,detr"
DEVICE="cuda"
QUICK=0
MAX_VIDEOS=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: run_main.sh [options]

Options:
  --output-root <path>   Output root directory
  --seeds <csv>          Comma-separated seeds (default: 41,42,43)
  --datasets <csv>       Comma-separated datasets (default: ucf_crime,xd_violence)
  --profiles <csv>       Comma-separated profiles (default: yolo,detr)
  --device <name>        Device name (default: cuda)
  --quick <0|1>          Quick mode flag (default: 0)
  --max-videos <int>     Optional max videos
  --dry-run <0|1>        Print commands only (default: 0)
  -h, --help             Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-root) OUTPUT_ROOT="$2"; shift 2 ;;
    --seeds) SEEDS="$2"; shift 2 ;;
    --datasets) DATASETS="$2"; shift 2 ;;
    --profiles) PROFILES="$2"; shift 2 ;;
    --device) DEVICE="$2"; shift 2 ;;
    --quick) QUICK="$2"; shift 2 ;;
    --max-videos) MAX_VIDEOS="$2"; shift 2 ;;
    --dry-run) DRY_RUN="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

mkdir -p "${OUTPUT_ROOT}"

if [[ "${DRY_RUN}" == "0" ]]; then
  if ! python3 -c "import omegaconf" >/dev/null 2>&1; then
    echo "[run_main] Missing python dependency: omegaconf" >&2
    echo "[run_main] Install runtime dependencies before execution." >&2
    exit 2
  fi
fi

IFS=',' read -r -a SEED_ARR <<< "${SEEDS}"
IFS=',' read -r -a DATASET_ARR <<< "${DATASETS}"
IFS=',' read -r -a PROFILE_ARR <<< "${PROFILES}"

for dataset in "${DATASET_ARR[@]}"; do
  dataset="$(echo "${dataset}" | xargs)"
  case "${dataset}" in
    ucf_crime) CONFIG_PATH="${REPO_ROOT}/experiments/configs/ucf_crime.yaml" ;;
    xd_violence) CONFIG_PATH="${REPO_ROOT}/experiments/configs/xd_violence.yaml" ;;
    *)
      echo "Unsupported dataset: ${dataset}" >&2
      exit 1
      ;;
  esac

  for profile in "${PROFILE_ARR[@]}"; do
    profile="$(echo "${profile}" | xargs)"
    case "${profile}" in
      yolo) DETECTOR="yolov8n" ;;
      detr) DETECTOR="detr-l" ;;
      *)
        echo "Unsupported profile: ${profile}" >&2
        exit 1
        ;;
    esac

    for seed in "${SEED_ARR[@]}"; do
      seed="$(echo "${seed}" | xargs)"
      RUN_DIR="${OUTPUT_ROOT}/${dataset}/${profile}/seed_${seed}"
      mkdir -p "${RUN_DIR}"

      CMD=(
        python3 "${REPO_ROOT}/experiments/evaluate.py"
        --config "${CONFIG_PATH}"
        --output-dir "${RUN_DIR}"
        --detector "${DETECTOR}"
        --device "${DEVICE}"
        --seed "${seed}"
      )

      if [[ "${QUICK}" == "1" ]]; then
        CMD+=(--quick)
      fi
      if [[ -n "${MAX_VIDEOS}" ]]; then
        CMD+=(--max-videos "${MAX_VIDEOS}")
      fi

      echo "[run_main] dataset=${dataset} profile=${profile} seed=${seed}"
      echo "[run_main] ${CMD[*]}"
      if [[ "${DRY_RUN}" == "0" ]]; then
        "${CMD[@]}"
      fi
    done
  done
done

if [[ "${DRY_RUN}" == "0" ]]; then
  python3 "${REPO_ROOT}/cera/experiments/scripts/collect_metrics.py" \
    --root "${OUTPUT_ROOT}" \
    --kind main \
    --out-dir "${OUTPUT_ROOT}/summary"
fi

echo "[run_main] done"
