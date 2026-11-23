#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python -m economic_libraries.stats_transformer.panel_ols
uv run python -m economic_libraries.stats_transformer.var
uv run python -m economic_libraries.stats_transformer.country_panel
