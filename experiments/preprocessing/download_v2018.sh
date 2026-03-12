#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RAW_DIR="${ROOT_DIR}/paper-workbench/data/raw"
BASE_URL="http://aliopentrace.oss-cn-beijing.aliyuncs.com/v2018Traces"

mkdir -p "${RAW_DIR}"

download() {
  local name="$1"
  local url="${BASE_URL}/${name}"
  local dest="${RAW_DIR}/${name}"
  echo "[download] ${name}"
  curl -L --retry 5 --retry-delay 2 --continue-at - --output "${dest}" "${url}"
}

download machine_meta.tar.gz

if [[ "${DOWNLOAD_MACHINE_USAGE:-0}" == "1" ]]; then
  download machine_usage.tar.gz
else
  echo "[skip] machine_usage.tar.gz is large. Re-run with DOWNLOAD_MACHINE_USAGE=1 to fetch it."
fi
