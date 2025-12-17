# Jira API Quick Reference

## Base URL

```
https://{your-domain}.atlassian.net/rest/api/3/
```

## Common Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Search | GET | `/search?jql={jql}` |
| Get Issue | GET | `/issue/{issueKey}` |
| Create Issue | POST | `/issue` |
| Update Issue | PUT | `/issue/{issueKey}` |
| Transitions | GET | `/issue/{issueKey}/transitions` |
| Do Transition | POST | `/issue/{issueKey}/transitions` |
| Add Comment | POST | `/issue/{issueKey}/comment` |
| Get Projects | GET | `/project` |
| Get Boards | GET | `/board` (Agile API) |
| Get Sprints | GET | `/board/{boardId}/sprint` |

## Agile API Base

```
https://{your-domain}.atlassian.net/rest/agile/1.0/
```

## Authentication

```bash
# Basic Auth with API Token
curl -u email@example.com:API_TOKEN \
  "https://your-domain.atlassian.net/rest/api/3/myself"
```

## Response Fields

### Issue Fields
- `key` - Issue key (PROJ-123)
- `fields.summary` - Title
- `fields.description` - Description (ADF format)
- `fields.status.name` - Current status
- `fields.assignee.displayName` - Assignee
- `fields.priority.name` - Priority
- `fields.issuetype.name` - Issue type
- `fields.labels` - Labels array
- `fields.created` - Created date
- `fields.updated` - Updated date

### Pagination
- `startAt` - Starting index
- `maxResults` - Max results per page
- `total` - Total count

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid JQL, missing fields) |
| 401 | Unauthorized (check credentials) |
| 403 | Forbidden (no permission) |
| 404 | Not found (invalid issue key) |
| 429 | Rate limited |
