"""SQLite storage for clipboard history."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

# Storage paths
CLIPSTACK_DIR = Path.home() / ".clipstack"
DB_PATH = CLIPSTACK_DIR / "history.db"
PID_PATH = CLIPSTACK_DIR / "daemon.pid"

# Max entries before auto-delete oldest
DEFAULT_MAX_ENTRIES = 1000


def ensure_db() -> None:
    """Ensure database exists with proper schema."""
    CLIPSTACK_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clipboard_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            content_hash TEXT,
            entry_type TEXT DEFAULT 'text',
            is_pinned INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            last_used_at TEXT
        )
    """)

    # Index for search
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_hash
        ON clipboard_history(content_hash)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_created_at
        ON clipboard_history(created_at)
    """)

    conn.commit()
    conn.close()


def get_content_hash(content: str) -> str:
    """Get hash of content for deduplication."""
    return hashlib.md5(content.encode()).hexdigest()


def classify_content(content: str) -> str:
    """Classify content type: url, code, text."""
    content = content.strip()

    # URL detection
    if content.startswith(("http://", "https://", "ftp://")):
        return "url"

    # Code detection (contains common code patterns)
    code_patterns = [
        "def ", "class ", "function ", "import ", "from ",
        "return ", "if ", "else ", "for ", "while ",
        "{", "}", "()", "[]", "->", "::", "===",
    ]
    if any(pattern in content for pattern in code_patterns):
        return "code"

    # Has indentation or special chars
    if "\n" in content and any(line.startswith((" ", "\t")) for line in content.split("\n") if line):
        return "code"

    return "text"


def add_entry(content: str) -> int:
    """
    Add clipboard entry to history.

    Args:
        content: Clipboard content

    Returns:
        Entry ID
    """
    ensure_db()

    content_hash = get_content_hash(content)
    entry_type = classify_content(content)
    created_at = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check for duplicate
    cursor.execute(
        "SELECT id FROM clipboard_history WHERE content_hash = ? ORDER BY created_at DESC LIMIT 1",
        (content_hash,)
    )
    existing = cursor.fetchone()

    if existing:
        # Update last_used_at for existing entry
        cursor.execute(
            "UPDATE clipboard_history SET last_used_at = ? WHERE id = ?",
            (created_at, existing[0])
        )
        entry_id = existing[0]
    else:
        # Insert new entry
        cursor.execute(
            "INSERT INTO clipboard_history (content, content_hash, entry_type, created_at) VALUES (?, ?, ?, ?)",
            (content, content_hash, entry_type, created_at)
        )
        entry_id = cursor.lastrowid

    # Auto-delete oldest if exceeds max (excluding pinned)
    cursor.execute("SELECT COUNT(*) FROM clipboard_history WHERE is_pinned = 0")
    unpinned_count = cursor.fetchone()[0]

    if unpinned_count > DEFAULT_MAX_ENTRIES:
        delete_count = unpinned_count - DEFAULT_MAX_ENTRIES
        cursor.execute(
            "DELETE FROM clipboard_history WHERE is_pinned = 0 ORDER BY created_at ASC LIMIT ?",
            (delete_count,)
        )

    conn.commit()
    conn.close()

    return entry_id


def get_entries(
    limit: int = 20,
    entry_type: str = "all",
    pinned_only: bool = False,
) -> List[Dict]:
    """
    Get clipboard entries.

    Args:
        limit: Max entries to return
        entry_type: Filter by type (text, url, code, all)
        pinned_only: Only return pinned entries

    Returns:
        List of entry dicts
    """
    ensure_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT id, content, entry_type, is_pinned, created_at, last_used_at FROM clipboard_history"
    conditions = []
    params = []

    if entry_type != "all":
        conditions.append("entry_type = ?")
        params.append(entry_type)

    if pinned_only:
        conditions.append("is_pinned = 1")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY is_pinned DESC, created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    entries = []
    for row in rows:
        entries.append({
            "id": row[0],
            "content": row[1],
            "type": row[2],
            "is_pinned": row[3],
            "created_at": row[4],
            "last_used_at": row[5],
        })

    return entries


def get_entry_by_id(entry_id: int) -> Optional[Dict]:
    """Get specific entry by ID."""
    ensure_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, content, entry_type, is_pinned, created_at, last_used_at FROM clipboard_history WHERE id = ?",
        (entry_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "content": row[1],
            "type": row[2],
            "is_pinned": row[3],
            "created_at": row[4],
            "last_used_at": row[5],
        }
    return None


def get_last_entry() -> Optional[Dict]:
    """Get most recent entry."""
    ensure_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, content, entry_type, is_pinned, created_at FROM clipboard_history ORDER BY created_at DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "content": row[1],
            "type": row[2],
            "is_pinned": row[3],
            "created_at": row[4],
        }
    return None


def pin_entry(entry_id: int) -> bool:
    """Pin an entry (won't be auto-deleted)."""
    ensure_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE clipboard_history SET is_pinned = 1 WHERE id = ?", (entry_id,))
    success = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return success


def unpin_entry(entry_id: int) -> bool:
    """Unpin an entry."""
    ensure_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE clipboard_history SET is_pinned = 0 WHERE id = ?", (entry_id,))
    success = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return success


def delete_entry(entry_id: int) -> bool:
    """Delete specific entry."""
    ensure_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clipboard_history WHERE id = ?", (entry_id,))
    success = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return success


def clear_history(keep_pinned: bool = False) -> int:
    """
    Clear all history.

    Args:
        keep_pinned: Keep pinned entries

    Returns:
        Number of entries deleted
    """
    ensure_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if keep_pinned:
        cursor.execute("DELETE FROM clipboard_history WHERE is_pinned = 0")
    else:
        cursor.execute("DELETE FROM clipboard_history")

    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted_count


def get_stats() -> Dict:
    """Get storage statistics."""
    ensure_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM clipboard_history")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM clipboard_history WHERE is_pinned = 1")
    pinned = cursor.fetchone()[0]

    cursor.execute("SELECT entry_type, COUNT(*) FROM clipboard_history GROUP BY entry_type")
    by_type = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    return {
        "total_entries": total,
        "pinned_entries": pinned,
        "by_type": by_type,
        "max_entries": DEFAULT_MAX_ENTRIES,
    }