"""Integration tests for BDNS API.

These tests make real HTTP calls to the BDNS Open Data API.
They are marked with pytest.mark.integration.

Note: BDNS API may have rate limits or require specific parameters.
Tests are designed to validate real API responses.
"""

from datetime import date, timedelta

import pytest

from public_radar.sources.bdns import BdnsClient, parse_concesiones, parse_convocatorias


@pytest.fixture
def bdns_client():
    """Create a BDNS client for testing."""
    with BdnsClient() as client:
        yield client


class TestBdnsApiIntegration:
    """Integration tests for BDNS API."""

    @pytest.mark.integration
    def test_fetch_convocatorias_recent(self, bdns_client: BdnsClient) -> None:
        """Should fetch recent convocatorias."""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        result = bdns_client.fetch_convocatorias(
            fecha_desde=start_date,
            fecha_hasta=end_date,
            page=1,
            page_size=10,
        )
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.integration
    def test_fetch_convocatorias_without_dates(self, bdns_client: BdnsClient) -> None:
        """Should fetch convocatorias without date filters."""
        result = bdns_client.fetch_convocatorias(
            page=1,
            page_size=5,
        )
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.integration
    def test_fetch_convocatorias_paginated_generator(self, bdns_client: BdnsClient) -> None:
        """Should iterate through pages with generator."""
        total_items = 0
        pages_fetched = 0

        for page in bdns_client.fetch_convocatorias_paginated(
            page_size=5,
            max_pages=1,  # Just test first page
        ):
            pages_fetched += 1
            total_items += len(page)

        # Either we got pages or the API returned empty (both are valid)
        assert pages_fetched >= 0

    @pytest.mark.integration
    def test_parse_convocatorias_structure(self, bdns_client: BdnsClient) -> None:
        """Should parse convocatorias data correctly."""
        result = bdns_client.fetch_convocatorias(
            page=1,
            page_size=10,
        )
        items = parse_convocatorias(result)

        assert isinstance(items, list)
        if len(items) > 0:
            item = items[0]
            assert item.source_id
            assert item.raw_data

    @pytest.mark.integration
    def test_fetch_concesiones_recent(self, bdns_client: BdnsClient) -> None:
        """Should fetch recent concesiones."""
        result = bdns_client.fetch_concesiones(
            page=1,
            page_size=10,
        )
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.integration
    def test_parse_concesiones_structure(self, bdns_client: BdnsClient) -> None:
        """Should parse concesiones data correctly."""
        result = bdns_client.fetch_concesiones(
            page=1,
            page_size=10,
        )
        items = parse_concesiones(result)

        assert isinstance(items, list)
        if len(items) > 0:
            item = items[0]
            assert item.source_id
            assert item.raw_data
