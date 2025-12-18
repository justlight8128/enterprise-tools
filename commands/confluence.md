---
description: Search and manage Confluence pages
---

# Confluence CLI

Use confluence-cli to interact with Confluence. Available at `~/bin/confluence-cli`.

## Quick Reference

### Search Pages
```bash
confluence-cli search --cql "text ~ 'keyword'" --max-results 10
confluence-cli search --cql "space = SPACE_KEY AND type = page"
confluence-cli search --cql "creator = currentUser()"
```

### Get Page Content
```bash
confluence-cli get --page-id 123456
confluence-cli get --page-id 123456 --format full
```

### Create Page
```bash
confluence-cli create --space SPACE --title "Page Title" --body "<p>Content here</p>"
confluence-cli create --space SPACE --title "Page Title" --parent-id 123456 --body "Content"
```

### Update Page
```bash
confluence-cli update --page-id 123456 --body "<p>New content</p>"
```

## Common CQL Patterns
```bash
# Recent pages in space
confluence-cli search --cql "space = SPACE AND type = page ORDER BY lastmodified DESC"

# Pages I created
confluence-cli search --cql "creator = currentUser() ORDER BY created DESC"

# Search by label
confluence-cli search --cql "label = 'important'"
```
