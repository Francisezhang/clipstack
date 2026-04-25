"""Rich display utilities."""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

console = Console()


def format_time(timestamp: str) -> str:
    """Format ISO timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return timestamp[:16] if len(timestamp) >= 16 else timestamp


def get_content_preview(content: str, max_length: int = 50) -> str:
    """Get truncated preview."""
    if len(content) <= max_length:
        return content.replace("\n", " ↵ ")

    preview = content[:max_length].replace("\n", " ↵ ")
    return preview + "..."


def show_entries_table(entries: List[Dict], title: str = None) -> None:
    """Display entries in rich table."""
    if not entries:
        console.print("[yellow]No entries found. 没有找到记录[/yellow]")
        return

    table = Table(title=title or "Clipboard History 剪贴板历史", show_header=True)
    table.add_column("ID", style="dim", width=5)
    table.add_column("Type 类型", style="cyan", width=6)
    table.add_column("Content 内容", style="white")
    table.add_column("Time 时间", style="blue", width=16)
    table.add_column("📌", style="yellow", width=3)

    for entry in entries:
        content_preview = get_content_preview(entry["content"])
        is_pinned = "📌" if entry["is_pinned"] else ""

        # Type emoji
        type_display = entry["type"]
        if entry["type"] == "url":
            type_display = "🔗 url"
        elif entry["type"] == "code":
            type_display = "💻 code"
        else:
            type_display = "📝 text"

        table.add_row(
            str(entry["id"]),
            type_display,
            content_preview,
            format_time(entry["created_at"]),
            is_pinned,
        )

    console.print(table)
    console.print(f"\n[green]Total: {len(entries)} entries[/green]")


def show_search_results(entries: List[Dict], keyword: str) -> None:
    """Display search results with highlighted matches."""
    if not entries:
        console.print(f"[yellow]No results for '{keyword}'. 搜索'{keyword}'无结果[/yellow]")
        return

    table = Table(title=f"Search Results for '{keyword}'", show_header=True)
    table.add_column("ID", style="dim", width=5)
    table.add_column("Match 匹配", style="white")
    table.add_column("Rel 相关度", style="green", width=5)
    table.add_column("Time 时间", style="blue", width=16)

    for entry in entries:
        # Highlight keyword in content preview
        content = entry["content"]
        preview = get_content_preview(content, 80)

        # Simple highlight
        highlighted = preview.replace(
            keyword,
            f"[bold yellow]{keyword}[/bold yellow]"
        ) if keyword.lower() in preview.lower() else preview

        table.add_row(
            str(entry["id"]),
            highlighted,
            str(entry["relevance"]),
            format_time(entry["created_at"]),
        )

    console.print(table)


def show_entry_detail(entry: Dict) -> None:
    """Show full entry content."""
    console.print(Panel(
        entry["content"],
        title=f"Entry #{entry['id']} ({entry['type']})",
        subtitle=f"Created: {format_time(entry['created_at'])} | Pinned: {'Yes' if entry['is_pinned'] else 'No'}",
    ))


def show_stats(stats: Dict) -> None:
    """Display storage statistics."""
    console.print(Panel(
        f"[green]Total Entries: {stats['total_entries']}[/green]\n"
        f"[yellow]Pinned: {stats['pinned_entries']}[/yellow]\n"
        f"[blue]Max Capacity: {stats['max_entries']}[/blue]\n"
        f"[cyan]By Type: {stats['by_type']}[/cyan]",
        title="ClipStack Stats 统计信息",
    ))


def show_daemon_status(running: bool) -> None:
    """Show daemon status."""
    if running:
        console.print("[green]Daemon is running. 监控进程运行中[/green]")
    else:
        console.print("[yellow]Daemon is not running. 监控进程未运行[/yellow]")