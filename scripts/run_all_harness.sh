#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

printf 'exit\n' | ECON_AGENT_MODEL=test ./scripts/agent_tests/agent_harness.sh
uv run pytest -q tests/test_agent.py tests/test_harness_stubs.py tests/test_harness_tools.py

echo "Offline harness checks passed."
echo "Optional live runs: ./scripts/agent_tests/run_benchmark.sh (LLM API) or ./scripts/agent_tests/dorcheco.sh (Docker)."
