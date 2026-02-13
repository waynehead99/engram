#!/bin/bash
set -e

# ── Engram Entrypoint ───────────────────────────────────────────────
# Validates required environment, sets up directories, and starts
# the OpenClaw gateway.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Engram — Personal AI Assistant${NC}"
echo -e "${GREEN}========================================${NC}"

# ── Validate required environment variables ─────────────────────────
MISSING=0

if [ -z "$OPENCLAW_GATEWAY_TOKEN" ]; then
    echo -e "${RED}ERROR: OPENCLAW_GATEWAY_TOKEN is not set.${NC}"
    echo "  Generate one with: openssl rand -hex 32"
    MISSING=1
fi

if [ -z "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
    echo -e "${RED}ERROR: CLAUDE_CODE_OAUTH_TOKEN is not set.${NC}"
    echo "  Generate one on your Mac with: claude setup-token"
    MISSING=1
fi

if [ "$MISSING" -eq 1 ]; then
    echo ""
    echo -e "${RED}Missing required environment variables. Cannot start.${NC}"
    echo "See .env.example for all required variables."
    exit 1
fi

# ── Check for config directory ──────────────────────────────────────
if [ ! -f "$HOME/.openclaw/openclaw.json" ]; then
    echo -e "${YELLOW}WARNING: No openclaw.json found at $HOME/.openclaw/openclaw.json${NC}"
    echo "  The gateway will start with default configuration."
    echo "  For full functionality, mount your config directory."
fi

# ── Check for workspace ─────────────────────────────────────────────
if [ ! -d "$HOME/.openclaw/workspace" ]; then
    echo -e "${YELLOW}WARNING: No workspace found at $HOME/.openclaw/workspace${NC}"
    echo "  Creating empty workspace directory."
    mkdir -p "$HOME/.openclaw/workspace"
fi

# ── Ensure memory directory exists ──────────────────────────────────
mkdir -p "$HOME/.openclaw/workspace/memory"

# ── Display startup info ────────────────────────────────────────────
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Config dir:  $HOME/.openclaw"
echo "  Workspace:   $HOME/.openclaw/workspace"
echo "  Gateway port: 18789"
echo ""
echo -e "${GREEN}Starting OpenClaw gateway...${NC}"
echo ""

# ── Start the gateway ───────────────────────────────────────────────
exec node /app/dist/index.js gateway \
    --allow-unconfigured \
    --bind lan \
    --port 18789
