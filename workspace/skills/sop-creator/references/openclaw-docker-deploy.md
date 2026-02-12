# How to Deploy Engram on Proxmox LXC via Portainer

> **TL;DR:** Build the custom Engram Docker image, deploy it as a Portainer stack on your Proxmox LXC, and verify Slack connectivity.

## Definition of Done

You're done when:
- [ ] Engram gateway container is running in Portainer (green/healthy)
- [ ] `http://<LXC-IP>:18789/` loads the Control UI
- [ ] Slack responds to a test message within 30 seconds
- [ ] Heartbeat fires on schedule (check after 30 minutes)
- [ ] Container restarts automatically after LXC reboot

## Prerequisites

- [ ] Proxmox LXC container running (Ubuntu 22.04+ or Debian 12+)
- [ ] Docker Engine installed on the LXC (`docker --version` returns 24+)
- [ ] Portainer agent or Portainer CE accessible for this LXC
- [ ] Network: LXC can reach the internet (for Slack, Claude API, Google APIs)
- [ ] Network: your workstation can reach `<LXC-IP>:18789`
- [ ] Files from macOS `~/.openclaw/` ready to copy (config + workspace)
- [ ] Claude AI session key (`claude auth status` on macOS, copy the session key)
- [ ] OpenClaw gateway token (from `~/.openclaw/.env` or generate new: `openssl rand -hex 32`)

## Steps

### 1. Prepare the LXC Host Directory Structure

SSH into the LXC and create the deployment directory:

```bash
ssh root@<LXC-IP>
mkdir -p /opt/openclaw/{config,workspace,docker}
```

**Done when:** `/opt/openclaw/docker/`, `/opt/openclaw/config/`, and `/opt/openclaw/workspace/` exist.

### 2. Copy Files from macOS to LXC

From your Mac, transfer the config, workspace, and docker build files:

```bash
# Copy OpenClaw config (contains openclaw.json, .env, channel auth, etc.)
scp -r ~/.openclaw/* root@<LXC-IP>:/opt/openclaw/config/

# Copy workspace (skills, scripts, memories)
scp -r ~/.openclaw/workspace/* root@<LXC-IP>:/opt/openclaw/workspace/

# Copy custom Docker files
scp -r ~/.openclaw/workspace/docker/* root@<LXC-IP>:/opt/openclaw/docker/

# Copy the OpenClaw source (needed for Docker build)
scp -r ~/Documents/dev/SecondBrain/openclaw root@<LXC-IP>:/opt/openclaw/docker/openclaw
```

**Done when:** `ls /opt/openclaw/docker/` shows `Dockerfile`, `docker-compose.yml`, `.env.example`, and `openclaw/` directory.

### 3. Fix Permissions (uid 1000)

The container runs as `node` (uid 1000). Host directories must match:

```bash
ssh root@<LXC-IP>
useradd -u 1000 -m node 2>/dev/null || true
chown -R 1000:1000 /opt/openclaw/config /opt/openclaw/workspace
```

**Done when:** `stat -c '%u' /opt/openclaw/config` returns `1000`.

### 4. Configure Environment Variables

```bash
cd /opt/openclaw/docker
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
nano .env
```

| Variable | Where to Get It |
|----------|-----------------|
| `OPENCLAW_GATEWAY_TOKEN` | From macOS `~/.openclaw/.env` or generate: `openssl rand -hex 32` |
| `CLAUDE_AI_SESSION_KEY` | Run `claude auth status` on macOS, copy the session key value |
| `OPENCLAW_CONFIG_DIR` | `/opt/openclaw/config` |
| `OPENCLAW_WORKSPACE_DIR` | `/opt/openclaw/workspace` |
| `OPENCLAW_GATEWAY_PORT` | `18789` (or change if port conflicts) |

**Done when:** `cat .env` shows all five variables filled in (no blanks).

### 5. Update openclaw.json for Docker

The config needs two changes for container mode:

```bash
ssh root@<LXC-IP>
nano /opt/openclaw/config/openclaw.json
```

Change these values:

| Setting | Old (macOS) | New (Docker) |
|---------|-------------|--------------|
| `gateway.bind` | `"loopback"` | `"lan"` |
| `gateway.port` | `3377` | `18789` |
| `agents.defaults.workspace` | `/Users/wayneerikson/.openclaw/workspace` | `/home/node/.openclaw/workspace` |
| `skills.load.extraDirs[0]` | `~/Documents/dev/SecondBrain/.claude/skills` | `/home/node/.openclaw/workspace/skills` |

**Done when:** `grep -c loopback /opt/openclaw/config/openclaw.json` returns `0`.

### 6. Build the Image (CLI) or Deploy via Portainer

**Option A: Portainer Stack (recommended)**

1. Open Portainer UI in your browser
2. Go to **Stacks** > **Add stack**
3. Name: `openclaw`
4. Build method: **Upload** > upload `docker-compose.yml`
5. Environment variables: add each variable from `.env` (or use "Load variables from .env file")
6. Click **Deploy the stack**

> **WARNING:** If using Portainer "Repository" method, the build context must contain the `openclaw/` source directory. "Upload" with a pre-built image is simpler.

**Option B: CLI on LXC host**

```bash
cd /opt/openclaw/docker
docker compose build
docker compose up -d
```

**Done when:** `docker ps` shows `engram` with status `Up`.

### 7. Verify the Deployment

Run these checks from the LXC host:

```bash
# Container is running
docker ps --filter name=engram --format "{{.Status}}"

# Health check
docker exec engram node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"

# Logs show successful startup
docker logs engram --tail 20
```

Check from your browser:
- Open `http://<LXC-IP>:18789/`
- Paste gateway token in Settings
- Verify "Connected" status

Check Slack:
- Send a DM to Engram bot in Slack
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
nano /opt/openclaw/config/openclaw.json
docker restart engram
```

### Update Image (New OpenClaw Version)

```bash
cd /opt/openclaw/docker

# Pull latest source
scp -r user@mac:~/Documents/dev/SecondBrain/openclaw /opt/openclaw/docker/openclaw

# Rebuild and restart
docker compose build --no-cache
docker compose up -d
```

### Update Skills/Workspace

No restart needed — workspace is bind-mounted:

```bash
scp -r user@mac:~/.openclaw/workspace/* /opt/openclaw/workspace/
```

## Troubleshooting

**Problem:** Container exits immediately with `EACCES` permission error
**Fix:** Ownership mismatch. Run `chown -R 1000:1000 /opt/openclaw/config /opt/openclaw/workspace`

**Problem:** Slack doesn't connect ("socket closed" in logs)
**Fix:** Check that `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` are in `/opt/openclaw/config/.env` and the LXC has outbound internet access. Restart the container.

**Problem:** Claude CLI returns "unauthorized" or "session expired"
**Fix:** Get a fresh `CLAUDE_AI_SESSION_KEY` from macOS (`claude auth status`), update `.env`, and restart: `docker compose up -d`

**Problem:** Memory flush / compaction not saving to Notion
**Fix:** Verify Google/Notion credentials are present in the config `.env`. Check logs for API errors: `docker logs engram | grep -i "notion\|google\|error"`

**Problem:** Container uses too much memory
**Fix:** Add memory limit to `docker-compose.yml` under the service: `deploy: resources: limits: memory: 2g`

**Problem:** Port 18789 already in use on LXC
**Fix:** Change `OPENCLAW_GATEWAY_PORT` in `.env` to a free port (e.g., `18790`), then `docker compose up -d`

**Problem:** Heartbeat not firing
**Fix:** Check that `heartbeat.every` and `heartbeat.activeHours` are configured in `openclaw.json`. Container timezone defaults to UTC — adjust `activeHours` accordingly or set `TZ` env var in compose.

## Undo

Stop and remove the deployment:

```bash
cd /opt/openclaw/docker
docker compose down
docker volume rm docker_engram_home
```

Config and workspace remain on disk at `/opt/openclaw/` and can be re-deployed.
