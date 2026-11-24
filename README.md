# AI Agents, Verification, and the Future of Research

[VIMM Lab Seminar](https://www.vimacro.org/lab) presentation materials


Solutions to the "AI" "Verification" "Crisis":

- **1. Folders/docs as INFRASTRUCTURE.**
  - Verification starts with tools: version control (git), code reproducibility (uv), folder/docs management
- **2. Tools as INFRASTRUCTURE.**
  - Econometrics, sentiment analysis, PDF extraction (evidence extraction) and verification pipeline (evidence creation)
  - Complements recent macroeconometric infrastructure built by BIS: [BIS MaRCo](https://github.com/bis-med-it/marco-BIS/tree/main)
- **3. Agent/harness as INFRASTRUCTURE.**
  - Creating a domain-specific AI harness for efficient, scalable, and verified research


## Workshop guides

Start here, in order:

- [0. Research Basics](docs/workshop/0_research_basics.md) — Recommended software for the workshop: uv, Git, Docker, Overleaf
- [1. Software for Macro](docs/workshop/1_software_for_macro.md) — Four open-source libraries as infrastructure
- [2. Agent Orchestration](docs/workshop/2_agent_orchestration.md) — From out-of-the-box agents to custom harnesses and Docker + Herdr
- [Quickstart Code](docs/workshop/quickstart_code.md) — Runnable `uv` scripts and Jupyter kernel setup
- [Notebooks](notebooks/README.md) — One runnable notebook per library
- [Citations](docs/citations.md) — Full citations for every paper, dataset, and dictionary the examples use

> Data sources and terms are in [data/LICENSES.md](data/LICENSES.md).

## 1. Folders/docs as INFRASTRUCTURE

- [Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science): track all project inputs and outputs via clean folders
  - `data/` — raw inputs (does not change) + data transforms
  - `references/` — research decisions: data transformations, econometrics, LLM prompts, dictionaries
  - `src/` — code used in analysis
  - `docs/` — explain code, data, references
  - `reports/` — outputs + `overleaf/`: the paper and slides that are direct outputs from code

## 2. Tools as INFRASTRUCTURE

- [stats-transformer](https://github.com/corybaird/stats-transformer) — config-driven data transforms and econometric estimation
- [auto-econ-sentiment](https://github.com/corybaird/auto-econ-sentiment) — transparent dictionary/LLM scoring for economic text
- [econ-pdf-extract](https://github.com/corybaird/econ-pdf-extract) — structured extraction of claims, formulas, and sections from PDFs
- [reproducible-econ](https://github.com/corybaird/reproducible-econ) — caching, provenance, and run manifests

## 3. Agent/harness as INFRASTRUCTURE

- **Out-of-the-box harnesses:** agent (claude code, codex, pi) — see [`.agents/`](.agents/README.md)
  -   Default prompt ([`.agents/prompts/1_research_basics.md`](.agents/prompts/1_research_basics.md)) leveraging tools from section 1
  -   Library skills ([`.agents/skills/`](.agents/skills/)) leveraging tools from section 2
  -   Combined lean system prompt ([`.agents/prompts/2_combined_econ_prompt.md`](.agents/prompts/2_combined_econ_prompt.md)) merging sections 1 and 2 to reduce token bloat
- **Custom harness:** Pydantic harness optimized for economic workflows
- **[Dorch](https://github.com/corybaird/dorch):** My custom software tool for coding agents in a Docker container *(link coming)*
  - [Herdr](https://github.com/herdrdev/herdr) agent orchestration/delgation (works across Claude Code, Pi, and Antigravity)
  - Agents only see the project folder you start them in, not the rest of your computer


## Project layout

```text
.agents/
├── prompts/                # Section 1 default prompt + lean combined prompt
├── skills/                 # one SKILL.md per Section 2 library
└── dorcheco/               # lean Docker + Herdr sandbox (./scripts/dorcheco.sh)
src/
├── econ_agent_harness/     # setup, pipeline, verify, agent, benchmark
└── economic_libraries/     # one folder per tool, plus verify_paper_claims
data/
├── raw/                    # immutable inputs, terms in data/LICENSES.md
├── intermediate/           # regenerable by code (placeholder)
└── final/                  # analysis-ready outputs (placeholder)
references/
├── configs/                # model decisions in YAML, one folder per library
└── dictionaries/           # shared lookup tables
docs/                       # framing and workshop guides
tests/
```
