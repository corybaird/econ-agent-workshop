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

Each shell wrapper runs its underlying `uv run python -m ...` modules in sequence.

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

## 4. Section 3 Agent & Harness Scripts (`scripts/`)

### Custom Pydantic-AI Harness

Defaults to `ECON_AGENT_MODEL=test` for an offline smoke run (set `ECON_AGENT_MODEL` to a live provider model for real runs):

```bash
./scripts/agent_harness.sh
# equivalent:
ECON_AGENT_MODEL=test uv run python -m econ_agent_harness.agent
```

### Prompts vs. Skills vs. Harness Benchmark

Runs the configured benchmark in [`references/configs/benchmarks/bench_econ_tasks.yaml`](../../references/configs/benchmarks/bench_econ_tasks.yaml):

```bash
./scripts/run_benchmark.sh

# Subset run without Langfuse telemetry:
uv run python -m econ_agent_harness.benchmark.runner \
  --arms C0_bare C3_combined C4_custom_harness \
  --tasks t1_proxy_svar \
  --no-langfuse
```

### Docker + Herdr Sandbox (`dorcheco`)

Requires Docker Desktop running. Mounts this repo at `/workspace` and `data/raw/` read-only (`:ro`):

```bash
./scripts/dorcheco.sh
```

See [`.agents/dorcheco/README.md`](../../.agents/dorcheco/README.md) for container setup and API key configuration.
