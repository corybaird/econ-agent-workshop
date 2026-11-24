# Notebooks

One per library, adapted from the library repositories and committed with outputs. `jupyter` (including `jupyterlab` and `ipykernel`) is locked in `pyproject.toml` and `uv.lock`.

Run from the repo root using the locked `uv` environment:

```bash
uv sync
uv run jupyter lab notebooks/
```

To select the locked `uv` kernel inside VS Code, Cursor, or an existing Jupyter server, register it once:

```bash
uv run python -m ipykernel install --user \
  --name econ-agent-workshop \
  --display-name "Python (econ-agent-workshop)"
```

| Notebook | Library | Shows | Inputs |
| --- | --- | --- | --- |
| [1_stats_transformer.ipynb](1_stats_transformer.ipynb) | stats-transformer | OLS and robust OLS checked against statsmodels | statsmodels datasets |
| [2_auto_econ_sentiment.ipynb](2_auto_econ_sentiment.ipynb) | auto-econ-sentiment | Six dictionaries on FOMC statements | committed |
| [3_econ_pdf_extract.ipynb](3_econ_pdf_extract.ipynb) | econ-pdf-extract | Claims and equations with page provenance | synthetic PDF, Shapiro, Sudhof and Wilson ([FRBSF WP 2017-01](https://doi.org/10.24148/wp2017-01)) downloaded |
| [4_reproducible_econ.ipynb](4_reproducible_econ.ipynb) | reproducible-econ | Cold run, cache hits, claim checks, manifest | synthetic |

Inputs are listed in [downloads.yaml](../references/configs/downloads.yaml) and hash-checked. The FOMC statements are committed and the PDF is downloaded to `data/raw/notebooks/`. Terms are in [data/LICENSES.md](../data/LICENSES.md).

Changes from the originals: paths, on-demand downloads, and an inline figure in `4_reproducible_econ.ipynb`.

Full citations are in [docs/citations.md](../docs/citations.md).
