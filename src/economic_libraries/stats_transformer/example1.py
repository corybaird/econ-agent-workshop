"""Example 1: YAML-driven fixed-effects panel OLS on the Grunfeld (1958) panel."""

import logging
from datetime import datetime

import yaml
from stats_transformer.data import load_example
from stats_transformer.models.regression.panel import PanelRegressionModel

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)


def run():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    with open(PROJECT_ROOT / "references/configs/stats_transformer/panel_ols.yaml") as f:
        config = yaml.safe_load(f)
    data_cfg, model_cfg = config["data"], config["model"]
    panel_cfg = model_cfg.get("panel_ols", {})

    df = load_example(data_cfg["example_dataset"])
    logger.info("Loaded Grunfeld panel: %d rows, %d firms", len(df), df["firm"].nunique())

    model = PanelRegressionModel(
        target=model_cfg["target_variable"],
        independent_variables=model_cfg["independent_variables"],
        entity_column=data_cfg["featurization"]["entity_column"],
        time_column=data_cfg["featurization"]["date_column"],
        entity_effects=panel_cfg.get("entity_effects", True),
        time_effects=panel_cfg.get("time_effects", False),
    )
    model.fit(df)
    summary = str(model.get_summary())
    logger.info("\n%s", summary)

    out_path = PROJECT_ROOT / f"data/final/grunfeld_panel_summary_{datetime.now():%Y%m%d_%H%M%S}.txt"
    out_path.write_text(summary)
    logger.info("Summary written to %s", out_path)


if __name__ == "__main__":
    run()
