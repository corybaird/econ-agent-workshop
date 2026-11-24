# Agent Prompts & Skills

All agent instructions and modular library skills live under `.agents/` to keep the repository root clean.

## Contents

- **Section 1 — Default Prompt (Research Basics):** [prompts/1_research_basics.md](prompts/1_research_basics.md)
  - Cookiecutter Data Science folder contract (`data/raw/` immutable, `references/configs/` YAML decisions, `src/`, `reports/overleaf/`), `uv`, `git`, sandbox discipline, and verification checks.
- **Section 2 — Modular Library Skills (one per library):**
  - [skills/stats-transformer/SKILL.md](skills/stats-transformer/SKILL.md)
  - [skills/auto-econ-sentiment/SKILL.md](skills/auto-econ-sentiment/SKILL.md)
  - [skills/econ-pdf-extract/SKILL.md](skills/econ-pdf-extract/SKILL.md)
  - [skills/reproducible-econ/SKILL.md](skills/reproducible-econ/SKILL.md)
- **Combined Lean System Prompt (Section 1 + Section 2, no separate skills):** [prompts/2_combined_econ_prompt.md](prompts/2_combined_econ_prompt.md)
  - Merges the folder/version-control rules with exact imports, minimal contracts for all four libraries, and a compact `reproducible-econ` YAML template to avoid multi-skill token bloat.
- **Lean Docker + Herdr Sandbox (Section 3):** [dorcheco/README.md](dorcheco/README.md)
  - Self-contained Docker Compose + Herdr setup (`./scripts/agent_tests/dorcheco.sh`) mounting `data/raw/` read-only with tabs for `claude`, `codex`, `pi`, and `agy`.

## Static Context Size Comparison

| Setup | Files Loaded | Lines | Words | Bytes |
| --- | --- | ---: | ---: | ---: |
| **Setup A (Modular)** | `prompts/1_research_basics.md` + 4 × `skills/*/SKILL.md` | 341 | 1,908 | 17,517 |
| **Setup B (Combined)** | `prompts/2_combined_econ_prompt.md` alone | 58 | 668 | 6,276 |

## Usage in Out-of-the-Box Harnesses

### Pi / OpenAI Codex
`.agents/skills/` is discovered automatically. Pass either setup explicitly:

```bash
# Setup A: Section 1 default prompt + modular skills
pi --append-system-prompt .agents/prompts/1_research_basics.md --skill .agents/skills

# Setup B: Single lean combined prompt (no separate skills)
pi --append-system-prompt .agents/prompts/2_combined_econ_prompt.md --no-skills
```

### Claude Code
Copy or symlink into Claude Code's expected paths in your research repo:

```bash
# Setup A (modular)
cp .agents/prompts/1_research_basics.md CLAUDE.md
mkdir -p .claude && ln -s ../.agents/skills .claude/skills

# Setup B (combined lean prompt, no skills)
cp .agents/prompts/2_combined_econ_prompt.md CLAUDE.md
```

## Reproducing the Benchmark (Optional Langfuse Telemetry)

Compare all five arms (`C0_bare`, `C1_prompt_only`, `C2_prompt_skills`, `C3_combined`, `C4_custom_harness`) on deterministic synthetic macro tasks declared in [references/configs/benchmarks/bench_econ_tasks.yaml](../references/configs/benchmarks/bench_econ_tasks.yaml):

```bash
# Full configured benchmark
./scripts/agent_tests/run_benchmark.sh

# Or run a subset locally without Langfuse
uv run python -m econ_agent_harness.benchmark.runner --arms C0_bare C3_combined C4_custom_harness --tasks t1_proxy_svar --no-langfuse
```

When `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_BASE_URL` are set in the environment, each run posts its trace, per-turn token spans, and deterministic rubric scores to Langfuse. Timestamped JSON and Markdown summaries are written locally under gitignored `data/final/benchmarks/`.
