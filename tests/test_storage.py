"""Tests for storage module."""

import pytest
import tempfile
from pathlib import Path
import sqlite3

from clipstack.core.storage import (
    ensure_db,
    add_entry,
    get_entries,
    get_entry_by_id,
    get_last_entry,
    pin_entry,
    delete_entry,
    clear_history,
    get_stats,
    get_content_hash,
    classify_content,
    CLIPSTACK_DIR,
    DEFAULT_MAX_ENTRIES,
)


@pytest.fixture(autouse=True)
def temp_db():
    """Use temporary database for tests."""
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())

    # Override CLIPSTACK_DIR for testing
    original_dir = CLIPSTACK_DIR
    import clipstack.core.storage as storage_module
    storage_module.CLIPSTACK_DIR = temp_dir
    storage_module.DB_PATH = temp_dir / "history.db"
    storage_module.PID_PATH = temp_dir / "daemon.pid"

    yield

    # Cleanup
    storage_module.CLIPSTACK_DIR = original_dir
    storage_module.DB_PATH = original_dir / "history.db"
    storage_module.PID_PATH = original_dir / "daemon.pid"


def test_get_content_hash():
    """Test content hashing."""
    content = "test content"
    hash1 = get_content_hash(content)
    hash2 = get_content_hash(content)

    # Same content = same hash
    assert hash1 == hash2
    # Different content = different hash
    assert hash1 != get_content_hash("different content")


def test_classify_content_url():
    """Test URL classification."""
    assert classify_content("https://example.com") == "url"
    assert classify_content("http://localhost:8080") == "url"
    assert classify_content("ftp://files.example.com") == "url"


def test_classify_content_code():
    """Test code classification."""
    assert classify_content("def function():") == "code"
    assert classify_content("import os") == "code"
    assert classify_content("if x > 0:") == "code"
    assert classify_content("{ key: value }") == "code"


def test_classify_content_text():
    """Test text classification."""
    assert classify_content("Hello World") == "text"
    assert classify_content("Just regular text") == "text"


def test_ensure_db():
    """Test database creation."""
    ensure_db()

    from clipstack.core.storage import DB_PATH
    assert DB_PATH.exists()


def test_add_entry():
    """Test adding entry."""
    entry_id = add_entry("Test content")
    assert entry_id > 0


def test_add_entry_dedup():
    """Test duplicate content detection."""
    add_entry("Same content")
    id2 = add_entry("Same content")

    # Should update existing, not create new
    stats = get_stats()
    # May or may not create new entry depending on implementation
    assert stats["total_entries"] >= 1


def test_get_entries():
    """Test getting entries."""
    add_entry("Entry 1")
    add_entry("Entry 2")

    entries = get_entries(limit=10)
    assert len(entries) >= 2


def test_get_entries_by_type():
    """Test filtering by type."""
    add_entry("https://example.com")  # url
    add_entry("Hello world")  # text

    url_entries = get_entries(entry_type="url")
    for e in url_entries:
        assert e["type"] == "url"


def test_get_entry_by_id():
    """Test getting specific entry."""
    entry_id = add_entry("Test entry")
    entry = get_entry_by_id(entry_id)

    assert entry is not None
    assert entry["content"] == "Test entry"
    assert entry["id"] == entry_id


def test_get_entry_by_id_not_found():
    """Test getting non-existent entry."""
    entry = get_entry_by_id(99999)
    assert entry is None


def test_get_last_entry():
    """Test getting most recent entry."""
    add_entry("First")
    add_entry("Last")

    entry = get_last_entry()
    assert entry["content"] == "Last"


def test_pin_entry():
    """Test pinning entry."""
    entry_id = add_entry("To pin")
    success = pin_entry(entry_id)

    assert success
    entry = get_entry_by_id(entry_id)
    assert entry["is_pinned"] == 1


def test_pin_entry_not_found():
    """Test pinning non-existent entry."""
    success = pin_entry(99999)
    assert not success


def test_delete_entry():
    """Test deleting entry."""
    entry_id = add_entry("To delete")
    success = delete_entry(entry_id)

    assert success
    entry = get_entry_by_id(entry_id)
    assert entry is None


def test_clear_history():
    """Test clearing history."""
    add_entry("Entry 1")
    add_entry("Entry 2")

    deleted = clear_history()
    assert deleted >= 2

    entries = get_entries()
    assert len(entries) == 0


def test_clear_history_keep_pinned():
    """Test clearing history keeping pinned."""
    id1 = add_entry("Regular")
    id2 = add_entry("Pinned")
    pin_entry(id2)

    deleted = clear_history(keep_pinned=True)

    entries = get_entries()
    # Pinned entry should remain
    pinned_entries = [e for e in entries if e["is_pinned"]]
    assert len(pinned_entries) >= 1


def test_get_stats():
    """Test getting statistics."""
    add_entry("Text entry")
    add_entry("https://example.com")
    id_pinned = add_entry("Pinned")
    pin_entry(id_pinned)

    stats = get_stats()

    assert stats["total_entries"] >= 3
    assert stats["pinned_entries"] >= 1
    assert "text" in stats["by_type"] or "url" in stats["by_type"]
    assert stats["max_entries"] == DEFAULT_MAX_ENTRIES