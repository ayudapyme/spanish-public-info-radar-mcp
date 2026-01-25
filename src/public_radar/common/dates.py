"""Date parsing utilities for handling various date formats.

This module provides functions for parsing dates from different
Spanish government data sources.
"""

from datetime import UTC, date, datetime
from typing import overload

from dateutil import parser as dateutil_parser


@overload
def parse_date(value: str) -> date: ...


@overload
def parse_date(value: None) -> None: ...


def parse_date(value: str | None) -> date | None:
    """Parse a date string to a date object.

    Supports various formats including:
    - ISO 8601: 2026-01-20
    - Spanish: 20/01/2026
    - BORME: 20260120

    :param value: Date string or None.
    :type value: str | None
    :return: Parsed date or None if input is None/empty.
    :rtype: date | None
    :raises ValueError: If the date cannot be parsed.

    Example::

        >>> parse_date("2026-01-20")
        date(2026, 1, 20)
        >>> parse_date("20/01/2026")
        date(2026, 1, 20)
    """
    if not value or not value.strip():
        return None

    value = value.strip()

    # Try YYYYMMDD format (BORME)
    if len(value) == 8 and value.isdigit():
        return date(int(value[:4]), int(value[4:6]), int(value[6:8]))

    # Check for ISO format (YYYY-MM-DD) - don't use dayfirst
    if len(value) == 10 and value[4] == "-" and value[7] == "-":
        try:
            parsed = dateutil_parser.parse(value, dayfirst=False)
            return parsed.date()
        except (ValueError, TypeError):
            pass

    # Use dateutil for other formats with dayfirst for European dates
    try:
        parsed = dateutil_parser.parse(value, dayfirst=True)
        return parsed.date()
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot parse date: {value}") from e


@overload
def parse_datetime(value: str) -> datetime: ...


@overload
def parse_datetime(value: None) -> None: ...


def parse_datetime(value: str | None) -> datetime | None:
    """Parse a datetime string to a datetime object.

    Supports various formats including ISO 8601 with timezone.
    Returns timezone-aware datetime in UTC when timezone info is present.

    :param value: Datetime string or None.
    :type value: str | None
    :return: Parsed datetime or None if input is None/empty.
    :rtype: datetime | None
    :raises ValueError: If the datetime cannot be parsed.

    Example::

        >>> parse_datetime("2026-01-20T14:30:00Z")
        datetime(2026, 1, 20, 14, 30, 0, tzinfo=timezone.utc)
    """
    if not value or not value.strip():
        return None

    value = value.strip()

    try:
        parsed = dateutil_parser.parse(value)
        # If no timezone, assume UTC
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot parse datetime: {value}") from e


def format_date_borme(d: date) -> str:
    """Format date for BORME API (YYYYMMDD).

    :param d: Date to format.
    :type d: date
    :return: Formatted string.
    :rtype: str

    Example::

        >>> format_date_borme(date(2026, 1, 20))
        '20260120'
    """
    return d.strftime("%Y%m%d")


def format_date_iso(d: date) -> str:
    """Format date as ISO 8601 (YYYY-MM-DD).

    :param d: Date to format.
    :type d: date
    :return: Formatted string.
    :rtype: str

    Example::

        >>> format_date_iso(date(2026, 1, 20))
        '2026-01-20'
    """
    return d.strftime("%Y-%m-%d")


def format_date_spanish(d: date) -> str:
    """Format date in Spanish format (DD/MM/YYYY).

    Used by BDNS API which requires dates in this format.

    :param d: Date to format.
    :type d: date
    :return: Formatted string.
    :rtype: str

    Example::

        >>> format_date_spanish(date(2026, 1, 20))
        '20/01/2026'
    """
    return d.strftime("%d/%m/%Y")
