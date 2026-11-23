---
name: econ-pdf-extract
description: Extract auditable empirical claims, math/logic objects, symbol definitions, and quantitative statistics with exact section and page provenance from economics PDFs via econ-pdf-extract. Use when parsing papers or auditing paper claims.
---

# econ-pdf-extract

Deterministic PDF extraction library for economics papers that preserves exact provenance (`page`, `section`, `attribution`, `bbox`) on every extracted claim, equation, and statistic.

## 1. When to Use
- Extracting empirical claims, equations, symbol definitions, cross-references, or headline statistics from working-paper or journal PDFs.
- Always prefer `econ-pdf-extract` over raw `pypdf`/`fitz` text dumps so every claim stays anchored to its exact page and section heading.

## 2. Minimal Usage

### Python API
```python
from econ_pdf_extract import ExtractionPipeline, JsonReportWriter, MarkdownReportWriter

result = ExtractionPipeline("data/raw/paper.pdf").run()

for claim in result.claims:
    print(claim.claim_id, f"p.{claim.page}", claim.section, claim.attribution.value, claim.quote)

for stat in result.statistics:
    print(stat.kind, stat.value, f"p.{stat.page}")

json_text = JsonReportWriter().to_json(result)
md_text = MarkdownReportWriter().render(result)
```

### CLI
```bash
uv run econ-pdf extract data/raw/paper.pdf --json --output-dir data/final/
uv run econ-pdf extract data/raw/paper.pdf --markdown --output-dir data/final/
uv run econ-pdf targets data/raw/paper.pdf --reports-dir reports/tables
```

## 3. Key Rules & Gotchas
- **Never drop provenance:** every reported claim must retain `claim_id`, `page`, `section`, `attribution` (`own`, `literature`, `comparison`), and exact `quote`.
- Filter numeric candidate claims before mapping them to `reproducible-econ` `ClaimCheckStage` entries; human confirmation is required before treating a draft claim map as verified.
- For degraded multi-line display equations, use `--ocr glm_ocr --ocr-policy fallback` with `VLLM_BASE_URL` (default `--ocr none` handles embedded-text PDFs directly).
- Optional `[nlp]` extra adds spaCy dependency filtering and `(cause, direction, outcome)` causal triples.

## 4. Workshop Examples (Read on Demand)
- Configs: `references/configs/econ_pdf_extract/{extraction,ref_claims_example_paper}.yaml`
- Scripts: `src/economic_libraries/econ_pdf_extract/{extract_claims,evaluate_claims}.py`
- Linked demo: `src/economic_libraries/verify_paper_claims/run.py`
- Notebook: `notebooks/3_econ_pdf_extract.ipynb`

## 5. Verification Boundary
- **Proves:** section heading and source page provenance for extracted text.
- **Does not prove:** empirical truth or complete recall (a fluent claim without a page number is unauditable; human verification stays required).
