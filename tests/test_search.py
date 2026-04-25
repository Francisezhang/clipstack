"""Tests for search module."""

import pytest
from pathlib import Path
import tempfile

from clipstack.core.storage import add_entry, clear_history
from clipstack.core.search import search_entries, highlight_match, get_content_preview


@pytest.fixture(autouse=True)
def temp_db():
    """Use temporary database."""
    temp_dir = Path(tempfile.mkdtemp())

    import clipstack.core.storage as storage_module
    storage_module.CLIPSTACK_DIR = temp_dir
    storage_module.DB_PATH = temp_dir / "history.db"

    yield

    storage_module.CLIPSTACK_DIR = Path.home() / ".clipstack"
    storage_module.DB_PATH = storage_module.CLIPSTACK_DIR / "history.db"


def test_search_exact_match():
    """Test search finds exact match."""
    clear_history()
    add_entry("Hello World")
    add_entry("Different content")

    results = search_entries("Hello")
    assert len(results) >= 1
    assert "Hello" in results[0]["content"]


def test_search_partial_match():
    """Test search finds partial matches."""
    clear_history()
    add_entry("Python programming")
    add_entry("JavaScript code")

    results = search_entries("program")
    assert len(results) >= 1


def test_search_no_results():
    """Test search returns empty when no match."""
    clear_history()
    add_entry("Some content")

    results = search_entries("xyz123")
    assert len(results) == 0


def test_search_relevance():
    """Test search results sorted by relevance."""
    clear_history()
    add_entry("keyword keyword keyword")  # 3 occurrences
    add_entry("keyword appears once")  # 1 occurrence
    add_entry("no match here")

    results = search_entries("keyword")
    # Higher relevance should be first
    assert results[0]["relevance"] >= results[1]["relevance"]


def test_highlight_match():
    """Test keyword highlighting."""
    content = "Hello World"
    highlighted = highlight_match(content, "Hello")

    assert "Hello" in highlighted
    assert "[bold yellow]" in highlighted


def test_highlight_match_case_insensitive():
    """Test highlighting works with different case."""
    content = "HELLO world"
    highlighted = highlight_match(content, "hello")

    # Should find and highlight
    assert "[bold yellow]" in highlighted


def test_get_content_preview_short():
    """Test preview for short content."""
    content = "Short"
    preview = get_content_preview(content)

    assert preview == content


def test_get_content_preview_long():
    """Test preview truncates long content."""
    content = "This is a very long piece of content that should be truncated"
    preview = get_content_preview(content, max_length=20)

    assert len(preview) <= 23  # 20 + "..."
    assert preview.endswith("...")