# Research Basics: Setup



### Software

You need **macOS or Linux**, plus:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/), open and running for agent exercises
- [Git](https://git-scm.com/downloads)
- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/), for the locked Python environment
- [zsh](https://www.zsh.org), already installed on macOS

The deterministic library exercises need only Python, uv, and Git. The agent runtime installs inside the Dorch container.

### Accounts and tokens

- Harness accounts and coding agents:
  - [Claude](https://claude.ai), for signing in to Claude Code
  - [Antigravity](https://antigravity.google), for signing in to the Antigravity agent
  - [Pi coding agent](https://github.com/earendil-works/pi/tree/main/packages/coding-agent), download and installation instructions
- API keys and access tokens:
  - [GitHub token](https://github.com/settings/tokens), for GitHub CLI authentication and repository access
  - [Ollama API key](https://ollama.com/settings/keys), for running Pi with Ollama Cloud models
  - [Overleaf Git-bridge token](https://www.overleaf.com/user/settings), for pushing and pulling the presentation through Git

## Project organization

```text
data/          raw, intermediate, final (placeholders only for now)
references/    recorded choices: configs and dictionaries
src/           code, one folder per tool
docs/          these guides
reports/       regenerable outputs
```

Two habits:

- Never edit `data/raw/` by hand.
- Write research decisions in `references/`, not in memory.
