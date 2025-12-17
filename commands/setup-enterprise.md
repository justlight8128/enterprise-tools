---
description: Configure enterprise tools (Jira, Confluence, Slack, GitLab) credentials
---

# Setup Enterprise Tools

Run the interactive setup wizard to configure your enterprise tool credentials.

## Instructions

1. Run the setup wizard:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py
```

2. Follow the prompts to configure each service

3. The wizard will:
   - Ask for API tokens/credentials for each service
   - Test the connection to verify credentials work
   - Save configuration to ~/.enterprise-tools/credentials.env

## Quick Commands

### Setup specific service:
```bash
# Jira only
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py --service jira

# Slack only
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py --service slack

# All services
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py --service all
```

### Test existing configuration:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py --test
```

### Show current configuration:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup/setup-wizard.py --show
```

## Where to Get Credentials

### Jira & Confluence (Atlassian Cloud)
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create new API token
3. Use your Atlassian email + this token

### Slack
1. Go to https://api.slack.com/apps
2. Create new app or use existing
3. Add required scopes: chat:write, channels:read, users:read, search:read
4. Install to workspace
5. Copy Bot User OAuth Token (xoxb-...)

### GitLab
1. Go to https://gitlab.com/-/profile/personal_access_tokens
2. Create token with scopes: api, read_api, read_repository
3. Copy the token

## Security Notes

- Credentials are stored in ~/.enterprise-tools/credentials.env
- File permissions are set to 600 (owner read/write only)
- Never commit this file to version control
- Use environment variables in CI/CD instead
