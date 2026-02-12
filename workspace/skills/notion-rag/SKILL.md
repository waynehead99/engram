---
name: notion-rag
description: |
  Search and retrieve knowledge from the Notion Second Brain workspace.
  Synthesize answers from your personal knowledge base with source citations.

  TRIGGERS - Use this skill when user says:
  - "search my notes" / "search my brain" / "search my knowledge base"
  - "what do I know about..." / "what have I written about..."
  - "find in my brain" / "find in my notes"
  - "recall" / "look up" / "pull up notes on"
  - "what did I learn about..." / "when did I..."
  - "summarize my notes on..." / "gather everything about..."
  - Any question that should be answered from the user's own stored knowledge
---

# Notion RAG

Search your Second Brain and synthesize answers from your own knowledge base.

## How It Works

1. Parse the user's query to identify search terms and intent
2. Search the Notion workspace using `notion-search` (semantic search)
3. Fetch full content of the top relevant results using `notion-fetch`
4. Synthesize an answer from the retrieved content
5. Always cite sources with page titles and Notion URLs

## Search Workflow

### Step 1: Query Analysis
Break the user's question into:
- **Primary keywords**: the core topic
- **Scope**: which databases to search (Knowledge Base, Projects, Tasks, SOPs, or all)
- **Filters**: date ranges, categories, tags if mentioned

### Step 2: Search
Use `notion-search` with the primary keywords.

If the initial search is too broad:
- Add category or date filters
- Try more specific keyword combinations
- Search within a specific database URL using the `data_source_url` parameter

If the initial search returns nothing:
- Try broader/related keywords
- Remove filters and search across all databases
- Try individual words from the query

### Step 3: Fetch Content
For the top 3-5 most relevant results:
- Use `notion-fetch` to get the full page content
- Scan content for relevance to the original question
- Discard results that are not actually relevant (search can return false positives)

### Step 4: Synthesize
Compose an answer that:
- Directly addresses the user's question
- Draws from the content of multiple pages when relevant
- Distinguishes between what your notes say vs. general knowledge
- Is honest about gaps ("your notes don't cover X specifically")

### Step 5: Cite Sources
Every response MUST include a Sources section at the end:

```
**Sources from your Second Brain:**
- [Page Title](notion-url) — brief note on what this page contributed
- [Page Title](notion-url) — brief note
```

## Scoped Searches

When the user specifies a scope, constrain the search:
- "in my dev notes" → filter to Knowledge Base, Category = Dev
- "in my projects" → search Projects database
- "in my tasks" → search Tasks database
- "in my SOPs" → search SOPs database
- "from last month" → use date range filters

## Cross-Referencing

When answering a knowledge question, also check for related:
- **Tasks**: Are there active tasks related to this topic?
- **Projects**: Is there an active project in this area?
- **SOPs**: Is there a documented process for this?

Mention related items briefly: "You also have an active project 'X' related to this topic."

## When No Results Are Found

If the search returns nothing relevant:
1. Tell the user clearly: "I didn't find anything in your Second Brain about [topic]"
2. Suggest: "Would you like me to capture some notes on this topic?"
3. Offer to search with broader terms

## Important Notes

- ALWAYS include source citations — never synthesize without attribution
- Distinguish between "your notes say" and "I know that" (general knowledge)
- Prefer recent/updated pages over old ones when content conflicts
- Keep synthesized answers concise — point to the full pages for details
- If the user asks a question you CAN answer from general knowledge but ALSO have notes on, lead with the notes and supplement with general knowledge

## References

- See references/search-strategies.md for advanced search patterns
