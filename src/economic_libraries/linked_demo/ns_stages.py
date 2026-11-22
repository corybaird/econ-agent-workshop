"""Adapted from reproducible-econ's projects/nakamura_steinsson_2018/stages.py
(reference project), trimmed to the stages the linked demo needs."""

import logging
from pathlib import Path

import pandas as pd
from reproducible_econ.pipeline.stage import BaseStage
from stats_transformer.models import RobustOLSModel

logger = logging.getLogger(__name__)


def _load_dated_parquet(path):
    frame = pd.read_parquet(Path(path)).reset_index()
    date_col = "date" if "date" in frame.columns else "Date"
    frame = frame.rename(columns={date_col: "date"})
    frame["date"] = pd.to_datetime(frame["date"])
    return frame.sort_values("date").reset_index(drop=True)


class PrepareEventDataStage(BaseStage):
    """Build FOMC event-study panel of daily Treasury, TIPS, and breakeven yield changes."""

    def run(self, data, config):
        """Load yield and policy-news shock files, compute daily changes, and filter FOMC dates."""
        data_cfg = config.get("data") or {}
        nominal = _load_dated_parquet(data_cfg["nominal_yields_path"])
        real = _load_dated_parquet(data_cfg["real_yields_path"])
        fomc = _load_dated_parquet(data_cfg["fomc_meetings_path"])
        shocks = _load_dated_parquet(data_cfg["shocks_path"])
        maturities = list(data_cfg.get("maturities", ["02", "03", "05", "10"]))

        nom_cols = ["date"]
        for mat in maturities:
            nominal[f"d_sveny{mat}"] = nominal[f"sveny{mat}"].diff()
            nom_cols.append(f"d_sveny{mat}")

        real_cols = ["date"]
        for mat in maturities:
            real[f"d_tipsy{mat}"] = real[f"tipsy{mat}"].diff()
            real_cols.append(f"d_tipsy{mat}")

        panel = shocks[["date", "ns"]].merge(nominal[nom_cols], on="date", how="inner")
        panel = panel.merge(real[real_cols], on="date", how="left")
        panel = panel.merge(fomc[["date", "unscheduled"]], on="date", how="left")
        panel["unscheduled"] = panel["unscheduled"].fillna(0).astype(int)

        for mat in maturities:
            panel[f"d_breakeven{mat}"] = panel[f"d_sveny{mat}"] - panel[f"d_tipsy{mat}"]

        panel = panel[
            (panel["date"] >= pd.Timestamp(data_cfg.get("start_date", "2000-01-01")))
            & (panel["date"] <= pd.Timestamp(data_cfg.get("end_date", "2014-03-31")))
        ].copy()
        if bool(data_cfg.get("scheduled_only", True)):
            panel = panel[panel["unscheduled"] == 0].copy()

        crisis_start = data_cfg.get("exclude_crisis_start")
        crisis_end = data_cfg.get("exclude_crisis_end")
        if crisis_start and crisis_end:
            panel = panel[
                ~((panel["date"] >= pd.Timestamp(crisis_start)) & (panel["date"] <= pd.Timestamp(crisis_end)))
            ].copy()

        panel["date"] = panel["date"].dt.strftime("%Y-%m-%d")
        logger.info("Prepared FOMC event panel: %d meetings (%s to %s)", len(panel), panel["date"].min(), panel["date"].max())
        data["event_panel"] = panel.reset_index(drop=True)
        return data


class EstimateYieldResponseStage(BaseStage):
    """Estimate high-frequency yield-curve responses via RobustOLSModel."""

    def run(self, data, config):
        """Run robust OLS event-study regressions across nominal, real, and breakeven yields."""
        panel = data["event_panel"]
        est_cfg = config.get("estimation") or {}
        shock_col = str(est_cfg.get("shock_column", "ns"))
        cov_type = str(est_cfg.get("cov_type", "HC1"))
        specs = list(est_cfg.get("specs") or [])
        if not specs:
            raise ValueError("estimation.specs must declare at least one regression specification")

        rows = []
        for spec in specs:
            dependent = spec["dependent"]
            sub = panel[["date", dependent, shock_col]].dropna()
            model = RobustOLSModel(target=dependent, independent_variables=[shock_col], cov_type=cov_type)
            metrics = model.fit(sub.reset_index(drop=True))
            res = model.results
            rows.append(
                {
                    "spec_name": spec["name"],
                    "outcome": spec.get("dependent", dependent),
                    "key_variable": spec.get("key_variable", shock_col),
                    "coef": float(res.params[shock_col]),
                    "se": float(res.model.bse[shock_col]),
                    "pval": float(res.pvalues[shock_col]),
                    "n_obs": int(metrics["num_observations"]),
                    "r2": float(metrics["r_squared"]),
                    "date_min": sub["date"].min(),
                    "date_max": sub["date"].max(),
                }
            )

        logger.info("Estimated %d yield-curve OLS specifications (%s SE)", len(rows), cov_type)
        data["estimates"] = pd.DataFrame(rows)
        return data
