#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export HOST_UID="$(id -u)"
export HOST_GID="$(id -g)"

BUILD=0
case "${1:-}" in
  --build|build)
    BUILD=1
    shift
    ;;
  up)
    shift
    ;;
esac

if [ "$BUILD" = 1 ]; then
  docker compose -f .agents/dorcheco/docker-compose.yml build
fi

COLS="$(tput cols 2>/dev/null || echo 120)"
ROWS="$(tput lines 2>/dev/null || echo 40)"
docker compose -f .agents/dorcheco/docker-compose.yml run --rm \
  -e "COLUMNS=${COLS}" \
  -e "LINES=${ROWS}" \
  dorcheco "$@"
