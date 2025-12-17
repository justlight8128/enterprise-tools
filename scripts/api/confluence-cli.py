#!/usr/bin/env python3
"""
Confluence CLI - REST API wrapper for Claude Code
Token-efficient output formats
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


def load_credentials():
    """Load credentials from environment or config file"""
    base_url = os.environ.get('CONFLUENCE_BASE_URL')
    email = os.environ.get('CONFLUENCE_EMAIL')
    token = os.environ.get('CONFLUENCE_API_TOKEN')

    if not all([base_url, email, token]):
        cred_file = Path.home() / '.enterprise-tools' / 'credentials.env'
        if cred_file.exists():
            with open(cred_file) as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        value = value.strip('"\'')
                        if key == 'CONFLUENCE_BASE_URL':
                            base_url = value
                        elif key == 'CONFLUENCE_EMAIL':
                            email = value
                        elif key == 'CONFLUENCE_API_TOKEN':
                            token = value

    if not all([base_url, email, token]):
        print("ERROR: Confluence credentials not configured.", file=sys.stderr)
        print("Run: python setup-wizard.py --service confluence", file=sys.stderr)
        sys.exit(1)

    return base_url.rstrip('/'), email, token


def html_to_text(html):
    """Convert HTML to plain text (simple)"""
    # Remove tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text


def format_output(data, format_type='summary'):
    """Token-efficient output formatting"""
    if format_type == 'full':
        return json.dumps(data, indent=2, ensure_ascii=False)

    if format_type == 'ids':
        if isinstance(data, list):
            return '\n'.join(str(item.get('id', '')) for item in data if 'id' in item)
        return str(data.get('id', ''))

    if format_type == 'markdown':
        if isinstance(data, dict) and 'content' in data:
            return data['content']

    # summary (default)
    if isinstance(data, list):
        lines = []
        for item in data:
            line = f"[{item.get('id', '')}] {item.get('title', '')}"
            if item.get('space'):
                line += f" ({item['space']})"
            if item.get('excerpt'):
                line += f"\n    {item['excerpt'][:100]}..."
            lines.append(line)
        return '\n'.join(lines) if lines else "No results found"
    elif isinstance(data, dict):
        return f"[{data.get('id', '')}] {data.get('title', '')}"

    return json.dumps(data, ensure_ascii=False)


def search_pages(base_url, auth, cql, limit=25):
    """Search pages with CQL"""
    url = f"{base_url}/wiki/rest/api/content/search"
    params = {
        'cql': cql,
        'limit': limit,
        'expand': 'space,body.view'
    }

    response = requests.get(url, params=params, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    data = response.json()
    pages = []

    for result in data.get('results', []):
        body = result.get('body', {}).get('view', {}).get('value', '')
        excerpt = html_to_text(body)[:200] if body else ''

        pages.append({
            'id': result.get('id'),
            'title': result.get('title', ''),
            'space': result.get('space', {}).get('key', ''),
            'excerpt': excerpt,
            'type': result.get('type', '')
        })

    return pages


def get_page(base_url, auth, page_id, expand='body.storage,space,version'):
    """Get page details"""
    url = f"{base_url}/wiki/rest/api/content/{page_id}"
    params = {'expand': expand}

    response = requests.get(url, params=params, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    data = response.json()
    body = data.get('body', {}).get('storage', {}).get('value', '')

    return {
        'id': data.get('id'),
        'title': data.get('title', ''),
        'space': data.get('space', {}).get('key', ''),
        'version': data.get('version', {}).get('number', 1),
        'content': html_to_text(body),
        'raw_content': body
    }


def create_page(base_url, auth, space, title, content, parent_id=None):
    """Create new page"""
    url = f"{base_url}/wiki/rest/api/content"

    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }

    if parent_id:
        payload["ancestors"] = [{"id": parent_id}]

    response = requests.post(url, json=payload, auth=auth, timeout=30)

    if response.status_code not in [200, 201]:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    data = response.json()
    return {
        'id': data.get('id'),
        'title': data.get('title'),
        'space': data.get('space', {}).get('key', '')
    }


def update_page(base_url, auth, page_id, content, title=None):
    """Update existing page"""
    # Get current version
    current = get_page(base_url, auth, page_id)

    url = f"{base_url}/wiki/rest/api/content/{page_id}"

    payload = {
        "type": "page",
        "title": title or current['title'],
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        },
        "version": {
            "number": current['version'] + 1
        }
    }

    response = requests.put(url, json=payload, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "page_id": page_id, "version": current['version'] + 1}


def list_spaces(base_url, auth, limit=50):
    """List all spaces"""
    url = f"{base_url}/wiki/rest/api/space"
    params = {'limit': limit}

    response = requests.get(url, params=params, auth=auth, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    data = response.json()
    return [
        {'key': s.get('key'), 'name': s.get('name'), 'type': s.get('type')}
        for s in data.get('results', [])
    ]


def main():
    parser = argparse.ArgumentParser(description='Confluence CLI (MCP-Free)')
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # Search
    search_parser = subparsers.add_parser('search', help='Search pages with CQL')
    search_parser.add_argument('--cql', required=True, help='CQL query')
    search_parser.add_argument('--limit', type=int, default=25)
    search_parser.add_argument('--format', choices=['summary', 'full', 'ids'], default='summary')

    # Get
    get_parser = subparsers.add_parser('get', help='Get page details')
    get_parser.add_argument('--page-id', required=True, help='Page ID')
    get_parser.add_argument('--format', choices=['summary', 'full', 'markdown'], default='summary')

    # Create
    create_parser = subparsers.add_parser('create', help='Create page')
    create_parser.add_argument('--space', required=True, help='Space key')
    create_parser.add_argument('--title', required=True, help='Page title')
    create_parser.add_argument('--content', required=True, help='Page content (HTML)')
    create_parser.add_argument('--parent-id', help='Parent page ID')

    # Update
    update_parser = subparsers.add_parser('update', help='Update page')
    update_parser.add_argument('--page-id', required=True, help='Page ID')
    update_parser.add_argument('--content', required=True, help='New content')
    update_parser.add_argument('--title', help='New title')

    # Spaces
    spaces_parser = subparsers.add_parser('spaces', help='List spaces')
    spaces_parser.add_argument('--format', choices=['summary', 'full'], default='summary')
    spaces_parser.add_argument('--limit', type=int, default=50)

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    base_url, email, token = load_credentials()
    auth = (email, token)

    if args.action == 'search':
        result = search_pages(base_url, auth, args.cql, args.limit)
        print(format_output(result, args.format))

    elif args.action == 'get':
        result = get_page(base_url, auth, args.page_id)
        print(format_output(result, args.format))

    elif args.action == 'create':
        result = create_page(base_url, auth, args.space, args.title, args.content, args.parent_id)
        print(f"Created: [{result['id']}] {result['title']} in {result['space']}")

    elif args.action == 'update':
        result = update_page(base_url, auth, args.page_id, args.content, args.title)
        print(f"Updated page {result['page_id']} to version {result['version']}")

    elif args.action == 'spaces':
        result = list_spaces(base_url, auth, args.limit)
        if args.format == 'summary':
            for s in result:
                print(f"{s['key']}: {s['name']} ({s['type']})")
        else:
            print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
