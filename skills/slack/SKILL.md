---
name: slack-expert
description: |
  Slack operations via REST API. Use for: sending messages, channel management,
  user lookup, notifications. Keywords: message, channel, DM, thread, notification,
  slack, send, post.
allowed-tools: Bash, Read, Write
---

# Slack Expert Skill

## Overview

This skill provides Slack operations through REST API (no MCP required).

## Quick Commands

### Send Message

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/slack-cli.py send \
  --channel "#general" \
  --message "Hello team!"
```

### Send to Thread

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/slack-cli.py send \
  --channel "#general" \
  --thread-ts "1234567890.123456" \
  --message "Reply to thread"
```

### Send DM

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/slack-cli.py dm \
  --user "@john.doe" \
  --message "Private message"
```

### List Channels

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/slack-cli.py channels \
  --format summary
```

### Get Channel History

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/slack-cli.py history \
  --channel "#general" \
  --limit 20
```

### Search Messages

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/slack-cli.py search \
  --query "deployment" \
  --in-channel "#devops"
```

## Message Formatting

### Basic Formatting
```
*bold* _italic_ ~strikethrough~ `code`
```

### Code Block
```
\`\`\`
code block here
\`\`\`
```

### Links
```
<https://example.com|Link Text>
```

### Mentions
```
<@U123456>     # User mention
<!channel>     # @channel
<!here>        # @here
```

## Block Kit (Rich Messages)

For Block Kit patterns, see [block-kit.md](references/block-kit.md).

### Quick Example

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/slack-cli.py send \
  --channel "#general" \
  --blocks '[{"type":"section","text":{"type":"mrkdwn","text":"*Title*\nDescription"}}]'
```

## Common Use Cases

### Deployment Notification

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/slack-cli.py send \
  --channel "#deployments" \
  --message ":rocket: *Deployment Complete*\nVersion: v1.2.3\nEnvironment: Production"
```

### Alert

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/api/slack-cli.py send \
  --channel "#alerts" \
  --message ":warning: *Alert*: High CPU usage detected on server-01"
```

## Output Formats

| Format | Use Case |
|--------|----------|
| `summary` | Channel name + topic |
| `full` | Complete JSON |
| `ids` | IDs only |

## Best Practices

1. **Use `--format summary`** when listing
2. **Prefer channels** over DMs for team visibility
3. **Use threads** for discussions
4. **Include context** in automated messages

## Setup

If not configured:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py --service slack
```
