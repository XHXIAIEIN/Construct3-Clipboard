"""Tests for ErrorNotebook."""
import json
import pytest
from src.errors.notebook import ErrorNotebook


def test_report_creates_entry(tmp_path):
    nb = ErrorNotebook(tmp_path)
    entry_id = nb.report(
        source="test",
        error_message="something went wrong",
        error_type="ValidationError",
    )
    assert nb.jsonl_path.exists()
    lines = [l for l in nb.jsonl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["id"] == entry_id
    assert entry["status"] == "pending"
    assert "ERR-" in entry_id


def test_pending_returns_pending_entries(tmp_path):
    nb = ErrorNotebook(tmp_path)
    nb.report(source="a", error_message="err1", error_type="TypeA")
    nb.report(source="b", error_message="err2", error_type="TypeB")
    pending = nb.get_pending()
    assert len(pending) == 2
    assert all(e["status"] == "pending" for e in pending)


def test_stats(tmp_path):
    nb = ErrorNotebook(tmp_path)
    nb.report(source="x", error_message="e1", error_type="TypeA")
    nb.report(source="x", error_message="e2", error_type="TypeA")
    nb.report(source="y", error_message="e3", error_type="TypeB")
    stats = nb.get_stats()
    assert stats["total"] == 3
    assert stats["by_type"]["TypeA"] == 2
    assert stats["by_type"]["TypeB"] == 1
    assert stats["by_status"]["pending"] == 3
