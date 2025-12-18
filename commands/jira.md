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
```

### Get Issue Details
```bash
jira-cli get --issue PROJ-123
jira-cli get --issue PROJ-123 --format full
```

### Create Issue
```bash
jira-cli create --project PROJ --type Task --summary "Issue title" --description "Details here"
jira-cli create --project PROJ --type Bug --summary "Bug title" --labels "bug,urgent"
```

### Update Issue Status
```bash
# List available transitions
jira-cli transitions --issue PROJ-123

# Transition to new status
jira-cli update --issue PROJ-123 --transition "In Progress"
jira-cli update --issue PROJ-123 --transition "Done" --comment "Completed!"
```

### Add Comment
```bash
jira-cli update --issue PROJ-123 --comment "This is my comment"
```

## Output Formats
- `--format summary` (default): Compact one-line per issue
- `--format table`: Tab-separated table
- `--format keys`: Issue keys only
- `--format full`: Complete JSON

## Examples

When user asks to:
- "Show my Jira issues" → `jira-cli search --jql "assignee = currentUser()"`
- "Create a task in PROJ" → `jira-cli create --project PROJ --type Task --summary "..."`
- "Move PROJ-123 to Done" → `jira-cli update --issue PROJ-123 --transition "Done"`
