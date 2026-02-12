# Search Strategies

## Query Decomposition

For complex questions, break into sub-queries:

**User asks:** "What approaches have I explored for improving API performance?"
**Sub-queries:**
1. "API performance" — find direct matches
2. "caching" — related optimization technique
3. "database optimization" — related area
4. "performance" in Projects — any active performance projects

## Filter Combinations

### By Category
Use when user specifies a domain:
- "dev notes about X" → search with scope to Knowledge Base Category=Dev
- "meeting where we discussed X" → scope to Category=Meetings

### By Date Range
Use when user asks about recent or time-specific items:
- "what did I learn last week" → filter to past 7 days
- "notes from January" → filter to date range

### By Database
Use when the type of content is clear:
- Process/procedure questions → search SOPs database
- Task/project questions → search Projects/Tasks databases
- Knowledge/learning questions → search Knowledge Base

## Result Ranking

When multiple results are returned, prioritize by:
1. **Direct keyword match** in title (strongest signal)
2. **Recency** — more recently edited pages are often more relevant
3. **Category match** — if user specified a domain, same-category results rank higher
4. **Content depth** — longer, more detailed pages over brief stubs

## Cross-Reference Patterns

### Knowledge → Projects
After finding knowledge entries, check:
- Are there projects in the same area?
- Are there tasks tagged with related topics?

### Projects → Tasks
When asked about a project:
- Fetch the project page
- Search for tasks linked to that project
- Provide a status summary

### SOPs → Knowledge
When an SOP references a concept:
- Look up related knowledge entries for context

## Citation Format

Always use this format for sources:

**Sources from your Second Brain:**
- [Page Title](notion-url) — what this page contributed to the answer
- [Page Title](notion-url) — what this page contributed

If no relevant sources found:
"No matching entries found in your Second Brain for [topic]."
