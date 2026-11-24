#!/usr/bin/env bash
set -euo pipefail

# Seed git commit identity from .env if provided
if [ -n "${GIT_USER_NAME:-}" ]; then
  git config --global user.name "$GIT_USER_NAME"
fi
if [ -n "${GIT_USER_EMAIL:-}" ]; then
  git config --global user.email "$GIT_USER_EMAIL"
fi

# Ensure mounted Docker volumes are writable by the current non-root user (handles macOS UID 501 vs root)
sudo chown -R "$(id -u):$(id -g)" \
  "$HOME/.config/gh" "$HOME/.config/herdr" \
  "$HOME/.claude" "$HOME/.codex" "$HOME/.pi" "$HOME/.gemini" "$HOME/.cache/uv" \
  /workspace-worktrees 2>/dev/null || true

# Seed Section 1+2 combined prompt for Codex, Pi, and Antigravity (Claude reads /etc/claude-code/CLAUDE.md)
mkdir -p "$HOME/.codex" "$HOME/.pi/agent" "$HOME/.gemini"
cp /etc/econ-agent/PROMPT.md "$HOME/.codex/instructions.md"
cp /etc/econ-agent/PROMPT.md "$HOME/.pi/agent/AGENTS.md"
cp /etc/econ-agent/PROMPT.md "$HOME/.gemini/GEMINI.md"

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
