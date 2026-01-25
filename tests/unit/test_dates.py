"""Unit tests for date parsing utilities."""

from datetime import UTC, date

import pytest

from public_radar.common.dates import (
    format_date_borme,
    format_date_iso,
    parse_date,
    parse_datetime,
)


class TestParseDate:
    """Tests for parse_date function."""

    def test_iso_format(self) -> None:
        """Should parse ISO 8601 format."""
        result = parse_date("2026-01-20")
        assert result == date(2026, 1, 20)

    def test_spanish_format(self) -> None:
        """Should parse Spanish date format (day first)."""
        result = parse_date("20/01/2026")
        assert result == date(2026, 1, 20)

    def test_borme_format(self) -> None:
        """Should parse BORME format (YYYYMMDD)."""
        result = parse_date("20260120")
        assert result == date(2026, 1, 20)

    def test_with_dashes(self) -> None:
        """Should parse date with dashes."""
        result = parse_date("20-01-2026")
        assert result == date(2026, 1, 20)

    def test_none_input(self) -> None:
        """Should return None for None input."""
        result = parse_date(None)
        assert result is None

    def test_empty_string(self) -> None:
        """Should return None for empty string."""
        result = parse_date("")
        assert result is None

    def test_whitespace_only(self) -> None:
        """Should return None for whitespace only."""
        result = parse_date("   ")
        assert result is None

    def test_strips_whitespace(self) -> None:
        """Should strip leading/trailing whitespace."""
        result = parse_date("  2026-01-20  ")
        assert result == date(2026, 1, 20)

    def test_invalid_date_raises(self) -> None:
        """Should raise ValueError for invalid date."""
        with pytest.raises(ValueError, match="Cannot parse date"):
            parse_date("not a date")

    def test_invalid_borme_format(self) -> None:
        """Should raise ValueError for invalid BORME format."""
        with pytest.raises(ValueError):
            parse_date("20261320")  # Invalid month


class TestParseDatetime:
    """Tests for parse_datetime function."""

    def test_iso_format_with_z(self) -> None:
        """Should parse ISO 8601 with Z timezone."""
        result = parse_datetime("2026-01-20T14:30:00Z")
        assert result is not None
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 20
        assert result.hour == 14
        assert result.minute == 30
        assert result.tzinfo is not None

    def test_iso_format_with_offset(self) -> None:
        """Should parse ISO 8601 with timezone offset."""
        result = parse_datetime("2026-01-20T14:30:00+01:00")
        assert result is not None
        assert result.hour == 14

    def test_without_timezone(self) -> None:
        """Should assume UTC for datetime without timezone."""
        result = parse_datetime("2026-01-20T14:30:00")
        assert result is not None
        assert result.tzinfo == UTC

    def test_none_input(self) -> None:
        """Should return None for None input."""
        result = parse_datetime(None)
        assert result is None

    def test_empty_string(self) -> None:
        """Should return None for empty string."""
        result = parse_datetime("")
        assert result is None

    def test_invalid_datetime_raises(self) -> None:
        """Should raise ValueError for invalid datetime."""
        with pytest.raises(ValueError, match="Cannot parse datetime"):
            parse_datetime("not a datetime")


class TestFormatDateBorme:
    """Tests for format_date_borme function."""

    def test_basic_format(self) -> None:
        """Should format date as YYYYMMDD."""
        result = format_date_borme(date(2026, 1, 20))
        assert result == "20260120"

    def test_single_digit_month(self) -> None:
        """Should zero-pad single digit month."""
        result = format_date_borme(date(2026, 1, 5))
        assert result == "20260105"

    def test_december(self) -> None:
        """Should handle December correctly."""
        result = format_date_borme(date(2026, 12, 31))
        assert result == "20261231"


class TestFormatDateIso:
    """Tests for format_date_iso function."""

    def test_basic_format(self) -> None:
        """Should format date as YYYY-MM-DD."""
        result = format_date_iso(date(2026, 1, 20))
        assert result == "2026-01-20"

    def test_single_digit_day(self) -> None:
        """Should zero-pad single digit day."""
        result = format_date_iso(date(2026, 1, 5))
        assert result == "2026-01-05"
