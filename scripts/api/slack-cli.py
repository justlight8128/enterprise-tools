#!/usr/bin/env python3
"""
Slack CLI - REST API wrapper for Claude Code
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
    bot_token = os.environ.get('SLACK_BOT_TOKEN')

    if not bot_token:
        cred_file = Path.home() / '.enterprise-tools' / 'credentials.env'
        if cred_file.exists():
            with open(cred_file, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        value = value.strip('"\'')
                        if key == 'SLACK_BOT_TOKEN':
                            bot_token = value

    if not bot_token:
        print("ERROR: Slack credentials not configured.", file=sys.stderr)
        print("Run: python setup-wizard.py --service slack", file=sys.stderr)
        sys.exit(1)

    return bot_token


def get_headers(token):
    """Get API headers"""
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=utf-8'
    }


def format_output(data, format_type='summary'):
    """Token-efficient output formatting"""
    if format_type == 'full':
        return json.dumps(data, indent=2, ensure_ascii=False)

    if format_type == 'ids':
        if isinstance(data, list):
            return '\n'.join(item.get('id', '') for item in data if 'id' in item)
        return data.get('id', '')

    # summary (default)
    if isinstance(data, list):
        lines = []
        for item in data:
            if 'name' in item:  # Channel
                line = f"#{item['name']}"
                if item.get('topic'):
                    line += f" - {item['topic'][:50]}"
                lines.append(line)
            elif 'text' in item:  # Message
                user = item.get('user', 'unknown')
                text = item['text'][:100]
                lines.append(f"@{user}: {text}")
        return '\n'.join(lines) if lines else "No results"

    return json.dumps(data, ensure_ascii=False)


def resolve_channel(token, channel):
    """Resolve channel name to ID"""
    headers = get_headers(token)

    if channel.startswith('C') and len(channel) > 8:
        return channel  # Already an ID

    # Remove # prefix if present
    channel_name = channel.lstrip('#')

    # List channels to find ID
    url = 'https://slack.com/api/conversations.list'
    params = {'types': 'public_channel,private_channel', 'limit': 200}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    data = response.json()

    if not data.get('ok'):
        print(f"ERROR: {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(2)

    for ch in data.get('channels', []):
        if ch['name'] == channel_name:
            return ch['id']

    print(f"ERROR: Channel '{channel}' not found", file=sys.stderr)
    sys.exit(2)


def resolve_user(token, user):
    """Resolve user name to ID"""
    headers = get_headers(token)

    if user.startswith('U') and len(user) > 8:
        return user  # Already an ID

    # Remove @ prefix if present
    user_name = user.lstrip('@')

    # List users to find ID
    url = 'https://slack.com/api/users.list'
    params = {'limit': 200}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    data = response.json()

    if not data.get('ok'):
        print(f"ERROR: {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(2)

    for u in data.get('members', []):
        if u.get('name') == user_name or u.get('profile', {}).get('display_name') == user_name:
            return u['id']

    print(f"ERROR: User '{user}' not found", file=sys.stderr)
    sys.exit(2)


def send_message(token, channel, message, thread_ts=None, blocks=None):
    """Send message to channel"""
    headers = get_headers(token)
    channel_id = resolve_channel(token, channel)

    url = 'https://slack.com/api/chat.postMessage'
    payload = {
        'channel': channel_id,
        'text': message
    }

    if thread_ts:
        payload['thread_ts'] = thread_ts

    if blocks:
        payload['blocks'] = json.loads(blocks) if isinstance(blocks, str) else blocks

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    data = response.json()

    if not data.get('ok'):
        print(f"ERROR: {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(2)

    return {
        'channel': data.get('channel'),
        'ts': data.get('ts'),
        'message': 'sent'
    }


def send_dm(token, user, message):
    """Send direct message"""
    headers = get_headers(token)
    user_id = resolve_user(token, user)

    # Open DM channel
    url = 'https://slack.com/api/conversations.open'
    response = requests.post(url, headers=headers, json={'users': user_id}, timeout=30)
    data = response.json()

    if not data.get('ok'):
        print(f"ERROR: {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(2)

    channel_id = data['channel']['id']

    # Send message
    return send_message(token, channel_id, message)


def list_channels(token, limit=100):
    """List channels"""
    headers = get_headers(token)
    url = 'https://slack.com/api/conversations.list'
    params = {
        'types': 'public_channel,private_channel',
        'limit': limit,
        'exclude_archived': True
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    data = response.json()

    if not data.get('ok'):
        print(f"ERROR: {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(2)

    return [
        {
            'id': ch['id'],
            'name': ch['name'],
            'topic': ch.get('topic', {}).get('value', ''),
            'members': ch.get('num_members', 0)
        }
        for ch in data.get('channels', [])
    ]


def get_history(token, channel, limit=20):
    """Get channel history"""
    headers = get_headers(token)
    channel_id = resolve_channel(token, channel)

    url = 'https://slack.com/api/conversations.history'
    params = {'channel': channel_id, 'limit': limit}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    data = response.json()

    if not data.get('ok'):
        print(f"ERROR: {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(2)

    return [
        {
            'user': msg.get('user', 'bot'),
            'text': msg.get('text', ''),
            'ts': msg.get('ts', '')
        }
        for msg in data.get('messages', [])
    ]


def search_messages(token, query, channel=None, limit=20):
    """Search messages"""
    headers = get_headers(token)
    url = 'https://slack.com/api/search.messages'

    search_query = query
    if channel:
        channel_name = channel.lstrip('#')
        search_query = f"in:#{channel_name} {query}"

    params = {'query': search_query, 'count': limit}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    data = response.json()

    if not data.get('ok'):
        print(f"ERROR: {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(2)

    matches = data.get('messages', {}).get('matches', [])
    return [
        {
            'user': m.get('user', 'unknown'),
            'text': m.get('text', '')[:200],
            'channel': m.get('channel', {}).get('name', ''),
            'ts': m.get('ts', '')
        }
        for m in matches
    ]


def main():
    parser = argparse.ArgumentParser(description='Slack CLI (MCP-Free)')
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # Send
    send_parser = subparsers.add_parser('send', help='Send message to channel')
    send_parser.add_argument('--channel', required=True, help='Channel name or ID')
    send_parser.add_argument('--message', required=True, help='Message text')
    send_parser.add_argument('--thread-ts', help='Thread timestamp for reply')
    send_parser.add_argument('--blocks', help='Block Kit JSON')

    # DM
    dm_parser = subparsers.add_parser('dm', help='Send direct message')
    dm_parser.add_argument('--user', required=True, help='User name or ID')
    dm_parser.add_argument('--message', required=True, help='Message text')

    # Channels
    channels_parser = subparsers.add_parser('channels', help='List channels')
    channels_parser.add_argument('--format', choices=['summary', 'full', 'ids'], default='summary')
    channels_parser.add_argument('--limit', type=int, default=100)

    # History
    history_parser = subparsers.add_parser('history', help='Get channel history')
    history_parser.add_argument('--channel', required=True, help='Channel name or ID')
    history_parser.add_argument('--limit', type=int, default=20)
    history_parser.add_argument('--format', choices=['summary', 'full'], default='summary')

    # Search
    search_parser = subparsers.add_parser('search', help='Search messages')
    search_parser.add_argument('--query', required=True, help='Search query')
    search_parser.add_argument('--in-channel', help='Limit to channel')
    search_parser.add_argument('--limit', type=int, default=20)
    search_parser.add_argument('--format', choices=['summary', 'full'], default='summary')

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    token = load_credentials()

    if args.action == 'send':
        result = send_message(token, args.channel, args.message, args.thread_ts, args.blocks)
        print(f"Message sent to {result['channel']} (ts: {result['ts']})")

    elif args.action == 'dm':
        result = send_dm(token, args.user, args.message)
        print(f"DM sent (ts: {result['ts']})")

    elif args.action == 'channels':
        result = list_channels(token, args.limit)
        print(format_output(result, args.format))

    elif args.action == 'history':
        result = get_history(token, args.channel, args.limit)
        print(format_output(result, args.format))

    elif args.action == 'search':
        result = search_messages(token, args.query, args.in_channel, args.limit)
        print(format_output(result, args.format))


if __name__ == '__main__':
    main()
