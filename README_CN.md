# ClipStack

**跨平台剪贴板历史管理工具 — 搜索、置顶、找回1000条记录**

[English](docs/README.md) | [中文](docs/README_CN.md)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Windows%20|%20Linux-lightgrey.svg)]()

## 快速开始

```bash
# 安装
pip install clipstack

# 启动监控
clipstack start

# 显示历史
clipstack list

# 搜索
clipstack search "API_KEY"

# 取回内容
clipstack get 5
```

## 功能特点

- 后台监控守护进程
- 1000条历史记录上限
- 全文搜索
- 置顶重要内容（永不被删除）
- 自动分类：URL、代码、文本
- **跨平台自动启动**：macOS LaunchAgent、Windows Startup、Linux systemd

## 文档

- [完整文档 (English)](docs/README.md)
- [完整文档 (中文)](docs/README_CN.md)

## 许可证

MIT 许可证 — 免费使用、修改和分发。

---

**由 [Francisezhang](https://github.com/Francisezhang) 开发**