# Engram — Custom Gateway Image (Claude CLI + Python for Google Workspace)
# Built on OpenClaw framework with Claude Code CLI and Python dependencies
# for Google Workspace scripts (Gmail, Calendar).
#
# OpenClaw source is cloned at build time — no submodule needed.

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

# Clone OpenClaw source at build time
# Pin to a specific commit/tag with OPENCLAW_VERSION for reproducible builds
ARG OPENCLAW_VERSION=main
RUN git clone --depth 1 --branch ${OPENCLAW_VERSION} \
    https://github.com/openclaw/openclaw.git /tmp/openclaw

# Copy lockfiles first for layer caching
RUN cp /tmp/openclaw/package.json /tmp/openclaw/pnpm-lock.yaml \
       /tmp/openclaw/pnpm-workspace.yaml /tmp/openclaw/.npmrc ./
RUN mkdir -p ui && cp /tmp/openclaw/ui/package.json ./ui/package.json
RUN cp -r /tmp/openclaw/patches ./patches
RUN cp -r /tmp/openclaw/scripts ./scripts

RUN pnpm install --frozen-lockfile

RUN cp -r /tmp/openclaw/. . && rm -rf /tmp/openclaw
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
