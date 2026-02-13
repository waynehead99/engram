# Engram — Personal AI Assistant Gateway
# Built on OpenClaw framework with Claude Code CLI and Python dependencies
# for Google Workspace scripts (Gmail, Calendar).
#
# OpenClaw source is cloned at build time — no submodule needed.
# Deploy with: docker compose up -d  (or via Portainer stack)

FROM node:22-bookworm AS builder

# System deps: Python for Google Workspace scripts, build tools
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv git curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

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

# Build the gateway runtime (rolldown bundle).
# The DTS (TypeScript declarations) step may fail on some OpenClaw versions
# due to upstream type errors — but dist/index.js is all we need for runtime.
RUN pnpm build || \
    (test -f dist/index.js && echo "Core build succeeded; DTS errors ignored")

ENV OPENCLAW_PREFER_PNPM=1
RUN pnpm ui:build

# ── Production stage ────────────────────────────────────────────────
FROM node:22-bookworm-slim

# System deps for runtime
# procps provides pkill/pgrep (required by OpenClaw CLI backend for process management)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv curl procps && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Python packages in a virtual environment (clean isolation)
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir \
    google-auth google-api-python-client python-dotenv PyYAML

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

WORKDIR /app

# Copy built application from builder stage
COPY --from=builder /app /app

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV NODE_ENV=production

# Allow non-root user to write temp files during runtime
RUN chown -R node:node /app && \
    mkdir -p /home/node/.openclaw/workspace && \
    chown -R node:node /home/node

# Security: run as non-root (node user, uid 1000)
USER node

# Health check — verify the gateway is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:18789/ || exit 1

EXPOSE 18789

ENTRYPOINT ["/app/entrypoint.sh"]
