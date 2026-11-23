"""Verify paper claims: econ-pdf-extract extracts them, reproducible-econ checks them.

Pipeline: download the public Nakamura and Steinsson NBER Working Paper 19260
PDF (SHA-256 checked), extract claims with page provenance via econ-pdf-extract,
write the numeric ones out as DRAFT ClaimCheckStage entries, apply the
AI-drafted mapping in references/configs/verify_paper_claims/paper_claims.yaml (not yet
confirmed by a person), then re-estimate the Nakamura and
Steinsson event-study regressions with reproducible-econ and verify each mapped
claim against the estimated coefficients. Draft claims and the injected
pipeline config land under data/intermediate/verify_paper_claims/; the claims report
and run manifest land under data/final/verify_paper_claims/.
"""

import hashlib
import json
import logging
import re
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml
from econ_pdf_extract import ExtractionPipeline
from econ_pdf_extract.core import PaperMetadata
from reproducible_econ.pipeline.runner import PipelineRunner

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)

CONFIG_PATH = "references/configs/verify_paper_claims/paper_claims.yaml"


class VerifyPaperClaims:
    """Extract claims from a paper and verify them against re-estimates."""

    def __init__(self, config_path=None):
        self.config_path = config_path or CONFIG_PATH

    def run(self):
        """Download the paper, draft claims, apply the claim map, and verify."""
        logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
        with open(PROJECT_ROOT / self.config_path) as f:
            config = yaml.safe_load(f)

        pdf_path = self._fetch_paper(config["paper"])
        result = ExtractionPipeline(pdf_path, paper=self._paper_metadata(config["paper"])).run()
        drafts = [c for c in result.claims if re.search(r"\d", c.quote)]
        logger.info("Extracted %d claims from %s (%d pages); %d containing numbers",
                    len(result.claims), Path(pdf_path).name, result.page_count, len(drafts))

        stamp = f"{datetime.now():%Y%m%d_%H%M%S}"
        drafts_dir = PROJECT_ROOT / f"data/intermediate/verify_paper_claims/{stamp}"
        drafts_dir.mkdir(parents=True, exist_ok=True)
        self._write_drafts(drafts, drafts_dir / "claim_drafts.yaml")

        mapped = self._apply_claim_map(config, drafts)
        claims_summary = self._run_pipeline(config, mapped, stamp)
        passed = claims_summary["passed"]
        total = claims_summary["total"]
        logger.info("Summary: extracted claims with numbers N=%d, mapped M=%d, verified K/M=%d/%d",
                    len(drafts), len(mapped), passed, total)
        if passed < total:
            raise AssertionError(f"only {passed}/{total} mapped claims verified against the re-estimates")
        return {"drafts": drafts, "mapped": mapped, "summary": claims_summary}

    @staticmethod
    def _paper_metadata(paper_cfg):
        return PaperMetadata(
            paper_id=paper_cfg["id"],
            source_path=str(PROJECT_ROOT / paper_cfg["pdf_path"]),
            authors=paper_cfg["authors"],
            title=paper_cfg["title"],
            journal=paper_cfg["journal"],
        )

    def _fetch_paper(self, paper_cfg):
        """Return the local PDF path, downloading on demand and checking SHA-256."""
        path = PROJECT_ROOT / paper_cfg["pdf_path"]
        expected = paper_cfg["sha256"]
        if not path.exists() or self._sha256(path) != expected:
            path.parent.mkdir(parents=True, exist_ok=True)
            logger.info("Downloading %s -> %s", paper_cfg["url"], path)
            request = urllib.request.Request(paper_cfg["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request) as response, open(path, "wb") as f:
                f.write(response.read())
        digest = self._sha256(path)
        if digest != expected:
            raise AssertionError(f"SHA-256 mismatch for {path.name}: got {digest}, expected {expected}")
        logger.info("PDF hash verified: %s", digest[:16])
        return path

    @staticmethod
    def _sha256(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    @staticmethod
    def _write_drafts(claims, path):
        payload = {"note": "DRAFT entries extracted by econ-pdf-extract; a subset is mapped in verify_paper_claims/paper_claims.yaml", "entries": [
            {"claim_id": c.claim_id, "page": c.page, "section": c.section, "quote": c.quote} for c in claims
        ]}
        with open(path, "w") as f:
            yaml.safe_dump(payload, f, sort_keys=False, width=100)
        logger.info("Draft claims written to %s", path)

    def _apply_claim_map(self, config, drafts):
        """Validate the committed claim map against the drafts and build ClaimCheckStage entries."""
        by_id = {c.claim_id: c for c in drafts}
        entries = []
        for entry in config["claims"]:
            claim = by_id.get(entry["claim_id"])
            if claim is None:
                raise AssertionError(f"claim map references {entry['claim_id']} but no such draft claim was extracted")
            span = entry["quote_span"]
            if span not in claim.quote:
                raise AssertionError(f"quote span no longer present in {entry['claim_id']}: {span!r}")
            entries.append({
                "id": f"{entry['spec']}_{entry['claim_id']}",
                "description": f"Extracted claim {entry['claim_id']} (WP 19260 p{entry['page']}, quote: '{span}') maps to {entry['spec']}",
                "tidy_key": "estimates",
                "spec": entry["spec"],
                "key_variable": entry["key_variable"],
                "coef": entry["coef"],
                "tol": entry["tol"],
            })
        logger.info("Claim map matched the PDF quotes for %d/%d extracted claims", len(entries), len(drafts))
        return entries

    def _run_pipeline(self, config, claims_entries, stamp):
        """Inject the mapped entries into the pipeline config and verify them."""
        with open(PROJECT_ROOT / config["pipeline_config_path"]) as f:
            pipeline_cfg = yaml.safe_load(f)
        pipeline_cfg["claims"]["entries"] = claims_entries
        injected_path = (PROJECT_ROOT / f"data/intermediate/verify_paper_claims/{stamp}/pipeline_injected.yaml")
        injected_path.parent.mkdir(parents=True, exist_ok=True)
        with open(injected_path, "w") as f:
            yaml.safe_dump(pipeline_cfg, f, sort_keys=False)

        runner = PipelineRunner(config_path=injected_path, targets=[config["claims_stage"]])
        runner.run()
        for name, stage in runner.last_manifest["stages"].items():
            logger.info("Stage %s: status=%s elapsed=%.3fs", name, stage["status"], stage["elapsed_sec"])
        return self._claims_summary(runner)

    @staticmethod
    def _claims_summary(runner):
        summary = runner.last_manifest.get("claims") or {}
        if not summary:
            raise AssertionError("claims summary missing from run manifest")
        report_rel = summary.get("report_path")
        report_path = Path(runner.manifest_path).parent / report_rel if report_rel else Path(runner.manifest_path).parent / "claims_report.json"
        if report_path.exists():
            logger.info("Claims report: %s", report_path)
            report = json.loads(report_path.read_text())
            for r in report.get("claims", []):
                logger.info("Claim %s: %s%s", r["id"], r["status"], f" ({r['reason']})" if r.get("reason") else "")
        else:
            raise AssertionError(f"claims report not found at {report_path}")
        return summary


if __name__ == "__main__":
    VerifyPaperClaims().run()
