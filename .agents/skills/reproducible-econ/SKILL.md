---
name: reproducible-econ
description: Orchestrate config-driven multi-stage research pipelines with atomic parquet caching, provenance manifests, LaTeX table/macro emitters, and declarative claim checks via reproducible-econ. Use when wiring end-to-end reproducible pipelines or Overleaf outputs.
---

# reproducible-econ

Config-driven stage DAG runner with atomic parquet caching (v2 fingerprints), `run_manifest.json` provenance, paper-ready LaTeX emitters, and declarative claim checks.

## 1. When to Use
- Wiring multi-stage research workflows (`data` -> `estimate` -> `report`) that must re-run in one command, cache unchanged stages, emit LaTeX tables/macros/figures directly for Overleaf, and verify numeric claims against estimates.
- Always prefer `reproducible-econ` over hand-rolled caching, ad-hoc manifest JSONs, or manual LaTeX table formatting.

## 2. Minimal Usage

### Stage Class Contract
Each stage exposes `run(self, data, config)` and stores pandas DataFrames in `data`:
```python
class EstimateStage:
    def run(self, data, config):
        # read data["panel"], fit model using config["estimation"], write tidy DF
        data["estimates"] = estimates_df
        return data
```

### YAML Pipeline Config (`references/configs/<name>/pipeline.yaml`)
```yaml
includes: []
project: {name: my_study, seed: 42}
output:
  cache_dir: data/cache/my_study
  reports_dir: reports/overleaf/my_study
  tables_dir: ${output.reports_dir}/tables
  macros_path: ${output.reports_dir}/macros.tex
  claims_path: ${output.reports_dir}/claims_report.json
tables:
  strict: true
  exports:
    - {key: estimates, filename: estimates.tex}
latex_macros:
  entries:
    - {tidy_key: estimates, spec: baseline, key_variable: x, name: Baseline}
claims:
  fail_on_error: false
  entries:
    - {id: slope_neg, tidy_key: estimates, spec: baseline, key_variable: x, sign: negative, pval_below: 0.05}
default_module: src.my_study.stages
stages:
  - {name: prepare, class: PrepareStage, phase: data, produces: [panel], cache: true, cache_inputs: [data, project]}
  - {name: estimate, class: EstimateStage, phase: estimate, requires: [panel], produces: [estimates], cache: true, cache_inputs: [estimation]}
  - {name: export_tables, module: reproducible_econ.emitters.tables, class: LatexTableStage, phase: report, requires: [estimates], cache: false}
  - {name: export_macros, module: reproducible_econ.emitters.macros, class: LatexMacroStage, phase: report, requires: [estimates], cache: false}
  - {name: check_claims, module: reproducible_econ.emitters.claims, class: ClaimCheckStage, phase: report, requires: [estimates], produces: [claims_results], cache: false}
```

### Run via CLI or Python
```bash
uv run python -m reproducible_econ.pipeline.runner --config references/configs/<name>/pipeline.yaml
uv run python -m reproducible_econ.pipeline.runner --config references/configs/<name>/pipeline.yaml --no-cache
```
```python
from reproducible_econ.pipeline.runner import PipelineRunner
runner = PipelineRunner(config_path="references/configs/<name>/pipeline.yaml")
data = runner.run()  # writes run_manifest.json, tables/*.tex, macros.tex, claims_report.json
```

## 3. Key Rules & Gotchas
- `LatexMacroStage` (YAML key `latex_macros`) and `ClaimCheckStage` (YAML key `claims`) expect a tidy `estimates` DataFrame with columns `spec_name`, `key_variable`, `coef`, `se`, `pval`, `n_obs`.
- `ClaimCheckStage` supports `sign` (`positive`/`negative`), `coef` + `tol`, `pval_below`/`pval_above`/`pval_between`, `n_obs`, `date_min`/`date_max`, and `bounds`.
- `reproducible-econ` intentionally has no Overleaf API code: point `output.reports_dir` at your report/Overleaf folder with stable filenames so `\input{}` never breaks.
- Combine with `econ-pdf-extract` to extract candidate paper claims and verify them via `ClaimCheckStage`.

## 4. Workshop Examples (Read on Demand)
- Configs: `references/configs/reproducible_econ/pipeline.yaml`, `references/configs/verify_paper_claims/pipeline.yaml`
- Scripts: `src/economic_libraries/reproducible_econ/{run_pipeline,cached_rerun}.py`, `src/economic_libraries/verify_paper_claims/run.py`
- Notebook: `notebooks/4_reproducible_econ.ipynb`

## 5. Verification Boundary
- **Proves:** DAG order, verified cache fingerprints, claim-check pass/fail, and config/git/artifact manifest match.
- **Does not prove:** scientific validity or that the underlying econometric design is correct.
