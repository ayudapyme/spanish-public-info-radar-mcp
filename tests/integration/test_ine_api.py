"""Integration tests for INE API.

These tests make real HTTP calls to the INE JSON API.
They are marked with pytest.mark.integration.

INE API is public and free, no authentication required.
Documentation: https://www.ine.es/dyngs/DAB/index.htm?cid=1099
"""

import pytest

from public_radar.sources.ine import (
    IneClient,
    parse_operations,
    parse_series,
    parse_tables,
    parse_variables,
)


@pytest.fixture
def ine_client():
    """Create an INE client for testing."""
    with IneClient() as client:
        yield client


class TestIneApiIntegration:
    """Integration tests for INE API."""

    @pytest.mark.integration
    def test_fetch_operations(self, ine_client: IneClient) -> None:
        """Should fetch list of available statistical operations."""
        operations = ine_client.fetch_operations()

        assert operations is not None
        assert isinstance(operations, list)
        assert len(operations) > 0

        # Check structure of first operation
        first = operations[0]
        assert "Id" in first or "Cod_IOE" in first
        assert "Nombre" in first

    @pytest.mark.integration
    def test_parse_operations(self, ine_client: IneClient) -> None:
        """Should parse operations into dataclass objects."""
        raw_data = ine_client.fetch_operations()
        parsed = parse_operations(raw_data)

        assert len(parsed) > 0
        first = parsed[0]
        assert first.id
        assert first.name

    @pytest.mark.integration
    def test_fetch_operation_ipc(self, ine_client: IneClient) -> None:
        """Should fetch IPC (Consumer Price Index) operation details."""
        # IPC is a well-known operation that should always exist
        operation = ine_client.fetch_operation("IPC")

        assert operation is not None
        assert isinstance(operation, dict)
        assert "Nombre" in operation

    @pytest.mark.integration
    def test_fetch_tables_by_operation(self, ine_client: IneClient) -> None:
        """Should fetch tables for IPC operation."""
        tables = ine_client.fetch_tables_by_operation("IPC")

        assert tables is not None
        assert isinstance(tables, list)
        assert len(tables) > 0

    @pytest.mark.integration
    def test_parse_tables(self, ine_client: IneClient) -> None:
        """Should parse tables into dataclass objects."""
        raw_data = ine_client.fetch_tables_by_operation("IPC")
        parsed = parse_tables(raw_data)

        assert len(parsed) > 0
        first = parsed[0]
        assert first.id
        assert first.name

    @pytest.mark.integration
    def test_fetch_table_data(self, ine_client: IneClient) -> None:
        """Should fetch data from a table."""
        # First get tables for IPC
        tables = ine_client.fetch_tables_by_operation("IPC")
        assert len(tables) > 0

        # Get data from first table (limit to last 5 periods)
        table_id = str(tables[0].get("Id", tables[0].get("id", "")))
        data = ine_client.fetch_table_data(table_id, nult=5)

        assert data is not None
        assert isinstance(data, list)

    @pytest.mark.integration
    def test_fetch_variables(self, ine_client: IneClient) -> None:
        """Should fetch list of all variables."""
        variables = ine_client.fetch_variables()

        assert variables is not None
        assert isinstance(variables, list)
        assert len(variables) > 0

    @pytest.mark.integration
    def test_parse_variables(self, ine_client: IneClient) -> None:
        """Should parse variables into dataclass objects."""
        raw_data = ine_client.fetch_variables()
        parsed = parse_variables(raw_data)

        assert len(parsed) > 0
        first = parsed[0]
        assert first.id
        assert first.name

    @pytest.mark.integration
    def test_fetch_variables_by_operation(self, ine_client: IneClient) -> None:
        """Should fetch variables for IPC operation."""
        variables = ine_client.fetch_variables_by_operation("IPC")

        assert variables is not None
        assert isinstance(variables, list)
        assert len(variables) > 0

    @pytest.mark.integration
    def test_fetch_series_by_operation(self, ine_client: IneClient) -> None:
        """Should fetch series for IPC operation."""
        series = ine_client.fetch_series_by_operation("IPC")

        assert series is not None
        assert isinstance(series, list)
        # IPC should have many series
        assert len(series) > 0

    @pytest.mark.integration
    def test_parse_series(self, ine_client: IneClient) -> None:
        """Should parse series into dataclass objects."""
        raw_data = ine_client.fetch_series_by_operation("IPC")
        if raw_data:
            parsed = parse_series(raw_data[:10])  # Parse first 10 only
            assert len(parsed) > 0
            first = parsed[0]
            assert first.code or first.name

    @pytest.mark.integration
    def test_fetch_periodicities(self, ine_client: IneClient) -> None:
        """Should fetch available periodicities."""
        periodicities = ine_client.fetch_periodicities()

        assert periodicities is not None
        assert isinstance(periodicities, list)
        assert len(periodicities) > 0

        # Should include common periodicities
        names = [p.get("Nombre", "").lower() for p in periodicities]
        # Check for at least one common periodicity type
        assert any("mensual" in n or "anual" in n or "trimestral" in n for n in names)

    @pytest.mark.integration
    def test_fetch_publications(self, ine_client: IneClient) -> None:
        """Should fetch available publications."""
        publications = ine_client.fetch_publications()

        assert publications is not None
        assert isinstance(publications, list)
        assert len(publications) > 0

    @pytest.mark.integration
    def test_fetch_classifications(self, ine_client: IneClient) -> None:
        """Should fetch available classifications."""
        classifications = ine_client.fetch_classifications()

        assert classifications is not None
        assert isinstance(classifications, list)
        assert len(classifications) > 0

    @pytest.mark.integration
    def test_fetch_operation_not_found(self, ine_client: IneClient) -> None:
        """Should return None for non-existent operation."""
        result = ine_client.fetch_operation("NONEXISTENT_OPERATION_12345")

        # API may return empty list or None
        assert result is None or result == []

    @pytest.mark.integration
    def test_language_parameter(self) -> None:
        """Should support English language parameter."""
        with IneClient(language="EN") as client:
            operations = client.fetch_operations()

            assert operations is not None
            assert len(operations) > 0
            # Names should be in English
            first = operations[0]
            assert "Nombre" in first  # Field name is still in Spanish
