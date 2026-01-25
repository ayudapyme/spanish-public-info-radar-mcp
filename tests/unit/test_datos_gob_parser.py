"""Unit tests for datos.gob.es parser functions."""

import json
from datetime import datetime
from pathlib import Path

from public_radar.sources.datos_gob import (
    _extract_multilingual_value,
    _parse_dataset,
    _parse_date,
    parse_datasets,
    parse_publishers,
    parse_themes,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestExtractMultilingualValue:
    """Tests for _extract_multilingual_value helper."""

    def test_returns_none_for_empty(self) -> None:
        """Should return None for empty input."""
        assert _extract_multilingual_value(None) is None
        assert _extract_multilingual_value([]) is None

    def test_returns_string_directly(self) -> None:
        """Should return string input directly."""
        assert _extract_multilingual_value("hello") == "hello"

    def test_extracts_preferred_language(self) -> None:
        """Should extract value for preferred language."""
        values = [
            {"_value": "English title", "_lang": "en"},
            {"_value": "Título en español", "_lang": "es"},
        ]
        assert _extract_multilingual_value(values, prefer_lang="es") == "Título en español"
        assert _extract_multilingual_value(values, prefer_lang="en") == "English title"

    def test_falls_back_to_any_value(self) -> None:
        """Should fall back to any value if preferred not found."""
        values = [{"_value": "Some value", "_lang": "fr"}]
        assert _extract_multilingual_value(values, prefer_lang="es") == "Some value"

    def test_handles_string_items_in_list(self) -> None:
        """Should handle string items in list."""
        values = ["direct string"]
        assert _extract_multilingual_value(values) == "direct string"


class TestParseDate:
    """Tests for _parse_date helper."""

    def test_returns_none_for_empty(self) -> None:
        """Should return None for empty input."""
        assert _parse_date(None) is None
        assert _parse_date("") is None

    def test_parses_iso_format(self) -> None:
        """Should parse ISO date format."""
        result = _parse_date("2024-01-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parses_iso_datetime(self) -> None:
        """Should parse ISO datetime format."""
        result = _parse_date("2024-01-15T10:30:00")
        assert result is not None
        assert result.year == 2024
        assert result.hour == 10
        assert result.minute == 30

    def test_parses_dict_with_value(self) -> None:
        """Should parse dict with _value key."""
        result = _parse_date({"_value": "2024-06-20"})
        assert result is not None
        assert result.year == 2024
        assert result.month == 6


class TestParseDataset:
    """Tests for _parse_dataset function."""

    def test_returns_none_without_identifier(self) -> None:
        """Should return None if no identifier."""
        assert _parse_dataset({}) is None

    def test_parses_basic_dataset(self) -> None:
        """Should parse basic dataset structure."""
        item = {
            "identifier": "test-dataset-123",
            "title": [{"_value": "Test Dataset", "_lang": "es"}],
            "description": [{"_value": "A test description", "_lang": "es"}],
        }
        result = _parse_dataset(item)

        assert result is not None
        assert result.identifier == "test-dataset-123"
        assert result.title == "Test Dataset"
        assert result.description == "A test description"

    def test_extracts_identifier_from_about(self) -> None:
        """Should extract identifier from _about URL if not in identifier field."""
        item = {"_about": "http://example.com/dataset/my-dataset-id"}
        result = _parse_dataset(item)

        assert result is not None
        assert result.identifier == "my-dataset-id"

    def test_parses_themes(self) -> None:
        """Should parse themes from URIs."""
        item = {
            "identifier": "test",
            "theme": [
                "http://datos.gob.es/kos/sector-publico/sector/medio-ambiente",
                "http://datos.gob.es/kos/sector-publico/sector/economia",
            ],
        }
        result = _parse_dataset(item)

        assert result is not None
        assert "medio-ambiente" in result.themes
        assert "economia" in result.themes

    def test_parses_keywords(self) -> None:
        """Should parse keywords."""
        item = {
            "identifier": "test",
            "keyword": [
                {"_value": "environment", "_lang": "en"},
                {"_value": "clima", "_lang": "es"},
            ],
        }
        result = _parse_dataset(item)

        assert result is not None
        assert "environment" in result.keywords
        assert "clima" in result.keywords

    def test_parses_distributions(self) -> None:
        """Should parse distributions."""
        item = {
            "identifier": "test",
            "distribution": [
                {
                    "accessURL": "http://example.com/data.csv",
                    "format": {"_value": "text/csv"},
                    "title": [{"_value": "CSV format", "_lang": "es"}],
                }
            ],
        }
        result = _parse_dataset(item)

        assert result is not None
        assert len(result.distributions) == 1
        assert result.distributions[0].url == "http://example.com/data.csv"
        assert result.distributions[0].format == "text/csv"

    def test_parses_publisher(self) -> None:
        """Should parse publisher info."""
        item = {
            "identifier": "test",
            "publisher": "http://datos.gob.es/recurso/sector-publico/org/Organismo/E00125901",
        }
        result = _parse_dataset(item)

        assert result is not None
        assert result.publisher_id == "E00125901"

    def test_parses_language(self) -> None:
        """Should parse language."""
        item = {
            "identifier": "test",
            "language": ["http://publications.europa.eu/resource/authority/language/SPA"],
        }
        result = _parse_dataset(item)

        assert result is not None
        assert result.language == "SPA"

    def test_parses_spatial(self) -> None:
        """Should parse spatial coverage."""
        item = {
            "identifier": "test",
            "spatial": "http://datos.gob.es/recurso/sector-publico/territorio/Pais/España",
        }
        result = _parse_dataset(item)

        assert result is not None
        assert result.spatial == "España"


class TestParseDatasets:
    """Tests for parse_datasets function."""

    def test_returns_empty_for_no_items(self) -> None:
        """Should return empty list for no items."""
        assert parse_datasets({}) == []
        assert parse_datasets({"items": []}) == []

    def test_parses_multiple_datasets(self) -> None:
        """Should parse multiple datasets."""
        data = {
            "items": [
                {"identifier": "dataset-1", "title": "Dataset 1"},
                {"identifier": "dataset-2", "title": "Dataset 2"},
            ]
        }
        result = parse_datasets(data)

        assert len(result) == 2
        assert result[0].identifier == "dataset-1"
        assert result[1].identifier == "dataset-2"


class TestParseThemes:
    """Tests for parse_themes function."""

    def test_returns_empty_for_no_items(self) -> None:
        """Should return empty list for no items."""
        assert parse_themes([]) == []

    def test_parses_themes(self) -> None:
        """Should parse theme items."""
        items = [
            {
                "_about": "http://datos.gob.es/kos/sector-publico/sector/medio-ambiente",
                "prefLabel": [{"_value": "Medio ambiente", "_lang": "es"}],
            },
            {
                "_about": "http://datos.gob.es/kos/sector-publico/sector/economia",
                "prefLabel": [{"_value": "Economía", "_lang": "es"}],
            },
        ]
        result = parse_themes(items)

        assert len(result) == 2
        assert result[0].code == "medio-ambiente"
        assert result[0].label == "Medio ambiente"
        assert result[1].code == "economia"
        assert result[1].label == "Economía"


class TestParsePublishers:
    """Tests for parse_publishers function."""

    def test_returns_empty_for_no_items(self) -> None:
        """Should return empty list for no items."""
        assert parse_publishers({}) == []
        assert parse_publishers({"items": []}) == []

    def test_parses_uri_items(self) -> None:
        """Should parse publisher URIs."""
        data = {
            "items": [
                "http://datos.gob.es/recurso/sector-publico/org/Organismo/E00125901",
                "http://datos.gob.es/recurso/sector-publico/org/Organismo/A10002983",
            ]
        }
        result = parse_publishers(data)

        assert len(result) == 2
        assert result[0].code == "E00125901"
        assert result[1].code == "A10002983"

    def test_parses_dict_items(self) -> None:
        """Should parse publisher dict items."""
        data = {
            "items": [
                {
                    "_about": "http://datos.gob.es/recurso/sector-publico/org/Organismo/E00125901",
                    "name": "Ministry of Example",
                }
            ]
        }
        result = parse_publishers(data)

        assert len(result) == 1
        assert result[0].code == "E00125901"
        assert result[0].name == "Ministry of Example"


class TestParseDateEdgeCases:
    """Additional edge case tests for _parse_date."""

    def test_parses_datetime_with_z(self) -> None:
        """Should parse ISO datetime with Z suffix."""
        result = _parse_date("2024-01-15T10:30:00Z")
        assert result is not None
        assert result.year == 2024

    def test_parses_datetime_with_milliseconds(self) -> None:
        """Should parse ISO datetime with milliseconds."""
        result = _parse_date("2024-01-15T10:30:00.123Z")
        assert result is not None
        assert result.year == 2024

    def test_returns_datetime_directly(self) -> None:
        """Should return datetime input directly."""
        dt = datetime(2024, 1, 15, 10, 30)
        result = _parse_date(dt)
        assert result == dt

    def test_returns_none_for_invalid_date(self) -> None:
        """Should return None for unparseable date."""
        result = _parse_date("not-a-date")
        assert result is None


class TestExtractMultilingualValueEdgeCases:
    """Additional edge case tests for _extract_multilingual_value."""

    def test_converts_non_string_to_string(self) -> None:
        """Should convert non-list non-string to string."""
        result = _extract_multilingual_value(123)
        assert result == "123"

    def test_handles_dict_without_value_key(self) -> None:
        """Should handle dict items without _value."""
        values = [{"_lang": "es"}]  # Missing _value
        result = _extract_multilingual_value(values, prefer_lang="es")
        assert result is None

    def test_handles_empty_value(self) -> None:
        """Should handle dict items with empty _value."""
        values = [{"_value": "", "_lang": "es"}]
        result = _extract_multilingual_value(values, prefer_lang="es")
        assert result is None


class TestParseDatasetEdgeCases:
    """Additional edge case tests for _parse_dataset."""

    def test_handles_single_theme(self) -> None:
        """Should handle single theme (not in list)."""
        item = {
            "identifier": "test",
            "theme": "http://datos.gob.es/kos/sector-publico/sector/economia",
        }
        result = _parse_dataset(item)
        assert result is not None
        assert "economia" in result.themes

    def test_handles_theme_dict(self) -> None:
        """Should handle theme as dict."""
        item = {
            "identifier": "test",
            "theme": [{"_about": "http://datos.gob.es/kos/sector-publico/sector/transporte"}],
        }
        result = _parse_dataset(item)
        assert result is not None
        assert "transporte" in result.themes

    def test_handles_string_keywords(self) -> None:
        """Should handle plain string keywords."""
        item = {
            "identifier": "test",
            "keyword": ["keyword1", "keyword2"],
        }
        result = _parse_dataset(item)
        assert result is not None
        assert "keyword1" in result.keywords
        assert "keyword2" in result.keywords

    def test_handles_single_keyword(self) -> None:
        """Should handle single keyword (not in list)."""
        item = {
            "identifier": "test",
            "keyword": {"_value": "single-keyword"},
        }
        result = _parse_dataset(item)
        assert result is not None
        assert "single-keyword" in result.keywords

    def test_handles_single_distribution(self) -> None:
        """Should handle single distribution (not in list)."""
        item = {
            "identifier": "test",
            "distribution": {
                "accessURL": "http://example.com/data.json",
                "format": "JSON",
            },
        }
        result = _parse_dataset(item)
        assert result is not None
        assert len(result.distributions) == 1
        assert result.distributions[0].format == "JSON"

    def test_handles_format_uri(self) -> None:
        """Should extract format from URI."""
        item = {
            "identifier": "test",
            "distribution": [
                {
                    "accessURL": "http://example.com/data",
                    "format": "http://example.com/format/CSV",
                }
            ],
        }
        result = _parse_dataset(item)
        assert result is not None
        assert result.distributions[0].format == "CSV"

    def test_handles_license_dict(self) -> None:
        """Should handle license as dict."""
        item = {
            "identifier": "test",
            "license": {"_about": "http://example.com/licenses/MIT"},
        }
        result = _parse_dataset(item)
        assert result is not None
        assert result.license == "MIT"

    def test_handles_publisher_dict(self) -> None:
        """Should handle publisher as dict."""
        item = {
            "identifier": "test",
            "publisher": {
                "_about": "http://datos.gob.es/recurso/org/E00123",
                "name": "Test Organization",
            },
        }
        result = _parse_dataset(item)
        assert result is not None
        assert result.publisher_id == "E00123"
        assert result.publisher == "Test Organization"

    def test_handles_spatial_dict(self) -> None:
        """Should handle spatial as dict."""
        item = {
            "identifier": "test",
            "spatial": {"_about": "http://example.com/region/Madrid"},
        }
        result = _parse_dataset(item)
        assert result is not None
        assert result.spatial == "Madrid"

    def test_handles_single_language(self) -> None:
        """Should handle single language string."""
        item = {
            "identifier": "test",
            "language": "http://example.com/lang/ESP",
        }
        result = _parse_dataset(item)
        assert result is not None
        assert result.language == "ESP"


class TestParseThemesEdgeCases:
    """Additional edge case tests for parse_themes."""

    def test_handles_string_uri_themes(self) -> None:
        """Should handle plain URI strings as themes."""
        items = [
            "http://datos.gob.es/kos/sector-publico/sector/urbanismo",
            "http://datos.gob.es/kos/sector-publico/sector/turismo",
        ]
        result = parse_themes(items)
        assert len(result) == 2
        assert result[0].code == "urbanismo"
        assert result[1].code == "turismo"

    def test_generates_label_from_code(self) -> None:
        """Should generate label from code when not provided."""
        items = [
            "http://datos.gob.es/kos/sector-publico/sector/medio-ambiente",
        ]
        result = parse_themes(items)
        assert len(result) == 1
        assert result[0].label == "Medio Ambiente"  # Title case from code

    def test_skips_items_without_about(self) -> None:
        """Should skip dict items without _about."""
        items = [{"prefLabel": "No about"}]
        result = parse_themes(items)
        assert len(result) == 0


class TestParsePublishersEdgeCases:
    """Additional edge case tests for parse_publishers."""

    def test_handles_prefLabel_list(self) -> None:
        """Should handle prefLabel as multilingual list."""
        data = {
            "items": [
                {
                    "_about": "http://example.com/org/A123",
                    "prefLabel": [{"_value": "Organization Name", "_lang": "es"}],
                }
            ]
        }
        result = parse_publishers(data)
        assert len(result) == 1
        assert result[0].name == "Organization Name"


class TestFixtureIntegration:
    """Tests using fixture files."""

    def test_parse_datasets_fixture(self) -> None:
        """Should parse datasets from fixture file."""
        fixture_path = FIXTURES_DIR / "datos_gob_datasets_sample.json"
        if fixture_path.exists():
            with open(fixture_path) as f:
                data = json.load(f)
            result = parse_datasets(data)
            assert len(result) >= 1
            # Check first dataset has expected fields
            assert result[0].identifier is not None
            assert result[0].title is not None

    def test_parse_themes_fixture(self) -> None:
        """Should parse themes from fixture file."""
        fixture_path = FIXTURES_DIR / "datos_gob_themes.json"
        if fixture_path.exists():
            with open(fixture_path) as f:
                items = json.load(f)
            result = parse_themes(items)
            assert len(result) >= 1
            # Check themes have code and label
            for theme in result:
                assert theme.code is not None
                assert theme.label is not None

    def test_parse_publishers_fixture(self) -> None:
        """Should parse publishers from fixture file."""
        fixture_path = FIXTURES_DIR / "datos_gob_publishers.json"
        if fixture_path.exists():
            with open(fixture_path) as f:
                data = json.load(f)
            result = parse_publishers(data)
            assert len(result) >= 1
            # Check publishers have code
            for pub in result:
                assert pub.code is not None
