"""Example 2: score a small dated text-corpus file and aggregate to a yearly sentiment index."""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from auto_econ_sentiment.models.sentiment_lexical import SentimentLexical

logger = logging.getLogger(__name__)


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
    input_cfg, lexical_cfg = config["input"], config["lexical"]
    score_col = f"{lexical_cfg['dictionary']}_sentiment_{lexical_cfg['aggregation']}"

    df = pd.read_csv(root / input_cfg["file_path"], parse_dates=[input_cfg["date_column"]])
    logger.info("Loaded %d texts from %s", len(df), input_cfg["file_path"])

    scorer = SentimentLexical(df_input=df, text_column=input_cfg["text_column"])
    scored = scorer.sentiment_pipeline(dictionary_name=lexical_cfg["dictionary"], method=lexical_cfg["aggregation"])

    ts = scored.groupby(scored[input_cfg["date_column"]].dt.year)[score_col].mean().reset_index()
    ts.columns = ["year", "mean_sentiment"]
    logger.info("\n%s", ts.to_string(index=False))

    out_path = root / f"data/final/sentiment_timeseries_{datetime.now():%Y%m%d_%H%M%S}.csv"
    ts.to_csv(out_path, index=False)
    logger.info("Time series written to %s", out_path)


if __name__ == "__main__":
    run()
