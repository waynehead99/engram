# Google Workspace Workflows

## Morning Briefing

A combined email + calendar overview to start the day.

### Steps
1. **Check unread emails**
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gmail.py inbox '{"max": 10, "unread_only": true}'
   ```
2. **Check today's calendar**
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gcalendar.py today
   ```
3. **Synthesize report**
   - Unread email count and top senders
   - Today's meetings with times
   - Flag anything urgent (emails from key contacts, imminent meetings)

### Example Output
```
Morning Briefing — Feb 11, 2026

Email: 5 unread messages
  - From boss@company.com: "Q1 Review" (unread)
  - From client@example.com: "Project Update" (unread)
  - 3 other unread messages

Calendar: 3 events today
  - 9:00 AM — Daily Standup (30 min)
  - 11:00 AM — 1:1 with Manager (30 min)
  - 2:00 PM — Sprint Planning (1 hr)

Action items: Review Q1 email before 11:00 AM 1:1
```

## Email Triage

Process and categorize unread emails efficiently.

### Steps
1. **Fetch unread inbox**
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gmail.py inbox '{"max": 20, "unread_only": true}'
   ```
2. **Categorize by priority**
   - Urgent: From known important contacts, time-sensitive subjects
   - Normal: Regular communications, newsletters
   - Low: Notifications, automated messages
3. **For urgent emails, read full content**
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gmail.py read '{"id": "msg_id"}'
   ```
4. **Suggest actions** for each email:
   - Reply needed (draft a response)
   - Follow up later (note the deadline)
   - Archive (no action needed)
   - Forward to someone else

## Scheduling Assistant

Help find time and create calendar events.

### Find Available Time
1. **Check upcoming schedule**
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gcalendar.py upcoming '{"days": 5}'
   ```
2. **Identify open slots** based on working hours (9 AM - 5 PM CT)
3. **Suggest times** that avoid conflicts

### Create Event
1. **Confirm details** with user: summary, date/time, attendees, location
2. **Check for conflicts** at the proposed time
3. **Create the event**
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gcalendar.py create '{"summary": "Team Sync", "start": "2026-02-12T10:00:00-06:00", "end": "2026-02-12T10:30:00-06:00", "attendees": ["colleague@company.com"]}'
   ```
4. **Confirm creation** and share the calendar link

## Email Search & Research

Find specific emails or conversation threads.

### Steps
1. **Search with specific criteria**
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gmail.py search '{"query": "from:client subject:invoice after:2026/01/01", "max": 10}'
   ```
2. **Read relevant messages**
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gmail.py read '{"id": "msg_id"}'
   ```
3. **Summarize findings** with key dates, amounts, action items

### Common Search Queries
- Recent from someone: `from:name after:2026/02/01`
- Unread important: `is:unread label:important`
- With attachments: `has:attachment from:name`
- Specific topic: `subject:keyword OR body:keyword`

## Reply Workflow

Draft and send a reply with review.

### Steps
1. **Read the original message**
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gmail.py read '{"id": "msg_id"}'
   ```
2. **Draft reply** based on context and user instructions
3. **Present draft for review** — show the complete reply text
4. **After user confirms**, send the reply
   ```bash
   python3 ~/.openclaw/workspace/skills/google-workspace/scripts/gmail.py reply '{"id": "msg_id", "body": "..."}'
   ```
