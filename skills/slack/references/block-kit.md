# Slack Block Kit Reference

## Basic Blocks

### Section Block
```json
{
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "*Title*\nDescription text here"
  }
}
```

### Section with Accessory
```json
{
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "Text with button"
  },
  "accessory": {
    "type": "button",
    "text": {"type": "plain_text", "text": "Click"},
    "action_id": "button_click"
  }
}
```

### Divider
```json
{
  "type": "divider"
}
```

### Header
```json
{
  "type": "header",
  "text": {
    "type": "plain_text",
    "text": "Header Text"
  }
}
```

### Context (Small Text)
```json
{
  "type": "context",
  "elements": [
    {
      "type": "mrkdwn",
      "text": "Posted by <@U123> | Jan 1, 2025"
    }
  ]
}
```

## Common Patterns

### Deployment Notification
```json
[
  {
    "type": "header",
    "text": {"type": "plain_text", "text": ":rocket: Deployment Complete"}
  },
  {
    "type": "section",
    "fields": [
      {"type": "mrkdwn", "text": "*Service:*\napi-server"},
      {"type": "mrkdwn", "text": "*Version:*\nv1.2.3"},
      {"type": "mrkdwn", "text": "*Environment:*\nProduction"},
      {"type": "mrkdwn", "text": "*Deployed by:*\n<@U123>"}
    ]
  },
  {
    "type": "context",
    "elements": [
      {"type": "mrkdwn", "text": "Deployed at <!date^1234567890^{date_short_pretty} {time}|Jan 1, 2025>"}
    ]
  }
]
```

### Alert Message
```json
[
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": ":warning: *Alert: High CPU Usage*"
    }
  },
  {
    "type": "section",
    "fields": [
      {"type": "mrkdwn", "text": "*Server:*\nweb-01"},
      {"type": "mrkdwn", "text": "*CPU:*\n95%"},
      {"type": "mrkdwn", "text": "*Duration:*\n5 minutes"},
      {"type": "mrkdwn", "text": "*Severity:*\nHigh"}
    ]
  },
  {
    "type": "actions",
    "elements": [
      {
        "type": "button",
        "text": {"type": "plain_text", "text": "View Dashboard"},
        "url": "https://grafana.example.com"
      },
      {
        "type": "button",
        "text": {"type": "plain_text", "text": "Acknowledge"},
        "style": "primary",
        "action_id": "ack_alert"
      }
    ]
  }
]
```

### PR Review Request
```json
[
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "*PR Review Requested*\n<https://github.com/org/repo/pull/123|#123: Add user authentication>"
    }
  },
  {
    "type": "section",
    "fields": [
      {"type": "mrkdwn", "text": "*Author:*\n<@U123>"},
      {"type": "mrkdwn", "text": "*Branch:*\nfeature/auth"},
      {"type": "mrkdwn", "text": "*Files:*\n12 changed"},
      {"type": "mrkdwn", "text": "*Lines:*\n+234 / -56"}
    ]
  }
]
```

## Emojis

| Emoji | Use Case |
|-------|----------|
| `:rocket:` | Deployment |
| `:white_check_mark:` | Success |
| `:x:` | Failure |
| `:warning:` | Warning |
| `:information_source:` | Info |
| `:hourglass:` | In Progress |
| `:bug:` | Bug |
| `:gear:` | Settings/Config |

## Tips

1. Use `mrkdwn` type for formatting
2. Keep messages concise
3. Use fields for key-value pairs
4. Add context for timestamps
