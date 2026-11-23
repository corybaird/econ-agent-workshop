# Workshop Task 1 (Simple): One-Line Config Change + Diff Audit

Role rules: `/etc/herdr/roles/WORKER.md` (Worker) and `/etc/herdr/roles/REVIEWER.md` (Reviewer)

## Goal
Change one parameter in one YAML config, re-run the verified `stats-transformer` module, and confirm the git diff touches exactly one file.

## Approved File
- `references/configs/stats_transformer/panel_ols.yaml` (set `time_effects: false`)

## Verification Command
```bash
uv run python -m economic_libraries.stats_transformer.panel_ols
```

## Acceptance Criteria
1. `git diff --name-only` lists **only** `references/configs/stats_transformer/panel_ols.yaml`.
2. `data/raw/` is untouched.
3. `uv run python -m economic_libraries.stats_transformer.panel_ols` exits 0 and writes a fresh summary under `data/final/`.
4. Worker writes `Status: DONE` and the updated coefficient table to `docs/herdr/active/task1/NOTES.md`.
5. Reviewer audits the diff, reruns the verification command, and writes `PASS` or `FAIL` to `docs/herdr/active/task1/REVIEW.md`.
