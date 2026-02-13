# Engram

**Your personal AI assistant with perfect memory.**

Engram is a self-hosted AI assistant that connects to your Slack, reads your email and calendar, manages projects in Notion, and remembers everything across conversations. It runs as a Docker container and is designed to be deployed via Portainer.

```
You (Slack DM) ──> Engram Container ──> Claude AI (thinking)
                        │                    │
                        ├── Notion (memory, projects, docs)
                        ├── Gmail (read/send email)
                        ├── Google Calendar (view/create events)
                        └── Ollama (optional local models)
```

---

## What Can Engram Do?

| Skill | What It Does |
|-------|-------------|
| **Notion Knowledge Capture** | Saves notes, articles, code snippets, and meeting notes to your Notion knowledge base. Auto-categorizes everything. |
| **Notion Project Manager** | Creates and tracks projects and tasks in Notion. Runs weekly reviews. Manages priorities. |
| **Notion RAG** | Searches your entire Notion knowledge base to answer questions using your own notes. |
| **Notion Memory Sync** | Automatically syncs conversation memories from local files to Notion for permanent storage. |
| **SOP Creator** | Creates runbooks, checklists, how-to guides, and other documentation. Saves them to Notion. |
| **Google Workspace** | Reads your Gmail inbox, searches emails, sends replies. Views and creates calendar events. |
| **MCP Client** | Connects to external tool servers (Zapier, GitHub, etc.) for additional integrations. |
| **Skill Creator** | A meta-skill for building new skills to extend Engram's capabilities. |

---

## Prerequisites

Before you start, you need:

1. **A server running Docker** (Linux LXC, VM, or bare metal)
   - Docker Engine 24+ and Docker Compose v2+
   - OR Portainer installed and running
2. **A Claude account** with API access (for the AI brain)
3. **A Slack workspace** where you want Engram to live
4. **(Optional)** A Notion workspace for knowledge management
5. **(Optional)** A Google Cloud project for Gmail/Calendar access
6. **(Optional)** An Ollama server for local model inference

---

## Quick Start

Engram only needs **two tokens** to start. Everything else (Slack, Notion, Google, Ollama) can be configured through the web UI after the container is running.

### Step 1: Clone the Repository

On your server, open a terminal and run:

```bash
git clone https://github.com/waynehead99/engram.git
cd engram
```

### Step 2: Create Your Environment File

```bash
cp .env.example .env
```

Open the `.env` file in a text editor (like `nano .env`) and fill in the two required tokens:

**Gateway Token** — protects your Engram web interface:
```bash
# Run this command to generate a random token:
openssl rand -hex 32
# Copy the output and paste it as your OPENCLAW_GATEWAY_TOKEN
```

**Claude OAuth Token** — lets Engram talk to Claude AI:
```bash
# On your Mac or PC where Claude is installed, run:
claude setup-token
# Copy the token (starts with sk-ant-oat01-...) and paste it as CLAUDE_CODE_OAUTH_TOKEN
```

**Host Paths** — where Engram stores its data on your server:
```
OPENCLAW_CONFIG_DIR=/opt/engram/config
OPENCLAW_WORKSPACE_DIR=/opt/engram/workspace
```

### Step 3: Set Up the Config Directory

Create the directories on your server:

```bash
sudo mkdir -p /opt/engram/config
sudo mkdir -p /opt/engram/workspace
```

Copy the config files from this repo into place:

```bash
# Copy the OpenClaw configuration
sudo cp openclaw.json /opt/engram/config/

# Copy the workspace (personality, skills, tools docs)
sudo cp -r workspace/* /opt/engram/workspace/

# Copy the secrets template (you can fill this in now or use the web UI later)
sudo cp config/.env.example /opt/engram/config/.env
```

### Step 4: Set Permissions

The container runs as user ID 1000 (the `node` user). Make sure it can read/write:

```bash
sudo chown -R 1000:1000 /opt/engram
```

### Step 5: Deploy

**Option A — Using Docker Compose (command line):**
```bash
docker compose up -d
```

**Option B — Using Portainer (web interface):**
1. Open Portainer in your browser
2. Go to **Stacks** > **Add stack**
3. Choose **Repository**
4. Enter: `https://github.com/waynehead99/engram`
5. Set the compose file path to `docker-compose.yml`
6. Under **Environment variables**, add:
   - `OPENCLAW_GATEWAY_TOKEN` = your generated token
   - `CLAUDE_CODE_OAUTH_TOKEN` = your Claude token
   - `OPENCLAW_CONFIG_DIR` = `/opt/engram/config`
   - `OPENCLAW_WORKSPACE_DIR` = `/opt/engram/workspace`
7. Click **Deploy the stack**

### Step 6: Verify and Configure

Check that the container started:
```bash
docker logs engram
```

You should see:
```
========================================
  Engram — Personal AI Assistant
========================================
Configuration:
  Config dir:  /home/node/.openclaw
  Workspace:   /home/node/.openclaw/workspace
  Gateway port: 18789
Starting OpenClaw gateway...
```

Open your browser to `http://your-server-ip:18789` — this is the **Control UI** where you'll finish setup.

### Step 7: Connect to the Control UI

When you first open the Control UI, you'll see the **Overview** tab with a **Gateway Access** card. You need to authenticate before you can use any features.

**How the gateway authenticates you:**

OpenClaw uses two layers of security: a **gateway token** (shared secret) and **device pairing** (per-browser/device approval). For a self-hosted Docker deployment, the included config has `allowInsecureAuth` enabled so that token-only authentication works over HTTP without requiring device-level pairing. Your gateway token is the only credential needed.

**To connect:**

1. The **WebSocket URL** should already be filled in (e.g., `ws://your-server-ip:18789`). If not, enter it.
2. Paste your **Gateway Token** (the `OPENCLAW_GATEWAY_TOKEN` from your `.env` file) into the **Gateway Token** field.
3. Click **Connect**.

If the connection succeeds, the status changes to **Connected** and all tabs become active. Your browser stores a device token locally, so you won't need to enter the gateway token again on that browser.

> **Tip:** If you see *"This gateway requires auth"*, double-check that your gateway token matches what's in your `.env` file.

**Enabling strict device pairing (optional):**

If you want each browser/device to be individually approved (more secure, recommended if the gateway is exposed to the internet):

1. Open the **Config** tab in the Control UI
2. Find `gateway.controlUi` and remove `allowInsecureAuth` (or set it to `false`)
3. Save the config
4. New devices will now require approval — their requests appear in the **Nodes** tab
5. Click **Approve** to grant access, or **Reject** to deny

You can manage all paired devices from the **Nodes** tab — rotate tokens, revoke access, or view connection status.

### Step 8: Configure Integrations via the Web UI

Once the gateway is running, you can set up all your integrations through the browser instead of editing files by hand. The Control UI has everything you need:

| Tab | What You Can Do |
|-----|----------------|
| **Config** | Edit all gateway settings (models, Ollama URL, heartbeat schedule, etc.) using a form or raw JSON editor. Sensitive fields like tokens are auto-masked. |
| **Channels** | Set up Slack, Discord, or Telegram connections and enter channel tokens |
| **Skills** | Enable/disable skills and inject API keys (Notion token, Google credentials, etc.) |
| **Sessions** | View and manage active conversations |
| **Cron** | Schedule recurring tasks and heartbeats |
| **Agents** | Manage agent workspaces and identities |
| **Logs** | Live-tail gateway logs for debugging |

**To connect Slack:**
1. Add your `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` to `/opt/engram/config/.env` (see [Slack Setup](#slack-setup-recommended) for how to create these tokens)
2. Enable the Slack channel — either:
   - Open the **Config** tab, find `channels.slack.enabled`, set it to `true`, and save
   - Or from the command line: `sudo sed -i 's/"enabled": false/"enabled": true/' /opt/engram/config/openclaw.json`
3. Restart: `docker restart engram`

> **Note:** Slack is disabled by default to prevent startup errors before tokens are configured. You must enable it after adding your tokens.

**To connect Notion:** Go to the **Skills** tab and inject your `NOTION_API_TOKEN` for the Notion skills. See [Notion Setup](#notion-setup-for-knowledge-management) for how to get this token.

**To connect Google:** Enter your Google credentials via the **Config** tab or the config `.env` file. See [Google Workspace Setup](#google-workspace-setup-for-gmail-and-calendar) for the full OAuth process.

> **Tip:** You can also configure everything by editing `/opt/engram/config/.env` directly if you prefer the command line. The web UI and the config files stay in sync.

### Built-in Diagnostic Tools

If something isn't working, OpenClaw has built-in tools to help:

```bash
# Run the doctor — checks config, connectivity, and offers auto-repair
docker exec -it engram node dist/index.js doctor

# Re-run the setup wizard interactively
docker exec -it engram node dist/index.js configure
```

---

## Integration Setup

Each integration is optional. Engram works with just Claude AI, but gets more powerful with each integration you add.

You can enter tokens and credentials either through the **Control UI** (recommended) or by editing `/opt/engram/config/.env` directly. Both methods work — the UI and config files stay in sync.

### Slack Setup (Recommended)

This lets you talk to Engram via Slack direct messages.

**Create the Slack App:**

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click **Create New App**
2. Choose **From scratch**, name it "Engram", and select your workspace
3. Go to **Socket Mode** and enable it. Create an app-level token with `connections:write` scope. This is your `SLACK_APP_TOKEN` (starts with `xapp-`)
4. Go to **OAuth & Permissions** and add these Bot Token Scopes:
   - `chat:write` — send messages
   - `channels:history` — read channel messages
   - `groups:history` — read private channel messages
   - `im:history` — read direct messages
   - `reactions:read` — see emoji reactions
   - `reactions:write` — add emoji reactions
   - `users:read` — look up user info
5. Go to **Event Subscriptions**, enable events, and subscribe to:
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `reaction_added`
6. Install the app to your workspace
7. Copy the **Bot User OAuth Token** (starts with `xoxb-`). This is your `SLACK_BOT_TOKEN`

**Add to Engram:** Go to the **Channels** tab in the Control UI and enter both tokens, or add them to `/opt/engram/config/.env`.

### Notion Setup (For Knowledge Management)

This lets Engram save and search your personal knowledge base.

**Create the Notion Integration:**

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **New integration**
3. Name it "Engram", select your workspace
4. Under Capabilities, enable: Read content, Update content, Insert content
5. Copy the **Internal Integration Secret** (starts with `ntn_`)

**Share your databases with the integration:**

1. Open each database (Knowledge Base, Projects, Tasks, SOPs) in Notion
2. Click the `...` menu in the top right
3. Click **Connections** > **Connect to** > select "Engram"

**Add to Engram:** Go to the **Skills** tab in the Control UI and inject the Notion token for each Notion skill, or add `NOTION_API_TOKEN` to `/opt/engram/config/.env`.

The default Notion database IDs are configured in `workspace/TOOLS.md`. If you use different databases, update the IDs there.

### Google Workspace Setup (For Gmail and Calendar)

This lets Engram read your email and calendar.

**Create Google OAuth Credentials:**

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (or select an existing one)
3. Go to **APIs & Services** > **Library**
4. Search for and enable: **Gmail API** and **Google Calendar API**
5. Go to **APIs & Services** > **Credentials**
6. Click **Create Credentials** > **OAuth 2.0 Client ID**
7. Choose **Desktop app** as the application type
8. Download the credentials JSON file

**Get a refresh token:**

1. Go to [developers.google.com/oauthplayground](https://developers.google.com/oauthplayground/)
2. Click the gear icon, check "Use your own OAuth credentials"
3. Enter your Client ID and Client Secret
4. In Step 1, select these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events`
5. Click **Authorize APIs** and sign in with your Google account
6. Click **Exchange authorization code for tokens**
7. Copy the **Refresh token**

**Add to Engram:** Add all three values to `/opt/engram/config/.env`:
```
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token
```

Or enter them via the **Config** tab in the Control UI.

### Ollama Setup (For Local Models — Optional)

If you run an Ollama server for local AI models:

1. Make sure Ollama is accessible from your Docker host
2. In the **Config** tab of the Control UI, find the Ollama provider section and update the base URL. Or edit `openclaw.json` directly:
   ```json
   "ollama": {
     "baseUrl": "http://YOUR_OLLAMA_IP:11434/v1"
   }
   ```
3. The default is `host.docker.internal:11434` which works if Ollama runs on the same machine as Docker (macOS/Windows). On Linux, use your host's LAN IP address.

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────┐
│                Docker Container                  │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │         OpenClaw Gateway                  │   │
│  │    (Node.js — manages conversations)      │   │
│  ├──────────────────────────────────────────┤   │
│  │         Claude Code CLI                   │   │
│  │    (AI backend — claude-cli/opus)         │   │
│  ├──────────────────────────────────────────┤   │
│  │         Python Runtime                    │   │
│  │    (Gmail, Calendar, MCP scripts)         │   │
│  └──────────────────────────────────────────┘   │
│       │           │           │          │       │
└───────│───────────│───────────│──────────│───────┘
        │           │           │          │
   ┌────▼────┐ ┌────▼────┐ ┌───▼───┐ ┌───▼────┐
   │  Slack  │ │ Notion  │ │Google │ │Ollama  │
   │  (DMs)  │ │  (KB)   │ │(Mail) │ │(Local) │
   └─────────┘ └─────────┘ └───────┘ └────────┘
```

### Key Concepts

- **Gateway**: The web server that runs inside Docker. It handles Slack messages, serves the web UI, and coordinates everything.
- **Workspace**: The agent's "brain" — personality files, skills, and memory. Stored at `/opt/engram/workspace/` on your server.
- **Config**: Gateway settings and secret tokens. Stored at `/opt/engram/config/` on your server.
- **Skills**: Modular capabilities (Notion, Gmail, etc.) that extend what Engram can do. Bundled in `workspace/skills/`.
- **Memory**: Engram saves important conversation details to local files, then syncs them to Notion for permanent storage.
- **Heartbeat**: Every 30 minutes (during active hours 7am-10pm), Engram checks email, calendar, and tasks to proactively notify you of important things.

### File Structure

```
engram/
├── Dockerfile              # How to build the container image
├── docker-compose.yml      # How to run the container (Portainer stack)
├── entrypoint.sh           # Startup script (validates config, starts gateway)
├── .env.example            # Template for Docker Compose variables
├── openclaw.json           # Gateway configuration (models, Slack, skills, etc.)
├── config/
│   └── .env.example        # Template for app secrets (Slack, Google, Notion)
├── workspace/
│   ├── IDENTITY.md         # Engram's name and personality summary
│   ├── SOUL.md             # Detailed personality and communication style
│   ├── USER.md             # Your profile (name, timezone, context)
│   ├── HEARTBEAT.md        # What Engram checks during periodic heartbeats
│   ├── AGENTS.md           # Agent behavior guidelines
│   ├── TOOLS.md            # Notion DB IDs and tool workflows
│   └── skills/             # All skill modules (see Skills section)
└── agents/
    └── main/agent/
        └── models.json     # Ollama model definitions
```

---

## Skills Reference

Each skill is a self-contained module in `workspace/skills/`. Here's what each one needs to work:

### Notion Knowledge Capture
- **Needs:** Notion API token
- **What it does:** When you say "save this" or "remember this", it creates a categorized entry in your Notion Knowledge Base
- **Auto-categories:** Dev, Research, Meetings, Personal

### Notion Project Manager
- **Needs:** Notion API token + Projects and Tasks databases in Notion
- **What it does:** Creates projects, tracks tasks, runs weekly reviews
- **Trigger phrases:** "create a project", "add a task", "what's on my plate", "weekly review"

### Notion RAG (Search & Retrieve)
- **Needs:** Notion API token
- **What it does:** Searches your Notion notes to answer questions from your own knowledge
- **Trigger phrases:** "what do I know about...", "search my notes", "find in my brain"

### Notion Memory Sync
- **Needs:** Notion API token
- **What it does:** Automatically syncs conversation memories from local files to Notion
- **Runs during:** Heartbeat cycles (every 30 min)

### SOP Creator
- **Needs:** Notion API token
- **What it does:** Creates professional documentation (runbooks, checklists, how-to guides) and saves to Notion
- **Trigger phrases:** "create a runbook for...", "document this process", "write a playbook"

### Google Workspace
- **Needs:** Google Client ID, Client Secret, and Refresh Token
- **What it does:** Reads Gmail inbox, sends emails, views calendar, creates events
- **Safety:** Always asks for confirmation before sending emails or creating events

### MCP Client
- **Needs:** Configuration for each MCP server you want to use (API keys, etc.)
- **What it does:** Connects to external tool servers like Zapier, GitHub, etc.
- **Setup:** Add MCP server configs to a `mcp-config.json` file in the workspace

### Skill Creator
- **Needs:** Nothing extra (uses Python, which is already installed)
- **What it does:** Helps you create new skills to extend Engram's capabilities
- **For developers:** Includes templates, validators, and packaging tools

---

## Customization

### Changing Engram's Personality

Edit the files in your workspace directory (`/opt/engram/workspace/`):

- `IDENTITY.md` — Name, emoji, and one-line description
- `SOUL.md` — Detailed personality, communication style, and values
- `USER.md` — Your name, timezone, and personal context

You can also manage workspace files through the **Agents** tab in the Control UI.

### Changing the AI Model

Open the **Config** tab in the Control UI, or edit `openclaw.json` in your config directory. The `agents.defaults.model` section controls which Claude model is used:

```json
"model": {
  "primary": "claude-cli/opus",
  "fallbacks": ["claude-cli/sonnet"]
}
```

### Adding New Skills

1. Create a new directory in `/opt/engram/workspace/skills/your-skill-name/`
2. Add a `SKILL.md` file with YAML frontmatter (name, description) and instructions
3. Engram will auto-detect it (skill watching is enabled)

You can manage skills and their API keys through the **Skills** tab in the Control UI.

---

## Maintenance

### Viewing Logs

```bash
docker logs engram          # Recent logs
docker logs -f engram       # Follow logs in real time
```

Or use the **Logs** tab in the Control UI for live log tailing in your browser.

### Running Diagnostics

```bash
# Doctor checks config, connectivity, and can auto-repair issues
docker exec -it engram node dist/index.js doctor

# Re-run the interactive setup wizard
docker exec -it engram node dist/index.js configure
```

### Restarting

```bash
docker compose restart      # Restart the container
```

### Updating

```bash
git pull                    # Get latest code
docker compose build        # Rebuild the image
docker compose up -d        # Restart with new image
```

### Backing Up

```bash
# Back up your config and workspace
sudo tar czf engram-backup-$(date +%Y%m%d).tar.gz /opt/engram/
```

---

## Troubleshooting

### Container won't start
- Check logs: `docker logs engram`
- Verify `.env` file exists and has all required values
- Verify `/opt/engram/config/openclaw.json` exists
- Check permissions: `ls -la /opt/engram/` (should be owned by UID 1000)

### "OPENCLAW_GATEWAY_TOKEN is not set"
- Make sure your `.env` file is in the same directory as `docker-compose.yml`
- Make sure the token value is filled in (not blank)

### "CLAUDE_CODE_OAUTH_TOKEN is not set"
- Run `claude setup-token` on your Mac to generate a new token
- Token is valid for ~1 year, then needs to be regenerated

### Slack not connecting
- Verify `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` are in `/opt/engram/config/.env`
- Make sure Socket Mode is enabled in your Slack app settings
- Check that Event Subscriptions are configured

### Gmail/Calendar not working
- Verify all three Google credentials are in `/opt/engram/config/.env`
- Make sure the Gmail API and Calendar API are enabled in Google Cloud Console
- Refresh tokens can expire — regenerate if needed

### Notion not connecting
- Verify `NOTION_API_TOKEN` is in `/opt/engram/config/.env`
- Make sure you've shared each database with the Engram integration in Notion
- Check that the database IDs in `workspace/TOOLS.md` match your actual databases

### Health check failing
- The gateway needs ~15 seconds to start up
- If it keeps failing: `docker logs engram` to see the actual error
- Check that port 18789 isn't already in use on your server

---

## License

MIT
