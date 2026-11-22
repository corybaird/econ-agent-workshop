"""Example 1: minimal stage pipeline via reproducible-econ's PipelineRunner.

The YAML config declares three stages shipped with reproducible-econ: two
cached stages (deterministic synthetic panel preparation, then OLS Philips
curve estimation) and one LaTeX table emitter. The runner resolves the DAG,
executes it in topological order, and writes a provenance manifest
(run_manifest.json) next to the emitted tables under data/final/.
"""

import logging

import yaml
from reproducible_econ.pipeline.runner import PipelineRunner

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)

CONFIG_PATH = "references/configs/reproducible_econ_example_pipeline.yaml"


def run():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    with open(PROJECT_ROOT / CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    runner = PipelineRunner(config_path=PROJECT_ROOT / CONFIG_PATH)
    data = runner.run()
    for name, stage in runner.last_manifest["stages"].items():
        logger.info("Stage %s: status=%s elapsed=%.3fs", name, stage["status"], stage["elapsed_sec"])
    logger.info("Baseline slope estimate: p=%.4f", data["estimates"]["pval"].iat[0])
    logger.info("Manifest written to %s", runner.manifest_path)


if __name__ == "__main__":
    run()
