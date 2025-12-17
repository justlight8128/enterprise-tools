---
name: jira-expert
description: |
  Jira operations via REST API. Use for: ticket search/create/update, sprint management,
  JQL queries, workflow transitions, reporting. Keywords: ticket, issue, sprint, board,
  backlog, JQL, story, epic, bug, assignee, reporter.
allowed-tools: Bash, Read, Write
---

# Jira Expert Skill

## Overview

This skill provides Jira expertise and operations through REST API (no MCP required).

## Quick Commands

### Search Issues (JQL)

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py search \
  --jql "project = PROJ AND status = 'In Progress'" \
  --format summary
```

### Create Issue

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py create \
  --project "PROJ" \
  --type "Story" \
  --summary "Title here" \
  --description "Details..."
```

### Update Issue

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py update \
  --issue "PROJ-123" \
  --transition "In Progress" \
  --comment "Starting work"
```

### Get Issue Details

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py get \
  --issue "PROJ-123" \
  --format full
```

### Sprint Info

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py sprint \
  --board-id 123 \
  --state active
```

## Output Formats

| Format | Use Case | Token Cost |
|--------|----------|------------|
| `summary` | Quick overview (default) | Low |
| `table` | Structured data | Medium |
| `full` | Complete JSON | High |
| `keys` | Issue keys only | Minimal |

**Always prefer `summary` or `keys` for token efficiency.**

## Common JQL Patterns

For comprehensive JQL patterns, see [jql-patterns.md](references/jql-patterns.md).

### Quick Reference

```jql
# My open tickets
assignee = currentUser() AND status != Done

# Current sprint
sprint in openSprints() AND project = PROJ

# Recent updates
updated >= -7d ORDER BY updated DESC

# High priority bugs
type = Bug AND priority in (High, Critical) AND status != Done

# Specific label
labels = "backend" AND status = "In Progress"
```

## Workflow Transitions

For workflow guides, see [workflows.md](references/workflows.md).

### Check Available Transitions

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py transitions \
  --issue "PROJ-123"
```

## Error Handling

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Authentication error - check credentials |
| 2 | Request error - check JQL syntax or issue key |
| 3 | Network error - check connectivity |

## Best Practices

1. **Use `--format summary`** for most operations
2. **Limit results** with `--max-results 20` when searching
3. **Use specific JQL** to reduce result size
4. **Cache board IDs** - look up once, reuse

## Setup

If not configured, run:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py --service jira
```
