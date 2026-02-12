# Tools & Workflows

Environment-specific configuration and workflow guides.

## Notion Database IDs

Use these data_source_ids when creating pages with `notion-create-pages`:

| Database | data_source_id |
|----------|----------------|
| Knowledge Base | `bd4e2fa5-c6ba-4597-bc3a-6b1485b844a6` |
| Projects | `ff911b7a-6b10-465a-ad4e-eea1448cddb3` |
| Tasks | `50d83065-e4eb-40da-aea7-1d287065e1cd` |
| SOPs | `63f2de7e-e872-428d-a2bf-8d7e100cee7a` |

Second Brain root page ID: `305ea7f3-418a-8182-94cd-e6fb078fd23d`

## Memory Capture Workflow

### When to save to Notion immediately
- Key decisions or conclusions from a conversation
- New learnings (TILs, debugging solutions, architecture insights)
- Meeting notes or action items
- Information the user explicitly asks to remember
- Project context that will matter across sessions

### When local memory is enough
- Routine session context (auto-captured by memory flush)
- Intermediate working state
- Temporary scratch notes
- Raw conversation history

### How to save to Notion
1. Determine content type and category (Dev, Research, Meetings, Personal)
2. Extract 2-5 relevant tags
3. Create page in Knowledge Base:
```
notion-create-pages with:
  parent: { data_source_id: "bd4e2fa5-c6ba-4597-bc3a-6b1485b844a6" }
  properties: { Title, Category, Tags, Status: "Done" }
  content: formatted markdown
```

## Memory Recall Workflow

### For broad knowledge questions
1. Search Notion with `notion-search` using relevant keywords
2. Fetch top results with `notion-fetch` for full content
3. Synthesize answer with source citations

### For recent session context
1. Use `memory_search` tool for fast local search
2. Check `memory/` directory files if needed

### Combined approach (default)
1. Start with `notion-search` for authoritative knowledge
2. Supplement with `memory_search` for recent context
3. Combine both sources in the response

## Knowledge Base Entry Format

**Title conventions:**
- Quick note: Descriptive title
- TIL: `TIL: [topic]`
- Meeting: `Meeting: [topic] - [date]`
- Article: Article title
- Code snippet: What the code does
- Memory sync: `Memory: [date] - [brief summary]`

**Content structure:**
- Use markdown headings for organization
- Include context for why this matters
- Add code blocks for technical content
- Keep entries focused — one topic per entry
