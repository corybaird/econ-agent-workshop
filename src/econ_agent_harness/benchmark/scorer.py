"""Deterministic session-log parser and sandbox artifact scorer."""

import hashlib
import json
import re
from pathlib import Path

import pandas as pd
from stats_transformer.featurization.feature_engineering import FeatureEngineer
from stats_transformer.models.timeseries.identification.proxy_svar import ProxySVARModel

IGNORED_ROOT_ENTRIES = {
    ".git",
    ".gitignore",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "pyproject.toml",
    "uv.lock",
    "README.md",
    "data",
    "references",
    "src",
    "reports",
    "docs",
    "tests",
    "archive",
    ".agents",
    ".claude",
    ".cache",
}

PROVENANCE_REGEX = re.compile(r"(page\s*\d+|p\.\s*\d+|\bp\d+\b|section\s+\d|empirical results)", re.IGNORECASE)


class BenchmarkScorer:
    """Parse pi session JSONL usage and score sandbox outputs deterministically."""

    def parse_session(self, session_dir):
        """Aggregate token usage, turns, tool calls, skill reads, and final reply."""
        jsonl_files = sorted(Path(session_dir).glob("*.jsonl"))
        usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "turns": 0,
            "tool_calls": 0,
            "skill_reads": 0,
        }
        turns = []
        final_reply = ""
        if not jsonl_files:
            return usage, turns, final_reply

        for line in jsonl_files[-1].read_text().splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("type") != "message":
                continue
            msg = event.get("message", {})
            if msg.get("role") != "assistant":
                continue

            u = msg.get("usage", {})
            inp = int(u.get("input", 0) or 0)
            out = int(u.get("output", 0) or 0)
            cr = int(u.get("cacheRead", 0) or 0)
            cw = int(u.get("cacheWrite", 0) or 0)
            tot = int(u.get("totalTokens", inp + out + cr + cw) or 0)

            usage["input_tokens"] += inp
            usage["output_tokens"] += out
            usage["cache_read_tokens"] += cr
            usage["cache_write_tokens"] += cw
            usage["total_tokens"] += tot
            usage["turns"] += 1

            tool_names = []
            text_chunks = []
            for block in msg.get("content", []):
                btype = block.get("type")
                if btype == "toolCall":
                    tname = block.get("name", "")
                    args = block.get("arguments", {})
                    tool_names.append(tname)
                    usage["tool_calls"] += 1
                    if "SKILL.md" in json.dumps(args):
                        usage["skill_reads"] += 1
                elif btype == "text":
                    text_chunks.append(block.get("text", ""))

            text = "\n".join(text_chunks).strip()
            if text:
                final_reply = text
            turns.append({
                "timestamp": event.get("timestamp", ""),
                "input": inp,
                "output": out,
                "cache_read": cr,
                "cache_write": cw,
                "total": tot,
                "duration_ms": int(msg.get("durationMs", 0) or 0),
                "tool_calls": tool_names,
                "text": text,
            })

        return usage, turns, final_reply

    def score_sandbox(self, sandbox_dir, baseline_files, raw_hashes, task_cfg, extra_used_libs=None):
        """Evaluate folder discipline, raw integrity, YAML configs, library use, and artifacts."""
        root = Path(sandbox_dir)
        raw_untouched = all(
            (root / "data/raw" / fname).is_file()
            and hashlib.sha256((root / "data/raw" / fname).read_bytes()).hexdigest() == digest
            for fname, digest in raw_hashes.items()
        )

        created_files = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if any(part in {".git", ".venv", "__pycache__", ".ruff_cache", ".pytest_cache"} for part in path.parts):
                continue
            if rel not in baseline_files:
                created_files.append(rel)

        root_clutter = [
            p.name for p in root.iterdir()
            if p.name not in IGNORED_ROOT_ENTRIES
        ]
        clean_root = len(root_clutter) == 0

        yaml_files = [
            f for f in created_files
            if f.startswith("references/configs/") and f.endswith((".yaml", ".yml"))
        ]
        yaml_config_used = len(yaml_files) > 0

        py_files = [f for f in created_files if f.endswith(".py")]
        py_source_all = ""
        custom_loc = 0
        for rel in py_files:
            content = (root / rel).read_text(errors="replace")
            py_source_all += "\n" + content
            custom_loc += sum(
                1 for ln in content.splitlines()
                if ln.strip() and not ln.strip().startswith("#")
            )

        expected_libs = task_cfg.get("expected_libraries", [])
        detected = set(extra_used_libs or [])
        for lib in expected_libs:
            if re.search(rf"\b{re.escape(lib)}\b", py_source_all):
                detected.add(lib)
        # Also detect reproducible_econ CLI runs via its signature cache/manifest artifacts
        if any(f.endswith("fingerprint_summary.json") for f in created_files) and any(
            f.endswith("run_manifest.json") for f in created_files
        ):
            detected.add("reproducible_econ")
        used_libs = [lib for lib in expected_libs if lib in detected]
        target_lib_ratio = round(len(used_libs) / len(expected_libs), 3) if expected_libs else 1.0

        expected_exts = task_cfg.get("expected_extensions", [])
        artifacts_ok = all(
            any(f.endswith(ext) for f in created_files)
            for ext in expected_exts
        )

        require_prov = bool(task_cfg.get("require_provenance_markers", False))
        if require_prov:
            report_files = [f for f in created_files if f.endswith((".md", ".json", ".txt"))]
            report_text = "\n".join((root / f).read_text(errors="replace") for f in report_files)
            provenance_ok = bool(PROVENANCE_REGEX.search(report_text))
        else:
            provenance_ok = True

        numerical_ok, numerical_note = self._check_numerical(root, created_files, task_cfg)

        checks = [
            float(raw_untouched),
            float(clean_root),
            float(yaml_config_used),
            float(target_lib_ratio),
            float(artifacts_ok),
            float(provenance_ok),
            float(numerical_ok),
        ]
        rubric_score = round(sum(checks) / len(checks), 3)

        return {
            "raw_data_untouched": raw_untouched,
            "clean_root": clean_root,
            "root_clutter": root_clutter,
            "yaml_config_used": yaml_config_used,
            "yaml_files": yaml_files,
            "expected_libraries": expected_libs,
            "used_libraries": used_libs,
            "target_lib_ratio": target_lib_ratio,
            "artifacts_ok": artifacts_ok,
            "provenance_ok": provenance_ok,
            "numerical_ok": numerical_ok,
            "numerical_note": numerical_note,
            "custom_python_loc": custom_loc,
            "python_files": py_files,
            "created_files": created_files,
            "rubric_score": rubric_score,
        }

    def _check_numerical(self, root, created_files, task_cfg):
        kind = task_cfg.get("numerical_check")
        if kind != "proxy_svar_irf":
            return True, ""
        raw_csv = root / "data/raw/macro_monthly.csv"
        if not raw_csv.is_file():
            return False, "missing macro_monthly.csv"
        df = pd.read_csv(raw_csv)
        fe = FeatureEngineer(
            transformations=["changepct_yoy"],
            entity_column="country",
            date_column="date",
            period="monthly",
            data_columns=["ip_level", "cpi_level"],
        )
        df_feat = fe.fit_transform(df)
        svar = ProxySVARModel(
            target_variables=["policy_rate", "ip_level_changepct_yoy", "cpi_level_changepct_yoy"],
            instrument_variable="mp_shock",
            date_column="date",
            maxlags=4,
        )
        svar.fit(df_feat)
        ref_b11 = float(svar.impact_column[0])
        ref_ip_h0 = float(svar.irf(horizons=13)["ip_level_changepct_yoy"].iloc[0])
        ref_ip_h6 = float(svar.irf(horizons=13)["ip_level_changepct_yoy"].iloc[6])

        # Strictly inspect saved IRF CSV h=0 and h=6 rows (catches unit scaling or silent Cholesky zero-impact)
        csv_files = [f for f in created_files if f.endswith(".csv") and "raw" not in f]
        b11_match, h0_match, h6_match = False, False, False
        for rel in csv_files:
            try:
                irf_cand = pd.read_csv(root / rel)
            except (pd.errors.ParserError, OSError, ValueError):
                continue
            if len(irf_cand) < 7:
                continue
            num_df = irf_cand.select_dtypes(include="number")
            drop_h = [c for c in num_df.columns if c.lower() in {"h", "horizon", "step", "unnamed: 0"}]
            val_df = num_df.drop(columns=drop_h, errors="ignore")
            if val_df.shape[1] < 2:
                continue
            r0 = [float(v) for v in val_df.iloc[0].dropna().values]
            r6 = [float(v) for v in val_df.iloc[6].dropna().values]
            if any(abs(v - ref_b11) <= 0.015 for v in r0):
                b11_match = True
            # Reject silent Cholesky (exact 0.0000 at h=0) and check sign/magnitude of h=0 & h=6 IP response
            if any(
                abs(v) > 1e-6
                and (
                    abs(v - ref_ip_h0) <= max(0.0005, 0.35 * abs(ref_ip_h0))
                    or abs(v - 100.0 * ref_ip_h0) <= max(0.05, 0.35 * abs(100.0 * ref_ip_h0))
                )
                for v in r0
            ):
                h0_match = True
            if any(
                abs(v - ref_ip_h6) <= max(0.002, 0.20 * abs(ref_ip_h6))
                or abs(v - 100.0 * ref_ip_h6) <= max(0.20, 0.20 * abs(100.0 * ref_ip_h6))
                for v in r6
            ):
                h6_match = True
        ok = b11_match and h0_match and h6_match
        note = (
            f"ref_b11={ref_b11:.4f} (match={b11_match}), "
            f"ref_ip_h0={ref_ip_h0:.4f} (match={h0_match}), "
            f"ref_ip_h6={ref_ip_h6:.4f} (match={h6_match})"
        )
        return ok, note
