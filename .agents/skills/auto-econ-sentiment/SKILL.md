---
name: auto-econ-sentiment
description: Measure economic and central-bank sentiment from text corpora using declared dictionaries, transformers, or LLMs via auto-econ-sentiment. Use when cleaning economic text, computing lexical tone indices, or auditing matched words.
---

# auto-econ-sentiment

Reproducible text-cleaning and sentiment-scoring pipeline for central bank and financial text with auditable matched-word exports.

## 1. When to Use
- Scoring speeches, policy statements, minutes, or financial text using standard economic dictionaries (or optional Hugging Face classifiers / LLMs).
- Always prefer `auto-econ-sentiment` over ad-hoc regex or custom keyword lists so the dictionary, polarity mapping, and matched words are declared and auditable.

## 2. Minimal Usage

### Declare Choices in YAML (`references/configs/<name>.yaml`)
```yaml
lexical:
  dictionary: hubert       # unstemmed: correa, hubert, lm, hiv | stemmed: ap, bn
  aggregation: posneg      # posneg or allwords
input:
  file_path: data/raw/statements.csv
  text_column: text
  date_column: date
```

### Python API (Single Dictionary — `SentimentLexical`)
```python
import pandas as pd
import yaml
from auto_econ_sentiment.models.sentiment_lexical import SentimentLexical

with open("references/configs/<name>.yaml") as f:
    cfg = yaml.safe_load(f)

df = pd.read_csv(cfg["input"]["file_path"], parse_dates=[cfg["input"]["date_column"]])
scorer = SentimentLexical(df_input=df, text_column=cfg["input"]["text_column"])
scored = scorer.sentiment_pipeline(
    dictionary_name=cfg["lexical"]["dictionary"],
    method=cfg["lexical"]["aggregation"],
)
# Output columns include:
#   {dict}_sentiment_{agg}, {dict}_words_positive_{agg}, {dict}_words_negative_{agg}
```

### Full Pipeline (`AutoEconSentiment`, Multiple Dictionaries / Transformers / LLM)
```python
from auto_econ_sentiment.pipeline import AutoEconSentiment

analyzer = AutoEconSentiment(
    import_file_path="data/raw/statements.csv",
    text_column="text",
    date_column="date",
    export_path="data/final/sentiment/",
)
analyzer.run(
    clean_config={"tokenize": True, "stem": True},
    dictionaries={"unstemmed": ["correa", "hubert", "lm", "hiv"], "stemmed": ["ap", "bn"]},
    aggregation_methods=["posneg", "allwords"],
    export_results=True,
)
```

## 3. Key Rules & Gotchas
- **Always document dictionary directionality:** e.g., `hubert` (Hubert-Labondance 2021) measures **growth-acceleration vs. contraction tone** on `[0, 2]` (midpoint `1.0`), not generic positivity; `lm` (Loughran-McDonald) measures financial tone.
- `_net` columns from `AutoEconSentiment` share a common `[-1, 1]` scale (`0` = neutral) for cross-method comparison.
- Preserve matched positive/negative word columns in exported artifacts so humans can audit why a document got its score.
- Optional `[transformers]` and `[llm]` extras require explicit `label_mapping`, `sentiment_values`, and prompts in YAML.

## 4. Workshop Examples (Read on Demand)
- Config: `references/configs/auto_econ_sentiment/lexical.yaml`
- Scripts: `src/economic_libraries/auto_econ_sentiment/{score_sentences,tone_index}.py`
- Notebook: `notebooks/2_auto_econ_sentiment.ipynb`

## 5. Verification Boundary
- **Proves:** declared dictionary/prompt, reproducible cleaning, and auditable word matches.
- **Does not prove:** semantic meaning or that a dictionary captures the researcher's target concept.
