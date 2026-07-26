"""Tests for the engram list command."""

import sys
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO


def test_list_json_empty(capsys):
    """Test that --json flag outputs empty JSON array when no memories exist."""
    sys.path.insert(0, "/tmp/engram-mcp")
    from engram import cmd_list

    args = MagicMock()
    args.json = True

    with patch("engram.get_db") as mock_db:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = []
        mock_db.return_value = mock_conn

        cmd_list(args)

        captured = capsys.readouterr()
        assert captured.out.strip() == "[]"
        assert "Memory bank is empty" not in captured.out


def test_list_json_with_data(capsys):
    """Test that --json flag outputs valid JSON array."""
    sys.path.insert(0, "/tmp/engram-mcp")
    from engram import cmd_list

    args = MagicMock()
    args.json = True

    with patch("engram.get_db") as mock_db:
        mock_conn = MagicMock()
        mock_row = {"id": "abc123", "category": "project", "content": "Test memory", "importance": 5, "created_at": "2026-01-01"}
        mock_conn.execute.return_value.fetchall.return_value = [mock_row]
        mock_db.return_value = mock_conn

        cmd_list(args)

        captured = capsys.readouterr()
        assert '"abc123"' in captured.out
        assert '"project"' in captured.out
        assert '"Test memory"' in captured.out
