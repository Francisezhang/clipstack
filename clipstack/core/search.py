"""Full-text search for clipboard history."""

import sqlite3
from typing import List, Dict

from .storage import ensure_db


def search_entries(keyword: str, limit: int = 50) -> List[Dict]:
    """
    Search clipboard entries by keyword.

    Args:
        keyword: Search keyword
        limit: Max results

    Returns:
        List of matching entries with relevance score
    """
    ensure_db()

    from .storage import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Use LIKE for simple text search
    # %keyword% for partial match
    search_pattern = f"%{keyword}%"

    cursor.execute(
        """
        SELECT id, content, entry_type, is_pinned, created_at, last_used_at
        FROM clipboard_history
        WHERE content LIKE ?
        ORDER BY is_pinned DESC, created_at DESC
        LIMIT ?
        """,
        (search_pattern, limit)
    )

    rows = cursor.fetchall()
    conn.close()

    entries = []
    for row in rows:
        content = row[1]
        # Calculate relevance: keyword frequency
        relevance = content.lower().count(keyword.lower())

        entries.append({
            "id": row[0],
            "content": content,
            "type": row[2],
            "is_pinned": row[3],
            "created_at": row[4],
            "last_used_at": row[5],
            "relevance": relevance,
        })

    # Sort by relevance descending (higher first)
    entries.sort(key=lambda x: x["relevance"], reverse=True)

    return entries


def highlight_match(content: str, keyword: str) -> str:
    """
    Highlight matching keyword in content.

    Args:
        content: Original content
        keyword: Keyword to highlight

    Returns:
        Content with keyword wrapped in rich markup
    """
    # Simple highlight: wrap keyword in bold yellow
    lower_content = content.lower()
    lower_keyword = keyword.lower()

    result = []
    i = 0
    while i < len(content):
        if lower_content[i:i+len(keyword)] == lower_keyword:
            # Found match
            result.append(f"[bold yellow]{content[i:i+len(keyword)]}[/bold yellow]")
            i += len(keyword)
        else:
            result.append(content[i])
            i += 1

    return "".join(result)


def get_content_preview(content: str, max_length: int = 100) -> str:
    """Get truncated preview of content."""
    if len(content) <= max_length:
        return content

    return content[:max_length] + "..."