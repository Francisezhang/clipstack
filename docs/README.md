# ClipStack

**Clipboard history manager for macOS — search, pin, and recall up to 1000 entries.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

ClipStack automatically captures clipboard history, letting you search, pin, and recall previous copies. Never lose important clipboard content again.

**Features:**
- Background monitoring daemon
- 1000 entry history limit
- Full-text search
- Pin important entries
- Auto-classify: URL, code, text
- Export history
- macOS LaunchAgent auto-start

## Installation

```bash
cd clipstack
pip install -e .
```

## Quick Start

```bash
# Start monitoring
clipstack start

# List history
clipstack list

# Search
clipstack search "keyword"

# Get last entry
clipstack get last

# Pin an entry
clipstack pin 5

# Stop monitoring
clipstack stop
```

## Commands

### `clipstack start`

Start clipboard monitoring daemon.

Options:
- `--max`: Max entries to keep (default 1000)
- `--auto-start`: Register as macOS LaunchAgent

### `clipstack stop`

Stop daemon.

Options:
- `--unregister`: Unregister LaunchAgent

### `clipstack status`

Show daemon status and statistics.

### `clipstack list`

Show clipboard history.

Options:
- `-n, --limit`: Number of entries (default 20)
- `-t, --type`: Filter by type: text, url, code, all
- `-p, --pinned`: Show only pinned

### `clipstack search <keyword>`

Search history by keyword.

Options:
- `-n, --limit`: Max results

### `clipstack get <id>`

Get entry and copy to clipboard. Use "last" for most recent.

Options:
- `-s, --show`: Display full content

### `clipstack pin <id>`

Pin entry (won't be auto-deleted).

### `clipstack unpin <id>`

Unpin entry.

### `clipstack delete <id>`

Delete entry.

### `clipstack clear`

Clear all history.

Options:
- `-k, --keep-pinned`: Keep pinned entries (default true)

### `clipstack export`

Export history.

Options:
- `-f, --format`: json or txt
- `-o, --output`: Output file path

## Auto-Start on Login

```bash
# Register as LaunchAgent (starts on login)
clipstack start --auto-start

# Unregister
clipstack stop --unregister
```

## Storage

- Database: `~/.clipstack/history.db`
- PID file: `~/.clipstack/daemon.pid`
- Max 1000 entries, oldest auto-deleted (pinned preserved)

## Requirements

- Python 3.9+
- macOS
- pyperclip

## License

MIT License

---

**Made by [Francisezhang](https://github.com/Francisezhang)**