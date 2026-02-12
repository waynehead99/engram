---
name: notion-project-manager
description: |
  Manage projects and tasks in the Notion Second Brain workspace.
  Create projects, add tasks, track progress, and run status reviews.

  TRIGGERS - Use this skill when user says:
  - "create a project" / "new project" / "start a project"
  - "add a task" / "create a task" / "new task"
  - "what's on my plate" / "show my tasks" / "task list"
  - "update project status" / "mark task as done" / "complete task"
  - "what's overdue" / "what's due this week"
  - "weekly review" / "project status" / "sprint review"
  - Any request to create, update, query, or review projects and tasks
---

# Notion Project Manager

## How It Works

1. Identify the operation: create, query, update, or review
2. Search for the relevant database (Projects or Tasks) using `notion-search`
3. Execute the operation using the appropriate Notion MCP tool
4. Report results clearly

## Database Schemas

### Projects Database
| Property | Type | Options |
|----------|------|---------|
| Title | title | — |
| Status | select | Planning, Active, On Hold, Done, Archived |
| Priority | select | P0 (critical), P1 (high), P2 (medium), P3 (low) |
| Area | select | Work, Personal, Learning |
| Start Date | date | — |
| Target Date | date | — |
| Description | rich_text | — |

### Tasks Database
| Property | Type | Options |
|----------|------|---------|
| Title | title | — |
| Status | select | To Do, In Progress, Blocked, Done |
| Priority | select | P0, P1, P2, P3 |
| Due Date | date | — |
| Project | relation | → Projects database |
| Effort | select | S (< 1hr), M (1-4hrs), L (4-8hrs), XL (> 1 day) |
| Tags | multi_select | — |

## Operations

### Create Project
1. Search for "Projects" database with notion-search
2. Create page with notion-create-pages
3. Set Status to "Planning", set Priority and Area
4. Ask user for: title, description, priority, area, target date
5. Offer to create initial tasks for the project

### Create Task
1. Search for "Tasks" database with notion-search
2. If linking to a project, also search "Projects" to find the project page ID
3. Create page with notion-create-pages
4. Set Status to "To Do"
5. Ask user for: title, priority, due date, effort estimate
6. If project context is clear from conversation, auto-link it

### Query Tasks
1. Search with notion-search using relevant keywords
2. Fetch results with notion-fetch for details
3. Present as a formatted summary table:
   | Task | Status | Priority | Due | Project |
4. Highlight overdue tasks
5. Support filters: by status, priority, project, due date

### Update Status
1. Find the task/project with notion-search
2. Use notion-update-page to update the Status property
3. Confirm the update to the user

### Weekly Review
See references/workflows.md for the full weekly review workflow.

Summary:
1. Query overdue tasks
2. Query tasks due this week
3. Query active projects status
4. Present a review summary
5. Ask user to update stale items

## Priority Guide

| Level | Meaning | Response Time |
|-------|---------|---------------|
| P0 | Critical/blocking | Same day |
| P1 | High importance | This week |
| P2 | Medium, planned | This sprint/month |
| P3 | Low, nice-to-have | When possible |

## Important Notes

- Always search for the database first using notion-search before creating/querying
- When creating tasks, try to link them to a project if context suggests one
- Default new tasks to "To Do" status and new projects to "Planning"
- For queries, present results in clean formatted tables
- Highlight overdue items prominently
- When user says "done" or "complete" for a task, update status to "Done"

## References

- See references/workflows.md for detailed PM workflows
