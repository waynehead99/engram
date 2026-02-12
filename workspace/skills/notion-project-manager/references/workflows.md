# Project Management Workflows

## Project Kickoff

When creating a new project:

1. Create the project page in the Projects database
   - Set Status: Planning
   - Set Priority, Area, Start Date, Target Date
2. Ask the user to define initial milestones or phases
3. Break milestones into concrete tasks
4. Create all tasks in the Tasks database linked to the project
5. Set task priorities and due dates
6. Update project Status to "Active" once tasks are created

## Weekly Review

Run this workflow when user asks for a weekly review:

1. **Overdue Check**
   - Search Tasks database for items past due date with status != Done
   - Present overdue items with how many days overdue
   - Ask user: reschedule, complete, or escalate each one

2. **This Week's Focus**
   - Search Tasks due in the next 7 days
   - Present by priority (P0 first)
   - Confirm the user's plan for each

3. **Active Projects Status**
   - Fetch all projects with Status = Active
   - For each, summarize: total tasks, done tasks, blocked tasks
   - Flag projects with no recent activity or all tasks blocked

4. **Inbox Processing**
   - Search Tasks with Status = To Do and no due date
   - Ask user to prioritize and schedule or defer each one

5. **Summary**
   - Provide a concise weekly summary:
     - X tasks completed this week
     - Y tasks overdue
     - Z tasks due next week
     - Active projects health check

## Task Triage

When user has many unprioritized tasks:

1. Fetch all tasks with Status = To Do
2. Group by project
3. For each task, suggest a priority based on:
   - Project priority (inherit from parent)
   - Due date proximity
   - User's stated goals
4. Present recommendations and let user confirm/adjust

## Project Closeout

When all tasks in a project are done:

1. Verify all linked tasks have Status = Done
2. Update project Status to "Done"
3. Ask user for a brief retrospective note (add to project page content)
4. Offer to archive the project (Status → Archived)
