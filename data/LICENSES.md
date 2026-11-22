# Data sources and terms

These terms apply to the data files only, not to the code in this repository. Full citations are in [docs/citations.md](../docs/citations.md).

| File under `data/raw/` | Source | Terms |
| --- | --- | --- |
| `nakamura_steinsson_2018/NominalYields.parquet.gzip` | Nakamura and Steinsson (2018) replication files, [doi:10.7910/DVN/HZOXKN](https://doi.org/10.7910/DVN/HZOXKN) | CC0 1.0 |
| `nakamura_steinsson_2018/RealYields.parquet.gzip` | Same as above | CC0 1.0 |
| `nakamura_steinsson_2018/FOMCmeetings.parquet.gzip` | Same as above | CC0 1.0 |
| `nakamura_steinsson_2018/ABJ-2024-monetary-policy-surprises_Data.parquet.gzip` | Acosta, Brennan and Jacobson (2024), [doi:10.7910/DVN/WUXWHS](https://doi.org/10.7910/DVN/WUXWHS) | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), non-commercial use only |
| `notebooks/monetary_policy_statement.parquet.gzip` | Board of Governors of the Federal Reserve System, FOMC statements, collected in [auto-econ-sentiment](https://github.com/corybaird/auto-econ-sentiment) | Public domain unless marked ([Board disclaimer](https://www.federalreserve.gov/disclaimer.htm)) |
| `sentiment_sample.csv` | Synthetic, made for this repository | None |
| `example_paper.pdf` | Synthetic, from econ-pdf-extract | None |

## Changes

- Nakamura and Steinsson files: converted from CSV to parquet, values unchanged
- Acosta, Brennan and Jacobson file: converted from Excel to parquet, column names in lower case, `country` column added, values unchanged

## Not committed

- Nakamura and Steinsson NBER Working Paper 19260 and FRBSF Working Paper 2017-01 are downloaded on first run and hash-checked
