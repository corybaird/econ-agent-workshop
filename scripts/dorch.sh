#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export HOST_UID="$(id -u)"
export HOST_GID="$(id -g)"
docker compose -f .agents/dorch/docker-compose.yml run --rm dorch "$@"
