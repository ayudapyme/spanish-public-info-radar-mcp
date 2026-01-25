"""Integration tests for BOE API.

These tests make real HTTP calls to the BOE Open Data API.
They are marked with pytest.mark.integration.

Note: BOE API may not publish on weekends/holidays.
Tests are designed to validate real API responses.
"""

from datetime import date, timedelta

import pytest

from public_radar.sources.boe import (
    BoeClient,
    parse_boe_summary,
    parse_borme_summary,
    parse_legislation_search,
)


@pytest.fixture
def boe_client():
    """Create a BOE client for testing."""
    with BoeClient() as client:
        yield client


def find_recent_weekday() -> date:
    """Find the most recent weekday (Monday-Friday)."""
    target = date.today()
    while target.weekday() >= 5:  # Saturday=5, Sunday=6
        target -= timedelta(days=1)
    return target


class TestBoeApiIntegration:
    """Integration tests for BOE API."""

    @pytest.mark.integration
    def test_search_legislation(self, boe_client: BoeClient) -> None:
        """Should search legislation without query (query param is broken on BOE server)."""
        # NOTE: BOE API returns 500 when using 'query' parameter - this is a server bug
        # We test the endpoint without query which works correctly
        results = boe_client.search_legislation(
            query="",  # Empty query to avoid the 500 error bug
            limit=5,
        )
        assert results is not None
        assert isinstance(results, list)

    @pytest.mark.integration
    @pytest.mark.xfail(reason="BOE API returns 500 when using query param - server bug")
    def test_search_legislation_with_query(self, boe_client: BoeClient) -> None:
        """Should search legislation with a query - currently broken on BOE server."""
        results = boe_client.search_legislation(
            query="subvenciones",
            limit=5,
        )
        assert results is not None
        assert isinstance(results, list)

    @pytest.mark.integration
    def test_fetch_legislation_by_id(self, boe_client: BoeClient) -> None:
        """Should fetch legislation details by ID.

        Uses /metadatos endpoint which supports JSON.
        """
        # Use a known valid legislation ID
        legislation_id = "BOE-A-2015-10566"  # Ley 40/2015

        details = boe_client.fetch_legislation_by_id(legislation_id)
        assert details is not None
        assert isinstance(details, dict)
        assert details.get("identificador") == legislation_id

    @pytest.mark.integration
    def test_fetch_legislation_text(self, boe_client: BoeClient) -> None:
        """Should fetch legislation full text.

        Uses XML endpoint and parses to dict.
        """
        # Use a known valid legislation ID
        legislation_id = "BOE-A-2015-10566"  # Ley 40/2015

        text_data = boe_client.fetch_legislation_text(legislation_id)
        assert text_data is not None
        assert isinstance(text_data, dict)
        # Should contain texto with bloques
        assert "texto" in text_data or "bloque" in text_data

    @pytest.mark.integration
    def test_fetch_legislation_analysis(self, boe_client: BoeClient) -> None:
        """Should fetch legislation analysis (references, matters)."""
        legislation_id = "BOE-A-2015-10566"  # Ley 40/2015

        analysis = boe_client.fetch_legislation_analysis(legislation_id)
        assert analysis is not None
        assert isinstance(analysis, dict)
        # Should contain analysis data
        assert "materias" in analysis or "referencias" in analysis or "notas" in analysis

    @pytest.mark.integration
    def test_fetch_legislation_index(self, boe_client: BoeClient) -> None:
        """Should fetch legislation structure/index."""
        legislation_id = "BOE-A-2015-10566"  # Ley 40/2015

        index_data = boe_client.fetch_legislation_index(legislation_id)
        assert index_data is not None
        assert isinstance(index_data, dict)
        # Should contain list of blocks
        assert "bloque" in index_data
        blocks = index_data["bloque"]
        assert isinstance(blocks, list)
        assert len(blocks) > 0

    @pytest.mark.integration
    def test_fetch_legislation_block(self, boe_client: BoeClient) -> None:
        """Should fetch a specific block of legislation text."""
        legislation_id = "BOE-A-2015-10566"  # Ley 40/2015
        block_id = "a1"  # Article 1

        block_data = boe_client.fetch_legislation_block(legislation_id, block_id)
        assert block_data is not None
        assert isinstance(block_data, dict)

    @pytest.mark.integration
    def test_fetch_auxiliary_table_departments(self, boe_client: BoeClient) -> None:
        """Should fetch departments auxiliary table.

        Note: BOE API returns departments as a dict {codigo: nombre}.
        """
        departments = boe_client.fetch_auxiliary_table("departamentos")
        assert departments is not None
        # API returns list with single dict item containing {codigo: nombre}
        assert isinstance(departments, list)
        assert len(departments) > 0
        first = departments[0]
        # The dict has department codes as keys and names as values
        assert isinstance(first, dict)
        assert len(first) > 0

    @pytest.mark.integration
    def test_fetch_auxiliary_table_rangos(self, boe_client: BoeClient) -> None:
        """Should fetch legal ranges auxiliary table."""
        rangos = boe_client.fetch_auxiliary_table("rangos")
        assert rangos is not None
        assert isinstance(rangos, list)
        assert len(rangos) > 0

    @pytest.mark.integration
    def test_fetch_auxiliary_table_materias(self, boe_client: BoeClient) -> None:
        """Should fetch matters/subjects auxiliary table."""
        materias = boe_client.fetch_auxiliary_table("materias")
        assert materias is not None
        assert isinstance(materias, list)
        assert len(materias) > 0

    @pytest.mark.integration
    def test_fetch_boe_summary(self, boe_client: BoeClient) -> None:
        """Should fetch BOE daily summary."""
        # Try recent weekdays (BOE not published on weekends)
        for days_ago in range(0, 7):
            target_date = date.today() - timedelta(days=days_ago)
            # Skip weekends
            if target_date.weekday() >= 5:
                continue

            result = boe_client.fetch_boe_summary(target_date)
            if result is not None:
                assert isinstance(result, dict)
                return

        pytest.skip("No BOE summary found in the last 7 weekdays")

    @pytest.mark.integration
    def test_fetch_borme_summary(self, boe_client: BoeClient) -> None:
        """Should fetch BORME daily summary."""
        # Try recent weekdays (BORME not published on weekends)
        for days_ago in range(0, 7):
            target_date = date.today() - timedelta(days=days_ago)
            # Skip weekends
            if target_date.weekday() >= 5:
                continue

            result = boe_client.fetch_borme_summary(target_date)
            if result is not None:
                assert isinstance(result, dict)
                return

        pytest.skip("No BORME summary found in the last 7 weekdays")

    @pytest.mark.integration
    def test_parse_boe_summary_real_data(self, boe_client: BoeClient) -> None:
        """Should parse real BOE summary data."""
        # Find a valid BOE day
        for days_ago in range(0, 7):
            target_date = date.today() - timedelta(days=days_ago)
            if target_date.weekday() >= 5:
                continue

            result = boe_client.fetch_boe_summary(target_date)
            if result is not None:
                parsed = parse_boe_summary(result)
                assert isinstance(parsed, list)

                if len(parsed) > 0:
                    item = parsed[0]
                    assert item.id
                    assert item.title
                return

        pytest.skip("No BOE summary found to parse")

    @pytest.mark.integration
    def test_parse_borme_summary_real_data(self, boe_client: BoeClient) -> None:
        """Should parse real BORME summary data."""
        # Find a valid BORME day
        for days_ago in range(0, 7):
            target_date = date.today() - timedelta(days=days_ago)
            if target_date.weekday() >= 5:
                continue

            result = boe_client.fetch_borme_summary(target_date)
            if result is not None:
                parsed = parse_borme_summary(result)
                assert isinstance(parsed, list)

                if len(parsed) > 0:
                    item = parsed[0]
                    assert item.id
                    assert item.title
                return

        pytest.skip("No BORME summary found to parse")

    @pytest.mark.integration
    def test_parse_legislation_search_real_data(self, boe_client: BoeClient) -> None:
        """Should parse real legislation search results."""
        # Use empty query to avoid the BOE server bug with query param
        results = boe_client.search_legislation(query="", limit=5)

        if not results:
            pytest.skip("No legislation found to parse")

        parsed = parse_legislation_search(results)
        assert isinstance(parsed, list)
        assert len(parsed) > 0

        item = parsed[0]
        assert item.id
        assert item.title
