#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python -m economic_libraries.auto_econ_sentiment.score_sentences
uv run python -m economic_libraries.auto_econ_sentiment.tone_index
