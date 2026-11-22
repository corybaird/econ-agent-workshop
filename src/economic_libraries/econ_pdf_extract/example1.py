"""Example 1: extract sections, claims, and statistics from the synthetic example paper.

The PDF is a 2-page synthetic working paper ("Example A. Author") shipped with
econ-pdf-extract; the run logs every claim with its page/section provenance and
writes a Markdown report to data/final/.
"""

import logging
from datetime import datetime

import yaml
from econ_pdf_extract import ExtractionPipeline, MarkdownReportWriter

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)


def run():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    with open(PROJECT_ROOT / "references/configs/econ_pdf_extract_example.yaml") as f:
        config = yaml.safe_load(f)
    pdf_path = PROJECT_ROOT / config["input"]["pdf_path"]

    result = ExtractionPipeline(pdf_path).run()
    logger.info(
        "Extracted %d pages: %d claims, %d math objects, %d symbols, %d links, %d statistics",
        result.page_count, len(result.claims), len(result.math_objects),
        len(result.symbols), len(result.links), len(result.statistics),
    )
    for claim in result.claims:
        types = ", ".join(t.value for t in claim.claim_types)
        logger.info("%s p%d [%s] (%s) %s: %s", claim.claim_id, claim.page, types, claim.attribution.value, claim.section, claim.quote)
    for stat in result.statistics:
        logger.info("STAT %s (%s) on page %d", stat.kind, stat.value, stat.page)

    report = MarkdownReportWriter().render(result)
    out_path = PROJECT_ROOT / f"data/final/example_paper_report_{datetime.now():%Y%m%d_%H%M%S}.md"
    out_path.write_text(report)
    logger.info("Markdown report written to %s", out_path)


if __name__ == "__main__":
    run()
