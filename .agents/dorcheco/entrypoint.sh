#!/usr/bin/env bash
set -euo pipefail

# Seed git commit identity from .env if provided
if [ -n "${GIT_USER_NAME:-}" ]; then
  git config --global user.name "$GIT_USER_NAME"
fi
if [ -n "${GIT_USER_EMAIL:-}" ]; then
  git config --global user.email "$GIT_USER_EMAIL"
fi

# Seed Section 1+2 combined prompt for Codex and Pi (Claude reads /etc/claude-code/CLAUDE.md)
mkdir -p "$HOME/.codex" "$HOME/.pi/agent"
cp /etc/econ-agent/PROMPT.md "$HOME/.codex/instructions.md"
cp /etc/econ-agent/PROMPT.md "$HOME/.pi/agent/AGENTS.md"

# Open labeled Herdr tabs once the interactive TUI workspace initializes
open_tabs() {
  local i=0
  until herdr tab list 2>/dev/null | jq -e '.result.tabs | length > 0' >/dev/null; do
    i=$((i + 1))
    [ "$i" -ge 120 ] && return 0
    sleep 0.5
  done

  local specs=(
    "claude=claude --dangerously-skip-permissions"
    "codex=codex"
    "pi=pi"
    "econ-harness=uv run python -m econ_agent_harness.agent"
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

exec herdr "$@"
