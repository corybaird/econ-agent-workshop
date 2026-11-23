"""Deterministic synthetic datasets (panel CSV, CB statements CSV, working paper PDF)."""

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf

STATEMENTS = [
    ("2021-03-17", "CB-01", "Economic activity expanded rapidly and firms reported strong gains in demand and employment."),
    ("2021-06-16", "CB-02", "Output accelerated across manufacturing and services as business confidence improved sharply."),
    ("2021-09-22", "CB-03", "Hiring strengthened and wage growth rose firmly alongside robust household spending."),
    ("2021-12-15", "CB-04", "Industrial production increased steadily and credit conditions remained supportive of expansion."),
    ("2022-03-16", "CB-05", "Inflationary pressures intensified as domestic demand surged above trend capacity."),
    ("2022-06-15", "CB-06", "Investment spending climbed higher and export orders posted substantial gains."),
    ("2022-09-21", "CB-07", "Consumer spending remained resilient with steady improvements in labor market participation."),
    ("2022-12-14", "CB-08", "GDP growth exceeded expectations and corporate profitability strengthened across regions."),
    ("2023-03-22", "CB-09", "Economic activity contracted sharply as tighter credit conditions weakened business investment."),
    ("2023-06-14", "CB-10", "Output declined and manufacturing orders fell amid deteriorating global trade."),
    ("2023-09-20", "CB-11", "Labor market conditions softened and unemployment rose as firms reduced hiring."),
    ("2023-12-13", "CB-12", "Household consumption slowed markedly and consumer confidence dropped to multi-year lows."),
    ("2024-03-20", "CB-13", "Industrial output weakened further and construction activity suffered steep losses."),
    ("2024-06-12", "CB-14", "Export volumes shrank and business sentiment declined on persistent recession risks."),
    ("2024-09-18", "CB-15", "Credit growth stalled and retail sales fell across major metropolitan districts."),
    ("2024-12-18", "CB-16", "Economic momentum decelerated and firms reported weaker profits and falling backlogs."),
]


class SyntheticDataBuilder:
    """Create deterministic raw benchmark files and return their SHA-256 hashes."""

    def __init__(self, config, seed=42):
        self.config = config
        self.seed = seed

    def build(self, raw_dir):
        """Write macro_panel.csv, cb_statements.csv, and synthetic_wp.pdf under raw_dir."""
        raw_path = Path(raw_dir)
        raw_path.mkdir(parents=True, exist_ok=True)
        panel_path = raw_path / "macro_panel.csv"
        stmt_path = raw_path / "cb_statements.csv"
        pdf_path = raw_path / "synthetic_wp.pdf"
        monthly_path = raw_path / "macro_monthly.csv"

        self._write_macro_panel(panel_path)
        self._write_cb_statements(stmt_path)
        self._write_working_paper(pdf_path)
        self._write_macro_monthly(monthly_path)

        return {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (panel_path, stmt_path, pdf_path, monthly_path)
        }

    def _write_macro_panel(self, out_path):
        rng = np.random.default_rng(self.seed)
        n_countries = self.config.get("n_countries", 10)
        n_quarters = self.config.get("n_quarters", 32)
        start_year = self.config.get("start_year", 2017)
        dgp = self.config.get("dgp", {})
        intercept = dgp.get("intercept", 2.0)
        slope_unemp = dgp.get("slope_unemp", -0.60)
        persistence = dgp.get("persistence", 0.50)
        noise_std = dgp.get("noise_std", 0.20)

        quarters = [f"{start_year + q // 4}Q{q % 4 + 1}" for q in range(n_quarters)]
        rows = []
        for idx in range(n_countries):
            country = f"ECON_{idx + 1:02d}"
            fe = rng.normal(0.0, 0.5)
            prev_inf = intercept + fe
            unemp = 0.0
            for q_idx, quarter in enumerate(quarters):
                unemp = 0.7 * unemp + rng.normal(0.0, 0.8)
                inf = intercept + fe + slope_unemp * unemp + persistence * prev_inf + rng.normal(0.0, noise_std)
                if q_idx > 0:
                    rows.append({
                        "country": country,
                        "quarter": quarter,
                        "inflation": round(float(inf), 4),
                        "unemployment_gap": round(float(unemp), 4),
                        "lag_inflation": round(float(prev_inf), 4),
                    })
                prev_inf = inf
        pd.DataFrame(rows).to_csv(out_path, index=False)

    def _write_cb_statements(self, out_path):
        df = pd.DataFrame(STATEMENTS, columns=["date", "statement_id", "text"])
        df.to_csv(out_path, index=False)

    def _write_working_paper(self, out_path):
        dgp = self.config.get("dgp", {})
        slope = abs(dgp.get("slope_unemp", -0.60))
        persist = dgp.get("persistence", 0.50)

        doc = pymupdf.open()
        p1 = doc.new_page(width=612, height=792)
        p1.insert_text((72, 72), "Inflation Dynamics and Labor Slack: A Synthetic Panel Study", fontsize=15)
        p1.insert_text((72, 96), "Synthetic Research Group — Working Paper No. 101", fontsize=10)
        p1.insert_text((72, 136), "1 Introduction", fontsize=13)
        p1.insert_textbox(
            pymupdf.Rect(72, 150, 540, 320),
            (
                "Understanding the slope of the Phillips curve remains central to monetary policy. "
                "Using a synthetic quarterly panel of ten economies from 2017 to 2024, we estimate the "
                "relationship between quarterly inflation, the unemployment gap, and lagged inflation "
                "with country fixed effects. Earlier studies such as Clarida et al. (1999) document "
                "substantial inflation persistence across advanced economies."
            ),
            fontsize=11,
        )
        p1.insert_text((72, 340), "2 Empirical Specification", fontsize=13)
        p1.insert_textbox(
            pymupdf.Rect(72, 355, 540, 470),
            (
                "We estimate the baseline country fixed-effects panel specification:\n"
                "pi_{i,t} = alpha_i + beta * ugap_{i,t} + rho * pi_{i,t-1} + eps_{i,t}    (1)\n"
                "where pi_{i,t} denotes quarterly inflation, ugap_{i,t} is the unemployment gap, "
                "and alpha_i captures country-specific fixed effects."
            ),
            fontsize=11,
        )

        p2 = doc.new_page(width=612, height=792)
        p2.insert_text((72, 72), "3 Empirical Results", fontsize=13)
        p2.insert_textbox(
            pymupdf.Rect(72, 90, 540, 320),
            (
                f"Our baseline fixed-effects panel estimates confirm a statistically significant "
                f"negative Phillips curve slope. We find that a one percentage point increase in "
                f"the unemployment gap reduces inflation by {slope:.2f} percentage points (p < 0.01). "
                f"In addition, we estimate that lagged inflation persistence equals {persist:.2f} "
                f"(p < 0.01), indicating strong quarterly inertia in price dynamics.\n\n"
                "Across robustness specifications, controlling for country fixed effects leaves "
                "the headline unemployment gap coefficient stable and economically meaningful."
            ),
            fontsize=11,
        )
        p2.insert_text((72, 350), "4 Conclusion", fontsize=13)
        p2.insert_textbox(
            pymupdf.Rect(72, 368, 540, 480),
            (
                "This synthetic working paper provides a clean benchmark target for automated "
                "evidence extraction and reproducible econometric verification pipelines."
            ),
            fontsize=11,
        )
        doc.save(out_path)
        doc.close()

    def _write_macro_monthly(self, out_path):
        """Generate 240 monthly obs with structural monetary shock & partial-sample proxy instrument."""
        rng = np.random.default_rng(self.seed + 100)
        n_months = int(self.config.get("n_months", 240))
        missing_iv_months = int(self.config.get("missing_iv_months", 48))
        dates = pd.date_range("2005-01-01", periods=n_months, freq="MS")

        # Structural VAR(2) in [policy_rate, ip_yoy, cpi_yoy] with genuine monetary tightening shock
        r = np.zeros(n_months)
        ip_yoy = np.zeros(n_months)
        cpi_yoy = np.zeros(n_months)
        eps_mp = rng.normal(0.0, 0.25, size=n_months)
        eps_ip = rng.normal(0.0, 0.40, size=n_months)
        eps_cpi = rng.normal(0.0, 0.25, size=n_months)

        r[0], ip_yoy[0], cpi_yoy[0] = 2.5, 2.0, 2.0
        r[1], ip_yoy[1], cpi_yoy[1] = 2.5, 2.0, 2.0
        for t in range(2, n_months):
            r[t] = (
                0.25
                + 0.85 * r[t - 1]
                - 0.08 * r[t - 2]
                + 0.08 * ip_yoy[t - 1]
                + 0.12 * cpi_yoy[t - 1]
                + eps_mp[t]
                + 0.10 * eps_ip[t]
            )
            ip_yoy[t] = (
                0.50
                + 0.78 * ip_yoy[t - 1]
                - 0.12 * ip_yoy[t - 2]
                - 0.35 * r[t - 1]
                - 0.25 * r[t - 2]
                - 0.45 * eps_mp[t]
                + eps_ip[t]
            )
            cpi_yoy[t] = (
                0.35
                + 0.80 * cpi_yoy[t - 1]
                - 0.10 * cpi_yoy[t - 2]
                + 0.06 * ip_yoy[t - 1]
                - 0.15 * r[t - 1]
                - 0.12 * eps_mp[t]
                + eps_cpi[t]
            )

        # Reconstruct smooth positive index levels (100 base) with clear macro variation
        ip_level = 100.0 * np.exp(np.cumsum(ip_yoy / 120.0))
        cpi_level = 100.0 * np.exp(np.cumsum(cpi_yoy / 120.0))

        # High-frequency external instrument z_t: noisy measure of eps_mp, missing for first 48 months
        mp_shock = 0.85 * eps_mp + rng.normal(0.0, 0.15, size=n_months)
        mp_shock[:missing_iv_months] = np.nan

        df = pd.DataFrame({
            "date": dates.strftime("%Y-%m-%d"),
            "country": "USA",
            "policy_rate": np.round(r, 4),
            "ip_level": np.round(ip_level, 4),
            "cpi_level": np.round(cpi_level, 4),
            "mp_shock": np.round(mp_shock, 5),
        })
        df.to_csv(out_path, index=False)
