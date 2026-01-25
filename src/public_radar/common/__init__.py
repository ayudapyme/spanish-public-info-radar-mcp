"""Common utilities for Spanish Public Data MCP."""

from public_radar.common.dates import (
    format_date_borme,
    format_date_iso,
    format_date_spanish,
    parse_date,
    parse_datetime,
)
from public_radar.common.http import (
    HttpClientError,
    NotFoundError,
    create_http_client,
    fetch_with_retry,
)
from public_radar.common.logging import get_logger, setup_logging

__all__ = [
    # Dates
    "parse_date",
    "parse_datetime",
    "format_date_borme",
    "format_date_iso",
    "format_date_spanish",
    # HTTP
    "HttpClientError",
    "NotFoundError",
    "create_http_client",
    "fetch_with_retry",
    # Logging
    "setup_logging",
    "get_logger",
]
