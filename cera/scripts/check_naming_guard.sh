#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TARGET_FILE="${ROOT_DIR}/cera/paper/main.tex"
LEGACY_PATTERN='Event-VLM|event-vlm'

if rg -n "${LEGACY_PATTERN}" "${TARGET_FILE}" > /tmp/cera_naming_guard.out; then
  echo "[FAIL] Legacy naming detected in ${TARGET_FILE}"
  cat /tmp/cera_naming_guard.out
  exit 1
fi

echo "[PASS] No legacy Event-VLM naming detected in ${TARGET_FILE}"
