# Agent Orchestration: Agent/Harness as Infrastructure

Module 3 of the presentation (**Section 3. Agent/Harness as Infrastructure**): connect AI agents to the Section 1 rules and Section 2 libraries using prompts, skills, custom harnesses, and Docker sandboxes.

## Contents

- [1. Out-of-the-Box Harnesses (Claude Code, Codex, Pi)](#1-out-of-the-box-harnesses-claude-code-codex-pi)
- [2. Custom Harness (`econ-agent-harness`)](#2-custom-harness-econ-agent-harness)
- [3. Multi-Agent Sandbox: Dorch (`dorcheco`) + Herdr](#3-multi-agent-sandbox-dorch-dorcheco--herdr)
- [4. Live Demo Task (Real Macro Proxy-SVAR)](#4-live-demo-task-real-macro-proxy-svar)

## 1. Out-of-the-Box Harnesses (Claude Code, Codex, Pi)

The default setup: one agent reads files, writes code, and runs commands in your terminal. Permissions are instructions, not hard walls.

We package two ways to steer an out-of-the-box coding agent under [`.agents/`](../../.agents/README.md) (keeping the repository root clean):

- **Setup A — Modular (Section 1 default prompt + Section 2 library skills):**
  - Default prompt: [`.agents/prompts/1_research_basics.md`](../../.agents/prompts/1_research_basics.md)
  - Four skills: `stats-transformer`, `auto-econ-sentiment`, `econ-pdf-extract`, `reproducible-econ` under [`.agents/skills/`](../../.agents/skills/)
- **Setup B — Combined lean system prompt (no separate skills):**
  - Single compact prompt: [`.agents/prompts/2_combined_econ_prompt.md`](../../.agents/prompts/2_combined_econ_prompt.md)
  - Matches modular skills on library accuracy while cutting token usage by up to 5.5x (fewer skill-loading turns)

```bash
# Pi / Codex: Setup A (modular skills) vs Setup B (combined lean prompt)
pi --append-system-prompt .agents/prompts/1_research_basics.md --skill .agents/skills
pi --append-system-prompt .agents/prompts/2_combined_econ_prompt.md --no-skills

# Claude Code: copy the lean combined prompt into CLAUDE.md
cp .agents/prompts/2_combined_econ_prompt.md CLAUDE.md
```

- **Benchmarking (requires live LLM key + `pi` CLI):** Compare all setups against a bare control using [`references/configs/benchmarks/bench_econ_tasks.yaml`](../../references/configs/benchmarks/bench_econ_tasks.yaml). **Cannot run without an API key** (`OLLAMA_API_KEY`); Langfuse is optional if you pass `--no-langfuse`:

```bash
./scripts/agent_tests/run_benchmark.sh

# Single-task subset without Langfuse:
uv run python -m econ_agent_harness.benchmark.runner \
  --arms C0_bare C3_combined C4_custom_harness \
  --tasks t1_proxy_svar \
  --no-langfuse
```

## 2. Custom Harness (`econ-agent-harness`)

Built in [`src/econ_agent_harness/`](../../src/econ_agent_harness/) on top of Pydantic-AI to turn folder rules and library calls into code-enforced boundaries — see the architecture diagram and tool table in [`pydantic_harness_explainer.md`](../../src/econ_agent_harness/pydantic_harness_explainer.md):

- Enforces `data/raw/` read-only access and clean repository roots in Python (invalid paths are rejected before touching disk).
- Exposes the Section 2 libraries as typed YAML-driven tools so the agent configures models without writing ad-hoc Python scripts.
- Passes 4/4 fixed-tool benchmark tasks (Proxy-SVAR + sentiment/PDF extraction) with zero hand-written Python, while open-ended new pipeline stages still benefit from a sandboxed terminal.
- **No token required for offline smoke tests** (`ECON_AGENT_MODEL=test` uses Pydantic-AI's built-in test model); copy `.env.example` to `.env` and set `OLLAMA_API_KEY` + `ECON_AGENT_MODEL=ollama:glm-5.3-flash:cloud` (or another provider key) for live runs:

```bash
# Offline smoke test + harness unit tests (no API key needed):
./scripts/run_all_harness.sh

# Interactive REPL (auto-loads .env; defaults to offline test model):
./scripts/agent_tests/agent_harness.sh

# Live LLM run via Ollama Cloud (reads OLLAMA_API_KEY from .env):
ECON_AGENT_MODEL=ollama:glm-5.3-flash:cloud ./scripts/agent_tests/agent_harness.sh
```

## 3. Multi-Agent Sandbox: Dorch (`dorcheco`) + Herdr

For an easy visual entry point without the terminal, start with [Zeron](https://zeron.sh/) (open-source desktop app for running multiple coding agents side by side). When open-ended research coding needs OS-enforced boundaries, use Docker + [Herdr](https://herdr.dev):

- Lean workshop sandbox in [`.agents/dorcheco/`](../../.agents/dorcheco/README.md): launches Docker + Herdr in one command with no `~/.zshrc` edits and isolated `dorcheco_*` volumes.
  - Mounts only this repo at `/workspace` (host files hidden) and mounts `data/raw/` read-only (`:ro`).
  - Auto-opens 4 Herdr tabs (`claude`, `codex`, `pi`, `agy`) seeded with the Section 1+2 combined prompt. Works with a single login by pairing a smaller Worker model and a stronger Reviewer model from the same provider.
  - Separates `ORCHESTRATOR.md`, `WORKER.md`, and `REVIEWER.md` under [`.agents/dorcheco/roles/`](../../.agents/dorcheco/roles/).
- Full multi-project launcher: [Dorch](https://github.com/corybaird/dorch).

```bash
# Launch Docker + Herdr:
./scripts/agent_tests/dorcheco.sh

# Clean reset + rebuild after Dockerfile or entrypoint changes:
docker rm -f $(docker ps -aq --filter "name=dorcheco") 2>/dev/null || true
docker compose -f .agents/dorcheco/docker-compose.yml build
./scripts/agent_tests/dorcheco.sh
```

## 4. Live Demo Task (Real Macro Proxy-SVAR)

Launch `./scripts/agent_tests/dorcheco.sh` (or open the repo in [Zeron](https://zeron.sh/)), then run one copy-paste workflow across two tabs (small/fast Worker + stronger Reviewer):

- **Worker prompt (small/fast model, e.g., Haiku / mini / flash):**
  > Create `project_example/` (`references/configs/`, `src/`, `reports/`). Using `data/raw/nakamura_steinsson_2018/` (read-only), resample daily 2Y & 10Y nominal yields and 10Y TIPS to month-end, compute 10Y breakeven inflation (`sveny10 - tipsy10`), sum monthly FOMC shocks (`ns`), and estimate a 4-lag Proxy-SVAR with `stats-transformer` instrumented by `ns`. Save the YAML config, script, and 12-month IRF CSV + plot.
- **Reviewer prompt (stronger model in a 2nd tab):**
  > Audit `project_example/`: verify `data/raw/` is untouched, check the monthly merge, breakeven formula, and `ProxySVARModel` config, rerun the script via `uv`, and report `PASS` or `FAIL`.
