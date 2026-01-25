"""Tests for MCP tool call logging module."""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from public_radar.mcp.logging import ToolCallLogger, get_tool_logger, log_tool_call


class TestToolCallLogger:
    """Tests for the ToolCallLogger class."""

    def test_creates_logs_directory(self, tmp_path: Path) -> None:
        """Test that the logger creates the logs directory if it doesn't exist."""
        logs_dir = tmp_path / "nonexistent" / "logs"
        _ = ToolCallLogger(logs_dir=logs_dir)

        assert logs_dir.exists()
        assert logs_dir.is_dir()

    def test_generates_daily_log_file_path(self, tmp_path: Path) -> None:
        """Test that log files are named by date."""
        logger = ToolCallLogger(logs_dir=tmp_path)
        log_file = logger._get_log_file_path()

        expected_name = f"mcp_calls_{date.today().isoformat()}.jsonl"
        assert log_file.name == expected_name
        assert log_file.parent == tmp_path

    def test_log_call_creates_file(self, tmp_path: Path) -> None:
        """Test that log_call creates a log file."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        logger.log_call(
            tool="test_tool",
            input_data={"param": "value"},
            output_data={"result": "success"},
            duration_ms=100.0,
            success=True,
        )

        log_file = logger._get_log_file_path()
        assert log_file.exists()

    def test_log_call_writes_valid_jsonl(self, tmp_path: Path) -> None:
        """Test that log entries are valid JSON."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        logger.log_call(
            tool="search_grants",
            input_data={"date_from": "2024-01-01", "limit": 10},
            output_data={"count": 5, "grants": [{"title": "Test Grant"}]},
            duration_ms=450.5,
            success=True,
        )

        log_file = logger._get_log_file_path()
        with open(log_file, encoding="utf-8") as f:
            line = f.readline()
            record = json.loads(line)

        assert record["tool"] == "search_grants"
        assert record["input"] == {"date_from": "2024-01-01", "limit": 10}
        assert record["duration_ms"] == 450.5
        assert record["success"] is True
        assert record["error"] is None
        assert "timestamp" in record

    def test_log_call_with_error(self, tmp_path: Path) -> None:
        """Test logging a failed tool call."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        logger.log_call(
            tool="get_grant_details",
            input_data={"grant_id": "123"},
            output_data={"error": "Grant not found"},
            duration_ms=50.0,
            success=False,
            error="Grant not found",
        )

        log_file = logger._get_log_file_path()
        with open(log_file, encoding="utf-8") as f:
            record = json.loads(f.readline())

        assert record["success"] is False
        assert record["error"] == "Grant not found"
        assert record["output_summary"]["error"] == "Grant not found"

    def test_log_call_appends_to_file(self, tmp_path: Path) -> None:
        """Test that multiple log calls append to the same file."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        for i in range(3):
            logger.log_call(
                tool=f"tool_{i}",
                input_data={"i": i},
                output_data={"i": i},
                duration_ms=float(i * 100),
                success=True,
            )

        log_file = logger._get_log_file_path()
        with open(log_file, encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 3

    def test_cleanup_old_logs(self, tmp_path: Path) -> None:
        """Test that old log files are cleaned up."""
        # Create old log files
        old_date = date.today() - timedelta(days=10)
        old_file = tmp_path / f"mcp_calls_{old_date.isoformat()}.jsonl"
        old_file.write_text("{}")

        recent_date = date.today() - timedelta(days=3)
        recent_file = tmp_path / f"mcp_calls_{recent_date.isoformat()}.jsonl"
        recent_file.write_text("{}")

        # Create logger with 7-day retention
        _ = ToolCallLogger(logs_dir=tmp_path, retention_days=7)

        # Old file should be deleted, recent file should remain
        assert not old_file.exists()
        assert recent_file.exists()

    def test_cleanup_ignores_invalid_filenames(self, tmp_path: Path) -> None:
        """Test that cleanup doesn't fail on invalid filenames."""
        invalid_file = tmp_path / "mcp_calls_not-a-date.jsonl"
        invalid_file.write_text("{}")

        # Should not raise
        _ = ToolCallLogger(logs_dir=tmp_path)

        # File should still exist (not deleted)
        assert invalid_file.exists()


class TestOutputSummary:
    """Tests for the output summarization functionality."""

    def test_summarize_output_with_error(self, tmp_path: Path) -> None:
        """Test summarization of error responses."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        summary = logger._summarize_output({"error": "Something went wrong"})

        assert summary == {"error": "Something went wrong"}

    def test_summarize_output_with_count(self, tmp_path: Path) -> None:
        """Test summarization extracts count."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        summary = logger._summarize_output({"count": 42, "grants": []})

        assert summary["count"] == 42

    def test_summarize_output_extracts_first_title(self, tmp_path: Path) -> None:
        """Test summarization extracts first item title."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        summary = logger._summarize_output(
            {
                "count": 2,
                "grants": [
                    {"title": "First Grant Title"},
                    {"title": "Second Grant Title"},
                ],
            }
        )

        assert summary["first_title"] == "First Grant Title"

    def test_summarize_output_truncates_long_titles(self, tmp_path: Path) -> None:
        """Test that long titles are truncated."""
        logger = ToolCallLogger(logs_dir=tmp_path)
        long_title = "A" * 200

        summary = logger._summarize_output({"count": 1, "grants": [{"title": long_title}]})

        assert len(summary["first_title"]) == 100

    def test_summarize_output_with_message(self, tmp_path: Path) -> None:
        """Test summarization extracts message."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        summary = logger._summarize_output({"count": 0, "grants": [], "message": "No results found"})

        assert summary["message"] == "No results found"

    def test_summarize_output_various_keys(self, tmp_path: Path) -> None:
        """Test summarization works with different list keys."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        # Test with different keys
        for key in ("awards", "legislation", "items", "tenders"):
            summary = logger._summarize_output({"count": 1, key: [{"title": f"Test {key}"}]})
            assert summary["first_title"] == f"Test {key}"

    def test_summarize_output_handles_null_title(self, tmp_path: Path) -> None:
        """Test summarization handles None title without error."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        # This should not raise "'NoneType' object is not subscriptable"
        summary = logger._summarize_output({"count": 1, "grants": [{"title": None}]})

        # first_title should not be in summary when title is None
        assert "first_title" not in summary
        assert summary["count"] == 1

    def test_summarize_output_handles_empty_title(self, tmp_path: Path) -> None:
        """Test summarization handles empty string title."""
        logger = ToolCallLogger(logs_dir=tmp_path)

        summary = logger._summarize_output({"count": 1, "grants": [{"title": ""}]})

        # first_title should not be in summary when title is empty string
        assert "first_title" not in summary


class TestGlobalLogger:
    """Tests for the global logger functions."""

    def test_get_tool_logger_returns_instance(self) -> None:
        """Test that get_tool_logger returns a ToolCallLogger."""
        logger = get_tool_logger()

        assert isinstance(logger, ToolCallLogger)

    def test_get_tool_logger_returns_same_instance(self) -> None:
        """Test that get_tool_logger returns the same instance."""
        logger1 = get_tool_logger()
        logger2 = get_tool_logger()

        assert logger1 is logger2

    def test_log_tool_call_convenience_function(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test the log_tool_call convenience function."""
        # Reset global logger and set custom logs dir
        import public_radar.mcp.logging as logging_module

        monkeypatch.setattr(logging_module, "_tool_logger", None)
        monkeypatch.setenv("MCP_LOGS_DIR", str(tmp_path))

        log_tool_call(
            tool="test_tool",
            input_data={"test": True},
            output_data={"result": "ok"},
            duration_ms=100.0,
            success=True,
        )

        # Check that a log file was created
        log_files = list(tmp_path.glob("mcp_calls_*.jsonl"))
        assert len(log_files) == 1

        with open(log_files[0], encoding="utf-8") as f:
            record = json.loads(f.readline())

        assert record["tool"] == "test_tool"


class TestEnvironmentConfiguration:
    """Tests for environment-based configuration."""

    def test_uses_env_var_for_logs_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that MCP_LOGS_DIR env var is respected."""
        custom_dir = tmp_path / "custom_logs"
        monkeypatch.setenv("MCP_LOGS_DIR", str(custom_dir))

        logger = ToolCallLogger()

        assert logger.logs_dir == custom_dir
        assert custom_dir.exists()

    def test_default_logs_dir_without_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test default logs directory when env var is not set."""
        monkeypatch.delenv("MCP_LOGS_DIR", raising=False)

        logger = ToolCallLogger()

        assert logger.logs_dir == Path("logs")
