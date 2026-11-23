#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python -m economic_libraries.econ_pdf_extract.extract_claims
uv run python -m economic_libraries.econ_pdf_extract.evaluate_claims
