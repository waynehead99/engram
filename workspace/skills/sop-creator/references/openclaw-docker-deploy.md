# How to Deploy Engram on Proxmox LXC via Portainer

> **TL;DR:** Point Portainer at the `waynehead99/engram` GitHub repo, copy config/workspace to the LXC, set env vars, and deploy.

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

SSH into the LXC and create directories for config and workspace:

```bash
ssh root@<LXC-IP>
mkdir -p /opt/engram/{config,workspace}
```

**Done when:** `/opt/engram/config/` and `/opt/engram/workspace/` exist.

### 2. Copy Config and Workspace from macOS

Only the config and workspace need to be on the LXC host (they contain secrets and are bind-mounted). The source code is pulled from GitHub by Portainer.

```bash
# Copy Engram config (openclaw.json, .env, channel auth, credentials)
scp -r ~/.openclaw/* root@<LXC-IP>:/opt/engram/config/

# Copy workspace (skills, scripts, identity files)
scp -r ~/.openclaw/workspace/* root@<LXC-IP>:/opt/engram/workspace/
```

**Done when:** `ls /opt/engram/config/` shows `openclaw.json` and `.env`, and `/opt/engram/workspace/skills/` has your skill directories.

### 3. Fix Permissions (uid 1000)

> **WARNING:** The container runs as `node` (uid 1000). Host directories must match or you'll get EACCES errors.

```bash
ssh root@<LXC-IP>
useradd -u 1000 -m node 2>/dev/null || true
chown -R 1000:1000 /opt/engram/config /opt/engram/workspace
```

**Done when:** `stat -c '%u' /opt/engram/config` returns `1000`.

### 4. Update openclaw.json for Docker

The config needs changes for container mode. Edit on the LXC:

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

### 5. Deploy via Portainer (Repository Method)

1. Open Portainer UI in your browser
2. Go to **Stacks** > **Add stack**
3. Name: `engram`
4. Build method: **Repository**
5. Repository URL: `https://github.com/waynehead99/engram`
6. Branch: `main`
7. Compose path: `docker-compose.yml`
8. **Enable "Git submodule support"** (toggle ON — required to pull the OpenClaw source)
9. Add environment variables:

| Variable | Value |
|----------|-------|
| `OPENCLAW_GATEWAY_TOKEN` | Your gateway token |
| `OPENCLAW_CONFIG_DIR` | `/opt/engram/config` |
| `OPENCLAW_WORKSPACE_DIR` | `/opt/engram/workspace` |
| `OPENCLAW_GATEWAY_PORT` | `18789` |

10. Click **Deploy the stack**

> **NOTE:** Slack, Google, and Ollama credentials are NOT set as Docker env vars. They live inside the config directory's `.env` file (`/opt/engram/config/.env`) which OpenClaw loads automatically via dotenv at startup.

> **NOTE:** The first build takes several minutes (cloning OpenClaw, `pnpm install`, `pnpm build`). Subsequent rebuilds are faster due to Docker layer caching.

**Done when:** Portainer shows the `engram` stack as running (green).

### 6. Verify the Deployment

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

### Update Engram (New Version / New Skills)

1. Push changes to `waynehead99/engram` on GitHub
2. In Portainer: **Stacks** > `engram` > **Editor** > **Pull and redeploy**
3. If the OpenClaw submodule was updated, Portainer re-clones and rebuilds

To update the OpenClaw submodule to latest upstream:

```bash
cd ~/Documents/dev/SecondBrain/engram
git submodule update --remote openclaw
git add openclaw
git commit -m "Update OpenClaw submodule to latest"
git push origin main
```

Then redeploy in Portainer.

### Update Skills/Workspace Only

No rebuild needed — workspace is bind-mounted:

```bash
scp -r ~/.openclaw/workspace/* root@<LXC-IP>:/opt/engram/workspace/
```

## Troubleshooting

**Problem:** Container exits with `EACCES` permission error
**Fix:** Run `chown -R 1000:1000 /opt/engram/config /opt/engram/workspace`

**Problem:** Portainer build fails on "openclaw/ directory not found"
**Fix:** Ensure **Git submodule support** is enabled in the Portainer stack settings.

**Problem:** Slack doesn't connect ("socket closed" in logs)
**Fix:** Check `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` in `/opt/engram/config/.env` and verify LXC has outbound internet. Restart the container.

**Problem:** Claude CLI returns "unauthorized" or "session expired"
**Fix:** Get a fresh `CLAUDE_AI_SESSION_KEY` from macOS (`claude auth status`), update the env var in Portainer stack settings, redeploy.

**Problem:** Memory flush not saving to Notion
**Fix:** Verify Google/Notion credentials in `/opt/engram/config/.env`. Check logs: `docker logs engram | grep -i "notion\|google\|error"`

**Problem:** Container uses too much memory
**Fix:** Add to compose env in Portainer or edit `docker-compose.yml`: `deploy: resources: limits: memory: 2g`

**Problem:** Port 18789 already in use
**Fix:** Change `OPENCLAW_GATEWAY_PORT` env var in Portainer stack settings, redeploy.

**Problem:** Heartbeat not firing
**Fix:** Check `heartbeat.every` and `heartbeat.activeHours` in `openclaw.json`. Container defaults to UTC — adjust `activeHours` or add `TZ=America/Chicago` env var in Portainer.

## Undo

In Portainer: **Stacks** > `engram` > **Delete this stack**

Or from CLI:

```bash
docker stop engram && docker rm engram
docker volume rm engram_engram_home
```

Config and workspace remain on disk at `/opt/engram/` and can be re-deployed.
