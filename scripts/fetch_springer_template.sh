#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_ZIP="${ROOT_DIR}/paper-workbench/sources/springer-template-2024-12.zip"
URL="https://resource-cms.springernature.com/springer-cms/rest/v1/content/18782940/data/v13"

mkdir -p "$(dirname "${OUT_ZIP}")"

echo "[fetch] Springer Nature journal template package"
curl -L --retry 5 --retry-delay 2 --output "${OUT_ZIP}" "${URL}"

if unzip -tq "${OUT_ZIP}" >/dev/null 2>&1; then
  echo "[ok] Template package downloaded to ${OUT_ZIP}"
else
  echo "[warn] Download completed but zip verification failed."
  exit 1
fi
