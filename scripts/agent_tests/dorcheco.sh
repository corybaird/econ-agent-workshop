#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
[ "${1:-}" = "up" ] && shift
export HOST_UID="$(id -u)"
export HOST_GID="$(id -g)"
COLS="$(tput cols 2>/dev/null || echo 120)"
ROWS="$(tput lines 2>/dev/null || echo 40)"
docker compose -f .agents/dorcheco/docker-compose.yml run --rm \
  -e "COLUMNS=${COLS}" \
  -e "LINES=${ROWS}" \
  dorcheco "$@"
