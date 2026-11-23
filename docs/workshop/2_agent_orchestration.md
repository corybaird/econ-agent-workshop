# Agent Orchestration

Module 2: put an agent behind walls and roles. Lean guide; fill in the live exercises later.

## Contents

- [1. Claude Code](#1-claude-code)
- [2. The harness](#2-the-harness)
- [3. Dorch + Herdr](#3-dorch--herdr)
- [4. The workshop tasks](#4-the-workshop-tasks)

## 1. Out-of-the-Box Harnesses (Claude Code, Codex, Pi)

The default harness: one agent writes, runs, and reviews its own work. Permissions are prompts, not walls.

We package two ways to steer an out-of-the-box coding agent under [`.agents/`](../../.agents/README.md) (keeping the repository root clean):

- **Setup A — Modular (Section 1 default prompt + Section 2 library skills):**
  - Default prompt: [`.agents/prompts/1_research_basics.md`](../../.agents/prompts/1_research_basics.md)
  - Four skills: `stats-transformer`, `auto-econ-sentiment`, `econ-pdf-extract`, `reproducible-econ` under [`.agents/skills/`](../../.agents/skills/)
- **Setup B — Combined lean system prompt (no separate skills):**
  - Single compact prompt: [`.agents/prompts/2_combined_econ_prompt.md`](../../.agents/prompts/2_combined_econ_prompt.md)
  - Cuts static context size and avoids extra skill-read turns while keeping folder rules and library routing intact
- **Benchmarking:** Compare both setups against a bare control (no prompt, no skills, no custom libraries) using `uv run python -m econ_agent_harness.benchmark.runner` configured by [`references/configs/benchmarks/bench_econ_tasks.yaml`](../../references/configs/benchmarks/bench_econ_tasks.yaml).

## 2. The harness

TBD

## 3. Dorch + Herdr

- Lean workshop sandbox in [`.agents/dorcheco/`](../../.agents/dorcheco/README.md): launch Docker + [Herdr](https://herdr.dev) in one command via `./scripts/dorcheco.sh` (no `~/.zshrc` edits; isolated from any existing `dorch` install)
  - Mounts only this repo at `/workspace` and mounts `data/raw/` read-only (`:ro`)
  - Pre-installs `claude`, `codex`, `pi`, and this repo's custom `econ-agent-harness` side by side
  - Separates `ORCHESTRATOR.md`, `WORKER.md`, and `REVIEWER.md` under [`.agents/dorcheco/roles/`](../../.agents/dorcheco/roles/)
- Full multi-project launcher: [Dorch](https://github.com/corybaird/dorch)

## 4. The workshop tasks
Dorch: 

Agents only see the project folder you start them in, not the rest of your computer
- **Simple:** TBD
- **Ambitious:** TBD
