# Heartbeat Tasks

When a heartbeat fires, check these in order. Only report items that need attention. If nothing needs attention, reply HEARTBEAT_OK.

## 1. Daily Standup (morning heartbeats, 7:00-9:00)
- Check the Notion Tasks database for overdue or due-today tasks
- Check the Notion Projects database for active projects with approaching target dates
- Summarize what's on the plate for today

## 2. Memory Sync (all heartbeats)
- Check the `memory/` directory for memory files
- For each file, check if it contains the `<!-- synced -->` marker
- For unsynced files: read content, create a Knowledge Base entry in Notion using `notion-create-pages` with data_source_id `bd4e2fa5-c6ba-4597-bc3a-6b1485b844a6`
  - Title: Use the filename date + a brief summary of the content
  - Category: Auto-classify based on content (Dev, Research, Meetings, Personal)
  - Tags: Extract relevant tags
  - Status: Done (these are processed memories, not inbox items)
- After successful Notion sync, append `<!-- synced -->` to the local file
- If no unsynced files exist, skip silently

## 3. Inbox Processing (all heartbeats)
- Check if there are unprocessed items in the Knowledge Base with Status: Inbox
- If any exist, flag them for categorization

## 4. Project Health (afternoon heartbeats, 14:00-16:00)
- Check for projects with Status: Active that have no recent task updates
- Flag blocked tasks that haven't been updated
- Note any tasks that have been In Progress for more than 3 days

## 5. Learning Reminders (evening heartbeats, 18:00-20:00)
- Check for recent Knowledge Base entries tagged with "review" or "learn"
- Suggest one item for review if available

## Rules
- Be brief. Heartbeat reports should be 2-5 bullet points max.
- Don't repeat yesterday's report. Check what's actually changed.
- If everything looks fine, just reply HEARTBEAT_OK.
- Use the Notion MCP tools to query databases — don't guess or assume.
