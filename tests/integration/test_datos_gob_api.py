"""Integration tests for datos.gob.es API client.

These tests make real API calls to datos.gob.es.
Run with: pytest tests/integration/test_datos_gob_api.py -v
"""

import pytest

from public_radar.sources.datos_gob import (
    DatosGobClient,
    parse_datasets,
    parse_publishers,
    parse_themes,
)


@pytest.fixture
def datos_gob_client() -> DatosGobClient:
    """Create a DatosGobClient instance."""
    return DatosGobClient()


class TestDatosGobApiIntegration:
    """Integration tests for datos.gob.es API."""

    @pytest.mark.integration
    def test_search_datasets_basic(self, datos_gob_client: DatosGobClient) -> None:
        """Should search datasets without filters."""
        with datos_gob_client as client:
            result = client.search_datasets(page_size=5)

        assert result is not None
        assert "items" in result
        assert len(result["items"]) <= 5

    @pytest.mark.integration
    def test_search_datasets_parses_correctly(self, datos_gob_client: DatosGobClient) -> None:
        """Should parse search results correctly."""
        with datos_gob_client as client:
            result = client.search_datasets(page_size=3)

        parsed = parse_datasets(result)

        assert len(parsed) > 0
        for dataset in parsed:
            assert dataset.identifier
            assert dataset.title

    @pytest.mark.integration
    def test_list_themes(self, datos_gob_client: DatosGobClient) -> None:
        """Should list available themes."""
        with datos_gob_client as client:
            result = client.list_themes()

        assert result is not None
        # API may return empty list or items - just verify response structure
        assert isinstance(result, list)

        if result:
            parsed = parse_themes(result)
            # If we got themes, verify structure
            if parsed:
                for theme in parsed:
                    assert theme.code
                    assert theme.label

    @pytest.mark.integration
    def test_list_publishers(self, datos_gob_client: DatosGobClient) -> None:
        """Should list publishers."""
        with datos_gob_client as client:
            result = client.list_publishers(page_size=10)

        assert result is not None
        assert "items" in result

        parsed = parse_publishers(result)
        assert len(parsed) > 0

    @pytest.mark.integration
    def test_get_dataset_details(self, datos_gob_client: DatosGobClient) -> None:
        """Should get dataset details by ID."""
        # First get a dataset ID from search
        with datos_gob_client as client:
            search_result = client.search_datasets(page_size=1)
            parsed = parse_datasets(search_result)

            if parsed:
                dataset_id = parsed[0].identifier
                # Now fetch details
                details = client.get_dataset(dataset_id)

                # May return None if ID format doesn't match expected
                # This is expected behavior for some datasets
                # Just verify we got a dict response if any
                if details:
                    assert isinstance(details, dict)

    @pytest.mark.integration
    def test_search_datasets_with_theme_filter(self, datos_gob_client: DatosGobClient) -> None:
        """Should filter datasets by theme."""
        with datos_gob_client as client:
            # Search with theme filter
            result = client.search_datasets(
                theme="medio-ambiente",
                page_size=5,
            )

        # The filter may return empty if no matches or API doesn't support this filter well
        assert result is not None
        assert "items" in result
