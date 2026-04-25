"""ClipStack CLI entry point."""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console

from .core.storage import (
    get_entries,
    get_entry_by_id,
    get_last_entry,
    pin_entry,
    delete_entry,
    clear_history,
    get_stats,
)
from .core.search import search_entries
from .core.monitor import (
    start_daemon,
    stop_daemon,
    is_running,
    register_launchctl_service,
    unregister_launchctl_service,
)
from .utils.display import (
    show_entries_table,
    show_search_results,
    show_entry_detail,
    show_stats,
    show_daemon_status,
)

try:
    import pyperclip
except ImportError:
    pyperclip = None

app = typer.Typer(
    name="clipstack",
    help="Clipboard history manager for macOS — search, pin, recall / 剪贴板历史管理",
    add_completion=False,
)
console = Console()


@app.command("start")
def start_cmd(
    max_entries: int = typer.Option(1000, "--max", help="Max entries to keep / 最大保存数量"),
    auto_start: bool = typer.Option(False, "--auto-start", help="Register as macOS LaunchAgent / 注册开机自启"),
):
    """
    Start clipboard monitoring daemon / 启动剪贴板监控.
    """
    if is_running():
        console.print("[yellow]Daemon already running. 监控进程已运行[/yellow]")
        return

    success = start_daemon(max_entries)
    if success:
        console.print("[green]Daemon started. 监控进程已启动[/green]")
        console.print("[blue]Clipboard changes will be recorded automatically. 剪贴板变化将自动记录[/blue]")

        if auto_start:
            register_launchctl_service()
            console.print("[green]Registered as LaunchAgent (auto-start on login). 已注册开机自启[/green]")
    else:
        console.print("[red]Failed to start daemon. 启动失败[/red]")


@app.command("stop")
def stop_cmd(
    unregister: bool = typer.Option(False, "--unregister", help="Unregister LaunchAgent / 取消开机自启"),
):
    """
    Stop clipboard monitoring daemon / 停止剪贴板监控.
    """
    if unregister:
        unregister_launchctl_service()
        console.print("[yellow]Unregistered LaunchAgent. 已取消开机自启[/yellow]")

    success = stop_daemon()
    if success:
        console.print("[green]Daemon stopped. 监控进程已停止[/green]")
    else:
        console.print("[yellow]Daemon was not running. 监控进程未运行[/yellow]")


@app.command("status")
def status_cmd():
    """
    Show daemon status / 显示监控进程状态.
    """
    running = is_running()
    show_daemon_status(running)
    stats = get_stats()
    show_stats(stats)


@app.command("list")
def list_cmd(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of entries / 显示数量"),
    entry_type: str = typer.Option("all", "--type", "-t", help="Filter type: text, url, code, all / 类型筛选"),
    pinned_only: bool = typer.Option(False, "--pinned", "-p", help="Show only pinned / 仅显示置顶"),
):
    """
    List clipboard history / 显示剪贴板历史.
    """
    entries = get_entries(limit=limit, entry_type=entry_type, pinned_only=pinned_only)
    show_entries_table(entries)


@app.command("search")
def search_cmd(
    keyword: str = typer.Argument(..., help="Search keyword / 搜索关键词"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max results / 最大结果数"),
):
    """
    Search clipboard history / 搜索剪贴板历史.
    """
    entries = search_entries(keyword, limit=limit)
    show_search_results(entries, keyword)


@app.command("get")
def get_cmd(
    entry_id: str = typer.Argument(..., help="Entry ID or 'last' / 记录ID或'last'"),
    show: bool = typer.Option(False, "--show", "-s", help="Show full content / 显示完整内容"),
):
    """
    Get entry and copy to clipboard / 获取记录并复制到剪贴板.
    """
    if pyperclip is None:
        console.print("[red]Error: pyperclip not installed[/red]")
        return

    if entry_id.lower() == "last":
        entry = get_last_entry()
    else:
        try:
            id_int = int(entry_id)
            entry = get_entry_by_id(id_int)
        except ValueError:
            console.print("[red]Error: Invalid ID[/red]")
            return

    if entry is None:
        console.print("[yellow]Entry not found. 记录不存在[/yellow]")
        return

    # Copy to clipboard
    pyperclip.copy(entry["content"])
    console.print(f"[green]Copied entry #{entry['id']} to clipboard. 已复制#{entry['id']}到剪贴板[/green]")

    if show:
        show_entry_detail(entry)


@app.command("pin")
def pin_cmd(
    entry_id: int = typer.Argument(..., help="Entry ID to pin / 要置顶的记录ID"),
):
    """
    Pin an entry (won't be auto-deleted) / 置顶记录.
    """
    success = pin_entry(entry_id)
    if success:
        console.print(f"[green]Entry #{entry_id} pinned. 已置顶#{entry_id}[/green]")
    else:
        console.print("[yellow]Entry not found. 记录不存在[/yellow]")


@app.command("unpin")
def unpin_cmd(
    entry_id: int = typer.Argument(..., help="Entry ID to unpin / 要取消置顶的记录ID"),
):
    """
    Unpin an entry / 取消置顶.
    """
    from .core.storage import unpin_entry
    success = unpin_entry(entry_id)
    if success:
        console.print(f"[yellow]Entry #{entry_id} unpinned. 已取消置顶#{entry_id}[/yellow]")
    else:
        console.print("[yellow]Entry not found. 记录不存在[/yellow]")


@app.command("delete")
def delete_cmd(
    entry_id: int = typer.Argument(..., help="Entry ID to delete / 要删除的记录ID"),
):
    """
    Delete an entry / 删除记录.
    """
    success = delete_entry(entry_id)
    if success:
        console.print(f"[red]Entry #{entry_id} deleted. 已删除#{entry_id}[/red]")
    else:
        console.print("[yellow]Entry not found. 记录不存在[/yellow]")


@app.command("clear")
def clear_cmd(
    keep_pinned: bool = typer.Option(True, "--keep-pinned", "-k", help="Keep pinned entries / 保留置顶"),
):
    """
    Clear clipboard history / 清空剪贴板历史.
    """
    deleted = clear_history(keep_pinned=keep_pinned)
    console.print(f"[red]Deleted {deleted} entries. 已删除{deleted}条记录[/red]")
    if keep_pinned:
        console.print("[yellow]Pinned entries preserved. 置顶记录已保留[/yellow]")


@app.command("export")
def export_cmd(
    format: str = typer.Option("json", "--format", "-f", help="Export format: json, txt / 导出格式"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file / 输出文件"),
):
    """
    Export clipboard history / 导出剪贴板历史.
    """
    entries = get_entries(limit=10000)  # Get all

    if not entries:
        console.print("[yellow]No entries to export. 没有可导出的记录[/yellow]")
        return

    if format == "json":
        import json
        content = json.dumps(entries, indent=2, ensure_ascii=False)
    else:
        content = "\n".join(
            f"#{e['id']} [{e['type']}] {e['created_at']}\n{e['content']}\n---"
            for e in entries
        )

    if output:
        output.write_text(content)
        console.print(f"[green]Exported to {output}. 已导出到{output}[/green]")
    else:
        console.print(content)


if __name__ == "__main__":
    app()