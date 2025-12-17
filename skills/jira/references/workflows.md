# Jira Workflow Guide

## Standard Workflow

```
┌─────────┐    ┌─────────────┐    ┌───────────┐    ┌──────┐
│  To Do  │───▶│ In Progress │───▶│ In Review │───▶│ Done │
└─────────┘    └─────────────┘    └───────────┘    └──────┘
     │                │                 │
     │                ▼                 │
     │          ┌─────────┐            │
     └─────────▶│ Blocked │◀───────────┘
                └─────────┘
```

## Common Transitions

| From | To | Typical Trigger |
|------|-----|-----------------|
| To Do | In Progress | Start work |
| In Progress | In Review | PR created |
| In Review | Done | PR merged |
| Any | Blocked | Dependency issue |
| Blocked | Previous | Unblocked |

## Transition Commands

### Check Available Transitions
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py transitions \
  --issue "PROJ-123"
```

### Perform Transition
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py update \
  --issue "PROJ-123" \
  --transition "In Progress"
```

### Transition with Comment
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py update \
  --issue "PROJ-123" \
  --transition "Done" \
  --comment "Completed in PR #456"
```

## Bulk Operations

### Move Multiple Issues to Sprint
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/jira-cli.py bulk-move \
  --issues "PROJ-1,PROJ-2,PROJ-3" \
  --sprint 123
```

### Batch Transition
```bash
# Search and transition all
for issue in $(python jira-cli.py search --jql "..." --format keys); do
  python jira-cli.py update --issue "$issue" --transition "Done"
done
```

## Best Practices

1. **Always add comments** when transitioning
2. **Check transitions first** - not all transitions are always available
3. **Use bulk operations** for multiple issues
4. **Respect workflow rules** - some transitions require fields
