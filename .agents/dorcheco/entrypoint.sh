#!/usr/bin/env bash
set -euo pipefail

# Seed git commit identity from .env if provided
if [ -n "${GIT_USER_NAME:-}" ]; then
  git config --global user.name "$GIT_USER_NAME"
fi
if [ -n "${GIT_USER_EMAIL:-}" ]; then
  git config --global user.email "$GIT_USER_EMAIL"
fi

# Verify mounted volumes match container UID (rebuild via ./scripts/agent_tests/dorcheco.sh --build if mismatched)
mkdir -p "$HOME/.codex" "$HOME/.pi/agent" "$HOME/.gemini" 2>/dev/null || true
if [ ! -w "$HOME/.codex" ] || [ ! -w "$HOME/.pi" ]; then
  echo "ERROR: Mounted dorcheco volumes are owned by a different UID than $(id -u)." >&2
  echo "Fix by rebuilding with your host UID: ./scripts/agent_tests/dorcheco.sh --build" >&2
  exit 1
fi

# Seed Section 1+2 combined prompt for Codex, Pi, and Antigravity (Claude reads /etc/claude-code/CLAUDE.md)
cp /etc/econ-agent/PROMPT.md "$HOME/.codex/instructions.md"
cp /etc/econ-agent/PROMPT.md "$HOME/.pi/agent/AGENTS.md"
cp /etc/econ-agent/PROMPT.md "$HOME/.gemini/GEMINI.md"
cp /etc/econ-agent/pi-models.json "$HOME/.pi/agent/models.json"

# Open labeled Herdr tabs once the interactive TUI workspace initializes
open_tabs() {
  local i=0
  until herdr tab list 2>/dev/null | jq -e '.result.tabs | length > 0' >/dev/null; do
    i=$((i + 1))
    [ "$i" -ge 120 ] && return 0
    sleep 0.5
  done

  local pi_cmd="pi"
  if [ -n "${OLLAMA_API_KEY:-}" ]; then
    pi_cmd="pi --provider ollama-api-key --model ${PI_OLLAMA_MODEL:-glm-5.3-flash:cloud}"
  fi

  local specs=(
    "claude=claude --dangerously-skip-permissions"
    "codex=codex"
    "pi=${pi_cmd}"
    "agy=agy"
  )
  local reuse=1
  for spec in "${specs[@]}"; do
    local label="${spec%%=*}"
    local cmd="${spec#*=}"
    if herdr tab list | jq -e --arg l "$label" '.result.tabs[] | select(.label == $l)' >/dev/null; then
      continue
    fi
    local pane=""
    if [ "$reuse" = 1 ]; then
      reuse=0
      local tab
      tab="$(herdr tab list | jq -r '.result.tabs[0].tab_id')"
      pane="$(herdr pane list | jq -r --arg t "$tab" '[.result.panes[] | select(.tab_id == $t)][0].pane_id')"
      herdr tab rename "$tab" "$label" >/dev/null
    else
      pane="$(herdr tab create --label "$label" --cwd /workspace --no-focus | jq -r '.result.root_pane.pane_id')"
    fi
    herdr pane run "$pane" "$cmd" >/dev/null || true
  done
}

if [ "${DORCHECO_AUTOTABS:-1}" != "0" ]; then
  open_tabs >/tmp/dorcheco-tabs.log 2>&1 &
fi

# Docker Compose on macOS can start a PTY at 0x0 before the first resize; ensure a usable grid
for _ in 1 2 3 4 5; do
  size="$(stty size 2>/dev/null || echo '0 0')"
  [ "$size" != "0 0" ] && break
  sleep 0.1
done
if [ "$(stty size 2>/dev/null || echo '0 0')" = "0 0" ]; then
  stty rows "${LINES:-40}" cols "${COLUMNS:-120}" 2>/dev/null || true
fi

exec herdr "$@"
