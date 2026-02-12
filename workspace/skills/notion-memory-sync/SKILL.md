---
name: notion-memory-sync
description: |
  Sync local memory files to the Notion Knowledge Base.
  Reads memory files from the memory/ directory, checks which ones haven't been synced yet,
  and creates corresponding entries in the Notion Knowledge Base database.

  TRIGGERS - Use this skill when user says:
  - "sync my memories" / "sync memories to Notion"
  - "push memories to Notion" / "upload memories"
  - "memory sync" / "sync memory files"
  - Any request to synchronize local memory files with Notion
---

# Notion Memory Sync

Sync local memory files from `memory/` to the Notion Knowledge Base.

## How It Works

1. List all files in the `memory/` directory
2. Read each file and check for the `<!-- synced -->` marker
3. For unsynced files, create a Knowledge Base entry in Notion
4. Mark synced files with `<!-- synced -->` appended to the file

## Step-by-Step

### 1. Find Unsynced Files

Read all `.md` files in `~/.openclaw/workspace/memory/`. Check each file's content for the presence of `<!-- synced -->` at the end. Files without this marker are unsynced.

Also check for `<!-- unsynced -->` which is added by the memory flush system — treat these the same as files with no marker.

### 2. Process Each Unsynced File

For each unsynced file:

1. **Read the full content**
2. **Generate a title**: `Memory: [date from filename] - [brief summary of content]`
3. **Auto-classify category**: Based on content (Dev, Research, Meetings, Personal)
4. **Extract tags**: 2-5 relevant tags from the content
5. **Create Notion page** using `notion-create-pages`:

```
parent: { data_source_id: "bd4e2fa5-c6ba-4597-bc3a-6b1485b844a6" }
properties:
  Title: "Memory: YYYY-MM-DD - [summary]"
  Category: [auto-classified]
  Tags: [extracted tags]
  Status: "Done"
content: [file content, cleaned up — remove the unsynced marker]
```

6. **Mark as synced**: Replace `<!-- unsynced -->` with `<!-- synced -->` or append `<!-- synced -->` to the end of the file

### 3. Report Results

After processing, report:
- How many files were found
- How many were already synced
- How many were newly synced
- Any errors encountered

## Important Notes

- Use data_source_id `bd4e2fa5-c6ba-4597-bc3a-6b1485b844a6` for Knowledge Base
- Always set Status to "Done" — synced memories are already processed
- Clean up the `<!-- unsynced -->` marker from content before sending to Notion
- If a file has no meaningful content, skip it and note it in the report
- If no unsynced files exist, report "All memory files are already synced"
