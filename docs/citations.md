# Citations for Workshop Examples

Full citations for every paper, dataset, and dictionary used by the workshop
examples in this repo, mirroring the inputs declared in
`references/configs/` and `data/raw/`. Grep targets:
`references/configs/*.yaml`, `src/economic_libraries/*/example*.py`,
`data/raw/*`.

## Papers

### Nakamura and Steinsson (2018) — used in the linked extract-then-verify demo

- Emi Nakamura and Jón Steinsson (2018). "High-Frequency Identification of
  Monetary Non-Neutrality: The Information Effect." *Quarterly Journal of
  Economics*, 133(3), 1283–1330. doi:[10.1093/qje/qjy004](https://doi.org/10.1093/qje/qjy004)
- Earlier version: NBER Working Paper 19260, "High Frequency Identification of
  Monetary Non-Neutrality: The Information Effect"
  (https://www.nber.org/papers/w19260). The linked demo extracts headline
  claims from this public working paper and verifies them against the
  replication estimates. PDF: https://www.nber.org/system/files/working_papers/w19260/w19260.pdf
- Replication inputs used here: raw Treasury/TIPS yields, FOMC meeting flags,
  and the high-frequency policy news shock (`ns`), as standardized in
  Nakamura and Steinsson's public replication files.

### Loughran and McDonald (2011) — "lm" dictionary in `auto_econ_sentiment`

- Tim Loughran and Bill McDonald (2011). "When Is a Liability Not a Liability?
  Textual Analysis, Dictionaries, and 10-Ks." *Journal of Finance*, 66(1),
  35–65. doi:[10.1111/j.1540-6261.2010.01625.x](https://doi.org/10.1111/j.1540-6261.2010.01625.x)
- Dictionary updates: https://sraf.nd.edu/

### Correa, Garud, Londono, and Mislang (2017/2021) — "correa" financial stability dictionary

- Ricardo Correa, Keshav Garud, Juan M. Londono, and Nathan Mislang (2017).
  "Sentiment in Central Bank as Financial Stability Reports." Federal Reserve
  Board, International Finance Discussion Paper 1203.
  https://www.federalreserve.gov/econres/ifdp/1203.htm (citation as listed in
  the auto-econ-sentiment package docs, which we follow)
- Published version: Ricardo Correa, Keshav Garud, Juan M. Londono, and Nathan
  Mislang (2021). "Sentiment in Central Banks' Financial Stability Reports."
  *Review of Finance*, 25(1), 85–120.
  doi:[10.1093/rof/rfaa014](https://doi.org/10.1093/rof/rfaa014)

### Hubert and Labondance (2021) — "hubert" dictionary (default in `auto_econ_sentiment_lexical.yaml`)

- Paul Hubert and Fabien Labondance (2021). "The Signaling Effects of Central
  Bank Tone." *European Economic Review*, 142, 103684.
  doi:[10.1016/j.euroecorev.2021.103684](https://doi.org/10.1016/j.euroecorev.2021.103684)

### Acosta, Brennan, and Jacobson (2024) — monetary policy surprises

- Miguel Acosta, Connor M. Brennan, and Margaret M. Jacobson (2024).
  "Constructing High-Frequency Monetary Policy Surprises from SOFR Futures."
  Finance and Economics Discussion Series 2024-034, Board of Governors of the
  Federal Reserve System. doi:[10.17016/feds.2024.034](https://doi.org/10.17016/feds.2024.034)
- Paper: https://www.federalreserve.gov/econres/feds/constructing-high-frequency-monetary-policy-surprises-from-sofr-futures.htm
- The `ns` policy news shock and the
  `ABJ-2024-monetary-policy-surprises_Data.parquet.gzip` input come from the
  authors' monetary policy surprises dataset, which extends Gurkaynak, Sack,
  and Swanson (2005) and Nakamura and Steinsson (2018).

## Datasets

### Grunfeld (1958) corporate investment panel — `stats_transformer_grunfeld_panel.yaml`

Original source:

- Yehuda Grunfeld (1958). *The Determinants of Corporate Investment*. Unpublished
  Ph.D. dissertation, University of Chicago. (Appendix, Tables 2–9 and 11–13)

What the example actually loads:

- `stats-transformer` bundled example `regression/grunfeld.csv` (registered as
  "Grunfeld (1958)" in `stats_transformer/data/registry.py`), a 10-firm panel
  of gross investment, firm value, and capital stock, 1935–1954.
- The same panel (11-firm version in some distributions) is also served by
  statsmodels as `statsmodels.datasets.grunfeld`; for the data's history and
  version differences see Christian Kleiber and Achim Zeileis (2010). "The
  Grunfeld Data at 50." *German Economic Review*, 11(4), 404–417.
  doi:[10.1111/j.1468-0475.2010.00513.x](https://doi.org/10.1111/j.1468-0475.2010.00513.x)

### Nakamura and Steinsson replication inputs — `data/raw/nakamura_steinsson_2018/`

Four standardized parquet files under `data/raw/nakamura_steinsson_2018/`
(symlinks, not committed):

- `NominalYields.parquet.gzip`, `RealYields.parquet.gzip` — daily nominal and
  TIPS yields (sveny/tipsy series, Gürkaynak, Sack, and Wright 2007 curve data)
- `FOMCmeetings.parquet.gzip` — FOMC meeting calendar, 2000–2014
- `ABJ-2024-monetary-policy-surprises_Data.parquet.gzip` — high-frequency
  policy surprises from Acosta, Brennan, and Jacobson (2024), above; its `ns`
  series is the policy news shock of Nakamura and Steinsson (2018)

### Synthetic/bundled workshop inputs

- `data/raw/example_paper.pdf` — **synthetic** 2-page working paper shipped
  with econ-pdf-extract ("A Synthetic Economics Working Paper", Example A.
  Author). Not real research output; used to demo claims/formula/statistics
  extraction with verbatim reference labels in
  `references/configs/econ_pdf_extract_example_refs/`.
- `data/raw/sentiment_sample.csv` — small synthetic sentiment demo sample
  bundled in this repo for `auto_econ_sentiment` examples. Not real data.
