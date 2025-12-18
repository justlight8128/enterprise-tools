---
description: Send messages and interact with Slack
---

# Slack CLI

Use slack-cli to interact with Slack. Available at `~/bin/slack-cli`.

## Quick Reference

### Send Message to Channel
```bash
slack-cli send --channel "#general" --text "Hello team!"
slack-cli send --channel "C0123456789" --text "Message here"
```

### Send Direct Message
```bash
slack-cli dm --user "@username" --text "Hey!"
slack-cli dm --user "U0123456789" --text "Direct message"
```

### List Channels
```bash
slack-cli channels
slack-cli channels --type public
slack-cli channels --type private
```

### Get Channel History
```bash
slack-cli history --channel "#general" --limit 10
```

### Search Messages
```bash
slack-cli search --query "keyword" --limit 20
```

## Examples

When user asks to:
- "Send message to #general" → `slack-cli send --channel "#general" --text "..."`
- "DM user about X" → `slack-cli dm --user "@username" --text "..."`
- "List Slack channels" → `slack-cli channels`
