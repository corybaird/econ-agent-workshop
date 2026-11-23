"""Inflation persistence in the G7: fixed-effects panel OLS with country codes from a shared dictionary.

The config lists ISO2 codes and the dataset uses ISO3 codes, so the dictionary in
references/dictionaries/dict_country_converter.py converts between them and
supplies the country names for the output table.
"""

import logging
from datetime import datetime

import yaml
from stats_transformer.data import load_example
from stats_transformer.models.regression.panel import PanelRegressionModel

from economic_libraries.paths import PROJECT_ROOT
from references.dictionaries.dict_country_converter import dict_country

logger = logging.getLogger(__name__)


class CountryPanel:
    """Estimate inflation persistence for the configured countries."""

    def __init__(self, config_path="references/configs/stats_transformer/country_panel.yaml"):
        self.config_path = config_path

    def run(self):
        """Estimate the panel regression and save its summary and a country table."""
        logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
        with open(PROJECT_ROOT / self.config_path) as f:
            config = yaml.safe_load(f)
        data_cfg, model_cfg = config["data"], config["model"]
        panel = self._load_panel(data_cfg)

        model = PanelRegressionModel(
            target=model_cfg["target_variable"],
            independent_variables=model_cfg["independent_variables"],
            entity_column=data_cfg["entity_column"],
            time_column=data_cfg["date_column"],
            **model_cfg["panel_ols"],
        )
        model.fit(panel)
        summary = str(model.get_summary())
        logger.info("\n%s", summary)

        table = panel.groupby("country_name")["inflation"].agg(["mean", "std", "count"]).round(2)
        logger.info("\n%s", table)

        stamp = f"{datetime.now():%Y%m%d_%H%M%S}"
        (PROJECT_ROOT / f"data/final/country_panel_summary_{stamp}.txt").write_text(summary)
        table.to_csv(PROJECT_ROOT / f"data/final/country_panel_table_{stamp}.csv")
        logger.info("Summary and table written to data/final/ with stamp %s", stamp)
        return {"panel": panel, "table": table, "summary": summary}

    @staticmethod
    def _load_panel(data_cfg):
        iso3 = [dict_country["iso2_to_iso3"][code] for code in data_cfg["countries"]]
        entity, date = data_cfg["entity_column"], data_cfg["date_column"]
        df = load_example(data_cfg["example_dataset"])[[entity, date, "inflation"]]
        panel = df[df[entity].isin(iso3)].sort_values([entity, date])
        missing = set(iso3) - set(panel[entity])
        if missing:
            raise ValueError(f"countries not in the dataset: {sorted(missing)}")
        lag = panel[[entity, date, "inflation"]].rename(columns={"inflation": "lag_inflation"})
        lag[date] = lag[date] + 1
        panel = panel.merge(lag, on=[entity, date], how="left").dropna()
        panel = panel[panel[date].between(data_cfg["start_year"], data_cfg["end_year"])]
        panel["country_name"] = panel[entity].map(dict_country["iso3_to_name_short"])
        return panel.reset_index(drop=True)


if __name__ == "__main__":
    CountryPanel().run()
