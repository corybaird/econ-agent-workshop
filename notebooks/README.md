# Notebooks

One per library, adapted from the library repositories and committed with outputs. Run from the repo root:

```bash
uv run --with jupyterlab --with matplotlib jupyter lab notebooks/
```

| Notebook | Library | Shows | Inputs |
| --- | --- | --- | --- |
| [01_stats_transformer_ols_vs_statsmodels.ipynb](01_stats_transformer_ols_vs_statsmodels.ipynb) | stats-transformer | OLS and robust OLS checked against statsmodels | statsmodels datasets |
| [02_auto_econ_sentiment_fomc_statements.ipynb](02_auto_econ_sentiment_fomc_statements.ipynb) | auto-econ-sentiment | Six dictionaries on FOMC statements | committed |
| [03_econ_pdf_extract_claims_and_equations.ipynb](03_econ_pdf_extract_claims_and_equations.ipynb) | econ-pdf-extract | Claims and equations with page provenance | synthetic PDF, Shapiro, Sudhof and Wilson ([FRBSF WP 2017-01](https://doi.org/10.24148/wp2017-01)) downloaded |
| [04_reproducible_econ_cached_pipeline_and_claim_checks.ipynb](04_reproducible_econ_cached_pipeline_and_claim_checks.ipynb) | reproducible-econ | Cold run, cache hits, claim checks, manifest | synthetic |

Inputs are listed in [notebook_inputs.yaml](../references/configs/notebook_inputs.yaml) and hash-checked. The FOMC statements are committed and the PDF is downloaded to `data/raw/notebooks/`. Terms are in [data/LICENSES.md](../data/LICENSES.md).

Changes from the originals: paths, on-demand downloads, and a forced cold run and inline figure in `04_reproducible_econ_cached_pipeline_and_claim_checks.ipynb`.

Full citations are in [docs/citations.md](../docs/citations.md).
