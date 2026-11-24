# Research Basics: Docs and Folders as Infrastructure

Module 1 of the presentation (**Section 1. Research Basics — Docs/Folders as Infrastructure**): version control, locked environments, and clean folder contracts before adding AI agents.

### Software

You need **macOS or Linux**, plus:

- [Git](https://git-scm.com/downloads) — code and decision history (and worktrees for multi-agent workflows)
- [uv](https://docs.astral.sh/uv/) — locked Python environment (`pyproject.toml`, `uv.lock`, `.python-version` pinned to Python 3.12)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — machine isolation and read-only sandboxes for Section 3 agent exercises
- [zsh](https://www.zsh.org) — already installed on macOS

The Section 2 library scripts and Jupyter notebooks need only `git` and `uv` (`uv sync` installs Python 3.12, all four libraries, and Jupyter). The coding agents install inside the `dorcheco` container (`./scripts/dorcheco.sh`).

### Quick Setup Check

```bash
uv sync
uv run pytest -q
```

See [Quickstart Code](quickstart_code.md) for all runnable `uv` scripts and Jupyter kernel commands.

### Accounts and Tokens (Section 3 Agent Exercises)

- Coding agents:
  - [Claude](https://claude.ai), for signing in to Claude Code
  - [Antigravity](https://antigravity.google), for signing in to the Antigravity agent
  - [Pi coding agent](https://github.com/earendil-works/pi/tree/main/packages/coding-agent), download and installation instructions
- API keys and access tokens:
  - [GitHub token](https://github.com/settings/tokens), for GitHub CLI authentication and repository access
  - [Ollama API key](https://ollama.com/settings/keys), for running Pi with Ollama Cloud models
  - [Overleaf Git-bridge token](https://www.overleaf.com/user/settings), for pushing and pulling manuscripts and slides through Git

## Project Organization

```text
data/          raw (immutable), intermediate, final
references/    recorded choices: YAML configs and shared dictionaries
src/           analysis and harness code, one package per tool
notebooks/     one interactive walkthrough notebook per library
scripts/       one-command shell wrappers around uv run
docs/          workshop guides and citations
reports/       regenerable tables, figures, manifests, and overleaf/ exports
.agents/       prompts, library skills, and dorcheco Docker + Herdr config
```

Two habits:

- Never edit `data/raw/` by hand.
- Write research decisions in `references/`, not in memory — and export results directly from code instead of pasting into papers.

Next: [Software for Macro](1_software_for_macro.md).
