---
name: gitlab-expert
description: |
  GitLab operations via REST API. Use for: merge requests, pipelines, CI/CD,
  repository operations, issues. Keywords: MR, merge request, pipeline, CI/CD,
  repository, branch, gitlab, runner, job.
allowed-tools: Bash, Read, Write
---

# GitLab Expert Skill

## Overview

This skill provides GitLab expertise and operations through REST API (no MCP required).

## Quick Commands

### List Merge Requests

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py mrs \
  --project "group/project" \
  --state "opened" \
  --format summary
```

### Get MR Details

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py mr \
  --project "group/project" \
  --mr-id 123 \
  --format full
```

### Create MR

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py create-mr \
  --project "group/project" \
  --source "feature/new-feature" \
  --target "main" \
  --title "Add new feature" \
  --description "Description here"
```

### List Pipelines

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py pipelines \
  --project "group/project" \
  --status "running" \
  --format summary
```

### Get Pipeline Details

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py pipeline \
  --project "group/project" \
  --pipeline-id 456
```

### Trigger Pipeline

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py trigger \
  --project "group/project" \
  --ref "main" \
  --variables "ENV=production"
```

### List Branches

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py branches \
  --project "group/project" \
  --format summary
```

## CI/CD Templates

For CI/CD templates, see [ci-templates.md](references/ci-templates.md).

## MR Workflows

For MR workflows, see [mr-workflows.md](references/mr-workflows.md).

## Common Patterns

### Check Pipeline Status
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py pipelines \
  --project "group/project" \
  --ref "main" \
  --limit 1
```

### Get Failed Jobs
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py jobs \
  --project "group/project" \
  --pipeline-id 456 \
  --status "failed"
```

### Retry Pipeline
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py retry \
  --project "group/project" \
  --pipeline-id 456
```

### Approve MR
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py approve \
  --project "group/project" \
  --mr-id 123
```

### Merge MR
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/gitlab-cli.py merge \
  --project "group/project" \
  --mr-id 123 \
  --squash true \
  --delete-source true
```

## Output Formats

| Format | Use Case |
|--------|----------|
| `summary` | Key info only (default) |
| `full` | Complete JSON |
| `ids` | IDs only |
| `table` | Formatted table |

## Best Practices

1. **Use project path** (`group/project`) not ID
2. **Filter by state/status** to reduce results
3. **Use `--format summary`** for listing
4. **Check pipeline before merge**

## Setup

If not configured:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py --service gitlab
```
