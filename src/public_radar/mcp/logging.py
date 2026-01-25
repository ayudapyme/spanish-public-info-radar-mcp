"""MCP tool call logging module.

This module provides JSONL-based logging for MCP tool calls, including
automatic daily file rotation and cleanup of old log files.
"""

import json
import logging
import os
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_LOGS_DIR = Path("logs")
DEFAULT_RETENTION_DAYS = 7


class ToolCallLogger:
    """Logger for MCP tool calls in JSONL format.

    Writes tool call records to daily log files with automatic rotation
    and cleanup of files older than the retention period.

    :param logs_dir: Directory to store log files.
    :type logs_dir: Path | str | None
    :param retention_days: Number of days to keep log files.
    :type retention_days: int

    Example::

        >>> tool_logger = ToolCallLogger()
        >>> tool_logger.log_call(
        ...     tool="search_grants",
        ...     input_data={"limit": 10},
        ...     output_data={"count": 5, "grants": [...]},
        ...     duration_ms=450.5,
        ...     success=True
        ... )
    """

    def __init__(
        self,
        logs_dir: Path | str | None = None,
        retention_days: int = DEFAULT_RETENTION_DAYS,
    ) -> None:
        """Initialize the tool call logger."""
        self.logs_dir = Path(logs_dir) if logs_dir else Path(os.environ.get("MCP_LOGS_DIR", DEFAULT_LOGS_DIR))
        self.retention_days = retention_days
        self._ensure_logs_dir()
        self._cleanup_old_logs()

    def _ensure_logs_dir(self) -> None:
        """Create logs directory if it doesn't exist.

        Handles permission errors gracefully by falling back to a temp directory.
        """
        try:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Fall back to temp directory if we can't create the logs dir
            import tempfile

            fallback_dir = Path(tempfile.gettempdir()) / "public_radar_logs"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            logger.warning("Cannot create logs directory %s, using fallback: %s", self.logs_dir, fallback_dir)
            self.logs_dir = fallback_dir
        except OSError as e:
            logger.error("Failed to create logs directory: %s", e)

    def _get_log_file_path(self) -> Path:
        """Get path for today's log file.

        :return: Path to the current day's JSONL log file.
        :rtype: Path
        """
        today = date.today().isoformat()
        return self.logs_dir / f"mcp_calls_{today}.jsonl"

    def _cleanup_old_logs(self) -> None:
        """Remove log files older than retention period."""
        cutoff_date = date.today() - timedelta(days=self.retention_days)

        for log_file in self.logs_dir.glob("mcp_calls_*.jsonl"):
            try:
                # Extract date from filename: mcp_calls_YYYY-MM-DD.jsonl
                date_str = log_file.stem.replace("mcp_calls_", "")
                file_date = date.fromisoformat(date_str)

                if file_date < cutoff_date:
                    log_file.unlink()
                    logger.debug("Deleted old log file: %s", log_file)
            except (ValueError, OSError) as e:
                logger.warning("Failed to process log file %s: %s", log_file, e)

    def _summarize_output(self, output_data: dict[str, Any]) -> dict[str, Any]:
        """Create a summary of the output for logging.

        :param output_data: Full output data from the tool.
        :type output_data: dict[str, Any]
        :return: Summarized output suitable for logging.
        :rtype: dict[str, Any]
        """
        summary: dict[str, Any] = {}

        if "error" in output_data:
            summary["error"] = output_data["error"]
            return summary

        if "count" in output_data:
            summary["count"] = output_data["count"]

        # Extract first item title from various list keys
        for key in ("grants", "awards", "legislation", "items", "tenders"):
            if key in output_data and output_data[key]:
                first_item = output_data[key][0]
                if isinstance(first_item, dict) and "title" in first_item:
                    title = first_item["title"]
                    if title:
                        summary["first_title"] = str(title)[:100]  # Truncate long titles
                break

        if "message" in output_data:
            summary["message"] = output_data["message"]

        return summary

    def log_call(
        self,
        tool: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        duration_ms: float,
        success: bool,
        error: str | None = None,
    ) -> None:
        """Log a tool call to the JSONL file.

        :param tool: Name of the tool that was called.
        :type tool: str
        :param input_data: Input arguments passed to the tool.
        :type input_data: dict[str, Any]
        :param output_data: Output returned by the tool.
        :type output_data: dict[str, Any]
        :param duration_ms: Duration of the call in milliseconds.
        :type duration_ms: float
        :param success: Whether the call succeeded.
        :type success: bool
        :param error: Error message if the call failed.
        :type error: str | None
        """
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "tool": tool,
            "input": input_data,
            "output_summary": self._summarize_output(output_data),
            "duration_ms": round(duration_ms, 2),
            "success": success,
            "error": error,
        }

        # Log to stdout/stderr for real-time visibility
        logger.info("Tool call: %s | success=%s | duration=%.2fms", tool, success, duration_ms)

        # Write to JSONL file
        try:
            log_file = self._get_log_file_path()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.error("Failed to write to log file: %s", e)


# Global logger instance (lazy initialization)
_tool_logger: ToolCallLogger | None = None


def get_tool_logger() -> ToolCallLogger:
    """Get or create the global tool call logger.

    :return: The tool call logger instance.
    :rtype: ToolCallLogger
    """
    global _tool_logger
    if _tool_logger is None:
        _tool_logger = ToolCallLogger()
    return _tool_logger


def log_tool_call(
    tool: str,
    input_data: dict[str, Any],
    output_data: dict[str, Any],
    duration_ms: float,
    success: bool,
    error: str | None = None,
) -> None:
    """Convenience function to log a tool call.

    :param tool: Name of the tool that was called.
    :type tool: str
    :param input_data: Input arguments passed to the tool.
    :type input_data: dict[str, Any]
    :param output_data: Output returned by the tool.
    :type output_data: dict[str, Any]
    :param duration_ms: Duration of the call in milliseconds.
    :type duration_ms: float
    :param success: Whether the call succeeded.
    :type success: bool
    :param error: Error message if the call failed.
    :type error: str | None

    Example::

        >>> log_tool_call(
        ...     tool="search_grants",
        ...     input_data={"date_from": "2024-01-01", "limit": 10},
        ...     output_data={"count": 10, "grants": [...]},
        ...     duration_ms=450.5,
        ...     success=True
        ... )
    """
    get_tool_logger().log_call(tool, input_data, output_data, duration_ms, success, error)
