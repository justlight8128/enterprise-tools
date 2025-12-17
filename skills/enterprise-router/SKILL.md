---
name: enterprise-router
description: |
  Routes to appropriate enterprise tool based on context. Use when user mentions:
  tickets, issues, sprints, boards (→ Jira), wiki, documentation, pages (→ Confluence),
  messages, channels, DMs (→ Slack), merge requests, pipelines, CI/CD (→ GitLab).
---

# Enterprise Tools Router

## Overview

This skill routes requests to the appropriate enterprise tool integration.
All integrations use REST API via Python scripts instead of MCP for token efficiency.

## Quick Reference

| Keywords | Tool | Skill |
|----------|------|-------|
| ticket, issue, sprint, board, JQL, story, epic, bug | Jira | `jira/SKILL.md` |
| page, wiki, documentation, space, CQL | Confluence | `confluence/SKILL.md` |
| message, channel, DM, thread, notification | Slack | `slack/SKILL.md` |
| MR, merge request, pipeline, CI/CD, repository, branch | GitLab | `gitlab/SKILL.md` |

## First-Time Setup

If credentials are not configured, run:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py
```

Or use the command: `/setup-enterprise`

## How It Works

1. **Skills provide knowledge** - When to use each tool, patterns, best practices
2. **Scripts provide execution** - REST API calls via Python CLI tools
3. **References loaded on-demand** - Detailed docs only when needed

## Token Efficiency

| Approach | Initial Load | Per Operation |
|----------|-------------|---------------|
| MCP (4 servers) | ~47,000 tokens | +result |
| This Plugin | ~200 tokens | +skill (~500) +result |

**Savings: ~99% on initial load**

## Environment Setup

Credentials are stored in `~/.enterprise-tools/credentials.env`:

```bash
# Check if configured
cat ~/.enterprise-tools/credentials.env

# If not, run setup
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py
```

## Script Locations

All CLI scripts are in `${CLAUDE_PLUGIN_ROOT}/scripts/api/`:

- `jira-cli.py` - Jira operations
- `confluence-cli.py` - Confluence operations
- `slack-cli.py` - Slack operations
- `gitlab-cli.py` - GitLab operations
