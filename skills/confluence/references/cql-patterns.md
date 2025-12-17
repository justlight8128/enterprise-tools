# CQL (Confluence Query Language) Patterns

## Basic Queries

### By Space
```cql
# All content in space
space = DEV

# Pages only (no blog posts)
space = DEV AND type = page

# Blog posts only
space = DEV AND type = blogpost
```

### By Type
```cql
# Pages
type = page

# Blog posts
type = blogpost

# Attachments
type = attachment

# Comments
type = comment
```

### Text Search
```cql
# Contains word
text ~ "API"

# Contains phrase
text ~ "user authentication"

# Title contains
title ~ "Guide"

# Title exact match
title = "Getting Started Guide"
```

## Time-based Queries

```cql
# Created today
created >= now("-1d")

# Modified this week
lastmodified >= now("-7d")

# Created in date range
created >= "2025-01-01" AND created <= "2025-01-31"

# Not modified in 90 days (stale)
lastmodified <= now("-90d")
```

## User-based Queries

```cql
# Created by me
creator = currentUser()

# Modified by specific user
contributor = "john.doe"

# Mentioned user
mention = currentUser()

# Watched by me
watcher = currentUser()
```

## Labels

```cql
# Has label
label = "api-docs"

# Multiple labels (AND)
label = "api-docs" AND label = "v2"

# Multiple labels (OR)
label IN ("api-docs", "user-guide")
```

## Hierarchy

```cql
# Direct children of page
parent = 12345

# All descendants
ancestor = 12345

# Root pages in space
space = DEV AND parent = homepage
```

## Combined Patterns

### Documentation Search
```cql
space = DEV
AND type = page
AND label = "documentation"
AND text ~ "authentication"
ORDER BY lastmodified DESC
```

### Stale Content Review
```cql
space = DEV
AND type = page
AND lastmodified <= now("-180d")
ORDER BY lastmodified ASC
```

### Recent Updates by Team
```cql
space IN (DEV, QA, OPS)
AND lastmodified >= now("-7d")
ORDER BY lastmodified DESC
```

### API Documentation
```cql
space = DEV
AND label = "api-docs"
AND type = page
ORDER BY title ASC
```

## Performance Tips

1. **Specify space** for faster queries
2. **Use type filter** when possible
3. **Limit results** with `limit` parameter
4. **Avoid wildcard-only** searches
