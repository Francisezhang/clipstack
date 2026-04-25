# ClipStack

**Cross-platform clipboard history manager — search, pin, and recall 1000 entries**

[English](docs/README.md) | [中文](docs/README_CN.md)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Windows%20|%20Linux-lightgrey.svg)]()

## Quick Start

```bash
# Install
pip install clipstack

# Start monitoring
clipstack start

# List history
clipstack list

# Search
clipstack search "API_KEY"

# Get entry back
clipstack get 5
```

## Features

- Background monitoring daemon
- 1000 entry history limit
- Full-text search
- Pin important entries (never deleted)
- Auto-classify: URL, code, text
- **Cross-platform auto-start**: macOS LaunchAgent, Windows Startup, Linux systemd

## Documentation

- [Full Documentation (English)](docs/README.md)
- [完整文档 (中文)](docs/README_CN.md)

## License

MIT License — Free to use, modify, and distribute.

---

**Made by [Francisezhang](https://github.com/Francisezhang)**