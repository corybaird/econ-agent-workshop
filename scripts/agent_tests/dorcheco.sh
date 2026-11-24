#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export HOST_UID="$(id -u)"
export HOST_GID="$(id -g)"
docker compose -f .agents/dorcheco/docker-compose.yml run --rm dorcheco "$@"
