"""Example 1: dictionary scoring on a few bundled sentences.

The chosen dictionary, "hubert", is the Hubert-Labondance (2021) central-bank
tone dictionary: "positive" entries are growth-acceleration words (increase,
accelerate, strong, gain, expand) and "negative" entries are contraction words
(decrease, decelerate, weak, loss, contract). The score is therefore a
growth-tone index on [0, 2] around a 1.0 midpoint, not ordinary positivity.
Sentences below are one clearly growth-positive, one clearly growth-negative,
and one neutral (no dictionary words) under that dictionary.
"""

import logging
from datetime import datetime

import pandas as pd
import yaml
from auto_econ_sentiment.models.sentiment_lexical import SentimentLexical

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)

SENTENCES = [
    "Output is expanding faster and firms report strong gains in demand.",
    "Investment contracted and the labor market is growing weaker.",
    "Budget planning continues under the framework approved last week.",
]


def run():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    with open(PROJECT_ROOT / "references/configs/auto_econ_sentiment_lexical.yaml") as f:
        config = yaml.safe_load(f)
    lexical_cfg = config["lexical"]
    dictionary, agg = lexical_cfg["dictionary"], lexical_cfg["aggregation"]
    score_col = f"{dictionary}_sentiment_{agg}"

    df = pd.DataFrame({"text": SENTENCES})
    scorer = SentimentLexical(df_input=df, text_column="text")
    scored = scorer.sentiment_pipeline(dictionary_name=dictionary, method=agg)
    logger.info(
        "\n%s",
        scored[["text", score_col, f"{dictionary}_words_positive_{agg}", f"{dictionary}_words_negative_{agg}"]].to_string(index=False),
    )

    out_path = PROJECT_ROOT / f"data/final/sentiment_sentences_{datetime.now():%Y%m%d_%H%M%S}.csv"
    scored.to_csv(out_path, index=False)
    logger.info("Results written to %s", out_path)


if __name__ == "__main__":
    run()
