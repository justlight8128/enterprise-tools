# GitLab Merge Request Workflows

## Standard Workflow

```
┌──────────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐
│ Create Branch│───▶│ Open MR  │───▶│  Review  │───▶│ Merged │
└──────────────┘    └──────────┘    └──────────┘    └────────┘
                          │              │
                          ▼              ▼
                    ┌──────────┐   ┌──────────────┐
                    │  Draft   │   │Changes Needed│
                    └──────────┘   └──────────────┘
```

## MR Commands

### Create MR
```bash
python gitlab-cli.py create-mr \
  --project "group/project" \
  --source "feature/new-feature" \
  --target "main" \
  --title "feat: Add new feature" \
  --description "## Summary\n\n## Changes\n\n## Testing"
```

### List Open MRs
```bash
python gitlab-cli.py mrs \
  --project "group/project" \
  --state "opened" \
  --author "me"
```

### Get MR Info
```bash
python gitlab-cli.py mr \
  --project "group/project" \
  --mr-id 123
```

### Approve MR
```bash
python gitlab-cli.py approve \
  --project "group/project" \
  --mr-id 123
```

### Merge
```bash
python gitlab-cli.py merge \
  --project "group/project" \
  --mr-id 123 \
  --squash true \
  --delete-source true
```

## MR Labels

| Label | Meaning |
|-------|---------|
| `WIP` / `Draft` | Not ready for review |
| `Ready for Review` | Awaiting review |
| `Changes Requested` | Needs updates |
| `Approved` | Ready to merge |
| `Blocked` | Blocked by dependency |

## MR Description Template

```markdown
## Summary
Brief description of changes

## Type
- [ ] Feature
- [ ] Bug Fix
- [ ] Refactor
- [ ] Documentation

## Changes
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing done

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No console.log/debug code

## Related Issues
Closes #123
```

## Best Practices

1. **Small, focused MRs** - Easier to review
2. **Clear descriptions** - Explain why, not just what
3. **Request specific reviewers** - Don't rely on defaults
4. **Respond to comments** - Don't just resolve, discuss
5. **Keep MRs updated** - Rebase often to avoid conflicts

## Pipeline Integration

### Auto-merge when Pipeline Passes
```bash
python gitlab-cli.py merge \
  --project "group/project" \
  --mr-id 123 \
  --merge-when-pipeline-succeeds true
```

### Check MR Pipeline Status
```bash
python gitlab-cli.py mr-pipelines \
  --project "group/project" \
  --mr-id 123
```
