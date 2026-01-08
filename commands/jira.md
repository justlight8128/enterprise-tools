---
description: Search, create, and manage Jira issues
---

# Jira CLI

Use jira-cli to interact with Jira. The CLI is available at `~/bin/jira-cli` or full path `~/.claude/plugins/marketplaces/enterprise-tools-marketplace/scripts/api/jira-cli.py`.

## Quick Reference

### Search Issues
```bash
jira-cli search --jql "assignee = currentUser() ORDER BY updated DESC" --max-results 10
```

### Common JQL Patterns
```bash
# My open issues
jira-cli search --jql "assignee = currentUser() AND status != Done"

# Project issues
jira-cli search --jql "project = PROJECT_KEY ORDER BY created DESC"

# Sprint issues
jira-cli search --jql "sprint in openSprints()"

# High priority
jira-cli search --jql "priority in (Highest, High) AND status != Done"

# Epic and child issues
jira-cli search --jql "parent = EPIC-KEY ORDER BY created DESC"

# Issues by specific user
jira-cli search --jql "assignee = 'username' AND status != Done"
```

### Get Issue Details
```bash
jira-cli get --issue PROJ-123
jira-cli get --issue PROJ-123 --format full
```

### Create Issue
```bash
# Basic creation
jira-cli create --project PROJ --type Task --summary "Issue title" --description "Details here"

# With labels
jira-cli create --project PROJ --type Bug --summary "Bug title" --labels "bug,urgent"

# With assignee (by name or email)
jira-cli create --project PROJ --type Task --summary "Issue title" --assignee "John Doe"

# With epic link
jira-cli create --project PROJ --type Task --summary "Issue title" --epic PROJ-100

# Full example with all options
jira-cli create --project PROJ --type Task --summary "Issue title" --description "Details" --assignee "John" --epic PROJ-100 --labels "feature,v2"
```

### Update Issue
```bash
# Transition to new status
jira-cli update --issue PROJ-123 --transition "In Progress"
jira-cli update --issue PROJ-123 --transition "Done" --comment "Completed!"

# Add comment
jira-cli update --issue PROJ-123 --comment "This is my comment"

# Change assignee
jira-cli update --issue PROJ-123 --assignee "Jane Doe"

# Update summary
jira-cli update --issue PROJ-123 --summary "New title"

# Multiple updates at once
jira-cli update --issue PROJ-123 --assignee "Jane" --comment "Reassigned"
```

### Assign Issues
```bash
# Assign to user (by name or email)
jira-cli assign --issue PROJ-123 --user "John Doe"
jira-cli assign --issue PROJ-123 --user "john@example.com"

# Unassign
jira-cli assign --issue PROJ-123 --user none
```

### Link to Epic
```bash
# Link existing issue to epic
jira-cli link-epic --issue PROJ-123 --epic PROJ-100
```

### Set Dates (Start/Due)
```bash
# Set start date only
jira-cli dates --issue PROJ-123 --start 2026-01-08

# Set due date only
jira-cli dates --issue PROJ-123 --due 2026-01-15

# Set both dates
jira-cli dates --issue PROJ-123 --start 2026-01-08 --due 2026-01-15
```

### Unresolve Issue (Clear Resolution)
```bash
# Reopen a resolved/completed issue (removes from "Done" and shows in backlog)
jira-cli unresolve --issue PROJ-123
```

### View Comments
```bash
jira-cli comments --issue PROJ-123
jira-cli comments --issue PROJ-123 --max-results 50
```

### Manage Labels
```bash
# Add labels
jira-cli labels --issue PROJ-123 --add "bug,urgent"

# Remove labels
jira-cli labels --issue PROJ-123 --remove "wontfix"

# Add and remove at once
jira-cli labels --issue PROJ-123 --add "priority" --remove "backlog"
```

### Set Priority
```bash
# List available priorities
jira-cli priority

# Set priority
jira-cli priority --issue PROJ-123 --set High
```

### Link Issues
```bash
# List available link types
jira-cli link --list-types

# Link two issues
jira-cli link --from PROJ-123 --to PROJ-456 --type "Blocks"
jira-cli link --from PROJ-123 --to PROJ-456 --type "Relates"
```

### Sprints Management
```bash
# List all boards
jira-cli boards

# List active/future sprints
jira-cli sprints
jira-cli sprints --board 1

# Move issue to sprint
jira-cli sprints --move PROJ-123 --to 5
```

### Search Users
```bash
# Find user by name
jira-cli users --query "John"

# Find user by email
jira-cli users --query "john@example.com"

# Full details
jira-cli users --query "John" --format full
```

### List Projects
```bash
jira-cli projects
```

### Get Available Transitions
```bash
jira-cli transitions --issue PROJ-123
```

## Output Formats
- `--format summary` (default): Compact one-line per issue
- `--format table`: Tab-separated table
- `--format keys`: Issue keys only
- `--format full`: Complete JSON

## Understanding Resolution vs Status

**Status**: Workflow state (To Do, In Progress, Done)
**Resolution**: Final outcome (Fixed, Won't Do, Duplicate)

When you transition to "Done", Resolution is automatically set and the issue disappears from backlog.
Use `jira-cli unresolve` to clear resolution and return issue to backlog.

## Examples

When user asks to:
- "Show my Jira issues" → `jira-cli search --jql "assignee = currentUser()"`
- "Create a task in PROJ" → `jira-cli create --project PROJ --type Task --summary "..."`
- "Move PROJ-123 to Done" → `jira-cli update --issue PROJ-123 --transition "Done"`
- "Assign PROJ-123 to John" → `jira-cli assign --issue PROJ-123 --user "John"`
- "Link PROJ-123 to epic PROJ-100" → `jira-cli link-epic --issue PROJ-123 --epic PROJ-100`
- "Find user John" → `jira-cli users --query "John"`
- "Show all projects" → `jira-cli projects`
- "Create task under epic" → `jira-cli create --project PROJ --type Task --summary "..." --epic PROJ-100`
- "Show epic's child issues" → `jira-cli search --jql "parent = EPIC-KEY"`
- "Show issues assigned to specific user" → `jira-cli search --jql "assignee = 'username'"`
- "Set start and due date" → `jira-cli dates --issue PROJ-123 --start 2026-01-08 --due 2026-01-15`
- "Reopen completed issue" → `jira-cli unresolve --issue PROJ-123`
- "Show comments" → `jira-cli comments --issue PROJ-123`
- "Add labels" → `jira-cli labels --issue PROJ-123 --add "bug,urgent"`
- "Set priority to High" → `jira-cli priority --issue PROJ-123 --set High`
- "Link PROJ-123 blocks PROJ-456" → `jira-cli link --from PROJ-123 --to PROJ-456 --type "Blocks"`
- "Show sprints" → `jira-cli sprints`
- "Move to sprint" → `jira-cli sprints --move PROJ-123 --to 5`
