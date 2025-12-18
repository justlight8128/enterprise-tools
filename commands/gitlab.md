---
description: Manage GitLab merge requests, pipelines, and branches
---

# GitLab CLI

Use gitlab-cli to interact with GitLab. Available at `~/bin/gitlab-cli`.

## Quick Reference

### List Merge Requests
```bash
gitlab-cli mrs --project "group/project" --state opened
gitlab-cli mrs --project "group/project" --state merged --limit 10
```

### Get MR Details
```bash
gitlab-cli mr --project "group/project" --mr 123
gitlab-cli mr --project "group/project" --mr 123 --format full
```

### Create Merge Request
```bash
gitlab-cli create-mr --project "group/project" --source feature-branch --target main --title "Feature: Add X"
```

### Merge MR
```bash
gitlab-cli merge --project "group/project" --mr 123
```

### List Pipelines
```bash
gitlab-cli pipelines --project "group/project" --limit 10
gitlab-cli pipelines --project "group/project" --status failed
```

### Get Pipeline Details
```bash
gitlab-cli pipeline --project "group/project" --pipeline 456
```

### List Pipeline Jobs
```bash
gitlab-cli jobs --project "group/project" --pipeline 456
```

### Retry Failed Pipeline
```bash
gitlab-cli retry --project "group/project" --pipeline 456
```

### List Branches
```bash
gitlab-cli branches --project "group/project"
```

## Examples

When user asks to:
- "Show open MRs" → `gitlab-cli mrs --project "group/project" --state opened`
- "Check pipeline status" → `gitlab-cli pipelines --project "group/project"`
- "Create MR from feature to main" → `gitlab-cli create-mr --project "..." --source feature --target main --title "..."`
