"""Example 1: dictionary scoring on a few bundled sentences."""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from auto_econ_sentiment.models.sentiment_lexical import SentimentLexical

logger = logging.getLogger(__name__)

SENTENCES = [
    "Faster growth is expected and investment is accelerating.",
    "Inflation is increasing and downside risks are getting stronger.",
    "The labor market remains strong while output is stable.",
    "Demand is weaker and firms expect lower profits.",
]


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
    with open(root / "references/configs/auto_econ_sentiment_lexical.yaml") as f:
        config = yaml.safe_load(f)
    lexical_cfg = config["lexical"]

    df = pd.DataFrame({config["input"]["text_column"]: SENTENCES})
    scorer = SentimentLexical(df_input=df, text_column=config["input"]["text_column"])
    score_col = f"{lexical_cfg['dictionary']}_sentiment_{lexical_cfg['aggregation']}"
    scored = scorer.sentiment_pipeline(dictionary_name=lexical_cfg["dictionary"], method=lexical_cfg["aggregation"])
    logger.info("\n%s", scored[["text", score_col, f"{lexical_cfg['dictionary']}_words_positive_{lexical_cfg['aggregation']}"]].to_string(index=False))

    out_path = root / f"data/final/sentiment_sentences_{datetime.now():%Y%m%d_%H%M%S}.csv"
    scored.to_csv(out_path, index=False)
    logger.info("Results written to %s", out_path)


if __name__ == "__main__":
    run()
