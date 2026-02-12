# Engram — Custom Gateway Image (Claude CLI + Python for Google Workspace)
# Built on OpenClaw framework with Claude Code CLI and Python dependencies
# for Google Workspace scripts (Gmail, Calendar).

FROM node:22-bookworm

# System deps: Python for Google Workspace scripts, build tools
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv git curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Python packages for Google Workspace skill
RUN pip3 install --break-system-packages \
    google-auth google-api-python-client python-dotenv

# Install Bun (required for OpenClaw build scripts)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN corepack enable

WORKDIR /app

# Copy lockfiles first for layer caching
COPY openclaw/package.json openclaw/pnpm-lock.yaml openclaw/pnpm-workspace.yaml openclaw/.npmrc ./
COPY openclaw/ui/package.json ./ui/package.json
COPY openclaw/patches ./patches
COPY openclaw/scripts ./scripts

RUN pnpm install --frozen-lockfile

COPY openclaw/ .
RUN pnpm build
ENV OPENCLAW_PREFER_PNPM=1
RUN pnpm ui:build

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

ENV NODE_ENV=production

# Allow non-root user to write temp files during runtime
RUN chown -R node:node /app

# Security: run as non-root (node user, uid 1000)
USER node

CMD ["node", "openclaw.mjs", "gateway", "--allow-unconfigured", "--bind", "lan", "--port", "18789"]
