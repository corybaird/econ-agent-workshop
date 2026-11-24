# Dorcheco: Lean Docker + Herdr Multi-Agent Sandbox

Minimal Docker + [Herdr](https://herdr.dev) setup (`dorcheco`) for this workshop repository. No `~/.zshrc` edits or shell wrapper scripts required, and uses isolated `dorcheco_*` volumes so it never collides with an existing `dorch` install.

## What It Provides

- **OS-level sandbox walls (`docker-compose.yml`):**
  - Mounts only this repository at `/workspace` (the rest of your computer is invisible; no Docker socket)
  - Mounts `data/raw/` **read-only (`:ro`)** at the OS level
  - Stores isolated git worktrees in a dedicated Docker volume (`/workspace-worktrees`)
- **Four harnesses pre-installed side by side inside Herdr:**
  - `claude` (Claude Code)
  - `codex` (OpenAI Codex CLI)
  - `pi` (Pi coding agent)
  - `econ-harness` (this repo's walled Pydantic-AI `econ-agent-harness`)
- **Three separated Herdr roles ([roles/](roles/)):**
  - `ORCHESTRATOR.md` (plans and dispatches briefs; no direct code edits)
  - `WORKER.md` (edits approved files in its own worktree; runs Section 2 libraries)
  - `REVIEWER.md` (read-only audit of `git diff` and reruns checks)

## Quick Start

1. Create your local `.env` (gitignored) with whichever provider keys you use:

```bash
cp .agents/dorcheco/.env.example .agents/dorcheco/.env
```

2. Build and launch Docker + Herdr (opens labeled tabs for `claude`, `codex`, `pi`, and `econ-harness`):

```bash
./scripts/agent_tests/dorcheco.sh
```

3. Inside the container, try Workshop Task 1 ([demo/BRIEF_task1_config.md](demo/BRIEF_task1_config.md)) from your Orchestrator tab:

```text
Read /etc/herdr/roles/ORCHESTRATOR.md and dispatch .agents/dorcheco/demo/BRIEF_task1_config.md to a Worker in a new worktree, then have a Reviewer audit the diff.
```

## Useful Herdr Keybindings (`ctrl+b` prefix)

| Keys | Action |
| --- | --- |
| `ctrl+b` then `n` / `p` | Next / previous tab (`claude`, `codex`, `pi`, `econ-harness`) |
| `ctrl+b` then `v` / `-` | Split pane vertically / horizontally |
| `ctrl+b` then `c` | Open a new shell tab |
| `ctrl+b` then `q` | Detach from Herdr |
