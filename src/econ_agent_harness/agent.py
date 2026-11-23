"""Domain-specific pydantic-ai econ harness with hard folder walls and typed library tools."""

import argparse
import json
import os
from pathlib import Path

from pydantic_ai import Agent, ModelRetry, RunContext

from econ_agent_harness.tools import EconHarnessToolkit

RECOVERABLE_ERRORS = (FileNotFoundError, KeyError, ValueError, PermissionError, ImportError, RuntimeError, OSError)


def _guarded(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except RECOVERABLE_ERRORS as exc:
        raise ModelRetry(f"{type(exc).__name__}: {exc}") from exc

ROOT = Path(__file__).resolve().parents[2]
MODEL = os.getenv("ECON_AGENT_MODEL", "test")

HARNESS_SYSTEM_PROMPT = """You are a domain-specific economic research agent running inside a walled harness.
- The harness enforces folder walls in code: data/raw/ is strictly read-only, and root clutter is blocked.
- ALWAYS propose research choices in YAML under references/configs/ and invoke the provided verified library tools (run_proxy_svar, run_panel_ols, run_sentiment, extract_pdf_claims, run_reproducible_pipeline) rather than inventing ad-hoc math or scrapers.
- Call get_config_template(library) when you need the exact YAML schema for a tool.
- For reproducible_econ pipelines, write stage classes under src/<study>/stages.py (each exposing run(self, data, config) and returning tidy DataFrames with columns spec_name, key_variable, coef, se, pval, n_obs for emitters), write the YAML config under references/configs/, and execute via run_reproducible_pipeline.
- Always report the exact files written, verified numbers, and the config path to reproduce the run."""


def build_agent(model=None, workspace_root=None):
    """Construct a walled pydantic-ai Agent and its toolkit bound to workspace_root."""
    toolkit = EconHarnessToolkit(workspace_root or ROOT)
    active_model = model or MODEL
    harness_agent = Agent(active_model, system_prompt=HARNESS_SYSTEM_PROMPT, retries=3)

    @harness_agent.tool
    def list_files(ctx: RunContext, subdir: str = "") -> str:
        """List files inside the project workspace."""
        return _guarded(toolkit.list_files, subdir)

    @harness_agent.tool
    def read_file(ctx: RunContext, rel_path: str) -> str:
        """Read a text file inside the project workspace."""
        return _guarded(toolkit.read_file, rel_path)

    @harness_agent.tool
    def write_file(ctx: RunContext, rel_path: str, content: str) -> str:
        """Write a file inside allowed non-raw project folders (references/configs/, src/, reports/, docs/, data/intermediate/, data/final/)."""
        return _guarded(toolkit.write_file, rel_path, content)

    @harness_agent.tool
    def get_config_template(ctx: RunContext, library: str) -> str:
        """Get a verified YAML config template for proxy_svar, panel_ols, sentiment, or reproducible_econ."""
        return _guarded(toolkit.get_config_template, library)

    @harness_agent.tool
    def run_proxy_svar(ctx: RunContext, config_path: str) -> str:
        """Run stats-transformer FeatureEngineer + Mertens-Ravn ProxySVARModel from a YAML config."""
        return _guarded(toolkit.run_proxy_svar, config_path)

    @harness_agent.tool
    def run_panel_ols(ctx: RunContext, config_path: str) -> str:
        """Run stats-transformer PanelRegressionModel from a YAML config."""
        return _guarded(toolkit.run_panel_ols, config_path)

    @harness_agent.tool
    def run_sentiment(ctx: RunContext, config_path: str) -> str:
        """Run auto-econ-sentiment SentimentLexical from a YAML config."""
        return _guarded(toolkit.run_sentiment, config_path)

    @harness_agent.tool
    def extract_pdf_claims(ctx: RunContext, pdf_path: str, output_md_path: str, output_json_path: str = "") -> str:
        """Run econ-pdf-extract on a PDF and save auditable Markdown (and optional JSON) with section and page provenance."""
        return _guarded(toolkit.extract_pdf_claims, pdf_path, output_md_path, output_json_path)

    @harness_agent.tool
    def run_reproducible_pipeline(ctx: RunContext, config_path: str, no_cache: bool = False) -> str:
        """Run reproducible-econ PipelineRunner on a YAML config inside the workspace."""
        return _guarded(toolkit.run_reproducible_pipeline, config_path, no_cache=no_cache)

    return harness_agent, toolkit


agent, _default_toolkit = build_agent(MODEL, ROOT)


class EconAgentHarness:
    """Interactive REPL and single-task runner for the custom econ agent harness."""

    def __init__(self, model=None, workspace_root=None):
        self.workspace_root = Path(workspace_root) if workspace_root else ROOT
        self.agent, self.toolkit = build_agent(model=model or MODEL, workspace_root=self.workspace_root)

    def run_task(self, prompt):
        """Run a single research task and return output, token usage, turns, and libraries used."""
        result = self.agent.run_sync(prompt)
        usage_obj = result.usage
        input_tok = int(getattr(usage_obj, "input_tokens", 0) or 0)
        output_tok = int(getattr(usage_obj, "output_tokens", 0) or 0)
        cache_tok = int(getattr(usage_obj, "cache_read_tokens", 0) or 0)
        requests = int(getattr(usage_obj, "requests", 0) or 0)
        tool_calls = int(getattr(usage_obj, "tool_calls", 0) or 0)

        turn_details = []
        for msg in result.all_messages():
            kind = getattr(msg, "kind", "")
            if kind != "response":
                continue
            m_usage = getattr(msg, "usage", None)
            t_in = int(getattr(m_usage, "input_tokens", 0) or 0) if m_usage else 0
            t_out = int(getattr(m_usage, "output_tokens", 0) or 0) if m_usage else 0
            t_cr = int(getattr(m_usage, "cache_read_tokens", 0) or 0) if m_usage else 0
            parts = getattr(msg, "parts", [])
            t_calls = [getattr(p, "tool_name", "") for p in parts if getattr(p, "part_kind", "") == "tool-call"]
            t_texts = [getattr(p, "content", "") for p in parts if getattr(p, "part_kind", "") == "text"]
            ts = getattr(msg, "timestamp", None)
            turn_details.append({
                "timestamp": ts.isoformat() if ts else "",
                "input": t_in,
                "output": t_out,
                "cache_read": t_cr,
                "cache_write": 0,
                "total": t_in + t_out + t_cr,
                "duration_ms": 0,
                "tool_calls": t_calls,
                "text": "\n".join(str(x) for x in t_texts).strip(),
            })

        usage = {
            "input_tokens": input_tok,
            "output_tokens": output_tok,
            "cache_read_tokens": cache_tok,
            "cache_write_tokens": 0,
            "total_tokens": input_tok + output_tok + cache_tok,
            "turns": requests or len(turn_details),
            "tool_calls": tool_calls or sum(len(t["tool_calls"]) for t in turn_details),
            "skill_reads": 0,
        }
        return {
            "final_reply": str(result.output),
            "usage": usage,
            "turn_details": turn_details,
            "used_libraries": sorted(self.toolkit.used_libraries),
        }

    def run(self):
        """Start an interactive REPL session."""
        history = []
        print(f"econ-agent-harness agent (model={MODEL}, root={self.workspace_root})")
        print("Type a request. 'exit' to quit.")
        while True:
            try:
                user = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not user or user.lower() in {"exit", "quit"}:
                break
            result = self.agent.run_sync(user, message_history=history)
            history = result.all_messages()
            print("agent>", result.output)


def _resolve_model(provider, model_name):
    if provider == "ollama-api-key":
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider

        return OpenAIChatModel(
            model_name,
            provider=OpenAIProvider(base_url="https://ollama.com/v1", api_key=os.environ["OLLAMA_API_KEY"]),
        )
    return model_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run EconAgentHarness REPL or single benchmark task.")
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--out-json", default=None)
    args = parser.parse_args()
    if args.prompt:
        resolved = _resolve_model(args.provider, args.model or MODEL)
        harness = EconAgentHarness(model=resolved, workspace_root=args.workspace)
        payload = harness.run_task(args.prompt)
        if args.out_json:
            Path(args.out_json).write_text(json.dumps(payload, indent=2))
        else:
            print(json.dumps(payload, indent=2))
    else:
        EconAgentHarness(workspace_root=args.workspace).run()
