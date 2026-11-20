"""Example 2: VAR on the packaged macrodata benchmark (US real GDP, consumption, investment)."""

import logging
from datetime import datetime

from stats_transformer.data import load_example
from stats_transformer.models.timeseries.reduced_form.var import VARModel

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)

TARGET_VARIABLES = ["realgdp", "realcons", "realinv"]
MAXLAGS = 2


def run():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    df = load_example("macrodata")
    logger.info("Loaded packaged macrodata example: %d observations, %d columns", len(df), df.shape[1])

    model = VARModel(target_variables=TARGET_VARIABLES, maxlags=MAXLAGS)
    model.fit(df)
    summary = str(model.get_summary())
    logger.info("\n%s", summary)

    out_path = PROJECT_ROOT / f"data/final/macro_var_summary_{datetime.now():%Y%m%d_%H%M%S}.txt"
    out_path.write_text(summary)
    logger.info("Summary written to %s", out_path)


if __name__ == "__main__":
    run()
