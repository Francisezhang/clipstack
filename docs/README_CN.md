# ClipStack 剪贴板历史管理

**macOS 剪贴板历史管理工具 — 搜索、置顶、回溯1000条记录**

## 简介

ClipStack 自动记录剪贴板历史，让你随时搜索、置顶和找回之前复制的内容。再也不怕剪贴板内容丢失了。

**核心功能：**
- 后台监控守护进程
- 1000条历史记录上限
- 全文搜索
- 置顶重要内容
- 自动分类：URL、代码、文本
- 导出历史
- macOS LaunchAgent 开机自启

## 安装

```bash
cd clipstack
pip install -e .
```

## 快速上手

```bash
# 启动监控
clipstack start

# 查看历史
clipstack list

# 搜索
clipstack search "关键词"

# 获取最近一条
clipstack get last

# 置顶记录
clipstack pin 5

# 停止监控
clipstack stop
```

## 命令详解

### `clipstack start`

启动剪贴板监控守护进程。

选项：
- `--max`: 最大保存数量（默认1000）
- `--auto-start`: 注册为 macOS LaunchAgent

### `clipstack stop`

停止监控进程。

选项：
- `--unregister`: 取消 LaunchAgent 注册

### `clipstack status`

显示监控状态和统计信息。

### `clipstack list`

显示剪贴板历史。

选项：
- `-n, --limit`: 显示数量（默认20）
- `-t, --type`: 按类型筛选：text, url, code, all
- `-p, --pinned`: 仅显示置顶

### `clipstack search <关键词>`

搜索历史记录。

选项：
- `-n, --limit`: 最大结果数

### `clipstack get <ID>`

获取记录并复制到剪贴板。使用 "last" 获取最近一条。

选项：
- `-s, --show`: 显示完整内容

### `clipstack pin <ID>`

置顶记录（不会被自动删除）。

### `clipstack unpin <ID>`

取消置顶。

### `clipstack delete <ID>`

删除记录。

### `clipstack clear`

清空历史。

选项：
- `-k, --keep-pinned`: 保留置顶记录（默认保留）

### `clipstack export`

导出历史记录。

选项：
- `-f, --format`: json 或 txt
- `-o, --output`: 输出文件路径

## 开机自启

```bash
# 注册为 LaunchAgent（登录时自动启动）
clipstack start --auto-start

# 取消注册
clipstack stop --unregister
```

## 存储

- 数据库：`~/.clipstack/history.db`
- PID文件：`~/.clipstack/daemon.pid`
- 最大1000条，超出自动删除最旧（置顶保留）

## 系统要求

- Python 3.9+
- macOS
- pyperclip

## 许可证

MIT License

---

**由 [Francisezhang](https://github.com/Francisezhang) 开发**