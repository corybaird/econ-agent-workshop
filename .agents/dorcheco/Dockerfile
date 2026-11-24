FROM ubuntu:24.04

ARG HOST_UID=1000
ARG HOST_GID=1000
ARG AGENT_HOME=/home/agent

ENV PATH="${AGENT_HOME}/.local/bin:/usr/local/bin:${PATH}"
ENV SHELL=/bin/bash
ENV TERM=xterm-256color
ENV UV_PROJECT_ENVIRONMENT=${AGENT_HOME}/.venv-workspace
ENV UV_LINK_MODE=copy

# Core OS tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git bash jq ripgrep ca-certificates sudo \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && apt-get install -y --no-install-recommends gh && \
    rm -rf /var/lib/apt/lists/*

# Node.js 22 LTS + out-of-the-box coding agents (Claude Code, OpenAI Codex, Pi)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    npm install -g @anthropic-ai/claude-code @openai/codex @earendil-works/pi-coding-agent

# Non-root agent user matching host uid/gid so files written to /workspace keep host ownership
RUN userdel -r ubuntu 2>/dev/null || true && \
    (getent group "${HOST_GID}" >/dev/null || groupadd -g "${HOST_GID}" agent) && \
    useradd -m -d "${AGENT_HOME}" -u "${HOST_UID}" -g "${HOST_GID}" -s /bin/bash agent && \
    echo "agent ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/agent && \
    chmod 0440 /etc/sudoers.d/agent && \
    mkdir -p /workspace /workspace-worktrees && \
    chown "${HOST_UID}:${HOST_GID}" /workspace /workspace-worktrees

USER agent
WORKDIR ${AGENT_HOME}
RUN mkdir -p .config/gh .config/herdr .claude .codex .pi/agent .gemini .cache/uv

# uv + Herdr multiplexer + Antigravity CLI (agy)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    curl -fsSL https://herdr.dev/install.sh | sh && \
    curl -fsSL https://antigravity.google/cli/install.sh | bash

# Optional Langfuse plugin for Pi (stays off unless LANGFUSE_* keys are set in .env)
RUN pi install npm:@langfuse/pi-observability-plugin

# Bake Section 1+2 combined prompt, attribution rules, Herdr roles, and entrypoint
USER root
COPY .agents/prompts/2_combined_econ_prompt.md /etc/econ-agent/PROMPT.md
COPY .agents/dorcheco/claude-settings.json /etc/claude-code/managed-settings.json
COPY .agents/prompts/2_combined_econ_prompt.md /etc/claude-code/CLAUDE.md
COPY .agents/dorcheco/roles/ /etc/herdr/roles/
COPY .agents/dorcheco/entrypoint.sh /usr/local/bin/dorcheco-entrypoint.sh
RUN chmod 0644 /etc/econ-agent/PROMPT.md /etc/claude-code/managed-settings.json \
    /etc/claude-code/CLAUDE.md /etc/herdr/roles/*.md && \
    chmod 0755 /usr/local/bin/dorcheco-entrypoint.sh

USER agent
RUN git config --global --add safe.directory /workspace && \
    git config --global credential.https://github.com.helper "!/usr/bin/gh auth git-credential"

WORKDIR /workspace
VOLUME ["/workspace-worktrees"]
ENTRYPOINT ["/usr/local/bin/dorcheco-entrypoint.sh"]
