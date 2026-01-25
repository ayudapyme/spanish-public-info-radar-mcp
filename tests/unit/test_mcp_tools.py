"""Unit tests for MCP tool handlers.

These tests mock the API clients to test tool handlers in isolation.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


class TestSearchGrants:
    """Tests for search_grants tool handler."""

    @pytest.mark.asyncio
    async def test_search_grants_success(self) -> None:
        """Should return grants from mocked BDNS API."""
        from public_radar.mcp.server import SearchGrantsInput, _search_grants

        mock_response = {
            "items": [
                {
                    "codigoBdns": "123456",
                    "titulo": "Test Grant",
                    "descripcion": "Test description",
                    "organo": "Test Body",
                    "presupuesto": 10000,
                }
            ]
        }

        with patch("public_radar.sources.bdns.BdnsClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_convocatorias.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _search_grants(SearchGrantsInput(limit=10))

            assert result["count"] == 1
            assert result["grants"][0]["id"] == "123456"
            assert result["grants"][0]["title"] == "Test Grant"

    @pytest.mark.asyncio
    async def test_search_grants_empty(self) -> None:
        """Should handle empty results."""
        from public_radar.mcp.server import SearchGrantsInput, _search_grants

        with patch("public_radar.sources.bdns.BdnsClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_convocatorias.return_value = {"items": []}
            MockClient.return_value = mock_instance

            result = await _search_grants(SearchGrantsInput())

            assert result["count"] == 0
            assert "message" in result

    @pytest.mark.asyncio
    async def test_search_grants_api_error(self) -> None:
        """Should handle API errors gracefully."""
        from public_radar.mcp.server import SearchGrantsInput, _search_grants

        with patch("public_radar.sources.bdns.BdnsClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_convocatorias.side_effect = Exception("API Error")
            MockClient.return_value = mock_instance

            result = await _search_grants(SearchGrantsInput())

            assert "error" in result


class TestSearchGrantAwards:
    """Tests for search_grant_awards tool handler."""

    @pytest.mark.asyncio
    async def test_search_grant_awards_success(self) -> None:
        """Should return grant awards from mocked BDNS API."""
        from public_radar.mcp.server import SearchGrantAwardsInput, _search_grant_awards

        mock_response = {
            "items": [
                {
                    "idConcesion": "789",
                    "codigoBdns": "123",
                    "beneficiario": "Test Company",
                    "nifBeneficiario": "B12345678",
                    "importe": 5000,
                    "fechaConcesion": "2024-01-15",
                }
            ]
        }

        with patch("public_radar.sources.bdns.BdnsClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_concesiones.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _search_grant_awards(SearchGrantAwardsInput(beneficiary_nif="B12345678"))

            assert result["count"] == 1
            assert result["awards"][0]["beneficiary"] == "Test Company"


class TestGetGrantDetails:
    """Tests for get_grant_details tool handler."""

    @pytest.mark.asyncio
    async def test_get_grant_details_success(self) -> None:
        """Should return grant details from mocked BDNS API."""
        from public_radar.mcp.server import GetGrantDetailsInput, _get_grant_details

        mock_response = {
            "idConvocatoria": "123456",
            "titulo": "Test Grant Details",
            "descripcion": "Full description",
            "organo": "Test Body",
            "importeTotal": 50000,
        }

        with patch("public_radar.sources.bdns.BdnsClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_convocatoria_by_id.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_grant_details(GetGrantDetailsInput(grant_id="123456"))

            assert result["id"] == "123456"
            assert result["title"] == "Test Grant Details"

    @pytest.mark.asyncio
    async def test_get_grant_details_not_found(self) -> None:
        """Should handle grant not found."""
        from public_radar.mcp.server import GetGrantDetailsInput, _get_grant_details

        with patch("public_radar.sources.bdns.BdnsClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_convocatoria_by_id.return_value = None
            MockClient.return_value = mock_instance

            result = await _get_grant_details(GetGrantDetailsInput(grant_id="999999"))

            assert "error" in result


class TestSearchLegislation:
    """Tests for search_legislation tool handler."""

    @pytest.mark.asyncio
    async def test_search_legislation_success(self) -> None:
        """Should return legislation from mocked BOE API."""
        from public_radar.mcp.server import SearchLegislationInput, _search_legislation

        mock_search_results = [
            {
                "id": "BOE-A-2024-1234",
                "titulo": "Test Law",
                "departamento": "Test Department",
                "rango": "Ley",
            }
        ]

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.search_legislation.return_value = mock_search_results
            MockClient.return_value = mock_instance

            result = await _search_legislation(SearchLegislationInput(query="test"))

            assert result["count"] == 1
            assert result["legislation"][0]["id"] == "BOE-A-2024-1234"


class TestGetLegislationDetails:
    """Tests for get_legislation_details tool handler."""

    @pytest.mark.asyncio
    async def test_get_legislation_details_success(self) -> None:
        """Should return legislation details from mocked BOE API."""
        from public_radar.mcp.server import GetLegislationDetailsInput, _get_legislation_details

        mock_response = {
            "id": "BOE-A-2024-1234",
            "titulo": "Test Law Details",
            "departamento": "Test Department",
            "rango": "Ley Orgánica",
            "fecha_publicacion": "2024-01-15",
        }

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_legislation_by_id.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_legislation_details(GetLegislationDetailsInput(legislation_id="BOE-A-2024-1234"))

            assert result["id"] == "BOE-A-2024-1234"
            assert result["title"] == "Test Law Details"

    @pytest.mark.asyncio
    async def test_get_legislation_details_not_found(self) -> None:
        """Should handle legislation not found."""
        from public_radar.mcp.server import GetLegislationDetailsInput, _get_legislation_details

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_legislation_by_id.return_value = None
            MockClient.return_value = mock_instance

            result = await _get_legislation_details(GetLegislationDetailsInput(legislation_id="INVALID"))

            assert "error" in result


class TestGetLegislationText:
    """Tests for get_legislation_text tool handler."""

    @pytest.mark.asyncio
    async def test_get_legislation_text_success(self) -> None:
        """Should return legislation text from mocked BOE API."""
        from public_radar.mcp.server import GetLegislationTextInput, _get_legislation_text

        mock_response = {"texto": "Article 1. This is the full text of the law..."}

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_legislation_text.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_legislation_text(GetLegislationTextInput(legislation_id="BOE-A-2024-1234"))

            assert "text" in result
            assert "Article 1" in result["text"]


class TestGetBoeSummary:
    """Tests for get_boe_summary tool handler."""

    @pytest.mark.asyncio
    async def test_get_boe_summary_success(self) -> None:
        """Should return BOE summary from mocked BOE API."""
        from public_radar.mcp.server import GetBoeSummaryInput, _get_boe_summary

        mock_response = {
            "sumario": {
                "diario": [
                    {
                        "seccion": [
                            {
                                "@nombre": "I. Disposiciones generales",
                                "departamento": [
                                    {
                                        "@nombre": "MINISTERIO TEST",
                                        "epigrafe": [
                                            {
                                                "@nombre": "Subvenciones",
                                                "item": [
                                                    {
                                                        "@id": "BOE-A-2024-001",
                                                        "titulo": "Test BOE Item",
                                                        "urlPdf": "https://example.com/pdf",
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ]
                    }
                ]
            }
        }

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_boe_summary.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_boe_summary(GetBoeSummaryInput(date="2024-01-15"))

            assert "date" in result
            assert result["count"] == 1
            assert result["items"][0]["id"] == "BOE-A-2024-001"

    @pytest.mark.asyncio
    async def test_get_boe_summary_empty(self) -> None:
        """Should handle no BOE published."""
        from public_radar.mcp.server import GetBoeSummaryInput, _get_boe_summary

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_boe_summary.return_value = None
            MockClient.return_value = mock_instance

            result = await _get_boe_summary(GetBoeSummaryInput(date="2024-01-14"))

            assert result["count"] == 0
            assert "message" in result


class TestGetBormeSummary:
    """Tests for get_borme_summary tool handler."""

    @pytest.mark.asyncio
    async def test_get_borme_summary_success(self) -> None:
        """Should return BORME summary from mocked BOE API."""
        from public_radar.mcp.server import GetBormeSummaryInput, _get_borme_summary

        mock_response = {
            "sumario": {
                "diario": [
                    {
                        "seccion": [
                            {
                                "@nombre": "ACTOS INSCRITOS",
                                "emisor": [
                                    {
                                        "@nombre": "MADRID",
                                        "item": [
                                            {
                                                "@id": "BORME-A-2024-001",
                                                "titulo": "Constitución - Test Company SL",
                                                "urlPdf": "https://example.com/pdf",
                                            }
                                        ],
                                    }
                                ],
                            }
                        ]
                    }
                ]
            }
        }

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_borme_summary.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_borme_summary(GetBormeSummaryInput(date="2024-01-15"))

            assert "date" in result
            assert result["count"] == 1
            assert result["items"][0]["id"] == "BORME-A-2024-001"


class TestGetSystemInfo:
    """Tests for get_system_info tool handler."""

    def test_returns_system_info(self) -> None:
        """Should return system info with data sources."""
        from public_radar.mcp.server import _get_system_info

        result = _get_system_info()

        assert result["name"] == "Spanish Public Data MCP Server"
        assert "data_sources" in result
        assert len(result["data_sources"]) == 5  # BDNS, BOE, BORME, INE, datos.gob.es
        assert "tips" in result

    def test_data_sources_have_required_fields(self) -> None:
        """Should have id, name, description, tools for each source."""
        from public_radar.mcp.server import _get_system_info

        result = _get_system_info()

        for source in result["data_sources"]:
            assert "id" in source
            assert "name" in source
            assert "description" in source
            assert "tools" in source
            assert isinstance(source["tools"], list)

    def test_ine_data_source_included(self) -> None:
        """Should include INE as a data source."""
        from public_radar.mcp.server import _get_system_info

        result = _get_system_info()

        ine_sources = [s for s in result["data_sources"] if s["id"] == "ine"]
        assert len(ine_sources) == 1
        ine = ine_sources[0]
        assert "INE" in ine["name"]
        assert "get_ine_operations" in ine["tools"]
        assert "get_ine_table_data" in ine["tools"]


class TestGetIneOperations:
    """Tests for get_ine_operations tool handler."""

    @pytest.mark.asyncio
    async def test_get_ine_operations_success(self) -> None:
        """Should return INE operations from mocked API."""
        from public_radar.mcp.server import _get_ine_operations

        mock_response = [
            {"Id": 25, "Cod_IOE": "IPC", "Nombre": "Índice de Precios de Consumo", "Url": "https://ine.es/ipc"},
            {"Id": 30, "Cod_IOE": "EPA", "Nombre": "Encuesta de Población Activa", "Url": "https://ine.es/epa"},
        ]

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_operations.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_ine_operations()

            assert result["count"] == 2
            assert result["operations"][0]["code"] == "IPC"
            assert result["operations"][1]["code"] == "EPA"

    @pytest.mark.asyncio
    async def test_get_ine_operations_empty(self) -> None:
        """Should handle empty operations list."""
        from public_radar.mcp.server import _get_ine_operations

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_operations.return_value = []
            MockClient.return_value = mock_instance

            result = await _get_ine_operations()

            assert result["count"] == 0
            assert "message" in result


class TestGetIneOperation:
    """Tests for get_ine_operation tool handler."""

    @pytest.mark.asyncio
    async def test_get_ine_operation_success(self) -> None:
        """Should return INE operation details from mocked API."""
        from public_radar.mcp.server import GetIneOperationInput, _get_ine_operation

        mock_response = {
            "Id": 25,
            "Cod_IOE": "IPC",
            "Nombre": "Índice de Precios de Consumo",
            "Url": "https://ine.es/ipc",
        }

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_operation.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_ine_operation(GetIneOperationInput(operation_id="IPC"))

            assert result["code"] == "IPC"
            assert result["name"] == "Índice de Precios de Consumo"

    @pytest.mark.asyncio
    async def test_get_ine_operation_not_found(self) -> None:
        """Should handle operation not found."""
        from public_radar.mcp.server import GetIneOperationInput, _get_ine_operation

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_operation.return_value = None
            MockClient.return_value = mock_instance

            result = await _get_ine_operation(GetIneOperationInput(operation_id="INVALID"))

            assert "error" in result


class TestGetIneTableData:
    """Tests for get_ine_table_data tool handler."""

    @pytest.mark.asyncio
    async def test_get_ine_table_data_success(self) -> None:
        """Should return table data from mocked INE API."""
        from public_radar.mcp.server import GetIneTableDataInput, _get_ine_table_data

        mock_response = [
            {
                "COD": "IPC001",
                "Nombre": "IPC General",
                "Data": [
                    {"Fecha": "2024M01", "Valor": 105.3, "Secreto": False},
                    {"Fecha": "2024M02", "Valor": 105.8, "Secreto": False},
                ],
            }
        ]

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_table_data.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_ine_table_data(GetIneTableDataInput(table_id="50902", nult=5))

            assert result["table_id"] == "50902"
            assert result["series_count"] == 1
            assert result["series"][0]["series_code"] == "IPC001"
            assert len(result["series"][0]["data_points"]) == 2

    @pytest.mark.asyncio
    async def test_get_ine_table_data_not_found(self) -> None:
        """Should handle table not found."""
        from public_radar.mcp.server import GetIneTableDataInput, _get_ine_table_data

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_table_data.return_value = None
            MockClient.return_value = mock_instance

            result = await _get_ine_table_data(GetIneTableDataInput(table_id="INVALID"))

            assert "error" in result


class TestSearchIneTables:
    """Tests for search_ine_tables tool handler."""

    @pytest.mark.asyncio
    async def test_search_ine_tables_success(self) -> None:
        """Should return tables for an operation from mocked INE API."""
        from public_radar.mcp.server import SearchIneTablesInput, _search_ine_tables

        mock_response = [
            {"Id": 50902, "Nombre": "IPC General"},
            {"Id": 50903, "Nombre": "IPC por grupos"},
        ]

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_tables_by_operation.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _search_ine_tables(SearchIneTablesInput(operation_id="IPC"))

            assert result["operation_id"] == "IPC"
            assert result["count"] == 2
            assert result["tables"][0]["id"] == "50902"
            assert result["tables"][0]["name"] == "IPC General"

    @pytest.mark.asyncio
    async def test_search_ine_tables_empty(self) -> None:
        """Should handle no tables found."""
        from public_radar.mcp.server import SearchIneTablesInput, _search_ine_tables

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_tables_by_operation.return_value = []
            MockClient.return_value = mock_instance

            result = await _search_ine_tables(SearchIneTablesInput(operation_id="INVALID"))

            assert result["count"] == 0
            assert "message" in result


class TestGetIneVariables:
    """Tests for get_ine_variables tool handler."""

    @pytest.mark.asyncio
    async def test_get_ine_variables_all(self) -> None:
        """Should return all variables from mocked INE API."""
        from public_radar.mcp.server import GetIneVariablesInput, _get_ine_variables

        mock_response = [
            {"Id": 1, "Nombre": "Comunidades Autónomas", "Codigo": "CCAA"},
            {"Id": 2, "Nombre": "Provincias", "Codigo": "PROV"},
        ]

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_variables.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_ine_variables(GetIneVariablesInput())

            assert result["count"] == 2
            assert result["operation_id"] is None

    @pytest.mark.asyncio
    async def test_get_ine_variables_by_operation(self) -> None:
        """Should return variables for specific operation."""
        from public_radar.mcp.server import GetIneVariablesInput, _get_ine_variables

        mock_response = [
            {"Id": 10, "Nombre": "Grupos ECOICOP", "Codigo": "ECOICOP"},
        ]

        with patch("public_radar.sources.ine.IneClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_variables_by_operation.return_value = mock_response
            MockClient.return_value = mock_instance

            result = await _get_ine_variables(GetIneVariablesInput(operation_id="IPC"))

            assert result["count"] == 1
            assert result["operation_id"] == "IPC"


class TestLatestWeekday:
    """Tests for _latest_weekday utility function."""

    def test_weekday_returns_same_day(self) -> None:
        """Monday through Friday should return the same day."""
        from public_radar.mcp.server import _latest_weekday

        # Monday (weekday 0)
        monday = date(2024, 1, 15)
        assert _latest_weekday(monday) == monday

        # Wednesday (weekday 2)
        wednesday = date(2024, 1, 17)
        assert _latest_weekday(wednesday) == wednesday

        # Friday (weekday 4)
        friday = date(2024, 1, 19)
        assert _latest_weekday(friday) == friday

    def test_saturday_returns_friday(self) -> None:
        """Saturday should return the previous Friday."""
        from public_radar.mcp.server import _latest_weekday

        saturday = date(2024, 1, 20)
        friday = date(2024, 1, 19)
        assert _latest_weekday(saturday) == friday

    def test_sunday_returns_friday(self) -> None:
        """Sunday should return the previous Friday."""
        from public_radar.mcp.server import _latest_weekday

        sunday = date(2024, 1, 21)
        friday = date(2024, 1, 19)
        assert _latest_weekday(sunday) == friday


class TestBormeSummaryWeekday:
    """Tests for get_borme_summary weekday handling."""

    @pytest.mark.asyncio
    async def test_borme_summary_defaults_to_weekday(self) -> None:
        """Should use latest_weekday when no date provided."""
        from public_radar.mcp.server import GetBormeSummaryInput, _get_borme_summary

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_borme_summary.return_value = None
            MockClient.return_value = mock_instance

            # Test without date - should not raise and should return a weekday
            result = await _get_borme_summary(GetBormeSummaryInput())

            # Result should have a date that is not a weekend
            result_date = date.fromisoformat(result["date"])
            assert result_date.weekday() < 5  # Monday=0, Friday=4


class TestFindRelatedLaws:
    """Tests for find_related_laws tool handler."""

    @pytest.mark.asyncio
    async def test_find_related_laws_all_relations(self) -> None:
        """Should return all relation types when no filter specified."""
        from public_radar.mcp.server import FindRelatedLawsInput, _find_related_laws

        mock_analysis = {
            "modifica": [{"id": "BOE-A-2020-1", "titulo": "Ley 1"}],
            "modificado_por": [{"id": "BOE-A-2022-1", "titulo": "Ley 2"}],
            "deroga": [],
            "derogado_por": [],
            "referencias": [{"id": "BOE-A-2010-1", "titulo": "Ley antigua"}],
            "referenciado_por": [],
        }

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_legislation_analysis.return_value = mock_analysis
            MockClient.return_value = mock_instance

            result = await _find_related_laws(FindRelatedLawsInput(legislation_id="BOE-A-2015-10566"))

            assert "error" not in result
            assert result["legislation_id"] == "BOE-A-2015-10566"
            assert result["total_relations"] == 3
            assert result["relations"]["modifies"]["count"] == 1
            assert result["relations"]["modified_by"]["count"] == 1
            assert result["relations"]["references"]["count"] == 1

    @pytest.mark.asyncio
    async def test_find_related_laws_with_filter(self) -> None:
        """Should filter by relation type when specified."""
        from public_radar.mcp.server import FindRelatedLawsInput, _find_related_laws

        mock_analysis = {
            "modifica": [{"id": "BOE-A-2020-1", "titulo": "Ley 1"}],
            "modificado_por": [],
            "deroga": [],
            "derogado_por": [],
            "referencias": [],
            "referenciado_por": [],
        }

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_legislation_analysis.return_value = mock_analysis
            MockClient.return_value = mock_instance

            result = await _find_related_laws(
                FindRelatedLawsInput(legislation_id="BOE-A-2015-10566", relation_type="modifies")
            )

            assert "error" not in result
            assert result["relation_type"] == "modifies"
            assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_find_related_laws_not_found(self) -> None:
        """Should return error when legislation not found."""
        from public_radar.mcp.server import FindRelatedLawsInput, _find_related_laws

        with patch("public_radar.sources.boe.BoeClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_legislation_analysis.return_value = None
            MockClient.return_value = mock_instance

            result = await _find_related_laws(FindRelatedLawsInput(legislation_id="INVALID"))

            assert "error" in result


class TestSearchRecentBoe:
    """Tests for search_recent_boe tool handler."""

    @pytest.mark.asyncio
    async def test_search_recent_boe_basic(self) -> None:
        """Should search recent BOE publications."""
        from public_radar.mcp.server import SearchRecentBoeInput, _search_recent_boe
        from public_radar.sources.boe import ParsedBoeSummaryItem

        mock_parsed = [
            ParsedBoeSummaryItem(id="1", title="Ley de subvenciones", section="I", department="Hacienda"),
            ParsedBoeSummaryItem(id="2", title="Real Decreto", section="I", department="Interior"),
        ]

        with (
            patch("public_radar.sources.boe.BoeClient") as MockClient,
            patch("public_radar.sources.boe.parse_boe_summary", return_value=mock_parsed),
        ):
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_boe_summary.return_value = {"sumario": {}}
            MockClient.return_value = mock_instance

            result = await _search_recent_boe(SearchRecentBoeInput(days_back=3, max_items=10))

            assert "error" not in result
            assert result["days_back"] == 3
            assert "items" in result

    @pytest.mark.asyncio
    async def test_search_recent_boe_with_search_terms(self) -> None:
        """Should filter by search terms."""
        from public_radar.mcp.server import SearchRecentBoeInput, _search_recent_boe
        from public_radar.sources.boe import ParsedBoeSummaryItem

        mock_parsed = [
            ParsedBoeSummaryItem(id="1", title="Ley de subvenciones", section="I", department="Hacienda"),
            ParsedBoeSummaryItem(id="2", title="Real Decreto sobre impuestos", section="I", department="Interior"),
        ]

        with (
            patch("public_radar.sources.boe.BoeClient") as MockClient,
            patch("public_radar.sources.boe.parse_boe_summary", return_value=mock_parsed),
        ):
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.fetch_boe_summary.return_value = {"sumario": {}}
            MockClient.return_value = mock_instance

            result = await _search_recent_boe(
                SearchRecentBoeInput(days_back=3, search_terms="subvenciones", max_items=10)
            )

            assert "error" not in result
            # Should only include items matching search terms
            for item in result["items"]:
                assert "subvenciones" in item["title"].lower()
