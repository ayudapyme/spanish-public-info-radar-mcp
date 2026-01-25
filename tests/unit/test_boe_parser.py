"""Tests for BOE API parsers."""

import json
from pathlib import Path

import pytest

from public_radar.sources.boe import (
    ParsedBoeSummaryItem,
    ParsedBormeSummaryItem,
    ParsedLegislation,
    parse_boe_summary,
    parse_borme_summary,
    parse_legislation_search,
)


@pytest.fixture
def boe_sumario_data() -> dict:
    """Load BOE summary sample fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "boe_sumario_sample.json"
    with open(fixture_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def borme_sumario_data() -> dict:
    """Load BORME summary sample fixture for parser tests."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "borme_sumario_parser_sample.json"
    with open(fixture_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def legislation_search_data() -> list:
    """Sample legislation search results."""
    return [
        {
            "id": "BOE-A-2023-12345",
            "titulo": "Ley 12/2023, de 15 de mayo, de energías renovables",
            "departamento": "MINISTERIO PARA LA TRANSICIÓN ECOLÓGICA",
            "rango": "Ley",
            "fecha_publicacion": "2023-05-16",
            "fecha_vigencia": "2023-06-01",
            "estado_consolidacion": "Vigente",
            "url_pdf": "https://www.boe.es/boe/dias/2023/05/16/pdfs/BOE-A-2023-12345.pdf",
            "url_html": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-12345",
            "url_epub": "https://www.boe.es/epub/BOE-A-2023-12345.epub",
        },
        {
            "identificador": "BOE-A-2022-9999",
            "title": "Real Decreto 100/2022 sobre subvenciones",
            "departamento": "MINISTERIO DE ECONOMÍA",
            "rango": "Real Decreto",
        },
    ]


class TestParseLegislationSearch:
    """Tests for parse_legislation_search function."""

    def test_parses_legislation_list(self, legislation_search_data: list) -> None:
        """Test parsing a list of legislation items."""
        results = parse_legislation_search(legislation_search_data)

        assert len(results) == 2
        assert all(isinstance(item, ParsedLegislation) for item in results)

    def test_extracts_id_from_id_field(self, legislation_search_data: list) -> None:
        """Test ID extraction from 'id' field."""
        results = parse_legislation_search(legislation_search_data)

        assert results[0].id == "BOE-A-2023-12345"

    def test_extracts_id_from_identificador_field(self, legislation_search_data: list) -> None:
        """Test ID extraction from 'identificador' field (fallback)."""
        results = parse_legislation_search(legislation_search_data)

        assert results[1].id == "BOE-A-2022-9999"

    def test_extracts_title_from_titulo_field(self, legislation_search_data: list) -> None:
        """Test title extraction from 'titulo' field."""
        results = parse_legislation_search(legislation_search_data)

        assert results[0].title == "Ley 12/2023, de 15 de mayo, de energías renovables"

    def test_extracts_title_from_title_field(self, legislation_search_data: list) -> None:
        """Test title extraction from 'title' field (fallback)."""
        results = parse_legislation_search(legislation_search_data)

        assert results[1].title == "Real Decreto 100/2022 sobre subvenciones"

    def test_extracts_department(self, legislation_search_data: list) -> None:
        """Test department extraction."""
        results = parse_legislation_search(legislation_search_data)

        assert results[0].department == "MINISTERIO PARA LA TRANSICIÓN ECOLÓGICA"
        assert results[1].department == "MINISTERIO DE ECONOMÍA"

    def test_extracts_rang(self, legislation_search_data: list) -> None:
        """Test regulatory rank extraction."""
        results = parse_legislation_search(legislation_search_data)

        assert results[0].rang == "Ley"
        assert results[1].rang == "Real Decreto"

    def test_extracts_dates(self, legislation_search_data: list) -> None:
        """Test date extraction."""
        results = parse_legislation_search(legislation_search_data)

        assert results[0].publication_date == "2023-05-16"
        assert results[0].effective_date == "2023-06-01"

    def test_extracts_status(self, legislation_search_data: list) -> None:
        """Test status extraction."""
        results = parse_legislation_search(legislation_search_data)

        assert results[0].status == "Vigente"
        assert results[1].status is None

    def test_extracts_urls(self, legislation_search_data: list) -> None:
        """Test URL extraction."""
        results = parse_legislation_search(legislation_search_data)

        assert results[0].url_pdf == "https://www.boe.es/boe/dias/2023/05/16/pdfs/BOE-A-2023-12345.pdf"
        assert results[0].url_html == "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-12345"
        assert results[0].url_epub == "https://www.boe.es/epub/BOE-A-2023-12345.epub"

    def test_handles_empty_list(self) -> None:
        """Test handling empty input."""
        results = parse_legislation_search([])

        assert results == []

    def test_handles_missing_fields(self) -> None:
        """Test handling items with missing fields."""
        data = [{"id": "test-id"}]
        results = parse_legislation_search(data)

        assert len(results) == 1
        assert results[0].id == "test-id"
        assert results[0].title == ""
        assert results[0].department is None


class TestParseBoeSummary:
    """Tests for parse_boe_summary function."""

    def test_parses_boe_summary(self, boe_sumario_data: dict) -> None:
        """Test parsing BOE summary data."""
        data = boe_sumario_data["data"]
        results = parse_boe_summary(data)

        assert len(results) > 0
        assert all(isinstance(item, ParsedBoeSummaryItem) for item in results)

    def test_extracts_item_ids(self, boe_sumario_data: dict) -> None:
        """Test extraction of item IDs."""
        data = boe_sumario_data["data"]
        results = parse_boe_summary(data)

        ids = [item.id for item in results]
        assert "BOE-A-2026-1234" in ids
        assert "BOE-A-2026-1235" in ids
        assert "BOE-A-2026-1236" in ids

    def test_extracts_titles(self, boe_sumario_data: dict) -> None:
        """Test extraction of item titles."""
        data = boe_sumario_data["data"]
        results = parse_boe_summary(data)

        titles = [item.title for item in results]
        assert any("subvenciones" in title.lower() for title in titles)

    def test_extracts_sections(self, boe_sumario_data: dict) -> None:
        """Test extraction of section names."""
        data = boe_sumario_data["data"]
        results = parse_boe_summary(data)

        sections = {item.section for item in results}
        assert "I. Disposiciones generales" in sections

    def test_extracts_departments(self, boe_sumario_data: dict) -> None:
        """Test extraction of department names."""
        data = boe_sumario_data["data"]
        results = parse_boe_summary(data)

        departments = {item.department for item in results}
        assert "MINISTERIO DE ECONOMÍA" in departments
        assert "MINISTERIO DE INDUSTRIA" in departments

    def test_extracts_epigraphs(self, boe_sumario_data: dict) -> None:
        """Test extraction of epigraph names."""
        data = boe_sumario_data["data"]
        results = parse_boe_summary(data)

        epigraphs = {item.epigraph for item in results if item.epigraph}
        assert "Subvenciones" in epigraphs
        assert "Nombramientos" in epigraphs

    def test_extracts_urls(self, boe_sumario_data: dict) -> None:
        """Test extraction of URLs."""
        data = boe_sumario_data["data"]
        results = parse_boe_summary(data)

        assert any(item.url_pdf is not None for item in results)
        assert any(item.url_html is not None for item in results)

    def test_handles_single_item_as_dict(self, boe_sumario_data: dict) -> None:
        """Test handling when item is a dict instead of list."""
        data = boe_sumario_data["data"]
        results = parse_boe_summary(data)

        # The fixture has single-item dicts in some places
        # Verify they are properly parsed
        assert any(item.id == "BOE-A-2026-1236" for item in results)

    def test_handles_empty_data(self) -> None:
        """Test handling empty data."""
        results = parse_boe_summary({})

        assert results == []

    def test_handles_missing_sumario(self) -> None:
        """Test handling data without sumario key."""
        results = parse_boe_summary({"other_key": "value"})

        assert results == []


class TestParseBormeSummary:
    """Tests for parse_borme_summary function."""

    def test_parses_borme_summary(self, borme_sumario_data: dict) -> None:
        """Test parsing BORME summary data."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        assert len(results) > 0
        assert all(isinstance(item, ParsedBormeSummaryItem) for item in results)

    def test_extracts_item_ids(self, borme_sumario_data: dict) -> None:
        """Test extraction of item IDs."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        ids = [item.id for item in results]
        assert "BORME-A-2026-15-28-001" in ids
        assert "BORME-A-2026-15-28-002" in ids

    def test_extracts_titles(self, borme_sumario_data: dict) -> None:
        """Test extraction of item titles."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        titles = [item.title for item in results]
        assert any("TECNOLOGIAS INNOVADORAS" in title for title in titles)

    def test_extracts_sections(self, borme_sumario_data: dict) -> None:
        """Test extraction of section names."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        sections = {item.section for item in results}
        assert "ACTOS INSCRITOS" in sections
        assert "OTROS ACTOS" in sections

    def test_extracts_provinces(self, borme_sumario_data: dict) -> None:
        """Test extraction of province names."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        provinces = {item.province for item in results}
        assert "MADRID" in provinces
        assert "BARCELONA" in provinces

    def test_extracts_act_type_from_title(self, borme_sumario_data: dict) -> None:
        """Test extraction of act type from title with ' - ' separator."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        act_types = {item.act_type for item in results if item.act_type}
        assert "Constitución" in act_types
        assert "Ampliación de capital" in act_types
        assert "Nombramientos" in act_types

    def test_extracts_company_name_from_title(self, borme_sumario_data: dict) -> None:
        """Test extraction of company name from title with ' - ' separator."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        company_names = {item.company_name for item in results if item.company_name}
        assert "TECNOLOGIAS INNOVADORAS SL" in company_names
        assert "CONSTRUCCIONES GARCIA LOPEZ SA" in company_names

    def test_extracts_urls(self, borme_sumario_data: dict) -> None:
        """Test extraction of PDF URLs."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        assert all(item.url_pdf is not None for item in results)
        assert any("BORME-A-2026-15-28-001.pdf" in (item.url_pdf or "") for item in results)

    def test_handles_single_item_as_dict(self, borme_sumario_data: dict) -> None:
        """Test handling when item is a dict instead of list."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        # The fixture has single-item dicts in some places
        # Verify they are properly parsed
        assert any(item.id == "BORME-A-2026-15-08-001" for item in results)

    def test_handles_single_emisor_as_dict(self, borme_sumario_data: dict) -> None:
        """Test handling when emisor is a dict instead of list."""
        data = borme_sumario_data["data"]
        results = parse_borme_summary(data)

        # The "OTROS ACTOS" section has emisor as a single dict
        assert any(item.province == "NACIONAL" for item in results)

    def test_handles_empty_data(self) -> None:
        """Test handling empty data."""
        results = parse_borme_summary({})

        assert results == []

    def test_handles_missing_sumario(self) -> None:
        """Test handling data without sumario key."""
        results = parse_borme_summary({"other_key": "value"})

        assert results == []


class TestParsedLegislationDataclass:
    """Tests for ParsedLegislation dataclass."""

    def test_dataclass_fields(self) -> None:
        """Test ParsedLegislation dataclass has expected fields."""
        item = ParsedLegislation(
            id="test-id",
            title="Test Title",
            department="Test Dept",
            rang="Ley",
            publication_date="2024-01-01",
            effective_date="2024-02-01",
            status="Vigente",
            url_pdf="https://example.com/pdf",
            url_html="https://example.com/html",
            url_epub="https://example.com/epub",
        )

        assert item.id == "test-id"
        assert item.title == "Test Title"
        assert item.department == "Test Dept"
        assert item.rang == "Ley"
        assert item.status == "Vigente"

    def test_optional_fields_default_to_none(self) -> None:
        """Test optional fields default to None."""
        item = ParsedLegislation(id="id", title="title")

        assert item.department is None
        assert item.rang is None
        assert item.publication_date is None
        assert item.effective_date is None
        assert item.status is None
        assert item.url_pdf is None
        assert item.url_html is None
        assert item.url_epub is None


class TestParsedBoeSummaryItemDataclass:
    """Tests for ParsedBoeSummaryItem dataclass."""

    def test_dataclass_fields(self) -> None:
        """Test ParsedBoeSummaryItem dataclass has expected fields."""
        item = ParsedBoeSummaryItem(
            id="BOE-A-2024-123",
            title="Test BOE Item",
            section="I. Disposiciones generales",
            department="Test Department",
            epigraph="Test Epigraph",
            url_pdf="https://example.com/pdf",
            url_html="https://example.com/html",
        )

        assert item.id == "BOE-A-2024-123"
        assert item.title == "Test BOE Item"
        assert item.section == "I. Disposiciones generales"
        assert item.department == "Test Department"
        assert item.epigraph == "Test Epigraph"

    def test_optional_fields_default_to_none(self) -> None:
        """Test optional fields default to None."""
        item = ParsedBoeSummaryItem(id="id", title="title")

        assert item.section is None
        assert item.department is None
        assert item.epigraph is None
        assert item.url_pdf is None
        assert item.url_html is None


class TestParsedBormeSummaryItemDataclass:
    """Tests for ParsedBormeSummaryItem dataclass."""

    def test_dataclass_fields(self) -> None:
        """Test ParsedBormeSummaryItem dataclass has expected fields."""
        item = ParsedBormeSummaryItem(
            id="BORME-A-2024-1-28-001",
            title="Constitución - Test Company SL",
            section="ACTOS INSCRITOS",
            province="MADRID",
            url_pdf="https://example.com/pdf",
            act_type="Constitución",
            company_name="Test Company SL",
        )

        assert item.id == "BORME-A-2024-1-28-001"
        assert item.title == "Constitución - Test Company SL"
        assert item.section == "ACTOS INSCRITOS"
        assert item.province == "MADRID"
        assert item.act_type == "Constitución"
        assert item.company_name == "Test Company SL"

    def test_optional_fields_default_to_none(self) -> None:
        """Test optional fields default to None."""
        item = ParsedBormeSummaryItem(id="id", title="title")

        assert item.section is None
        assert item.province is None
        assert item.url_pdf is None
        assert item.act_type is None
        assert item.company_name is None
