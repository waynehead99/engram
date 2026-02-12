---
name: notion-knowledge-capture
description: |
  Capture and organize knowledge into the Notion Second Brain knowledge base.
  Auto-categorizes content and extracts tags for easy retrieval.

  TRIGGERS - Use this skill when user says:
  - "save this to my brain" / "capture this note" / "add to knowledge base"
  - "remember this" / "note this down" / "save this"
  - "TIL" / "today I learned"
  - "meeting notes for..." / "capture meeting notes"
  - "save this article" / "bookmark this"
  - "code snippet" / "save this code"
  - Any request to store, save, or capture information for later
---

# Notion Knowledge Capture

## How It Works

1. Determine the content type (quick note, article summary, meeting notes, code snippet, TIL)
2. Auto-categorize into one of: Dev, Research, Meetings, Personal
3. Extract relevant tags from the content
4. Search for the "Knowledge Base" database in Notion using `notion-search`
5. Create a page in the database using `notion-create-pages`

## Database Properties

When creating a page, set these properties:
- **Title**: Clear, descriptive title for the entry
- **Category**: One of Dev, Research, Meetings, Personal (see references/categories.md for classification rules)
- **Tags**: Relevant tags extracted from content (multi_select)
- **Source**: URL if applicable
- **Status**: "Inbox" for new captures (user can process later)

## Content Type Workflows

### Quick Note
Simplest capture. Title + body. Minimal formatting needed.

### Article Summary
Extract: title, source URL, 3-5 key takeaways, relevant tags.

### Meeting Notes
Structure: title (Meeting: [topic] - [date]), attendees, agenda items, key decisions, action items.

### Code Snippet
Structure: title, language tag, code block, explanation of what it does and when to use it.

### TIL (Today I Learned)
Structure: title (TIL: [topic]), what was learned, context/source, tags.

## Auto-Classification

See references/categories.md for detailed classification rules. Quick guide:
- **Dev**: code, programming, architecture, debugging, deployment, APIs, tools
- **Research**: articles, papers, tutorials, courses, books, concepts, learning
- **Meetings**: meeting notes, decisions, action items, stakeholder discussions
- **Personal**: goals, journal, health, habits, ideas, personal projects

## Tag Extraction

Extract 2-5 tags from the content. Use existing tags when possible (search with notion-search first). Tags should be specific enough to be useful but general enough to group related items.

## Important Notes

- Always search for the Knowledge Base database first using notion-search
- If the user doesn't specify a category, classify it automatically based on content
- If the user provides a URL, set the Source property
- Default Status to "Inbox" — the user processes entries later
- Keep page content in Notion-flavored markdown format
- For meeting notes, always ask for attendees and action items if not provided

## References

- See references/categories.md for detailed category definitions and auto-classification rules
- See references/capture-templates.md for content type templates
