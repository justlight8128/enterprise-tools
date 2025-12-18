# Enterprise Tools Plugin for Claude Code

> Token-efficient enterprise integrations without MCP overhead

## Overview

This plugin provides Jira, Confluence, Slack, and GitLab integration using **Skills + REST API** instead of MCP servers. This approach reduces token consumption by **~99%** compared to traditional MCP setup.

| Approach | Initial Token Load |
|----------|-------------------|
| MCP (4 servers) | ~47,000+ tokens |
| This Plugin | ~200 tokens |

## Installation

### Option 1: From GitHub (Recommended)

```bash
# Add marketplace from GitHub
/plugin marketplace add justlight8128/enterprise-tools

# Install the plugin
/plugin install enterprise-tools@enterprise-tools-marketplace
```

Then **restart Claude Code**.

### Option 2: Local Install (for development)

```bash
git clone https://github.com/justlight8128/enterprise-tools.git
cd enterprise-tools
/plugin marketplace add ./enterprise-tools
/plugin install enterprise-tools@enterprise-tools-marketplace
```

---

## ⚙️ Credential Setup (Required)

**This plugin does NOT include any credentials.** Each user must configure their own API tokens.

### Option A: Interactive Setup Wizard (Recommended)

```bash
# After plugin installation, run:
python3 ~/.claude/plugins/marketplaces/enterprise-tools-marketplace/scripts/setup/setup-wizard.py
```

The wizard will:
1. Ask for your API tokens interactively
2. Test each connection
3. Save to `~/.enterprise-tools/credentials.env`

### Option B: Manual Configuration

1. Create the config directory:
```bash
mkdir -p ~/.enterprise-tools
```

2. Create `~/.enterprise-tools/credentials.env`:
```bash
# Jira (Atlassian Cloud)
JIRA_BASE_URL="https://your-company.atlassian.net"
JIRA_EMAIL="your-email@company.com"
JIRA_API_TOKEN="your-jira-api-token"

# Confluence (Atlassian Cloud) - usually same as Jira
CONFLUENCE_BASE_URL="https://your-company.atlassian.net"
CONFLUENCE_EMAIL="your-email@company.com"
CONFLUENCE_API_TOKEN="your-api-token"

# Slack
SLACK_BOT_TOKEN="xoxb-your-bot-token"

# GitLab
GITLAB_BASE_URL="https://gitlab.com"
GITLAB_TOKEN="your-personal-access-token"
```

3. Secure the file:
```bash
chmod 600 ~/.enterprise-tools/credentials.env
```

### Option C: Environment Variables

Set credentials directly in your shell:

```bash
# Add to ~/.bashrc or ~/.zshrc
export JIRA_BASE_URL="https://your-company.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-token"
# ... etc
```

---

## 🔑 Where to Get API Tokens

### Jira & Confluence (Atlassian Cloud)

1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **"Create API token"**
3. Give it a name (e.g., "Claude Code")
4. Copy the token (shown only once!)

**Required permissions:** Read/write access to projects you want to use.

### Slack

1. Go to [Slack Apps](https://api.slack.com/apps)
2. Click **"Create New App"** → "From scratch"
3. Go to **"OAuth & Permissions"**
4. Add these **Bot Token Scopes**:
   - `chat:write` - Send messages
   - `channels:read` - List channels
   - `users:read` - Lookup users
   - `search:read` - Search messages
5. Click **"Install to Workspace"**
6. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)

### GitLab

1. Go to [GitLab Personal Access Tokens](https://gitlab.com/-/profile/personal_access_tokens)
2. Create token with scopes:
   - `api` - Full API access
   - `read_api` - Read API
   - `read_repository` - Read repo
3. Copy the token (shown only once!)

For self-hosted GitLab: Use your instance URL instead of `gitlab.com`

---

## 🚀 Quick Start

After setup, just ask Claude naturally:

```
"Show me my open Jira tickets"
"Search Confluence for API documentation"
"Send a message to #general on Slack"
"List open merge requests in my-project"
```

### Verify Setup

```bash
# Test all connections
python3 ~/.claude/plugins/marketplaces/enterprise-tools-marketplace/scripts/setup/setup-wizard.py --test

# Show current config (tokens masked)
python3 ~/.claude/plugins/marketplaces/enterprise-tools-marketplace/scripts/setup/setup-wizard.py --show
```

---

## Features

### Jira
- Search issues with JQL
- Create/update issues
- Transition workflow status
- Sprint management
- Add comments

### Confluence
- Search pages with CQL
- Get page content
- Create/update pages
- List spaces

### Slack
- Send messages to channels
- Send DMs
- Reply to threads
- Search messages
- List channels

### GitLab
- List/create merge requests
- View/retry pipelines
- List branches
- Check job status

---

## Token Efficiency

The plugin uses a **progressive loading** architecture:

1. **Session Start**: Only skill metadata loads (~50 tokens per skill)
2. **On Request**: Full skill loads when needed (~500 tokens)
3. **References**: Loaded on-demand from `references/` folders
4. **Scripts**: Execute via Bash, results only (no schema overhead)

### Output Formats

All CLI scripts support token-efficient output:

```bash
--format summary  # Default: minimal output
--format table    # Structured data
--format keys     # IDs only
--format full     # Complete JSON (use sparingly)
```

---

## 🔒 Security

### What's in this repository (SAFE to publish):
- ✅ Skill definitions (markdown)
- ✅ CLI scripts (Python)
- ✅ Setup wizard
- ✅ Documentation
- ✅ Example config template (`credentials.env.example`)

### What's NOT in this repository:
- ❌ No actual API tokens
- ❌ No passwords
- ❌ No company URLs
- ❌ No personal information

### Credential Storage:
- Credentials are stored **locally** at `~/.enterprise-tools/credentials.env`
- File permissions: `600` (owner read/write only)
- **Never committed to git** (in `.gitignore`)
- Each user maintains their own credentials

### Public vs Private Repository:

| Choice | Pros | Cons |
|--------|------|------|
| **Public** | Easy sharing, discoverable | Anyone can see code |
| **Private** | More control | Need to invite collaborators |

**Recommendation:** Public is fine for this plugin since it contains no secrets. Anyone can use it, they just need their own API tokens.

---

## For Team Admins

### Rolling out to your team:

1. **Share the repository URL** with team members
2. Each person runs:
   ```bash
   /plugin marketplace add justlight8128/enterprise-tools
   /plugin install enterprise-tools@enterprise-tools-marketplace
   # Restart Claude Code
   python3 ~/.claude/plugins/marketplaces/enterprise-tools-marketplace/scripts/setup/setup-wizard.py
   ```
3. Each person enters **their own** API tokens
4. Tokens are stored locally, never shared

### Corporate API Tokens (Optional):

If your company has shared service accounts:
1. Create a separate documentation page with instructions
2. Share service account tokens through secure channels (not GitHub!)
3. Consider using environment variables in CI/CD

---

## Requirements

- Python 3.8+
- `requests` package (auto-installed)
- Claude Code 1.0+

## Troubleshooting

### "Credentials not configured"
Run the setup wizard:
```bash
python3 ~/.claude/plugins/marketplaces/enterprise-tools-marketplace/scripts/setup/setup-wizard.py
```

### "HTTP 401 - Unauthorized"
- Check your API token is correct
- Verify the token hasn't expired
- Ensure the token has required permissions

### "HTTP 403 - Forbidden"
- Your account may not have access to that resource
- Check project/space permissions

### Plugin not loading
- Restart Claude Code after installation
- Check `/plugin list` to verify installation

---

## Support

- Issues: https://github.com/justlight8128/enterprise-tools/issues
- Discussions: https://github.com/justlight8128/enterprise-tools/discussions

## License

MIT - Feel free to use, modify, and share!
