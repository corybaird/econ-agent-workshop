#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/economic_libraries/stats_transformer.sh
./scripts/economic_libraries/auto_econ_sentiment.sh
./scripts/economic_libraries/econ_pdf_extract.sh
./scripts/economic_libraries/reproducible_econ.sh
./scripts/economic_libraries/verify_paper_claims.sh
