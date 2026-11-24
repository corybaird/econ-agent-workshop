"""VAR on the packaged macrodata benchmark (US real GDP, consumption, investment)."""

import logging
from datetime import datetime

import yaml
from stats_transformer.data import load_example
from stats_transformer.models.timeseries.reduced_form.var import VARModel

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)


class MacroVAR:
    def run(self):
        """Estimate the VAR and save its summary."""
        logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
        with open(PROJECT_ROOT / "references/configs/stats_transformer/var.yaml") as f:
            config = yaml.safe_load(f)
        data_cfg, model_cfg = config["data"], config["model"]
        df = load_example(data_cfg["example_dataset"])
        logger.info("Loaded packaged macrodata example: %d observations, %d columns", len(df), df.shape[1])

        model = VARModel(target_variables=model_cfg["target_variables"], maxlags=model_cfg["maxlags"])
        model.fit(df)
        summary = str(model.get_summary())
        logger.info("\n%s", summary)

        out_dir = PROJECT_ROOT / "data/final/econometrics"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"macro_var_summary_{datetime.now():%Y%m%d_%H%M%S}.txt"
        out_path.write_text(summary)
        logger.info("Summary written to %s", out_path)


if __name__ == "__main__":
    MacroVAR().run()
