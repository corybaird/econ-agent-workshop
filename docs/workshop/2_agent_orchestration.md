# Agent Orchestration: Agent/Harness as Infrastructure

Module 3 of the presentation (**Section 3. Agent/Harness as Infrastructure**): connect AI agents to the Section 1 rules and Section 2 libraries using prompts, skills, custom harnesses, and Docker sandboxes.

## Contents

- [1. Out-of-the-Box Harnesses (Claude Code, Codex, Pi)](#1-out-of-the-box-harnesses-claude-code-codex-pi)
- [2. Custom Harness (`econ-agent-harness`)](#2-custom-harness-econ-agent-harness)
- [3. Multi-Agent Sandbox: Dorch (`dorcheco`) + Herdr](#3-multi-agent-sandbox-dorch-dorcheco--herdr)
- [4. The Workshop Tasks](#4-the-workshop-tasks)

## 1. Out-of-the-Box Harnesses (Claude Code, Codex, Pi)

The default setup: one agent reads files, writes code, and runs commands in your terminal. Permissions are instructions, not hard walls.

We package two ways to steer an out-of-the-box coding agent under [`.agents/`](../../.agents/README.md) (keeping the repository root clean):

- **Setup A — Modular (Section 1 default prompt + Section 2 library skills):**
  - Default prompt: [`.agents/prompts/1_research_basics.md`](../../.agents/prompts/1_research_basics.md)
  - Four skills: `stats-transformer`, `auto-econ-sentiment`, `econ-pdf-extract`, `reproducible-econ` under [`.agents/skills/`](../../.agents/skills/)
- **Setup B — Combined lean system prompt (no separate skills):**
  - Single compact prompt: [`.agents/prompts/2_combined_econ_prompt.md`](../../.agents/prompts/2_combined_econ_prompt.md)
  - Matches modular skills on library accuracy while cutting token usage by up to 5.5x (fewer skill-loading turns)
- **Benchmarking:** Compare all setups against a bare control using `./scripts/agent_tests/run_benchmark.sh` (`uv run python -m econ_agent_harness.benchmark.runner`), configured by [`references/configs/benchmarks/bench_econ_tasks.yaml`](../../references/configs/benchmarks/bench_econ_tasks.yaml).

## 2. Custom Harness (`econ-agent-harness`)

Built in [`src/econ_agent_harness/`](../../src/econ_agent_harness/) on top of Pydantic-AI to turn folder rules and library calls into code-enforced boundaries:

- Enforces `data/raw/` read-only access and clean repository roots in Python (invalid paths are rejected before touching disk).
- Exposes the Section 2 libraries as typed YAML-driven tools so the agent configures models without writing ad-hoc Python scripts.
- Passes 4/4 fixed-tool benchmark tasks (Proxy-SVAR + sentiment/PDF extraction) with zero hand-written Python, while open-ended new pipeline stages still benefit from a sandboxed terminal.
- Smoke-test locally via `./scripts/run_all_harness.sh` or `./scripts/agent_tests/agent_harness.sh` (see [Quickstart Code](quickstart_code.md)).

## 3. Multi-Agent Sandbox: Dorch (`dorcheco`) + Herdr

When open-ended research coding needs a real terminal, enforce boundaries at the OS level:

- Lean workshop sandbox in [`.agents/dorcheco/`](../../.agents/dorcheco/README.md): launch Docker + [Herdr](https://herdr.dev) in one command via `./scripts/agent_tests/dorcheco.sh` (no `~/.zshrc` edits; isolated from any existing `dorch` install).
  - Mounts only this repo at `/workspace` (host files hidden) and mounts `data/raw/` read-only (`:ro`).
  - Mixes Claude Code, Codex, Antigravity, Pi (cloud or local), and `econ-agent-harness` side by side in isolated git worktrees.
  - Separates `ORCHESTRATOR.md` (strongest model plans briefs), `WORKER.md` (small flash models edit approved files and run tests), and `REVIEWER.md` (independent model audits `git diff` and reruns code) under [`.agents/dorcheco/roles/`](../../.agents/dorcheco/roles/).
- Full multi-project launcher: [Dorch](https://github.com/corybaird/dorch).

## 4. The Workshop Tasks

- **Task 1 (simple):** change one value in one YAML config, rerun the pipeline, and report the diff — the reviewer verifies the diff touches exactly one file.
- **Task 2 (ambitious):** add a stage to the `reproducible-econ` pipeline to extract a paper's headline claim (`econ-pdf-extract`), re-estimate it (`stats-transformer`), and compare the result in `run_manifest.json` — the agent builds it under the harness and the reviewer audits every commit.
