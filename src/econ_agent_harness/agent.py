"""Lean pydantic-ai harness agent for econ research. Interactive REPL via run()."""
import os
from pathlib import Path

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import LocalWorkspace

ROOT = Path(__file__).resolve().parents[2]
from pydantic_ai_harness.coder import Coder

AGENTS_MD = ROOT / "AGENTS.md"
MODEL = os.getenv("ECON_AGENT_MODEL", "test")


def _system_prompt() -> str:
    if AGENTS_MD.is_file():
        return AGENTS_MD.read_text()
    return "You are a concise econ research coding agent. Prefer small deterministic changes."


agent = Agent(MODEL, capabilities=[LocalWorkspace(str(ROOT)), Coder()],
              system_prompt=_system_prompt(), retries=2)


@agent.tool
def list_configs(ctx: RunContext, kind: str = "") -> str:
    """List YAML configs under references/configs, optionally filtered."""
    base = ROOT / "references" / "configs"
    files = sorted(p.relative_to(ROOT).as_posix() for p in base.rglob("*.yaml"))
    if kind:
        files = [f for f in files if kind in f]
    return "\n".join(files)


class EconAgentHarness:
    def __init__(self, model=None):
        global agent
        if model:
            agent = Agent(model, capabilities=[LocalWorkspace(str(ROOT)), Coder()],
                          system_prompt=_system_prompt(), retries=2)
        self.agent = agent

    def run(self):
        history = []
        print(f"econ-agent-harness agent (model={MODEL})")
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


if __name__ == "__main__":
    EconAgentHarness().run()
