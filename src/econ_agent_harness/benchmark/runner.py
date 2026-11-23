"""Config-driven benchmark comparing bare, prompt-only, skills, and combined econ agent setups."""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

import yaml

from econ_agent_harness.benchmark.langfuse_client import LangfuseClient
from econ_agent_harness.benchmark.scorer import BenchmarkScorer
from econ_agent_harness.benchmark.synthetic_data import SyntheticDataBuilder

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = "references/configs/benchmarks/bench_econ_tasks.yaml"

logger = logging.getLogger(__name__)


class EconAgentBenchmark:
    """Run controlled pi agent benchmarks across arms and models with Langfuse logging."""

    def __init__(self, config_path=None, models=None, arms=None, tasks=None, use_langfuse=True):
        self.config_path = Path(config_path) if config_path else PROJECT_ROOT / DEFAULT_CONFIG
        self.model_filter = set(models) if models else None
        self.arm_filter = set(arms) if arms else None
        self.task_filter = set(tasks) if tasks else None
        self.use_langfuse = use_langfuse

    def run(self):
        """Provision environments, execute all selected runs, log to Langfuse, and save report."""
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
        with open(self.config_path) as f:
            config = yaml.safe_load(f)

        models = [
            m for m in config["models"]
            if not self.model_filter or m["label"] in self.model_filter
        ]
        arms = [
            a for a in config["arms"]
            if not self.arm_filter or a["id"] in self.arm_filter
        ]
        tasks = [
            t for t in config["tasks"]
            if (self.task_filter and t["id"] in self.task_filter)
            or (not self.task_filter and t.get("enabled", True))
        ]

        if any(a["venv"] == "bare" for a in arms):
            self._ensure_bare_venv(Path(config["bare_venv_path"]), config["bare_packages"])

        langfuse_cfg = config.get("langfuse", {})
        langfuse = LangfuseClient(enabled=self.use_langfuse and langfuse_cfg.get("enabled", True))
        scorer = BenchmarkScorer()
        data_builder = SyntheticDataBuilder(config.get("synthetic_data", {}), seed=config.get("seed", 42))

        results = []
        total_runs = len(models) * len(arms) * len(tasks)
        run_idx = 0
        for model_cfg in models:
            for task_cfg in tasks:
                for arm_cfg in arms:
                    run_idx += 1
                    logger.info(
                        "[%d/%d] Running model=%s task=%s arm=%s",
                        run_idx, total_runs, model_cfg["label"], task_cfg["id"], arm_cfg["id"],
                    )
                    record = self._run_single(config, model_cfg, arm_cfg, task_cfg, data_builder, scorer)
                    trace_id = langfuse.log_benchmark_run(record, tags=langfuse_cfg.get("tags", []))
                    record["langfuse_trace_id"] = trace_id
                    results.append(record)
                    logger.info(
                        "  -> exit=%s tokens=%d (in=%d out=%d cache=%d) turns=%d skills=%d loc=%d rubric=%.2f libs=%s time=%.1fs",
                        record["exit_code"],
                        record["usage"]["total_tokens"],
                        record["usage"]["input_tokens"],
                        record["usage"]["output_tokens"],
                        record["usage"]["cache_read_tokens"],
                        record["usage"]["turns"],
                        record["usage"]["skill_reads"],
                        record["rubric"]["custom_python_loc"],
                        record["rubric"]["rubric_score"],
                        record["rubric"]["used_libraries"],
                        record["wall_time_sec"],
                    )

        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        out_dir = PROJECT_ROOT / config.get("output_dir", "data/final/benchmarks")
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / f"bench_results_{stamp}.json"
        md_path = out_dir / f"bench_summary_{stamp}.md"
        json_path.write_text(json.dumps(results, indent=2))
        md_path.write_text(self._render_markdown(results))
        logger.info("Saved JSON results to %s", json_path)
        logger.info("Saved Markdown summary to %s", md_path)
        return results

    def _ensure_bare_venv(self, bare_venv, packages):
        python_bin = bare_venv / "bin/python"
        if python_bin.is_file():
            check = subprocess.run(
                [str(python_bin), "-c", "import pandas, numpy, statsmodels, pymupdf, yaml"],
                capture_output=True,
                check=False,
            )
            if check.returncode == 0:
                logger.info("Reusing bare control venv at %s", bare_venv)
                return
        logger.info("Creating bare control venv at %s with %s", bare_venv, packages)
        subprocess.run(["uv", "venv", "--clear", str(bare_venv)], check=True)
        subprocess.run(["uv", "pip", "install", "--python", str(python_bin), *packages], check=True)

    def _prepare_sandbox(self, sandbox_dir, arm_cfg, config, data_builder):
        for sub in ("data/raw", "data/intermediate", "data/final", "references/configs", "src", "reports"):
            (sandbox_dir / sub).mkdir(parents=True, exist_ok=True)

        raw_hashes = data_builder.build(sandbox_dir / "data/raw")
        if arm_cfg["venv"] == "bare":
            deps = ", ".join(f'"{pkg}"' for pkg in config["bare_packages"])
            venv_path = Path(config["bare_venv_path"])
        else:
            deps = '"stats-transformer", "auto-econ-sentiment", "econ-pdf-extract", "reproducible-econ", "pyyaml", "pandas"'
            venv_path = Path(sys.prefix)

        pyproject = (
            '[project]\nname = "econ-bench-sandbox"\nversion = "0.1.0"\n'
            f'requires-python = ">=3.12"\ndependencies = [{deps}]\n'
        )
        (sandbox_dir / "pyproject.toml").write_text(pyproject)

        baseline_files = {
            p.relative_to(sandbox_dir).as_posix()
            for p in sandbox_dir.rglob("*")
            if p.is_file()
        }
        return raw_hashes, baseline_files, venv_path

    def _run_single(self, config, model_cfg, arm_cfg, task_cfg, data_builder, scorer):
        started_at = datetime.now(UTC).isoformat()
        t0 = time.monotonic()
        with tempfile.TemporaryDirectory(prefix=f"econ_bench_{arm_cfg['id']}_") as tmp:
            tmp_path = Path(tmp)
            sandbox_dir = tmp_path / "project"
            session_dir = tmp_path / "session"
            sandbox_dir.mkdir()
            session_dir.mkdir()

            raw_hashes, baseline_files, venv_path = self._prepare_sandbox(
                sandbox_dir, arm_cfg, config, data_builder
            )

            timeout = int(config.get("timeout_sec", 180))
            extra_used_libs = []
            if arm_cfg.get("harness") == "custom":
                out_json = tmp_path / "custom_harness_out.json"
                cmd = [
                    "uv",
                    "--directory", str(PROJECT_ROOT),
                    "run", "--with", "openai",
                    "python", "-m", "econ_agent_harness.agent",
                    "--workspace", str(sandbox_dir),
                    "--provider", model_cfg["provider"],
                    "--model", model_cfg["model"],
                    "--prompt", task_cfg["prompt"],
                    "--out-json", str(out_json),
                ]
                env = os.environ.copy()
                env["PYDANTIC_AI_NO_BANNER"] = "1"
                try:
                    proc = subprocess.run(
                        cmd,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                    exit_code = proc.returncode
                    stderr_tail = proc.stderr[-1000:] if proc.stderr else ""
                except subprocess.TimeoutExpired:
                    exit_code = 124
                    stderr_tail = f"Timed out after {timeout}s"

                wall_time = round(time.monotonic() - t0, 2)
                if out_json.is_file():
                    payload = json.loads(out_json.read_text())
                    usage = payload["usage"]
                    turns = payload["turn_details"]
                    final_reply = payload["final_reply"]
                    extra_used_libs = payload.get("used_libraries", [])
                else:
                    usage = {
                        "input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0,
                        "cache_write_tokens": 0, "total_tokens": 0, "turns": 0,
                        "tool_calls": 0, "skill_reads": 0,
                    }
                    turns, final_reply = [], ""
            else:
                cmd = [
                    "pi",
                    "-p",
                    "--provider", model_cfg["provider"],
                    "--model", model_cfg["model"],
                    "--no-context-files",
                    "--session-dir", str(session_dir),
                ]
                pi_opts = config.get("pi_options", {})
                if pi_opts.get("disable_user_extensions", True):
                    cmd.extend(["--no-extensions", "--no-prompt-templates", "--no-themes", "--no-mcp"])
                if pi_opts.get("thinking"):
                    cmd.extend(["--thinking", str(pi_opts["thinking"])])

                if arm_cfg.get("prompt_path"):
                    prompt_abs = PROJECT_ROOT / arm_cfg["prompt_path"]
                    cmd.extend(["--append-system-prompt", str(prompt_abs)])

                skill_paths = arm_cfg.get("skill_paths") or []
                if skill_paths:
                    for sp in skill_paths:
                        cmd.extend(["--skill", str(PROJECT_ROOT / sp)])
                else:
                    cmd.append("--no-skills")

                env_note = (
                    "Python environment: run commands with `uv run --no-sync python ...` "
                    "(or `python ...`, already on PATH in this sandbox). Do not install new packages from the internet."
                )
                full_prompt = f"{task_cfg['prompt']}\n\n{env_note}"
                cmd.append(full_prompt)

                env = os.environ.copy()
                env["VIRTUAL_ENV"] = str(venv_path)
                env["UV_PROJECT_ENVIRONMENT"] = str(venv_path)
                env["PATH"] = f"{venv_path / 'bin'}:{env.get('PATH', '')}"
                env["UV_NO_SYNC"] = "1"

                try:
                    proc = subprocess.run(
                        cmd,
                        cwd=str(sandbox_dir),
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                    exit_code = proc.returncode
                    stderr_tail = proc.stderr[-1000:] if proc.stderr else ""
                except subprocess.TimeoutExpired:
                    exit_code = 124
                    stderr_tail = f"Timed out after {timeout}s"

                wall_time = round(time.monotonic() - t0, 2)
                usage, turns, final_reply = scorer.parse_session(session_dir)

            rubric = scorer.score_sandbox(
                sandbox_dir, baseline_files, raw_hashes, task_cfg, extra_used_libs=extra_used_libs
            )

            sample_code = {}
            for py_rel in rubric["python_files"][:3]:
                sample_code[py_rel] = (sandbox_dir / py_rel).read_text(errors="replace")[:1500]

            return {
                "started_at": started_at,
                "model_label": model_cfg["label"],
                "provider": model_cfg["provider"],
                "model": model_cfg["model"],
                "arm_id": arm_cfg["id"],
                "arm_label": arm_cfg["label"],
                "task_id": task_cfg["id"],
                "task_title": task_cfg["title"],
                "task_prompt": task_cfg["prompt"],
                "exit_code": exit_code,
                "stderr_tail": stderr_tail,
                "wall_time_sec": wall_time,
                "usage": usage,
                "turn_details": turns,
                "final_reply": final_reply,
                "rubric": rubric,
                "sample_code": sample_code,
            }

    def _render_markdown(self, results):
        lines = [
            "# Econ Agent Prompt & Skill Benchmark Results",
            "",
            "| Model | Task | Arm | Exit | Total Tokens | Input | Output | Cache | Turns | Skill Reads | Custom LOC | Clean Root | YAML | Libs Used | Artifacts | Num OK | Rubric | Time (s) |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :---: | --- | :---: | :---: | ---: | ---: |",
        ]
        for r in results:
            u = r["usage"]
            rb = r["rubric"]
            libs = ", ".join(rb["used_libraries"]) if rb["used_libraries"] else "-"
            lines.append(
                f"| {r['model_label']} | {r['task_id']} | {r['arm_id']} | {r['exit_code']} "
                f"| {u['total_tokens']:,} | {u['input_tokens']:,} | {u['output_tokens']:,} | {u['cache_read_tokens']:,} "
                f"| {u['turns']} | {u['skill_reads']} | {rb['custom_python_loc']} "
                f"| {'Y' if rb['clean_root'] else 'N'} | {'Y' if rb['yaml_config_used'] else 'N'} "
                f"| {libs} | {'Y' if rb['artifacts_ok'] else 'N'} | {'Y' if rb.get('numerical_ok', True) else 'N'} "
                f"| {rb['rubric_score']:.2f} | {r['wall_time_sec']:.1f} |"
            )

        lines.extend(["", "## Qualitative Notes (Files Created per Run)", ""])
        for r in results:
            rb = r["rubric"]
            lines.append(f"### {r['model_label']} / {r['task_id']} / {r['arm_id']}")
            lines.append(f"- Files created: `{rb['created_files']}`")
            if rb["root_clutter"]:
                lines.append(f"- Root clutter: `{rb['root_clutter']}`")
            lines.append(f"- Langfuse trace: `{r.get('langfuse_trace_id')}`")
            lines.append("")
        return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run econ agent prompt/skill benchmarks.")
    parser.add_argument("--config", default=None)
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--arms", nargs="*", default=None)
    parser.add_argument("--tasks", nargs="*", default=None)
    parser.add_argument("--no-langfuse", action="store_true")
    cli_args = parser.parse_args()
    EconAgentBenchmark(
        config_path=cli_args.config,
        models=cli_args.models,
        arms=cli_args.arms,
        tasks=cli_args.tasks,
        use_langfuse=not cli_args.no_langfuse,
    ).run()
