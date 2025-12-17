---
name: confluence-expert
description: |
  Confluence operations via REST API. Use for: page search/create/update, space management,
  documentation, wiki pages. Keywords: page, wiki, documentation, space, CQL, template,
  knowledge base, article.
allowed-tools: Bash, Read, Write
---

# Confluence Expert Skill

## Overview

This skill provides Confluence expertise and operations through REST API (no MCP required).

## Quick Commands

### Search Pages (CQL)

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/confluence-cli.py search \
  --cql "space = DEV AND type = page AND text ~ 'API'" \
  --format summary
```

### Get Page Content

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/confluence-cli.py get \
  --page-id 12345 \
  --format markdown
```

### Create Page

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/confluence-cli.py create \
  --space "DEV" \
  --title "New Documentation" \
  --content "# Content here" \
  --parent-id 12345
```

### Update Page

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/confluence-cli.py update \
  --page-id 12345 \
  --content "Updated content"
```

### List Spaces

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/confluence-cli.py spaces \
  --format summary
```

## Output Formats

| Format | Use Case | Token Cost |
|--------|----------|------------|
| `summary` | Title + excerpt (default) | Low |
| `markdown` | Content as markdown | Medium |
| `full` | Complete JSON | High |

## Common CQL Patterns

For comprehensive CQL patterns, see [cql-patterns.md](references/cql-patterns.md).

### Quick Reference

```cql
# All pages in space
space = DEV AND type = page

# Recent updates
space = DEV AND lastmodified >= now("-7d")

# My pages
creator = currentUser()

# Text search
text ~ "authentication"

# By label
label = "api-docs"

# Pages with specific ancestor
ancestor = 12345
```

## Page Templates

For templates, see [templates.md](references/templates.md).

### Common Templates

- Technical Design Document
- Meeting Notes
- Release Notes
- How-To Guide
- API Documentation

## Content Format

Confluence uses **Storage Format** (XHTML-based). The CLI handles conversion:

- Input: Markdown or plain text
- Output: Can be markdown, HTML, or raw storage format

## Best Practices

1. **Use `--format summary`** when searching
2. **Get specific pages** instead of broad searches
3. **Use labels** for organization
4. **Cache space keys** - look up once

## Setup

If not configured:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py --service confluence
```
