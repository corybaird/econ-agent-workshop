"""Example 2: cached rerun proves the pipeline is reproducible.

Runs the same config twice. The cold run executes and caches both stages
(parquet under data/cache/); the warm run loads them from cache
(status=cache_hit, elapsed 0) and reproduces byte-identical estimates.
"""

import logging

import pandas as pd
from reproducible_econ.pipeline.runner import PipelineRunner

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)

CONFIG_PATH = "references/configs/reproducible_econ_example_pipeline.yaml"


def run():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    config_path = PROJECT_ROOT / CONFIG_PATH

    cold_runner = PipelineRunner(config_path=config_path)
    cold_data = cold_runner.run()
    cold_statuses = {name: stage["status"] for name, stage in cold_runner.last_manifest["stages"].items()}
    logger.info("Cold run statuses: %s", cold_statuses)

    warm_runner = PipelineRunner(config_path=config_path)
    warm_data = warm_runner.run()
    warm_statuses = {name: stage["status"] for name, stage in warm_runner.last_manifest["stages"].items()}
    logger.info("Warm run statuses: %s", warm_statuses)

    pd.testing.assert_frame_equal(cold_data["estimates"], warm_data["estimates"])
    warm_hits = [warm_statuses[n] for n in ("prepare_data", "estimate_ols")]
    if warm_hits != ["cache_hit", "cache_hit"]:
        raise AssertionError(f"expected cache_hit on both cached stages, got {warm_hits}")
    logger.info("Warm rerun reproduced identical estimates from cache")


if __name__ == "__main__":
    run()
