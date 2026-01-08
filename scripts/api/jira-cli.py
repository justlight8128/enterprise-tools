#!/usr/bin/env python3
"""
Jira CLI - REST API wrapper for Claude Code
Token-efficient output formats

Features:
- Search issues with JQL
- Create/update issues
- Transition workflow states
- Assign issues to users
- Link issues to epics
- Search users by name/email
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
    url = f"{base_url}/rest/api/3/search/jql"
    payload = {
        'jql': jql,
        'fields': [f.strip() for f in fields.split(',')],
        'maxResults': max_results
    }

    response = requests.post(url, json=payload, auth=auth, timeout=30)

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


def search_users(base_url, auth, query, max_results=10):
    """Search users by name or email"""
    url = f"{base_url}/rest/api/3/user/search"
    params = {
        'query': query,
        'maxResults': max_results
    }

    response = requests.get(url, params=params, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    users = []
    for user in response.json():
        users.append({
            'accountId': user.get('accountId', ''),
            'displayName': user.get('displayName', ''),
            'email': user.get('emailAddress', ''),
            'active': user.get('active', False)
        })

    return users


def get_user_account_id(base_url, auth, name_or_email):
    """Get user accountId by name or email"""
    users = search_users(base_url, auth, name_or_email)
    if not users:
        return None
    # Return first match
    return users[0]['accountId']


def assign_issue(base_url, auth, issue_key, assignee_account_id):
    """Assign issue to user"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}/assignee"
    payload = {"accountId": assignee_account_id}

    response = requests.put(url, json=payload, auth=auth, timeout=30)

    if response.status_code != 204:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "issue": issue_key}


def unassign_issue(base_url, auth, issue_key):
    """Remove assignee from issue"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}/assignee"
    payload = {"accountId": None}

    response = requests.put(url, json=payload, auth=auth, timeout=30)

    if response.status_code != 204:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "issue": issue_key}


def link_to_epic(base_url, auth, issue_key, epic_key):
    """Link issue to epic (set parent)"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}"
    payload = {
        "fields": {
            "parent": {"key": epic_key}
        }
    }

    response = requests.put(url, json=payload, auth=auth, timeout=30)

    if response.status_code != 204:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "issue": issue_key, "epic": epic_key}


def update_issue_fields(base_url, auth, issue_key, fields):
    """Update issue fields"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}"
    payload = {"fields": fields}

    response = requests.put(url, json=payload, auth=auth, timeout=30)

    if response.status_code != 204:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "issue": issue_key}


def get_projects(base_url, auth):
    """Get list of projects"""
    url = f"{base_url}/rest/api/3/project"

    response = requests.get(url, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    projects = []
    for proj in response.json():
        projects.append({
            'key': proj.get('key', ''),
            'name': proj.get('name', ''),
            'id': proj.get('id', '')
        })

    return projects


def set_dates(base_url, auth, issue_key, start_date=None, due_date=None):
    """Set start date and/or due date for issue"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}"
    fields = {}

    if start_date:
        fields["customfield_10015"] = start_date  # Start date custom field
    if due_date:
        fields["duedate"] = due_date

    if not fields:
        return {"success": False, "message": "No dates provided"}

    payload = {"fields": fields}
    response = requests.put(url, json=payload, auth=auth, timeout=30)

    if response.status_code != 204:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "issue": issue_key}


def clear_resolution(base_url, auth, issue_key):
    """Clear resolution (unresolve issue) by transitioning back"""
    # Get available transitions
    transitions = get_transitions(base_url, auth, issue_key)

    # Find a transition that goes back to an unresolved state
    reopen_transitions = ['해야 할 일', '진행 중', 'To Do', 'In Progress', 'Reopen', 'Back to']
    for t in transitions:
        for reopen in reopen_transitions:
            if reopen.lower() in t['name'].lower():
                transition_issue(base_url, auth, issue_key, t['name'])
                return {"success": True, "issue": issue_key, "transition": t['name']}

    return {"success": False, "message": "No reopen transition found", "available": [t['name'] for t in transitions]}


def get_comments(base_url, auth, issue_key, max_results=20):
    """Get comments for an issue"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}/comment"
    params = {'maxResults': max_results, 'orderBy': '-created'}

    response = requests.get(url, params=params, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    comments = []
    for c in response.json().get('comments', []):
        # Extract text from ADF format
        body = c.get('body', {})
        text = ""
        if isinstance(body, dict):
            for content in body.get('content', []):
                for item in content.get('content', []):
                    if item.get('type') == 'text':
                        text += item.get('text', '')
        comments.append({
            'id': c.get('id'),
            'author': c.get('author', {}).get('displayName', ''),
            'created': c.get('created', ''),
            'body': text[:200] + '...' if len(text) > 200 else text
        })

    return comments


def update_labels(base_url, auth, issue_key, add_labels=None, remove_labels=None):
    """Add or remove labels from issue"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}"

    update_payload = {"update": {"labels": []}}

    if add_labels:
        for label in add_labels:
            update_payload["update"]["labels"].append({"add": label})

    if remove_labels:
        for label in remove_labels:
            update_payload["update"]["labels"].append({"remove": label})

    response = requests.put(url, json=update_payload, auth=auth, timeout=30)

    if response.status_code != 204:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "issue": issue_key}


def set_priority(base_url, auth, issue_key, priority_name):
    """Set issue priority"""
    url = f"{base_url}/rest/api/3/issue/{issue_key}"
    payload = {"fields": {"priority": {"name": priority_name}}}

    response = requests.put(url, json=payload, auth=auth, timeout=30)

    if response.status_code != 204:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "issue": issue_key, "priority": priority_name}


def get_priorities(base_url, auth):
    """Get available priorities"""
    url = f"{base_url}/rest/api/3/priority"

    response = requests.get(url, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return [{'id': p['id'], 'name': p['name']} for p in response.json()]


def link_issues(base_url, auth, from_issue, to_issue, link_type):
    """Create link between two issues"""
    url = f"{base_url}/rest/api/3/issueLink"
    payload = {
        "type": {"name": link_type},
        "inwardIssue": {"key": from_issue},
        "outwardIssue": {"key": to_issue}
    }

    response = requests.post(url, json=payload, auth=auth, timeout=30)

    if response.status_code not in [200, 201]:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "from": from_issue, "to": to_issue, "type": link_type}


def get_link_types(base_url, auth):
    """Get available issue link types"""
    url = f"{base_url}/rest/api/3/issueLinkType"

    response = requests.get(url, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return [{'name': lt['name'], 'inward': lt['inward'], 'outward': lt['outward']}
            for lt in response.json().get('issueLinkTypes', [])]


def get_sprints(base_url, auth, board_id=None):
    """Get sprints (requires board_id or searches all boards)"""
    # First get boards if no board_id
    if not board_id:
        boards_url = f"{base_url}/rest/agile/1.0/board"
        response = requests.get(boards_url, auth=auth, timeout=30)
        if response.status_code != 200:
            print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
            sys.exit(2)
        boards = response.json().get('values', [])
        if not boards:
            return []
        board_id = boards[0]['id']  # Use first board

    url = f"{base_url}/rest/agile/1.0/board/{board_id}/sprint"
    params = {'state': 'active,future'}

    response = requests.get(url, params=params, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    sprints = []
    for s in response.json().get('values', []):
        sprints.append({
            'id': s['id'],
            'name': s['name'],
            'state': s['state'],
            'startDate': s.get('startDate', ''),
            'endDate': s.get('endDate', '')
        })

    return sprints


def move_to_sprint(base_url, auth, issue_key, sprint_id):
    """Move issue to sprint"""
    url = f"{base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
    payload = {"issues": [issue_key]}

    response = requests.post(url, json=payload, auth=auth, timeout=30)

    if response.status_code != 204:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "issue": issue_key, "sprint": sprint_id}


def get_boards(base_url, auth):
    """Get all boards"""
    url = f"{base_url}/rest/agile/1.0/board"

    response = requests.get(url, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return [{'id': b['id'], 'name': b['name'], 'type': b.get('type', '')}
            for b in response.json().get('values', [])]


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
    create_parser.add_argument('--assignee', help='Assignee name or email')
    create_parser.add_argument('--epic', help='Epic key to link to')

    # Update/Transition
    update_parser = subparsers.add_parser('update', help='Update/transition issue')
    update_parser.add_argument('--issue', required=True, help='Issue key')
    update_parser.add_argument('--transition', help='Transition to status')
    update_parser.add_argument('--comment', help='Add comment')
    update_parser.add_argument('--assignee', help='Change assignee (name or email)')
    update_parser.add_argument('--summary', help='Update summary')

    # Transitions
    trans_parser = subparsers.add_parser('transitions', help='Get available transitions')
    trans_parser.add_argument('--issue', required=True, help='Issue key')

    # Assign
    assign_parser = subparsers.add_parser('assign', help='Assign issue to user')
    assign_parser.add_argument('--issue', required=True, help='Issue key')
    assign_parser.add_argument('--user', required=True, help='User name or email (use "none" to unassign)')

    # Link to Epic
    epic_parser = subparsers.add_parser('link-epic', help='Link issue to epic')
    epic_parser.add_argument('--issue', required=True, help='Issue key to link')
    epic_parser.add_argument('--epic', required=True, help='Epic key')

    # Users search
    users_parser = subparsers.add_parser('users', help='Search users')
    users_parser.add_argument('--query', required=True, help='Search query (name or email)')
    users_parser.add_argument('--format', choices=['summary', 'full'], default='summary')

    # Projects list
    projects_parser = subparsers.add_parser('projects', help='List projects')

    # Set dates
    dates_parser = subparsers.add_parser('dates', help='Set start/due dates')
    dates_parser.add_argument('--issue', required=True, help='Issue key')
    dates_parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    dates_parser.add_argument('--due', help='Due date (YYYY-MM-DD)')

    # Unresolve (clear resolution)
    unresolve_parser = subparsers.add_parser('unresolve', help='Clear resolution and reopen issue')
    unresolve_parser.add_argument('--issue', required=True, help='Issue key')

    # Comments
    comments_parser = subparsers.add_parser('comments', help='Get issue comments')
    comments_parser.add_argument('--issue', required=True, help='Issue key')
    comments_parser.add_argument('--max-results', type=int, default=20)

    # Labels
    labels_parser = subparsers.add_parser('labels', help='Add or remove labels')
    labels_parser.add_argument('--issue', required=True, help='Issue key')
    labels_parser.add_argument('--add', help='Labels to add (comma-separated)')
    labels_parser.add_argument('--remove', help='Labels to remove (comma-separated)')

    # Priority
    priority_parser = subparsers.add_parser('priority', help='Set issue priority')
    priority_parser.add_argument('--issue', help='Issue key (optional, lists priorities if not provided)')
    priority_parser.add_argument('--set', help='Priority name to set')

    # Issue links
    link_parser = subparsers.add_parser('link', help='Link two issues')
    link_parser.add_argument('--from', dest='from_issue', help='Source issue key')
    link_parser.add_argument('--to', dest='to_issue', help='Target issue key')
    link_parser.add_argument('--type', dest='link_type', help='Link type (e.g., "Blocks", "Relates")')
    link_parser.add_argument('--list-types', action='store_true', help='List available link types')

    # Sprints
    sprint_parser = subparsers.add_parser('sprints', help='List or manage sprints')
    sprint_parser.add_argument('--board', type=int, help='Board ID (optional)')
    sprint_parser.add_argument('--move', help='Issue key to move to sprint')
    sprint_parser.add_argument('--to', type=int, dest='sprint_id', help='Sprint ID to move issue to')

    # Boards
    boards_parser = subparsers.add_parser('boards', help='List boards')

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
        # Resolve assignee name to accountId if provided
        assignee_id = None
        if args.assignee:
            assignee_id = get_user_account_id(base_url, auth, args.assignee)
            if not assignee_id:
                print(f"WARNING: User '{args.assignee}' not found, creating without assignee", file=sys.stderr)

        result = create_issue(base_url, auth, args.project, args.type, args.summary,
                             args.description, args.labels, assignee_id)
        issue_key = result.get('key')
        print(f"Created: {issue_key}")

        # Link to epic if specified
        if args.epic and issue_key:
            link_to_epic(base_url, auth, issue_key, args.epic)
            print(f"Linked to epic: {args.epic}")

    elif args.action == 'update':
        updated = False

        # Handle assignee change
        if args.assignee:
            assignee_id = get_user_account_id(base_url, auth, args.assignee)
            if assignee_id:
                assign_issue(base_url, auth, args.issue, assignee_id)
                print(f"Assigned {args.issue} to {args.assignee}")
                updated = True
            else:
                print(f"WARNING: User '{args.assignee}' not found", file=sys.stderr)

        # Handle summary change
        if args.summary:
            update_issue_fields(base_url, auth, args.issue, {"summary": args.summary})
            print(f"Updated summary of {args.issue}")
            updated = True

        # Handle transition
        if args.transition:
            result = transition_issue(base_url, auth, args.issue, args.transition, args.comment)
            print(f"Transitioned {result['issue']} to {result['transition']}")
            updated = True
        elif args.comment:
            add_comment(base_url, auth, args.issue, args.comment)
            print(f"Comment added to {args.issue}")
            updated = True

        if not updated:
            print("ERROR: Specify --transition, --comment, --assignee, or --summary", file=sys.stderr)
            sys.exit(2)

    elif args.action == 'transitions':
        result = get_transitions(base_url, auth, args.issue)
        for t in result:
            print(f"{t['id']}: {t['name']}")

    elif args.action == 'assign':
        if args.user.lower() == 'none':
            unassign_issue(base_url, auth, args.issue)
            print(f"Unassigned {args.issue}")
        else:
            assignee_id = get_user_account_id(base_url, auth, args.user)
            if not assignee_id:
                print(f"ERROR: User '{args.user}' not found", file=sys.stderr)
                sys.exit(2)
            assign_issue(base_url, auth, args.issue, assignee_id)
            print(f"Assigned {args.issue} to {args.user}")

    elif args.action == 'link-epic':
        link_to_epic(base_url, auth, args.issue, args.epic)
        print(f"Linked {args.issue} to epic {args.epic}")

    elif args.action == 'users':
        result = search_users(base_url, auth, args.query)
        if args.format == 'full':
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            for user in result:
                status = "active" if user['active'] else "inactive"
                print(f"{user['displayName']} ({user['email']}) [{status}] - {user['accountId']}")

    elif args.action == 'projects':
        result = get_projects(base_url, auth)
        for proj in result:
            print(f"{proj['key']}: {proj['name']}")

    elif args.action == 'dates':
        if not args.start and not args.due:
            print("ERROR: Specify --start and/or --due date", file=sys.stderr)
            sys.exit(2)
        set_dates(base_url, auth, args.issue, args.start, args.due)
        msgs = []
        if args.start:
            msgs.append(f"start={args.start}")
        if args.due:
            msgs.append(f"due={args.due}")
        print(f"Updated {args.issue}: {', '.join(msgs)}")

    elif args.action == 'unresolve':
        result = clear_resolution(base_url, auth, args.issue)
        if result.get('success'):
            print(f"Reopened {args.issue} → {result.get('transition')}")
        else:
            print(f"Failed: {result.get('message')}", file=sys.stderr)
            if result.get('available'):
                print(f"Available transitions: {', '.join(result['available'])}", file=sys.stderr)
            sys.exit(2)

    elif args.action == 'comments':
        result = get_comments(base_url, auth, args.issue, args.max_results)
        if not result:
            print("No comments found")
        else:
            for c in result:
                print(f"[{c['created'][:10]}] {c['author']}: {c['body']}")

    elif args.action == 'labels':
        if not args.add and not args.remove:
            print("ERROR: Specify --add and/or --remove labels", file=sys.stderr)
            sys.exit(2)
        add_list = [l.strip() for l in args.add.split(',')] if args.add else None
        remove_list = [l.strip() for l in args.remove.split(',')] if args.remove else None
        update_labels(base_url, auth, args.issue, add_list, remove_list)
        msgs = []
        if add_list:
            msgs.append(f"added: {', '.join(add_list)}")
        if remove_list:
            msgs.append(f"removed: {', '.join(remove_list)}")
        print(f"Updated {args.issue} labels: {'; '.join(msgs)}")

    elif args.action == 'priority':
        if not args.issue:
            # List priorities
            result = get_priorities(base_url, auth)
            print("Available priorities:")
            for p in result:
                print(f"  {p['name']}")
        elif args.set:
            set_priority(base_url, auth, args.issue, args.set)
            print(f"Set {args.issue} priority to {args.set}")
        else:
            print("ERROR: Specify --set priority", file=sys.stderr)
            sys.exit(2)

    elif args.action == 'link':
        if args.list_types:
            result = get_link_types(base_url, auth)
            print("Available link types:")
            for lt in result:
                print(f"  {lt['name']}: {lt['outward']} / {lt['inward']}")
        elif args.from_issue and args.to_issue and args.link_type:
            link_issues(base_url, auth, args.from_issue, args.to_issue, args.link_type)
            print(f"Linked {args.from_issue} → {args.to_issue} ({args.link_type})")
        else:
            print("ERROR: Specify --from, --to, --type or use --list-types", file=sys.stderr)
            sys.exit(2)

    elif args.action == 'sprints':
        if args.move and args.sprint_id:
            move_to_sprint(base_url, auth, args.move, args.sprint_id)
            print(f"Moved {args.move} to sprint {args.sprint_id}")
        else:
            result = get_sprints(base_url, auth, args.board)
            if not result:
                print("No active/future sprints found")
            else:
                for s in result:
                    dates = f" ({s['startDate'][:10]} ~ {s['endDate'][:10]})" if s['startDate'] else ""
                    print(f"{s['id']}: {s['name']} [{s['state']}]{dates}")

    elif args.action == 'boards':
        result = get_boards(base_url, auth)
        for b in result:
            print(f"{b['id']}: {b['name']} ({b['type']})")


if __name__ == '__main__':
    main()
