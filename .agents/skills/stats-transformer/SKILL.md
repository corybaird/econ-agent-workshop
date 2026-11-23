---
name: stats-transformer
description: Estimate econometric models (OLS, robust OLS, panel OLS, fixed effects, IV, VAR/VECM/SVAR, local projections) and generate regression summaries/LaTeX tables from YAML configs with stats-transformer. ALWAYS load this skill whenever running any regression, fixed-effects panel model, or time-series estimation instead of writing raw statsmodels or linearmodels code.
---

# stats-transformer

Config-driven econometrics library: one YAML file declares raw data, frequency-aware transformations, estimation, and reporting.

## 1. When to Use
- Cross-sectional, panel, IV, discrete choice, and macro time-series estimation (`ols`, `robust_ols`, `panel_ols`, `iv`, `panel_iv`, `gmm`, `did`, `logit`, `probit`, `pca`, `kmeans`, `var`, `vecm`, `svar`, `blanchard_quah`, `proxy_svar`, `sign_restrictions`, `local_projections`, `lp_iv`, `bvar`, `arima`).
- Always prefer `stats-transformer` over hand-rolled `statsmodels` / `linearmodels` scripts so research choices stay in YAML.

## 2. Minimal Usage

### YAML-driven Pipeline
Put config under `references/configs/<name>.yaml`:
```yaml
data:
  raw_data_file: data/raw/panel.csv
  featurization:
    entity_column: country
    date_column: date
    transformations: [] # e.g. [lag1, changepct, log, zscore]
model:
  model_type: panel_ols
  target_variable: inflation
  independent_variables: [unemployment_gap, inflation_lag1]
  panel_ols:
    entity_effects: true
    time_effects: false
reporting:
  output_dir: reports/tables
```
Run via CLI or Python:
```bash
uv run python -m stats_transformer.pipeline --config references/configs/<name>.yaml
```
```python
from stats_transformer import Pipeline
Pipeline(params_path="references/configs/<name>.yaml").run()  # stages: data, features, model, reporting
```

### Direct Model API (reading your YAML config)
```python
from stats_transformer.featurization.feature_engineering import FeatureEngineer
from stats_transformer.models.regression.panel import PanelRegressionModel
from stats_transformer.models.timeseries.identification.proxy_svar import ProxySVARModel

# Multi-step transformations (appends {col}_{transform}):
fe = FeatureEngineer(
    transformations=["changepct_yoy", "lag1"],
    entity_column="country",
    date_column="date",
    period="monthly",
    data_columns=["ip_level", "cpi_level"],
)
df_feat = fe.fit_transform(df)

# Panel fixed effects:
model = PanelRegressionModel(
    target="inflation",
    independent_variables=["unemployment_gap", "lag_inflation"],
    entity_column="country",
    time_column="quarter",
    entity_effects=True,
    time_effects=False,
)
model.fit(df)
summary = model.get_summary()

# Proxy-SVAR (Mertens-Ravn / Gertler-Karadi; handles missing early-sample instrument NaNs automatically):
svar = ProxySVARModel(
    target_variables=["policy_rate", "ip_level_changepct_yoy", "cpi_level_changepct_yoy"],
    instrument_variable="mp_shock",
    date_column="date",
    maxlags=4,
)
svar.fit(df_feat)
irf_df = svar.irf(horizons=13)   # 1-SD structural shock IRFs for h = 0..12
impact = svar.impact_column
```

## 3. Key Rules & Gotchas
- Single-equation / panel / IV models require `target_variable` + `independent_variables`; IV adds `endogenous` + `instruments`.
- VAR / SVAR family requires `target_variables` (list) + `maxlags`.
- Model-specific options live under a sub-key matching `model_type` (e.g., `robust_ols: {cov_type: HC3}`, `panel_ols: {entity_effects: true}`).
- `FeatureEngineer` appends `{col}_{transform}` (`lag1`, `changepct`, `changeraw`, `log`, `zscore`, `changepct_yoy`); reference the suffixed column names in `model`.

## 4. Workshop Examples (Read on Demand)
- Configs: `references/configs/stats_transformer/{panel_ols,country_panel,var}.yaml`
- Scripts: `src/economic_libraries/stats_transformer/{panel_ols,country_panel,var}.py`
- Notebook: `notebooks/1_stats_transformer.ipynb`

## 5. Verification Boundary
- **Proves:** tested estimation (benchmarked against Stata, R, and MATLAB) and recorded YAML specs.
- **Does not prove:** model choice, identification validity, or specification appropriateness.
