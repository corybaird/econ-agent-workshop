#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python -m economic_libraries.reproducible_econ.run_pipeline
uv run python -m economic_libraries.reproducible_econ.cached_rerun
