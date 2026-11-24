# Quickstart Code

Runnable commands for every script and notebook in this repository using `uv`. Run all commands from the repository root.

## 1. Environment Setup

`.python-version` pins Python 3.12 so all dependencies resolve with prebuilt wheels:

```bash
uv sync
uv run pytest -q
```

## 2. Notebooks with the `uv` Jupyter Kernel

`jupyter` (including `jupyterlab` and `ipykernel`) is locked in `pyproject.toml` and `uv.lock`, so notebooks run inside the exact project environment.

Launch JupyterLab directly from `uv`:

```bash
uv run jupyter lab notebooks/
# or classic Notebook:
uv run jupyter notebook notebooks/
```

To also select this locked environment as a kernel inside VS Code, Cursor, or an existing Jupyter server, register the kernel once:

```bash
uv run python -m ipykernel install --user \
  --name econ-agent-workshop \
  --display-name "Python (econ-agent-workshop)"
```

See [notebooks/README.md](../../notebooks/README.md) for the list of all four library notebooks.

## 3. Section 2 Library Scripts (`scripts/economic_libraries/`)

Run all five library workflows in one command:

```bash
./scripts/run_all_econ.sh
```

Or run each library script (or its underlying `uv run python -m ...` modules) individually:

### `stats-transformer` (Panel OLS, VAR, Country Panel)

```bash
./scripts/economic_libraries/stats_transformer.sh
```

Or run individual modules directly with `uv`:

```bash
uv run python -m economic_libraries.stats_transformer.panel_ols
uv run python -m economic_libraries.stats_transformer.var
uv run python -m economic_libraries.stats_transformer.country_panel
```

### `auto-econ-sentiment` (Sentence Scoring & Tone Index)

```bash
./scripts/economic_libraries/auto_econ_sentiment.sh
```

Or run individually:

```bash
uv run python -m economic_libraries.auto_econ_sentiment.score_sentences
uv run python -m economic_libraries.auto_econ_sentiment.tone_index
```

### `econ-pdf-extract` (Claim Extraction & Offline Evaluation)

```bash
./scripts/economic_libraries/econ_pdf_extract.sh
```

Or run individually:

```bash
uv run python -m economic_libraries.econ_pdf_extract.extract_claims
uv run python -m economic_libraries.econ_pdf_extract.evaluate_claims
```

### `reproducible-econ` (Cold Run & Cached Rerun)

```bash
./scripts/economic_libraries/reproducible_econ.sh
```

Or run individually:

```bash
uv run python -m economic_libraries.reproducible_econ.run_pipeline
uv run python -m economic_libraries.reproducible_econ.cached_rerun
```

### End-to-End Claim Verification (Nakamura & Steinsson)

Downloads NBER WP 19260 (SHA-256 verified), extracts claims with `econ-pdf-extract`, re-estimates with `stats-transformer`, and checks claims with `reproducible-econ`:

```bash
./scripts/economic_libraries/verify_paper_claims.sh
# equivalent:
uv run python -m economic_libraries.verify_paper_claims.run
```

## 4. Section 3 Agent & Harness Scripts (`scripts/agent_tests/`)

| Script | Needs API Key / Token? | What It Runs |
| --- | --- | --- |
| `./scripts/run_all_harness.sh` | **No** (fully offline) | `agent_harness.sh` in `test` mode + harness `pytest` suite |
| `./scripts/agent_tests/agent_harness.sh` | **No** for `test` mode; **Yes** for live LLM | Custom Pydantic-AI REPL (`ECON_AGENT_MODEL=test` by default) |
| `./scripts/agent_tests/run_benchmark.sh` | **Yes** (`OLLAMA_API_KEY` + `pi` CLI) | Live prompts vs. skills vs. harness benchmark (`--no-langfuse` skips Langfuse) |
| `./scripts/agent_tests/dorcheco.sh` | **Yes** (any 1 agent login or key) | Docker + Herdr sandbox with `claude`, `codex`, `pi`, and `agy` tabs |

### Offline Harness Smoke Test (No API Key Required)

```bash
./scripts/run_all_harness.sh
```

### Custom Pydantic-AI Harness

Auto-loads `.env` (copy from [`.env.example`](../../.env.example)) and defaults to `ECON_AGENT_MODEL=test` (offline smoke test — no API key needed). Set `OLLAMA_API_KEY` in `.env` and pass `ollama:glm-5.3-flash:cloud` (or any provider model) for live runs — see [`pydantic_harness_explainer.md`](../../src/econ_agent_harness/pydantic_harness_explainer.md):

```bash
# Offline smoke run (no token required):
./scripts/agent_tests/agent_harness.sh

# Live LLM run via Ollama Cloud (reads OLLAMA_API_KEY from .env):
ECON_AGENT_MODEL=ollama:glm-5.3-flash:cloud ./scripts/agent_tests/agent_harness.sh
```

### Prompts vs. Skills vs. Harness Benchmark (Requires Live Model Key)

Requires `OLLAMA_API_KEY` and the `pi` CLI (configured in [`references/configs/benchmarks/bench_econ_tasks.yaml`](../../references/configs/benchmarks/bench_econ_tasks.yaml)). Langfuse keys are optional if you pass `--no-langfuse`:

```bash
./scripts/agent_tests/run_benchmark.sh

# Smaller subset without Langfuse telemetry:
uv run python -m econ_agent_harness.benchmark.runner \
  --arms C0_bare C3_combined C4_custom_harness \
  --tasks t1_proxy_svar \
  --no-langfuse
```

### Docker + Herdr Sandbox (`dorcheco`)

Requires Docker Desktop running. Mounts only this repo at `/workspace`, keeps `data/raw/` read-only (`:ro`), and opens Herdr tabs for `claude`, `codex`, `pi`, and `agy`:

```bash
# Normal launch (also accepts optional "up"):
./scripts/agent_tests/dorcheco.sh

# Clean reset + rebuild with host UID after Dockerfile or entrypoint changes:
docker rm -f $(docker ps -aq --filter "name=dorcheco") 2>/dev/null || true
./scripts/agent_tests/dorcheco.sh --build
```

See [`.agents/dorcheco/README.md`](../../.agents/dorcheco/README.md) for container setup, Herdr keybindings (`ctrl+b` then `n`/`p`/`v`/`c`/`q`), and API key configuration.
