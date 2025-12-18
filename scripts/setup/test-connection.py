#!/usr/bin/env python3
"""
Quick connection test for all configured services
"""

import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


def load_config():
    """Load configuration"""
    config = {}
    cred_file = Path.home() / '.enterprise-tools' / 'credentials.env'

    if cred_file.exists():
        with open(cred_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value.strip('"\'')
    return config


def test_all():
    """Test all services"""
    config = load_config()

    print("Enterprise Tools - Connection Test")
    print("=" * 40)

    results = []

    # Jira
    if config.get('JIRA_BASE_URL') and config.get('JIRA_API_TOKEN'):
        try:
            url = f"{config['JIRA_BASE_URL'].rstrip('/')}/rest/api/3/myself"
            response = requests.get(url, auth=(config['JIRA_EMAIL'], config['JIRA_API_TOKEN']), timeout=10)
            if response.status_code == 200:
                print("✅ Jira: OK")
                results.append(True)
            else:
                print(f"❌ Jira: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ Jira: {e}")
            results.append(False)
    else:
        print("⏭️  Jira: Not configured")

    # Confluence
    if config.get('CONFLUENCE_BASE_URL') and config.get('CONFLUENCE_API_TOKEN'):
        try:
            url = f"{config['CONFLUENCE_BASE_URL'].rstrip('/')}/wiki/rest/api/user/current"
            response = requests.get(url, auth=(config['CONFLUENCE_EMAIL'], config['CONFLUENCE_API_TOKEN']), timeout=10)
            if response.status_code == 200:
                print("✅ Confluence: OK")
                results.append(True)
            else:
                print(f"❌ Confluence: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ Confluence: {e}")
            results.append(False)
    else:
        print("⏭️  Confluence: Not configured")

    # Slack
    if config.get('SLACK_BOT_TOKEN'):
        try:
            url = "https://slack.com/api/auth.test"
            headers = {'Authorization': f"Bearer {config['SLACK_BOT_TOKEN']}"}
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            if data.get('ok'):
                print("✅ Slack: OK")
                results.append(True)
            else:
                print(f"❌ Slack: {data.get('error')}")
                results.append(False)
        except Exception as e:
            print(f"❌ Slack: {e}")
            results.append(False)
    else:
        print("⏭️  Slack: Not configured")

    # GitLab
    if config.get('GITLAB_TOKEN'):
        try:
            base_url = config.get('GITLAB_BASE_URL', 'https://gitlab.com')
            url = f"{base_url.rstrip('/')}/api/v4/user"
            headers = {'PRIVATE-TOKEN': config['GITLAB_TOKEN']}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print("✅ GitLab: OK")
                results.append(True)
            else:
                print(f"❌ GitLab: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ GitLab: {e}")
            results.append(False)
    else:
        print("⏭️  GitLab: Not configured")

    print("=" * 40)

    if results:
        success = sum(results)
        total = len(results)
        print(f"Result: {success}/{total} services connected")
        return 0 if all(results) else 1
    else:
        print("No services configured. Run setup-wizard.py")
        return 1


if __name__ == '__main__':
    sys.exit(test_all())
