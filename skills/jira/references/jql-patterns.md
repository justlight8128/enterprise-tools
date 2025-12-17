# JQL Patterns Reference

## Basic Queries

### My Work
```jql
# All my open issues
assignee = currentUser() AND resolution is EMPTY

# My issues updated today
assignee = currentUser() AND updated >= startOfDay()

# Issues I'm watching
watcher = currentUser()

# Issues I created
reporter = currentUser()
```

### Sprint Queries
```jql
# Current sprint issues
sprint in openSprints()

# Current sprint for specific project
sprint in openSprints() AND project = PROJ

# Issues not in any sprint
sprint is EMPTY AND project = PROJ

# Future sprints
sprint in futureSprints()

# Completed sprints
sprint in closedSprints()
```

### Status Queries
```jql
# In progress
status = "In Progress"

# Not done
status != Done

# Multiple statuses
status in ("To Do", "In Progress", "In Review")

# Status changed recently
status changed during (startOfWeek(), now())

# Status changed to Done today
status changed to Done during (startOfDay(), now())
```

## Advanced Patterns

### Time-based
```jql
# Created this week
created >= startOfWeek()

# Updated in last 7 days
updated >= -7d

# Due this week
due >= startOfWeek() AND due <= endOfWeek()

# Overdue
due < now() AND resolution is EMPTY

# No activity in 30 days
updated <= -30d AND resolution is EMPTY
```

### Priority & Type
```jql
# Critical/High bugs
type = Bug AND priority in (Critical, High)

# Stories with no story points
type = Story AND "Story Points" is EMPTY

# Epics with children
type = Epic AND "Epic Link" is not EMPTY
```

### Labels & Components
```jql
# Specific label
labels = "backend"

# Multiple labels (AND)
labels = "backend" AND labels = "api"

# Multiple labels (OR)
labels in ("backend", "frontend")

# Component
component = "Authentication"
```

### Text Search
```jql
# Summary contains
summary ~ "login"

# Summary or description contains
text ~ "authentication"

# Exact phrase
summary ~ "\"user login\""
```

## Combined Patterns

### Sprint Review
```jql
sprint in openSprints()
AND project = PROJ
AND status in ("To Do", "In Progress", "In Review", "Done")
ORDER BY status ASC, priority DESC
```

### Bug Triage
```jql
type = Bug
AND resolution is EMPTY
AND priority in (Critical, High)
AND created >= -7d
ORDER BY priority DESC, created ASC
```

### Blocked Issues
```jql
status = "Blocked"
OR ("Flagged" is not EMPTY AND resolution is EMPTY)
ORDER BY priority DESC
```

### Team Workload
```jql
project = PROJ
AND sprint in openSprints()
AND assignee is not EMPTY
ORDER BY assignee ASC, status ASC
```

### Release Readiness
```jql
fixVersion = "1.2.0"
AND resolution is EMPTY
ORDER BY priority DESC
```

## Performance Tips

1. **Always specify project** when possible
2. **Limit date ranges** - avoid `created > 2020-01-01`
3. **Use `ORDER BY`** for consistent results
4. **Add `maxResults`** in API calls
