"""Typed, wall-enforced domain tools wrapping the four econ research libraries."""

import importlib
import json
import os
import sys
from pathlib import Path

import pandas as pd
import yaml
from auto_econ_sentiment.models.sentiment_lexical import SentimentLexical
from econ_pdf_extract import ExtractionPipeline, JsonReportWriter, MarkdownReportWriter
from reproducible_econ.pipeline.runner import PipelineRunner
from stats_transformer.featurization.feature_engineering import FeatureEngineer
from stats_transformer.models.regression.panel import PanelRegressionModel
from stats_transformer.models.timeseries.identification.proxy_svar import ProxySVARModel

ALLOWED_WRITE_PREFIXES = (
    "references/configs/",
    "references/dictionaries/",
    "src/",
    "reports/",
    "docs/",
    "data/intermediate/",
    "data/final/",
)

CONFIG_TEMPLATES = {
    "proxy_svar": """data:
  raw_data_file: data/raw/macro_monthly.csv
  entity_column: country
  date_column: date
  period: monthly
  transform_columns: [ip_level, cpi_level]
  transformations: [changepct_yoy]
model:
  target_variables: [policy_rate, ip_level_changepct_yoy, cpi_level_changepct_yoy]
  instrument_variable: mp_shock
  maxlags: 4
  horizons: 13
output:
  irf_csv: data/final/proxy_svar_irfs.csv
  irf_tex: reports/proxy_svar_irfs.tex
  summary_txt: reports/proxy_svar_summary.txt
""",
    "panel_ols": """data:
  raw_data_file: data/raw/macro_panel.csv
  entity_column: country
  time_column: quarter
model:
  target_variable: inflation
  independent_variables: [unemployment_gap, lag_inflation]
  entity_effects: true
  time_effects: false
output:
  summary_txt: reports/panel_ols_summary.txt
  table_tex: reports/panel_ols_table.tex
""",
    "sentiment": """input:
  file_path: data/raw/cb_statements.csv
  text_column: text
  date_column: date
lexical:
  dictionary: hubert
  aggregation: posneg
  directionality_note: "Hubert-Labondance (2021) central-bank growth-acceleration vs contraction tone on [0, 2], midpoint 1.0."
output:
  csv_path: data/final/cb_statements_scored.csv
""",
    "reproducible_econ": """includes: []
project: {name: study, seed: 42}
output:
  cache_dir: data/intermediate/cache/study
  reports_dir: reports/study
  tables_dir: "${output.reports_dir}/tables"
  macros_path: "${output.reports_dir}/macros.tex"
  claims_path: "${output.reports_dir}/claims_report.json"
tables:
  strict: true
  exports:
    - {key: estimates, filename: estimates.tex}
latex_macros:
  entries:
    - {tidy_key: estimates, spec: baseline, key_variable: unemployment_gap, name: BaselineSlope}
claims:
  fail_on_error: false
  entries:
    - {id: phillips_slope, tidy_key: estimates, spec: baseline, key_variable: unemployment_gap, coef: -0.60, tol: 0.10, sign: negative, pval_below: 0.05}
default_module: src.study.stages
stages:
  - {name: extract_claims, class: ExtractClaimsStage, phase: data, produces: [claims_df], cache: true, cache_inputs: [project]}
  - {name: estimate, class: EstimatePanelStage, phase: estimate, produces: [estimates], cache: true, cache_inputs: [project]}
  - {name: export_tables, module: reproducible_econ.emitters.tables, class: LatexTableStage, phase: report, requires: [estimates], cache: false}
  - {name: export_macros, module: reproducible_econ.emitters.macros, class: LatexMacroStage, phase: report, requires: [estimates], cache: false}
  - {name: check_claims, module: reproducible_econ.emitters.claims, class: ClaimCheckStage, phase: report, requires: [estimates], produces: [claims_results], cache: false}
""",
}


class EconHarnessToolkit:
    """Enforces folder walls and exposes deterministic tools for the four econ libraries."""

    def __init__(self, workspace_root):
        self.root = Path(workspace_root).resolve()
        self.used_libraries = set()

    def _resolve_read(self, rel_path):
        raw = Path(rel_path)
        if raw.is_absolute():
            raise PermissionError(f"Absolute path not allowed: {rel_path}")
        target = (self.root / raw).resolve()
        if not target.is_relative_to(self.root):
            raise PermissionError(f"Path escapes workspace root: {rel_path}")
        return target

    def _resolve_write(self, rel_path):
        raw = Path(rel_path)
        if raw.is_absolute():
            raise PermissionError(f"Absolute path not allowed: {rel_path}")
        target = (self.root / raw).resolve()
        if not target.is_relative_to(self.root):
            raise PermissionError(f"Path escapes workspace root: {rel_path}")
        rel_norm = target.relative_to(self.root).as_posix()
        if rel_norm.startswith("data/raw/") or rel_norm == "data/raw":
            raise PermissionError("WALL BLOCKED: data/raw/ is strictly read-only.")
        if not any(rel_norm.startswith(prefix) for prefix in ALLOWED_WRITE_PREFIXES):
            raise PermissionError(
                f"WALL BLOCKED: '{rel_norm}' is outside allowed output folders ({', '.join(ALLOWED_WRITE_PREFIXES)})."
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def list_files(self, subdir=""):
        """List files inside the workspace (read-only)."""
        base = self._resolve_read(subdir) if subdir else self.root
        if not base.exists():
            return f"Directory not found: {subdir}"
        files = sorted(
            p.relative_to(self.root).as_posix()
            for p in base.rglob("*")
            if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts
        )
        return "\n".join(files) if files else "(empty)"

    def read_file(self, rel_path, max_chars=4000):
        """Read a text file inside the workspace (read-only)."""
        target = self._resolve_read(rel_path)
        if not target.is_file():
            return f"File not found: {rel_path}"
        return target.read_text(errors="replace")[:max_chars]

    def write_file(self, rel_path, content):
        """Write a file strictly inside allowed non-raw folders (enforces data/raw and clean-root walls)."""
        target = self._resolve_write(rel_path)
        target.write_text(content)
        return f"Wrote {target.relative_to(self.root).as_posix()} ({len(content)} bytes)"

    def get_config_template(self, library):
        """Return a minimal verified YAML template for proxy_svar, panel_ols, sentiment, or reproducible_econ."""
        key = library.strip().lower().replace("-", "_")
        if key not in CONFIG_TEMPLATES:
            return f"Unknown template '{library}'. Choose one of: {', '.join(CONFIG_TEMPLATES)}"
        return CONFIG_TEMPLATES[key]

    def run_proxy_svar(self, config_path):
        """Run FeatureEngineer + ProxySVARModel from a YAML config and save IRF CSV, LaTeX table, and summary."""
        self.used_libraries.add("stats_transformer")
        cfg_file = self._resolve_read(config_path)
        cfg = yaml.safe_load(cfg_file.read_text())
        dcfg, mcfg, ocfg = cfg["data"], cfg["model"], cfg["output"]

        df = pd.read_csv(self._resolve_read(dcfg["raw_data_file"]))
        fe = FeatureEngineer(
            transformations=dcfg.get("transformations", ["changepct_yoy"]),
            entity_column=dcfg.get("entity_column", "country"),
            date_column=dcfg.get("date_column", "date"),
            period=dcfg.get("period", "monthly"),
            data_columns=dcfg.get("transform_columns", ["ip_level", "cpi_level"]),
        )
        df_feat = fe.fit_transform(df)
        svar = ProxySVARModel(
            target_variables=mcfg["target_variables"],
            instrument_variable=mcfg["instrument_variable"],
            date_column=dcfg.get("date_column", "date"),
            maxlags=int(mcfg.get("maxlags", 4)),
        )
        svar.fit(df_feat)
        horizons = int(mcfg.get("horizons", 13))
        irf_df = svar.irf(horizons=horizons)
        irf_out = irf_df.copy()
        irf_out.insert(0, "horizon", range(len(irf_out)))

        csv_path = self._resolve_write(ocfg["irf_csv"])
        tex_path = self._resolve_write(ocfg["irf_tex"])
        sum_path = self._resolve_write(ocfg["summary_txt"])
        irf_out.to_csv(csv_path, index=False)
        tex_path.write_text(self._df_to_booktabs(irf_out, caption="Proxy-SVAR 1-SD Impulse Responses"))
        sum_path.write_text(svar.get_summary())

        t0 = mcfg["target_variables"][0]
        t1 = mcfg["target_variables"][1]
        return json.dumps({
            "status": "ok",
            "var_nobs": int(svar.var_result.nobs),
            "h0_impact": {col: round(float(irf_df[col].iloc[0]), 6) for col in mcfg["target_variables"]},
            "h6_irf": {col: round(float(irf_df[col].iloc[min(6, len(irf_df) - 1)]), 6) for col in mcfg["target_variables"]},
            "policy_h0": round(float(irf_df[t0].iloc[0]), 6),
            "second_var_h0": round(float(irf_df[t1].iloc[0]), 6),
            "second_var_h6": round(float(irf_df[t1].iloc[min(6, len(irf_df) - 1)]), 6),
            "files": [
                csv_path.relative_to(self.root).as_posix(),
                tex_path.relative_to(self.root).as_posix(),
                sum_path.relative_to(self.root).as_posix(),
            ],
        }, indent=2)

    def run_panel_ols(self, config_path):
        """Run PanelRegressionModel from a YAML config and save summary and booktabs LaTeX table."""
        self.used_libraries.add("stats_transformer")
        cfg = yaml.safe_load(self._resolve_read(config_path).read_text())
        dcfg, mcfg, ocfg = cfg["data"], cfg["model"], cfg["output"]

        df = pd.read_csv(self._resolve_read(dcfg["raw_data_file"]))
        time_col = dcfg["time_column"]
        if df[time_col].dtype == object or str(df[time_col].dtype) == "str":
            df = df.copy()
            df["_time_idx"] = pd.PeriodIndex(df[time_col], freq="Q").asi8
            time_col = "_time_idx"

        model = PanelRegressionModel(
            target=mcfg["target_variable"],
            independent_variables=mcfg["independent_variables"],
            entity_column=dcfg["entity_column"],
            time_column=time_col,
            entity_effects=bool(mcfg.get("entity_effects", True)),
            time_effects=bool(mcfg.get("time_effects", False)),
        )
        model.fit(df)
        summary = str(model.get_summary())
        coef_df = pd.DataFrame({
            "variable": list(model.model.params.index),
            "coef": [round(float(v), 4) for v in model.model.params.values],
            "se": [round(float(v), 4) for v in model.model.std_errors.values],
            "pval": [round(float(v), 4) for v in model.model.pvalues.values],
        })

        sum_path = self._resolve_write(ocfg["summary_txt"])
        tex_path = self._resolve_write(ocfg["table_tex"])
        sum_path.write_text(summary)
        tex_path.write_text(self._df_to_booktabs(coef_df, caption="Fixed-Effects Panel OLS Estimates"))
        return json.dumps({
            "status": "ok",
            "n_obs": int(model.model.nobs),
            "estimates": coef_df.to_dict(orient="records"),
            "files": [sum_path.relative_to(self.root).as_posix(), tex_path.relative_to(self.root).as_posix()],
        }, indent=2)

    def run_sentiment(self, config_path):
        """Run SentimentLexical from a YAML config and export scored CSV with matched words and directionality."""
        self.used_libraries.add("auto_econ_sentiment")
        cfg = yaml.safe_load(self._resolve_read(config_path).read_text())
        icfg, lcfg, ocfg = cfg["input"], cfg["lexical"], cfg["output"]

        df = pd.read_csv(self._resolve_read(icfg["file_path"]), parse_dates=[icfg["date_column"]])
        scorer = SentimentLexical(df_input=df, text_column=icfg["text_column"])
        dname, agg = lcfg["dictionary"], lcfg["aggregation"]
        scored = scorer.sentiment_pipeline(dictionary_name=dname, method=agg)
        scored["dictionary"] = dname
        scored["directionality_note"] = lcfg.get(
            "directionality_note",
            "Hubert-Labondance (2021): growth-acceleration vs contraction tone on [0, 2], midpoint 1.0.",
        )

        out_path = self._resolve_write(ocfg["csv_path"])
        scored.to_csv(out_path, index=False)
        score_col = f"{dname}_sentiment_{agg}"
        return json.dumps({
            "status": "ok",
            "rows": len(scored),
            "dictionary": dname,
            "score_column": score_col,
            "mean_score": round(float(scored[score_col].mean()), 4),
            "columns": list(scored.columns),
            "file": out_path.relative_to(self.root).as_posix(),
        }, indent=2)

    def extract_pdf_claims(self, pdf_path, output_md_path, output_json_path=""):
        """Run ExtractionPipeline on a PDF and write provenance-preserving Markdown (and optional JSON) reports."""
        self.used_libraries.add("econ_pdf_extract")
        result = ExtractionPipeline(self._resolve_read(pdf_path)).run()
        md_path = self._resolve_write(output_md_path)
        md_path.write_text(MarkdownReportWriter().render(result))
        written = [md_path.relative_to(self.root).as_posix()]
        if output_json_path:
            js_path = self._resolve_write(output_json_path)
            js_path.write_text(JsonReportWriter().to_json(result))
            written.append(js_path.relative_to(self.root).as_posix())

        return json.dumps({
            "status": "ok",
            "pages": result.page_count,
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "page": c.page,
                    "section": c.section,
                    "attribution": c.attribution.value,
                    "quote": c.quote,
                }
                for c in result.claims
            ],
            "files": written,
        }, indent=2)

    def run_reproducible_pipeline(self, config_path, no_cache=False):
        """Run reproducible-econ PipelineRunner on a YAML config inside the workspace."""
        self.used_libraries.add("reproducible_econ")
        cfg_file = self._resolve_read(config_path)
        if not cfg_file.is_file():
            raise FileNotFoundError(f"YAML config file not found: {config_path}")
        root_str = str(self.root)
        prev_cwd = os.getcwd()
        added = root_str not in sys.path
        if added:
            sys.path.insert(0, root_str)
        importlib.invalidate_caches()
        try:
            os.chdir(self.root)
            runner = PipelineRunner(config_path=cfg_file, no_cache=bool(no_cache))
            runner.run()
        finally:
            os.chdir(prev_cwd)
            if added and root_str in sys.path:
                sys.path.remove(root_str)

        stages = {
            k: {"status": v["status"], "elapsed_sec": round(float(v["elapsed_sec"]), 3)}
            for k, v in runner.last_manifest.get("stages", {}).items()
        }
        return json.dumps({
            "status": "ok",
            "stages": stages,
            "claims": runner.last_manifest.get("claims", {}),
            "manifest_path": Path(runner.manifest_path).resolve().relative_to(self.root).as_posix(),
        }, indent=2)

    def _df_to_booktabs(self, df, caption=""):
        cols = list(df.columns)
        align = "l" + "r" * (len(cols) - 1)
        header = " & ".join(str(c).replace("_", r"\_") for c in cols) + r" \\"
        rows = []
        for _, row in df.iterrows():
            vals = [f"{v:.4f}" if isinstance(v, float) else str(v).replace("_", r"\_") for v in row]
            rows.append(" & ".join(vals) + r" \\")
        return "\n".join([
            r"\begin{table}[htbp]",
            r"\centering",
            f"\\caption{{{caption}}}",
            f"\\begin{{tabular}}{{{align}}}",
            r"\toprule",
            header,
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "",
        ])
