"""Example 2: offline claim evaluation against hand-labelled reference claims.

The reference YAML in references/configs/econ_pdf_extract_example_refs/ quotes
the synthetic example paper verbatim. ClaimEvaluator re-runs the extraction
pipeline, scores extracted claims against the references (token F1 /
sequence ratio), and reports recall/precision plus page and section accuracy.
Expected metrics are 1.0 everywhere because the references are verbatim.
"""

import logging
from datetime import datetime

import yaml
from econ_pdf_extract import ExtractionPipeline
from econ_pdf_extract.core import PaperMetadata
from econ_pdf_extract.eval import ClaimEvaluator

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)


def run():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    with open(PROJECT_ROOT / "references/configs/econ_pdf_extract_example.yaml") as f:
        config = yaml.safe_load(f)
    eval_cfg, expected = config["eval"], config["expected_eval"]
    paper = PaperMetadata(
        paper_id="example_paper",
        source_path=str(PROJECT_ROOT / "data/raw/example_paper.pdf"),
        authors="Example A. Author",
        title="A Synthetic Economics Working Paper",
        journal="Workshop",
    )
    result = ExtractionPipeline(paper.source_path, paper=paper).run()
    logger.info("Extracted %d claims from %s", len(result.claims), paper.source_path)

    evaluator = ClaimEvaluator(
        refs_dir=PROJECT_ROOT / eval_cfg["refs_dir"],
        papers=[paper],
        seq_threshold=eval_cfg["seq_threshold"],
        f1_threshold=eval_cfg["f1_threshold"],
        output_dir=PROJECT_ROOT / f"data/final/eval_claims_{datetime.now():%Y%m%d_%H%M%S}",
    )
    summary = evaluator.run()
    agg = summary["aggregate"]
    logger.info(
        "Eval: refs=%d tp=%d recall=%.2f precision=%.2f exact_page=%.2f strict_section=%.2f",
        agg["refs"], agg["tp"], agg["recall"], agg["precision"], agg["exact_page_accuracy"], agg["strict_section_accuracy"],
    )
    for metric, want in expected.items():
        if agg[metric] != want:
            raise AssertionError(f"{metric}={agg[metric]} but expected {want}")


if __name__ == "__main__":
    run()
