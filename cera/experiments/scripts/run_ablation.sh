#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

OUTPUT_ROOT="${REPO_ROOT}/cera/experiments/results/ablation"
SEEDS="41,42,43"
DATASETS="ucf_crime,xd_violence"
DEVICE="cuda"
EXECUTE_SUPPORTED=1
QUICK=0
MAX_VIDEOS=""

usage() {
  cat <<'EOF'
Usage: run_ablation.sh [options]

Options:
  --output-root <path>      Output root directory
  --seeds <csv>             Comma-separated seeds (default: 41,42,43)
  --datasets <csv>          Comma-separated datasets (default: ucf_crime,xd_violence)
  --device <name>           Device name (default: cuda)
  --execute-supported <0|1> Execute supported ablations (default: 1)
  --quick <0|1>             Quick mode flag (default: 0)
  --max-videos <int>        Optional max videos
  -h, --help                Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-root) OUTPUT_ROOT="$2"; shift 2 ;;
    --seeds) SEEDS="$2"; shift 2 ;;
    --datasets) DATASETS="$2"; shift 2 ;;
    --device) DEVICE="$2"; shift 2 ;;
    --execute-supported) EXECUTE_SUPPORTED="$2"; shift 2 ;;
    --quick) QUICK="$2"; shift 2 ;;
    --max-videos) MAX_VIDEOS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ "${EXECUTE_SUPPORTED}" == "1" ]]; then
  if ! python3 -c "import omegaconf" >/dev/null 2>&1; then
    echo "[run_ablation] Missing python dependency: omegaconf" >&2
    echo "[run_ablation] Install runtime dependencies before execution." >&2
    exit 2
  fi
fi

CMD=(
  python3 "${REPO_ROOT}/cera/experiments/scripts/run_ablation.py"
  --output-root "${OUTPUT_ROOT}"
  --seeds "${SEEDS}"
  --datasets "${DATASETS}"
  --device "${DEVICE}"
  --execute-supported "${EXECUTE_SUPPORTED}"
)

if [[ "${QUICK}" == "1" ]]; then
  CMD+=(--quick)
fi
if [[ -n "${MAX_VIDEOS}" ]]; then
  CMD+=(--max-videos "${MAX_VIDEOS}")
fi

echo "[run_ablation] ${CMD[*]}"
"${CMD[@]}"

if [[ "${EXECUTE_SUPPORTED}" == "1" ]]; then
  python3 "${REPO_ROOT}/cera/experiments/scripts/collect_metrics.py" \
    --root "${OUTPUT_ROOT}" \
    --kind ablation \
    --out-dir "${OUTPUT_ROOT}/summary"
fi

echo "[run_ablation] done"
