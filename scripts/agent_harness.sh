#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ECON_AGENT_MODEL="${ECON_AGENT_MODEL:-test}" uv run python -m econ_agent_harness.agent
