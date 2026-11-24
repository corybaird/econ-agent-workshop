# Software for Macro: Tools as Infrastructure

Module 2 of the presentation (**Section 2. Software for Macro — Tools as Infrastructure**): four open-source Python libraries that replace ad-hoc scripts with YAML-configured, auditable building blocks.

```text
Data ──▶ Variables ──▶ Model ──▶ Tables / Figs ──▶ Verification
```

- Run everything from the terminal: [Quickstart Code](quickstart_code.md)
- Interactive walkthroughs: [Notebooks](../../notebooks/README.md)
- Next module: [Agent Orchestration](2_agent_orchestration.md)

## Contents

- [1. stats-transformer — The Econometrics Layer](#1-stats-transformer--the-econometrics-layer)
- [2. auto-econ-sentiment — The Text Layer](#2-auto-econ-sentiment--the-text-layer)
- [3. econ-pdf-extract — The Evidence Layer](#3-econ-pdf-extract--the-evidence-layer)
- [4. reproducible-econ — The Pipeline Layer](#4-reproducible-econ--the-pipeline-layer)
- [5. End-to-End Verification](#5-end-to-end-verification)

---

## 1. stats-transformer — The Econometrics Layer

[stats-transformer](https://github.com/corybaird/stats-transformer) — config-driven data transformations and macroeconometric estimation (OLS, panel OLS, VAR, Proxy-SVAR, LP-IV), validated against R, Stata, and MATLAB.

- **Why it matters:** transformations (`changepct_yoy`, lags, differences) and model specs live in a single YAML file rather than scattered scripts.
- **Configs:** [`references/configs/stats_transformer/`](../../references/configs/stats_transformer/) (`panel_ols.yaml`, `var.yaml`, `country_panel.yaml`)
- **Run scripts:** `./scripts/economic_libraries/stats_transformer.sh`
- **Notebook:** [`notebooks/1_stats_transformer.ipynb`](../../notebooks/1_stats_transformer.ipynb)

## 2. auto-econ-sentiment — The Text Layer

[auto-econ-sentiment](https://github.com/corybaird/auto-econ-sentiment) — standardized text cleaning and economic sentiment scoring using transparent dictionaries (Hubert-Labondance, Loughran-McDonald, Correa, and others), transformer models, or LLM prompts declared in YAML.

- **Why it matters:** exports both document/sentence scores and matched words so text indicators can be audited and fed straight into downstream econometrics.
- **Config:** [`references/configs/auto_econ_sentiment/lexical.yaml`](../../references/configs/auto_econ_sentiment/lexical.yaml)
- **Run scripts:** `./scripts/economic_libraries/auto_econ_sentiment.sh`
- **Notebook:** [`notebooks/2_auto_econ_sentiment.ipynb`](../../notebooks/2_auto_econ_sentiment.ipynb)

## 3. econ-pdf-extract — The Evidence Layer

[econ-pdf-extract](https://github.com/corybaird/econ-pdf-extract) — deterministic extraction of empirical claims, quantitative statistics, and formulas from economics PDFs with exact page, section, and attribution provenance.

- **Why it matters:** a fluent summary without a page number is impossible to audit; every extracted claim links back to its section heading, page, and verbatim quote.
- **Configs:** [`references/configs/econ_pdf_extract/`](../../references/configs/econ_pdf_extract/) (`extraction.yaml`, `ref_claims_example_paper.yaml`)
- **Run scripts:** `./scripts/economic_libraries/econ_pdf_extract.sh`
- **Notebook:** [`notebooks/3_econ_pdf_extract.ipynb`](../../notebooks/3_econ_pdf_extract.ipynb)

## 4. reproducible-econ — The Pipeline Layer

[reproducible-econ](https://github.com/corybaird/reproducible-econ) — one-command YAML stage runner with atomic parquet caching, LaTeX table and macro emitters, declarative econometric claim checks, and `run_manifest.json` provenance tracking.

- **Why it matters:** one command runs the full DAG top-to-bottom, skips unchanged stages via content-hashed cache hits, and exports paper-ready LaTeX outputs directly toward Overleaf.
- **Config:** [`references/configs/reproducible_econ/pipeline.yaml`](../../references/configs/reproducible_econ/pipeline.yaml)
- **Run scripts:** `./scripts/economic_libraries/reproducible_econ.sh`
- **Notebook:** [`notebooks/4_reproducible_econ.ipynb`](../../notebooks/4_reproducible_econ.ipynb)

## 5. End-to-End Verification

[`src/economic_libraries/verify_paper_claims/run.py`](../../src/economic_libraries/verify_paper_claims/run.py) wires the libraries together into one reproducible check:

1. Downloads Nakamura and Steinsson (NBER WP 19260) with SHA-256 verification.
2. Extracts candidate empirical claims and page provenance with `econ-pdf-extract`.
3. Re-estimates the FOMC event-study regressions using `stats-transformer` inside a `reproducible-econ` pipeline.
4. Verifies mapped claims against estimated coefficients and writes `claims_report.json` and `run_manifest.json` under `data/final/verify_paper_claims/`.

- **Configs:** [`references/configs/verify_paper_claims/`](../../references/configs/verify_paper_claims/)
- **Run script:** `./scripts/economic_libraries/verify_paper_claims.sh`
