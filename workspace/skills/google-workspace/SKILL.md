---
name: google-workspace
description: |
  Read and manage Gmail and Google Calendar.
  Search emails, read messages, send replies, check schedule, create events.

  TRIGGERS - Use this skill when user says:
  - "check my email" / "any new emails" / "read my inbox"
  - "search email for..." / "find email from..."
  - "send an email to..." / "reply to that email"
  - "what's on my calendar" / "schedule for today"
  - "any meetings today" / "what's coming up this week"
  - "schedule a meeting" / "create an event"
  - "morning briefing" (email + calendar combined)
---

# Google Workspace Skill

## Script Paths

All scripts are at: `~/.openclaw/workspace/skills/google-workspace/scripts/`

```
GMAIL=~/.openclaw/workspace/skills/google-workspace/scripts/gmail.py
CALENDAR=~/.openclaw/workspace/skills/google-workspace/scripts/gcalendar.py
```

## Gmail Commands

```bash
python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gmail.py <command> '<json_args>'
```

| Command | Args | Description |
|---------|------|-------------|
| `inbox` | `{"max": 10, "unread_only": true}` | List recent inbox messages |
| `search` | `{"query": "from:boss subject:review", "max": 10}` | Search with Gmail query syntax |
| `read` | `{"id": "msg_id"}` | Read full message (headers + body) |
| `send` | `{"to": "...", "subject": "...", "body": "..."}` | Send a new email |
| `reply` | `{"id": "msg_id", "body": "..."}` | Reply to a message (preserves thread) |

### Gmail Query Syntax (for search)
- `is:unread` — unread messages
- `from:name` — from a specific sender
- `to:name` — sent to someone
- `subject:keyword` — subject contains keyword
- `has:attachment` — has attachments
- `after:2026/01/01` — after a date
- `label:important` — specific label
- Combine: `from:boss is:unread after:2026/02/01`

## Calendar Commands

```bash
python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gcalendar.py <command> '<json_args>'
```

| Command | Args | Description |
|---------|------|-------------|
| `today` | `{}` | List today's events |
| `upcoming` | `{"days": 7}` | List events in the next N days |
| `search` | `{"query": "standup", "days": 30}` | Search events by text |
| `create` | `{"summary": "...", "start": "...", "end": "...", ...}` | Create a calendar event |

### Create Event Args
- **Required**: `summary`, `start`, `end`
- **Optional**: `location`, `description`, `attendees` (list of emails)
- **Time format**: ISO 8601 with timezone (`2026-02-11T14:00:00-06:00`) or date-only for all-day events (`2026-02-11`)

## Workflows

### Morning Briefing
1. Check unread emails: `gmail.py inbox '{"max": 10, "unread_only": true}'`
2. Check today's schedule: `gcalendar.py today`
3. Summarize: unread count, important senders, today's meetings

### Email Triage
1. Fetch inbox: `gmail.py inbox '{"max": 20, "unread_only": true}'`
2. For each important email, read full content: `gmail.py read '{"id": "..."}'`
3. Summarize and suggest actions (reply, archive, follow up)

### Schedule a Meeting
1. Check availability: `gcalendar.py upcoming '{"days": 3}'`
2. Find open slots
3. Create event: `gcalendar.py create '{"summary": "...", "start": "...", "end": "..."}'`

## Safety Rules

- **Always confirm before sending**: Show the draft email (to, subject, body) and ask for explicit confirmation before calling `send` or `reply`.
- **Always confirm before creating events**: Show event details and ask for confirmation before calling `create`.
- **Never auto-send**: Even if the user says "send an email to X", compose the draft first and present it for review.
- **Sensitive content**: Flag emails that appear to contain sensitive information (financial, legal, personal) before taking action.
