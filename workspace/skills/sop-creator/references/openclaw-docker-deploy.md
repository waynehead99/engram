# How to Deploy Engram on Proxmox LXC via Portainer

> **TL;DR:** Clone the engram repo on the LXC, build the image via CLI, copy config/workspace, then manage with Portainer.

## Definition of Done

- [ ] Engram container is running in Portainer (green/healthy)
- [ ] `http://<LXC-IP>:18789/` loads the Control UI
- [ ] Slack responds to a test message within 30 seconds
- [ ] Heartbeat fires on schedule (check after 30 minutes)
- [ ] Container restarts automatically after LXC reboot

## Prerequisites

- [ ] Proxmox LXC container running (Ubuntu 22.04+ or Debian 12+)
- [ ] Docker Engine installed on the LXC (`docker --version` returns 24+)
- [ ] Portainer CE accessible for this LXC
- [ ] Network: LXC can reach the internet (GitHub, Slack API, Claude API, Google APIs)
- [ ] Network: your workstation can reach `<LXC-IP>:18789`
- [ ] Gateway token (from `~/.openclaw/.env` or generate new: `openssl rand -hex 32`)
- [ ] Config `.env` file with Slack, Google, and Ollama keys (already in `~/.openclaw/.env`)

## Steps

### 1. Prepare the LXC Host

SSH into the LXC and create directories:

```bash
ssh root@<LXC-IP>
mkdir -p /opt/engram/{config,workspace}
```

**Done when:** `/opt/engram/config/` and `/opt/engram/workspace/` exist.

### 2. Copy Config and Workspace from macOS

Only the config and workspace need to be on the LXC host (they contain secrets and are bind-mounted). The OpenClaw source is cloned from GitHub during the Docker build.

```bash
# Copy Engram config (openclaw.json, .env, channel auth, credentials)
scp -r ~/.openclaw/* root@<LXC-IP>:/opt/engram/config/

# Copy workspace (skills, scripts, identity files)
scp -r ~/.openclaw/workspace/* root@<LXC-IP>:/opt/engram/workspace/
```

**Done when:** `ls /opt/engram/config/` shows `openclaw.json` and `.env`.

### 3. Fix Permissions (uid 1000)

> **WARNING:** The container runs as `node` (uid 1000). Host directories must match or you'll get EACCES errors.

```bash
useradd -u 1000 -m node 2>/dev/null || true
chown -R 1000:1000 /opt/engram/config /opt/engram/workspace
```

**Done when:** `stat -c '%u' /opt/engram/config` returns `1000`.

### 4. Update openclaw.json for Docker

The config needs changes for container mode:

```bash
nano /opt/engram/config/openclaw.json
```

| Setting | Old (macOS) | New (Docker) |
|---------|-------------|--------------|
| `gateway.bind` | `"loopback"` | `"lan"` |
| `gateway.port` | `3377` | `18789` |
| `agents.defaults.workspace` | `/Users/wayneerikson/.openclaw/workspace` | `/home/node/.openclaw/workspace` |
| `skills.load.extraDirs[0]` | `~/Documents/dev/SecondBrain/.claude/skills` | `/home/node/.openclaw/workspace/skills` |

**Done when:** `grep -c loopback /opt/engram/config/openclaw.json` returns `0`.

### 5. Clone Repo and Build Image (CLI)

> **WARNING:** Do NOT use Portainer's "Repository" build method — the build takes 10-15 minutes and Portainer will timeout with "Gateway Timeout". Build the image via CLI instead.

```bash
cd /opt/engram
git clone https://github.com/waynehead99/engram.git repo
cd repo
docker build -t engram:latest .
```

This clones OpenClaw from GitHub during the build and compiles everything. First build takes 10-15 minutes. Subsequent rebuilds are faster due to Docker layer caching.

**Done when:** `docker images engram` shows `engram:latest`.

### 6. Configure Environment and Start

```bash
cd /opt/engram/repo
cp .env.example .env
nano .env
```

Fill in these values:

| Variable | Value |
|----------|-------|
| `OPENCLAW_GATEWAY_TOKEN` | Your gateway token |
| `OPENCLAW_CONFIG_DIR` | `/opt/engram/config` |
| `OPENCLAW_WORKSPACE_DIR` | `/opt/engram/workspace` |
| `OPENCLAW_GATEWAY_PORT` | `18789` |

> **NOTE:** Slack, Google, and Ollama credentials are NOT set here. They live in the config directory's `.env` file (`/opt/engram/config/.env`) which OpenClaw loads automatically via dotenv.

Start the container:

```bash
docker compose up -d
```

**Done when:** `docker ps` shows `engram` with status `Up`.

### 7. Import into Portainer

The container is already running. To manage it through Portainer:

1. Open Portainer UI
2. Go to **Stacks** > **Add stack**
3. Name: `engram`
4. Build method: **Web editor**
5. Paste the contents of `docker-compose.yml` (remove the `build:` section since the image already exists):

```yaml
services:
  engram:
    image: engram:latest
    container_name: engram
    environment:
      HOME: /home/node
      TERM: xterm-256color
      OPENCLAW_GATEWAY_TOKEN: ${OPENCLAW_GATEWAY_TOKEN}
    volumes:
      - ${OPENCLAW_CONFIG_DIR:-./config}:/home/node/.openclaw
      - ${OPENCLAW_WORKSPACE_DIR:-./workspace}:/home/node/.openclaw/workspace
      - engram_home:/home/node
    ports:
      - "${OPENCLAW_GATEWAY_PORT:-18789}:18789"
    init: true
    restart: unless-stopped
    command:
      - "node"
      - "dist/index.js"
      - "gateway"
      - "--bind"
      - "lan"
      - "--port"
      - "18789"

volumes:
  engram_home:
```

6. Add environment variables: `OPENCLAW_GATEWAY_TOKEN`, `OPENCLAW_CONFIG_DIR`, `OPENCLAW_WORKSPACE_DIR`, `OPENCLAW_GATEWAY_PORT`
7. Click **Deploy the stack**

> **NOTE:** If Portainer complains the container already exists, stop it first: `docker stop engram && docker rm engram`

**Done when:** Portainer shows `engram` stack as running (green).

### 8. Verify the Deployment

From the LXC host:

```bash
# Container is running
docker ps --filter name=engram --format "{{.Status}}"

# Health check
docker exec engram node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"

# Logs show successful startup
docker logs engram --tail 20
```

From your browser:
- Open `http://<LXC-IP>:18789/`
- Paste gateway token in Settings
- Verify "Connected" status

From Slack:
- Send a DM to Engram bot
- Expect a response within 30 seconds

**Done when:** All three checks pass (container up, UI loads, Slack responds).

## Maintenance

### View Logs

```bash
docker logs engram --tail 100 -f
```

### Restart

```bash
docker restart engram
```

### Update Config

Edit config on host, then restart:

```bash
nano /opt/engram/config/openclaw.json
docker restart engram
```

### Update Engram (New Code or OpenClaw Version)

```bash
cd /opt/engram/repo
git pull origin main
docker build -t engram:latest .
docker compose up -d
```

The Dockerfile clones OpenClaw from GitHub at build time (`main` branch by default). To pin a specific version, pass a build arg:

```bash
docker build --build-arg OPENCLAW_VERSION=v2026.2.10 -t engram:latest .
```

### Update Skills/Workspace Only

No rebuild needed — workspace is bind-mounted:

```bash
scp -r ~/.openclaw/workspace/* root@<LXC-IP>:/opt/engram/workspace/
```

## Troubleshooting

**Problem:** Container exits with `EACCES` permission error
**Fix:** Run `chown -R 1000:1000 /opt/engram/config /opt/engram/workspace`

**Problem:** Portainer "Gateway Timeout" when deploying stack
**Fix:** Don't use Portainer's Repository build method. Build the image via CLI first (`docker build -t engram:latest .`), then use the Web Editor method in Portainer with the pre-built image.

**Problem:** Slack doesn't connect ("socket closed" in logs)
**Fix:** Check `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` in `/opt/engram/config/.env` and verify LXC has outbound internet. Restart the container.

**Problem:** Claude CLI returns "unauthorized" or "session expired"
**Fix:** Get a fresh `CLAUDE_AI_SESSION_KEY` from macOS (`claude auth status`), update the env var in Portainer stack settings, redeploy.

**Problem:** Memory flush not saving to Notion
**Fix:** Verify Google/Notion credentials in `/opt/engram/config/.env`. Check logs: `docker logs engram | grep -i "notion\|google\|error"`

**Problem:** Container uses too much memory
**Fix:** Add to `docker-compose.yml`: `deploy: resources: limits: memory: 2g`

**Problem:** Port 18789 already in use
**Fix:** Change `OPENCLAW_GATEWAY_PORT` in `.env`, then `docker compose up -d`

**Problem:** Heartbeat not firing
**Fix:** Check `heartbeat.every` and `heartbeat.activeHours` in `openclaw.json`. Container defaults to UTC — adjust `activeHours` or add `TZ=America/Chicago` env var in compose.

## Undo

In Portainer: **Stacks** > `engram` > **Delete this stack**

Or from CLI:

```bash
docker stop engram && docker rm engram
docker volume rm engram_engram_home
```

Config and workspace remain on disk at `/opt/engram/` for re-deploy.
