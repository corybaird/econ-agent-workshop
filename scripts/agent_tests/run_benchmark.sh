#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python -m econ_agent_harness.benchmark.runner "$@"
