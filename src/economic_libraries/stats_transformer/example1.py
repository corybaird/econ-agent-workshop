"""Example 1: YAML-driven fixed-effects panel OLS on the Grunfeld (1958) panel."""

import logging
from datetime import datetime
from pathlib import Path

import yaml
from stats_transformer.data import load_example
from stats_transformer.models.regression.panel import PanelRegressionModel

logger = logging.getLogger(__name__)


def _project_root():
    for start in (Path(__file__).resolve(), Path.cwd()):
        for cand in (start, *start.parents):
            if (cand / "src/economic_libraries").is_dir():
                return cand
    # Fallback for the copied (non-editable) venv install: the dist-info records
    # the source tree this package was built from.
    import json
    from importlib.metadata import distribution
    url = json.loads(distribution("econ-agent-harness").read_text("direct_url.json"))["url"]
    root = Path(url.removeprefix("file://"))
    if (root / "src/economic_libraries").is_dir():
        return root
    raise FileNotFoundError("Could not locate the econ-agent-workshop project root")


def run():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    root = _project_root()
    with open(root / "references/configs/stats_transformer_grunfeld_panel.yaml") as f:
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

    out_path = root / f"data/final/grunfeld_panel_summary_{datetime.now():%Y%m%d_%H%M%S}.txt"
    out_path.write_text(summary)
    logger.info("Summary written to %s", out_path)


if __name__ == "__main__":
    run()
