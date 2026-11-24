"""Score a small dated text-corpus file and aggregate to a yearly index.

Uses the "hubert" (Hubert-Labondance 2021) dictionary, whose "positive" words
are growth-acceleration terms and "negative" words are contraction terms, so
the yearly average is a growth-tone index on [0, 2] (1.0 = no directional
words), not an ordinary positive/negative sentiment score.
"""

import logging
from datetime import datetime

import pandas as pd
import yaml
from auto_econ_sentiment.models.sentiment_lexical import SentimentLexical

from economic_libraries.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)


class ToneIndex:
    def run(self):
        """Score the dated texts and save a yearly tone index."""
        logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
        with open(PROJECT_ROOT / "references/configs/auto_econ_sentiment/lexical.yaml") as f:
            config = yaml.safe_load(f)
        input_cfg, lexical_cfg = config["input"], config["lexical"]
        score_col = f"{lexical_cfg['dictionary']}_sentiment_{lexical_cfg['aggregation']}"

        df = pd.read_csv(PROJECT_ROOT / input_cfg["file_path"], parse_dates=[input_cfg["date_column"]])
        logger.info("Loaded %d texts from %s", len(df), input_cfg["file_path"])

        scorer = SentimentLexical(df_input=df, text_column=input_cfg["text_column"])
        scored = scorer.sentiment_pipeline(dictionary_name=lexical_cfg["dictionary"], method=lexical_cfg["aggregation"])

        ts = scored.groupby(scored[input_cfg["date_column"]].dt.year)[score_col].mean().reset_index()
        ts.columns = ["year", "mean_growth_tone"]
        logger.info("\n%s", ts.to_string(index=False))

        out_dir = PROJECT_ROOT / "data/final/sentiment"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"sentiment_timeseries_{datetime.now():%Y%m%d_%H%M%S}.csv"
        ts.to_csv(out_path, index=False)
        logger.info("Time series written to %s", out_path)


if __name__ == "__main__":
    ToneIndex().run()
