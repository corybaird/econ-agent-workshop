import pytest

from economic_libraries.auto_econ_sentiment.score_sentences import ScoreSentences
from economic_libraries.auto_econ_sentiment.tone_index import ToneIndex
from economic_libraries.econ_pdf_extract.evaluate_claims import EvaluateClaims
from economic_libraries.econ_pdf_extract.extract_claims import ExtractClaims
from economic_libraries.reproducible_econ.cached_rerun import CachedRerun
from economic_libraries.reproducible_econ.run_pipeline import RunPipeline
from economic_libraries.stats_transformer.country_panel import CountryPanel
from economic_libraries.stats_transformer.panel_ols import PanelOLS
from economic_libraries.stats_transformer.var import MacroVAR
from economic_libraries.verify_paper_claims.run import VerifyPaperClaims

EXAMPLES = (PanelOLS, MacroVAR, ScoreSentences, ToneIndex, ExtractClaims, EvaluateClaims, RunPipeline, CachedRerun, VerifyPaperClaims)


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda example: example.__name__)
def test_example_runs(example):
    example().run()


def test_country_panel_covers_the_g7():
    out = CountryPanel().run()
    assert set(out["table"].index) == {"Canada", "France", "Germany", "Italy", "Japan", "United Kingdom", "United States"}
    assert (out["table"]["count"] == 49).all()
    assert out["panel"].duplicated(["country", "date"]).sum() == 0
