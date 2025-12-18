#!/usr/bin/env python3
"""
GitLab CLI - REST API wrapper for Claude Code
Token-efficient output formats
"""

import argparse
import json
import os
import sys
import urllib.parse
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


def load_credentials():
    """Load credentials from environment or config file"""
    base_url = os.environ.get('GITLAB_BASE_URL', 'https://gitlab.com')
    token = os.environ.get('GITLAB_TOKEN')

    if not token:
        cred_file = Path.home() / '.enterprise-tools' / 'credentials.env'
        if cred_file.exists():
            with open(cred_file, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        value = value.strip('"\'')
                        if key == 'GITLAB_BASE_URL':
                            base_url = value
                        elif key == 'GITLAB_TOKEN':
                            token = value

    if not token:
        print("ERROR: GitLab credentials not configured.", file=sys.stderr)
        print("Run: python setup-wizard.py --service gitlab", file=sys.stderr)
        sys.exit(1)

    return base_url.rstrip('/'), token


def get_headers(token):
    """Get API headers"""
    return {'PRIVATE-TOKEN': token}


def encode_project(project):
    """URL encode project path"""
    return urllib.parse.quote(project, safe='')


def format_output(data, format_type='summary'):
    """Token-efficient output formatting"""
    if format_type == 'full':
        return json.dumps(data, indent=2, ensure_ascii=False)

    if format_type == 'ids':
        if isinstance(data, list):
            return '\n'.join(str(item.get('id', item.get('iid', ''))) for item in data)
        return str(data.get('id', data.get('iid', '')))

    # summary (default)
    if isinstance(data, list):
        lines = []
        for item in data:
            if 'iid' in item and 'title' in item:  # MR
                line = f"!{item['iid']}: {item['title']} [{item.get('state', '')}]"
                if item.get('author'):
                    line += f" @{item['author']}"
                lines.append(line)
            elif 'id' in item and 'status' in item:  # Pipeline
                line = f"#{item['id']}: {item.get('ref', '')} [{item['status']}]"
                lines.append(line)
            elif 'name' in item:  # Branch
                line = f"{item['name']}"
                if item.get('merged'):
                    line += " (merged)"
                lines.append(line)
        return '\n'.join(lines) if lines else "No results"

    return json.dumps(data, ensure_ascii=False)


def list_merge_requests(base_url, token, project, state='opened', limit=20):
    """List merge requests"""
    headers = get_headers(token)
    project_encoded = encode_project(project)
    url = f"{base_url}/api/v4/projects/{project_encoded}/merge_requests"
    params = {'state': state, 'per_page': limit}

    response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return [
        {
            'iid': mr['iid'],
            'title': mr['title'],
            'state': mr['state'],
            'author': mr.get('author', {}).get('username', ''),
            'source_branch': mr['source_branch'],
            'target_branch': mr['target_branch'],
            'web_url': mr['web_url']
        }
        for mr in response.json()
    ]


def get_merge_request(base_url, token, project, mr_iid):
    """Get merge request details"""
    headers = get_headers(token)
    project_encoded = encode_project(project)
    url = f"{base_url}/api/v4/projects/{project_encoded}/merge_requests/{mr_iid}"

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    mr = response.json()
    return {
        'iid': mr['iid'],
        'title': mr['title'],
        'state': mr['state'],
        'author': mr.get('author', {}).get('username', ''),
        'source_branch': mr['source_branch'],
        'target_branch': mr['target_branch'],
        'description': mr.get('description', ''),
        'web_url': mr['web_url'],
        'merge_status': mr.get('merge_status', ''),
        'has_conflicts': mr.get('has_conflicts', False)
    }


def create_merge_request(base_url, token, project, source, target, title, description=''):
    """Create merge request"""
    headers = get_headers(token)
    project_encoded = encode_project(project)
    url = f"{base_url}/api/v4/projects/{project_encoded}/merge_requests"

    payload = {
        'source_branch': source,
        'target_branch': target,
        'title': title,
        'description': description
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code not in [200, 201]:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    mr = response.json()
    return {
        'iid': mr['iid'],
        'title': mr['title'],
        'web_url': mr['web_url']
    }


def merge_mr(base_url, token, project, mr_iid, squash=False, delete_source=False):
    """Merge a merge request"""
    headers = get_headers(token)
    project_encoded = encode_project(project)
    url = f"{base_url}/api/v4/projects/{project_encoded}/merge_requests/{mr_iid}/merge"

    payload = {
        'squash': squash,
        'should_remove_source_branch': delete_source
    }

    response = requests.put(url, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "iid": mr_iid}


def list_pipelines(base_url, token, project, status=None, ref=None, limit=20):
    """List pipelines"""
    headers = get_headers(token)
    project_encoded = encode_project(project)
    url = f"{base_url}/api/v4/projects/{project_encoded}/pipelines"
    params = {'per_page': limit}

    if status:
        params['status'] = status
    if ref:
        params['ref'] = ref

    response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return [
        {
            'id': p['id'],
            'status': p['status'],
            'ref': p['ref'],
            'sha': p['sha'][:8],
            'web_url': p['web_url']
        }
        for p in response.json()
    ]


def get_pipeline(base_url, token, project, pipeline_id):
    """Get pipeline details"""
    headers = get_headers(token)
    project_encoded = encode_project(project)
    url = f"{base_url}/api/v4/projects/{project_encoded}/pipelines/{pipeline_id}"

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return response.json()


def list_jobs(base_url, token, project, pipeline_id, status=None):
    """List pipeline jobs"""
    headers = get_headers(token)
    project_encoded = encode_project(project)
    url = f"{base_url}/api/v4/projects/{project_encoded}/pipelines/{pipeline_id}/jobs"
    params = {}

    if status:
        params['scope'] = status

    response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return [
        {
            'id': j['id'],
            'name': j['name'],
            'stage': j['stage'],
            'status': j['status']
        }
        for j in response.json()
    ]


def retry_pipeline(base_url, token, project, pipeline_id):
    """Retry failed pipeline"""
    headers = get_headers(token)
    project_encoded = encode_project(project)
    url = f"{base_url}/api/v4/projects/{project_encoded}/pipelines/{pipeline_id}/retry"

    response = requests.post(url, headers=headers, timeout=30)

    if response.status_code not in [200, 201]:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return {"success": True, "pipeline_id": pipeline_id}


def list_branches(base_url, token, project, limit=20):
    """List branches"""
    headers = get_headers(token)
    project_encoded = encode_project(project)
    url = f"{base_url}/api/v4/projects/{project_encoded}/repository/branches"
    params = {'per_page': limit}

    response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(2)

    return [
        {
            'name': b['name'],
            'merged': b.get('merged', False),
            'protected': b.get('protected', False)
        }
        for b in response.json()
    ]


def main():
    parser = argparse.ArgumentParser(description='GitLab CLI (MCP-Free)')
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # MRs
    mrs_parser = subparsers.add_parser('mrs', help='List merge requests')
    mrs_parser.add_argument('--project', required=True, help='Project path (group/project)')
    mrs_parser.add_argument('--state', default='opened', choices=['opened', 'closed', 'merged', 'all'])
    mrs_parser.add_argument('--limit', type=int, default=20)
    mrs_parser.add_argument('--format', choices=['summary', 'full', 'ids'], default='summary')

    # MR
    mr_parser = subparsers.add_parser('mr', help='Get merge request details')
    mr_parser.add_argument('--project', required=True)
    mr_parser.add_argument('--mr-id', required=True, type=int)
    mr_parser.add_argument('--format', choices=['summary', 'full'], default='summary')

    # Create MR
    create_mr_parser = subparsers.add_parser('create-mr', help='Create merge request')
    create_mr_parser.add_argument('--project', required=True)
    create_mr_parser.add_argument('--source', required=True, help='Source branch')
    create_mr_parser.add_argument('--target', required=True, help='Target branch')
    create_mr_parser.add_argument('--title', required=True)
    create_mr_parser.add_argument('--description', default='')

    # Merge
    merge_parser = subparsers.add_parser('merge', help='Merge MR')
    merge_parser.add_argument('--project', required=True)
    merge_parser.add_argument('--mr-id', required=True, type=int)
    merge_parser.add_argument('--squash', action='store_true')
    merge_parser.add_argument('--delete-source', action='store_true')

    # Pipelines
    pipelines_parser = subparsers.add_parser('pipelines', help='List pipelines')
    pipelines_parser.add_argument('--project', required=True)
    pipelines_parser.add_argument('--status', choices=['running', 'pending', 'success', 'failed', 'canceled'])
    pipelines_parser.add_argument('--ref', help='Branch/tag ref')
    pipelines_parser.add_argument('--limit', type=int, default=20)
    pipelines_parser.add_argument('--format', choices=['summary', 'full', 'ids'], default='summary')

    # Pipeline
    pipeline_parser = subparsers.add_parser('pipeline', help='Get pipeline details')
    pipeline_parser.add_argument('--project', required=True)
    pipeline_parser.add_argument('--pipeline-id', required=True, type=int)

    # Jobs
    jobs_parser = subparsers.add_parser('jobs', help='List pipeline jobs')
    jobs_parser.add_argument('--project', required=True)
    jobs_parser.add_argument('--pipeline-id', required=True, type=int)
    jobs_parser.add_argument('--status', choices=['failed', 'success', 'running', 'pending'])
    jobs_parser.add_argument('--format', choices=['summary', 'full'], default='summary')

    # Retry
    retry_parser = subparsers.add_parser('retry', help='Retry pipeline')
    retry_parser.add_argument('--project', required=True)
    retry_parser.add_argument('--pipeline-id', required=True, type=int)

    # Branches
    branches_parser = subparsers.add_parser('branches', help='List branches')
    branches_parser.add_argument('--project', required=True)
    branches_parser.add_argument('--limit', type=int, default=20)
    branches_parser.add_argument('--format', choices=['summary', 'full'], default='summary')

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    base_url, token = load_credentials()

    if args.action == 'mrs':
        result = list_merge_requests(base_url, token, args.project, args.state, args.limit)
        print(format_output(result, args.format))

    elif args.action == 'mr':
        result = get_merge_request(base_url, token, args.project, args.mr_id)
        print(format_output(result, args.format))

    elif args.action == 'create-mr':
        result = create_merge_request(base_url, token, args.project, args.source,
                                      args.target, args.title, args.description)
        print(f"Created !{result['iid']}: {result['title']}\n{result['web_url']}")

    elif args.action == 'merge':
        result = merge_mr(base_url, token, args.project, args.mr_id, args.squash, args.delete_source)
        print(f"Merged !{result['iid']}")

    elif args.action == 'pipelines':
        result = list_pipelines(base_url, token, args.project, args.status, args.ref, args.limit)
        print(format_output(result, args.format))

    elif args.action == 'pipeline':
        result = get_pipeline(base_url, token, args.project, args.pipeline_id)
        print(json.dumps(result, indent=2))

    elif args.action == 'jobs':
        result = list_jobs(base_url, token, args.project, args.pipeline_id, args.status)
        if args.format == 'summary':
            for j in result:
                print(f"{j['stage']}/{j['name']}: {j['status']}")
        else:
            print(json.dumps(result, indent=2))

    elif args.action == 'retry':
        result = retry_pipeline(base_url, token, args.project, args.pipeline_id)
        print(f"Retrying pipeline #{result['pipeline_id']}")

    elif args.action == 'branches':
        result = list_branches(base_url, token, args.project, args.limit)
        print(format_output(result, args.format))


if __name__ == '__main__':
    main()
