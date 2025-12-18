#!/usr/bin/env python3
"""
Jira CLI - REST API wrapper for Claude Code
Token-efficient output formats
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


def load_credentials():
    """Load credentials from environment or config file"""
    base_url = os.environ.get('JIRA_BASE_URL')
    email = os.environ.get('JIRA_EMAIL')
    token = os.environ.get('JIRA_API_TOKEN')

    if not all([base_url, email, token]):
        cred_file = Path.home() / '.enterprise-tools' / 'credentials.env'
        if cred_file.exists():
            with open(cred_file, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        value = value.strip('"\'')
                        if key == 'JIRA_BASE_URL':
                            base_url = value
                        elif key == 'JIRA_EMAIL':
                            email = value
                        elif key == 'JIRA_API_TOKEN':
                            token = value

    if not all([base_url, email, token]):
        print("ERROR: Jira credentials not configured.", file=sys.stderr)
        print("Run: python setup-wizard.py --service jira", file=sys.stderr)
        sys.exit(1)

    return base_url.rstrip('/'), email, token


def format_output(data, format_type='summary'):
    """Token-efficient output formatting"""
    if format_type == 'full':
        return json.dumps(data, indent=2, ensure_ascii=False)

    if format_type == 'keys':
        if isinstance(data, list):
            return '\n'.join(item.get('key', '') for item in data if 'key' in item)
        return data.get('key', '')

    if format_type == 'table':
        if isinstance(data, list) and data:
            lines = ['KEY\tSTATUS\tASSIGNEE\tSUMMARY']
            for item in data:
                line = f"{item.get('key', '')}\t{item.get('status', '')}\t{item.get('assignee', '-')}\t{item.get('summary', '')[:50]}"
                lines.append(line)
            return '\n'.join(lines)

    # summary (default)
    if isinstance(data, list):
        lines = []
        for item in data:
            if 'key' in item:
                line = f"{item['key']}: {item.get('summary', '')} [{item.get('status', '')}]"
                if item.get('assignee'):
                    line += f" @{item['assignee']}"
                lines.append(line)
        return '\n'.join(lines) if lines else "No results found"
    elif isinstance(data, dict) and 'key' in data:
        return f"{data['key']}: {data.get('summary', '')} [{data.get('status', '')}]"

    return json.dumps(data, ensure_ascii=False)


def search_issues(base_url, auth, jql, fields='key,summary,status,assignee', max_results=50):
    """Search issues with JQL"""
    url = f"{base_url}/rest/api/3/search"
    params = {
        'jql': jql,
        'fields': fields,
        'maxResults': max_results
    }

    response = requests.get(url, params=params, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    data = response.json()
    issues = []

    for issue in data.get('issues', []):
        fields_data = issue.get('fields', {})
        assignee = fields_data.get('assignee')
        issues.append({
            'key': issue['key'],
            'summary': fields_data.get('summary', ''),
            'status': fields_data.get('status', {}).get('name', ''),
            'assignee': assignee.get('displayName', '') if assignee else ''
        })

    return issues


def get_issue(base_url, auth, issue_key):
    """Get single issue details"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}"

    response = requests.get(url, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    data = response.json()
    fields = data.get('fields', {})
    assignee = fields.get('assignee')

    return {
        'key': data['key'],
        'summary': fields.get('summary', ''),
        'status': fields.get('status', {}).get('name', ''),
        'assignee': assignee.get('displayName', '') if assignee else '',
        'description': fields.get('description', ''),
        'priority': fields.get('priority', {}).get('name', ''),
        'type': fields.get('issuetype', {}).get('name', ''),
        'labels': fields.get('labels', []),
        'created': fields.get('created', ''),
        'updated': fields.get('updated', '')
    }


def create_issue(base_url, auth, project, issue_type, summary, description='', labels=None, assignee=None):
    """Create new issue"""
    url = f"{base_url}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {"key": project},
            "issuetype": {"name": issue_type},
            "summary": summary
        }
    }

    if description:
        payload["fields"]["description"] = {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
        }

    if labels:
        payload["fields"]["labels"] = labels.split(',') if isinstance(labels, str) else labels

    if assignee:
        payload["fields"]["assignee"] = {"accountId": assignee}

    response = requests.post(url, json=payload, auth=auth, timeout=30)

    if response.status_code not in [200, 201]:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return response.json()


def get_transitions(base_url, auth, issue_key):
    """Get available transitions for issue"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}/transitions"

    response = requests.get(url, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    data = response.json()
    return [{'id': t['id'], 'name': t['name']} for t in data.get('transitions', [])]


def transition_issue(base_url, auth, issue_key, transition_name, comment=None):
    """Transition issue to new status"""
    # Get available transitions
    transitions = get_transitions(base_url, auth, issue_key)
    transition_id = None

    for t in transitions:
        if t['name'].lower() == transition_name.lower():
            transition_id = t['id']
            break

    if not transition_id:
        available = ', '.join(t['name'] for t in transitions)
        print(f"ERROR: Transition '{transition_name}' not found. Available: {available}", file=sys.stderr)
        sys.exit(2)

    url = f"{base_url}/rest/api/3/issue/{issue_key}/transitions"
    payload = {"transition": {"id": transition_id}}

    response = requests.post(url, json=payload, auth=auth, timeout=30)

    if response.status_code != 204:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    if comment:
        add_comment(base_url, auth, issue_key, comment)

    return {"success": True, "issue": issue_key, "transition": transition_name}


def add_comment(base_url, auth, issue_key, comment):
    """Add comment to issue"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}/comment"
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]
        }
    }

    response = requests.post(url, json=payload, auth=auth, timeout=30)

    if response.status_code not in [200, 201]:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return response.json()


def main():
    parser = argparse.ArgumentParser(description='Jira CLI (MCP-Free)')
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # Search
    search_parser = subparsers.add_parser('search', help='Search issues with JQL')
    search_parser.add_argument('--jql', required=True, help='JQL query')
    search_parser.add_argument('--fields', default='key,summary,status,assignee')
    search_parser.add_argument('--max-results', type=int, default=50)
    search_parser.add_argument('--format', choices=['summary', 'full', 'table', 'keys'], default='summary')

    # Get
    get_parser = subparsers.add_parser('get', help='Get issue details')
    get_parser.add_argument('--issue', required=True, help='Issue key')
    get_parser.add_argument('--format', choices=['summary', 'full'], default='summary')

    # Create
    create_parser = subparsers.add_parser('create', help='Create issue')
    create_parser.add_argument('--project', required=True, help='Project key')
    create_parser.add_argument('--type', required=True, help='Issue type')
    create_parser.add_argument('--summary', required=True, help='Issue summary')
    create_parser.add_argument('--description', default='')
    create_parser.add_argument('--labels', help='Comma-separated labels')

    # Update/Transition
    update_parser = subparsers.add_parser('update', help='Update/transition issue')
    update_parser.add_argument('--issue', required=True, help='Issue key')
    update_parser.add_argument('--transition', help='Transition to status')
    update_parser.add_argument('--comment', help='Add comment')

    # Transitions
    trans_parser = subparsers.add_parser('transitions', help='Get available transitions')
    trans_parser.add_argument('--issue', required=True, help='Issue key')

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    base_url, email, token = load_credentials()
    auth = (email, token)

    if args.action == 'search':
        result = search_issues(base_url, auth, args.jql, args.fields, args.max_results)
        print(format_output(result, args.format))

    elif args.action == 'get':
        result = get_issue(base_url, auth, args.issue)
        print(format_output(result, args.format))

    elif args.action == 'create':
        result = create_issue(base_url, auth, args.project, args.type, args.summary,
                             args.description, args.labels)
        print(f"Created: {result.get('key')}")

    elif args.action == 'update':
        if args.transition:
            result = transition_issue(base_url, auth, args.issue, args.transition, args.comment)
            print(f"Transitioned {result['issue']} to {result['transition']}")
        elif args.comment:
            add_comment(base_url, auth, args.issue, args.comment)
            print(f"Comment added to {args.issue}")
        else:
            print("ERROR: Specify --transition or --comment", file=sys.stderr)
            sys.exit(2)

    elif args.action == 'transitions':
        result = get_transitions(base_url, auth, args.issue)
        for t in result:
            print(f"{t['id']}: {t['name']}")


if __name__ == '__main__':
    main()
