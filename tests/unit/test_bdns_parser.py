"""Unit tests for BDNS parser."""

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from public_radar.sources.bdns import (
    ParsedConcesion,
    ParsedConvocatoria,
    parse_concesiones,
    parse_convocatorias,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def sample_convocatorias() -> dict:
    """Load sample BDNS convocatorias fixture."""
    with open(FIXTURES_DIR / "bdns_convocatorias_sample.json") as f:
        return json.load(f)


@pytest.fixture
def sample_concesiones() -> dict:
    """Load sample BDNS concesiones fixture."""
    with open(FIXTURES_DIR / "bdns_concesiones_sample.json") as f:
        return json.load(f)


class TestParseConvocatorias:
    """Tests for parse_convocatorias function."""

    def test_parses_sample_convocatorias(self, sample_convocatorias: dict) -> None:
        """Should parse sample convocatorias into items."""
        items = parse_convocatorias(sample_convocatorias)

        assert len(items) == 3
        assert all(isinstance(item, ParsedConvocatoria) for item in items)

    def test_extracts_source_ids(self, sample_convocatorias: dict) -> None:
        """Should extract correct source IDs."""
        items = parse_convocatorias(sample_convocatorias)
        source_ids = [item.source_id for item in items]

        assert "700001" in source_ids
        assert "700002" in source_ids
        assert "700003" in source_ids

    def test_extracts_titles(self, sample_convocatorias: dict) -> None:
        """Should extract correct titles."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        assert "innovacion" in items_by_id["700001"].title.lower()
        assert "emprendimiento" in items_by_id["700002"].title.lower()
        assert "becas" in items_by_id["700003"].title.lower()

    def test_extracts_summaries(self, sample_convocatorias: dict) -> None:
        """Should extract summaries where available."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        assert items_by_id["700001"].summary is not None
        assert "fomentar" in items_by_id["700001"].summary.lower()

    def test_extracts_publication_dates(self, sample_convocatorias: dict) -> None:
        """Should extract publication dates."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        item1 = items_by_id["700001"]
        assert item1.published_at is not None
        assert item1.published_at.year == 2026
        assert item1.published_at.month == 1
        assert item1.published_at.day == 10

    def test_extracts_deadlines(self, sample_convocatorias: dict) -> None:
        """Should extract application deadlines."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        item1 = items_by_id["700001"]
        assert item1.deadline_at is not None
        assert item1.deadline_at.month == 3
        assert item1.deadline_at.day == 31

    def test_extracts_granting_body(self, sample_convocatorias: dict) -> None:
        """Should extract granting body details."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        item1 = items_by_id["700001"]
        assert item1.granting_body == "Ministerio de Ciencia e Innovacion"
        assert item1.granting_body_id == "S2826001E"

        # String organo format
        item3 = items_by_id["700003"]
        assert item3.granting_body == "INAP"

    def test_extracts_budget(self, sample_convocatorias: dict) -> None:
        """Should extract budget amounts."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        assert items_by_id["700001"].budget == Decimal("5000000.00")
        assert items_by_id["700001"].currency == "EUR"
        assert items_by_id["700002"].budget == Decimal("2000000.00")
        assert items_by_id["700003"].budget == Decimal("1500000")

    def test_extracts_urls(self, sample_convocatorias: dict) -> None:
        """Should extract official URLs."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        assert "boe.es" in items_by_id["700001"].url_official
        assert "comunidad.madrid" in items_by_id["700002"].url_official

    def test_extracts_beneficiary_types(self, sample_convocatorias: dict) -> None:
        """Should extract beneficiary types."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        assert "Empresas" in items_by_id["700001"].beneficiary_types
        assert "Centros de investigacion" in items_by_id["700001"].beneficiary_types
        assert len(items_by_id["700001"].beneficiary_types) == 2

    def test_extracts_sector(self, sample_convocatorias: dict) -> None:
        """Should extract sector classification."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        assert "Tecnologia" in items_by_id["700001"].sector

    def test_extracts_geographic_scope(self, sample_convocatorias: dict) -> None:
        """Should extract geographic scope."""
        items = parse_convocatorias(sample_convocatorias)
        items_by_id = {item.source_id: item for item in items}

        assert items_by_id["700001"].geographic_scope == "Nacional"
        assert "Madrid" in items_by_id["700002"].geographic_scope

    def test_stores_raw_data(self, sample_convocatorias: dict) -> None:
        """Should store raw data."""
        items = parse_convocatorias(sample_convocatorias)

        for item in items:
            assert item.raw_data is not None
            assert isinstance(item.raw_data, dict)

    def test_empty_data_returns_empty_list(self) -> None:
        """Should return empty list for empty data."""
        items = parse_convocatorias({})
        assert items == []

    def test_none_data_returns_empty_list(self) -> None:
        """Should return empty list for None data."""
        items = parse_convocatorias(None)  # type: ignore
        assert items == []

    def test_no_items_returns_empty_list(self) -> None:
        """Should return empty list when no items."""
        items = parse_convocatorias({"total": 0, "items": []})
        assert items == []


class TestParseConcesiones:
    """Tests for parse_concesiones function."""

    def test_parses_sample_concesiones(self, sample_concesiones: dict) -> None:
        """Should parse sample concesiones into items."""
        items = parse_concesiones(sample_concesiones)

        assert len(items) == 3
        assert all(isinstance(item, ParsedConcesion) for item in items)

    def test_extracts_source_ids(self, sample_concesiones: dict) -> None:
        """Should extract correct source IDs."""
        items = parse_concesiones(sample_concesiones)
        source_ids = [item.source_id for item in items]

        assert "CON-2026-001" in source_ids
        assert "CON-2026-002" in source_ids
        assert "CON-2026-003" in source_ids

    def test_extracts_convocatoria_ids(self, sample_concesiones: dict) -> None:
        """Should extract related convocatoria IDs."""
        items = parse_concesiones(sample_concesiones)
        items_by_id = {item.source_id: item for item in items}

        assert items_by_id["CON-2026-001"].convocatoria_id == "700001"
        assert items_by_id["CON-2026-003"].convocatoria_id == "700002"

    def test_extracts_titles(self, sample_concesiones: dict) -> None:
        """Should extract titles from convocatoria."""
        items = parse_concesiones(sample_concesiones)
        items_by_id = {item.source_id: item for item in items}

        assert "innovacion" in items_by_id["CON-2026-001"].title.lower()

    def test_extracts_award_dates(self, sample_concesiones: dict) -> None:
        """Should extract award dates."""
        items = parse_concesiones(sample_concesiones)
        items_by_id = {item.source_id: item for item in items}

        item1 = items_by_id["CON-2026-001"]
        assert item1.awarded_at is not None
        assert item1.awarded_at.year == 2026
        assert item1.awarded_at.month == 1
        assert item1.awarded_at.day == 18

    def test_extracts_beneficiary(self, sample_concesiones: dict) -> None:
        """Should extract beneficiary details."""
        items = parse_concesiones(sample_concesiones)
        items_by_id = {item.source_id: item for item in items}

        item1 = items_by_id["CON-2026-001"]
        assert item1.beneficiary_name == "TECNOLOGIAS AVANZADAS SL"
        assert item1.beneficiary_id == "B12345678"

        # Alternative field names
        item3 = items_by_id["CON-2026-003"]
        assert item3.beneficiary_name == "GARCIA MARTINEZ JUAN"
        assert item3.beneficiary_id == "12345678A"

    def test_extracts_granting_body(self, sample_concesiones: dict) -> None:
        """Should extract granting body details."""
        items = parse_concesiones(sample_concesiones)
        items_by_id = {item.source_id: item for item in items}

        item1 = items_by_id["CON-2026-001"]
        assert item1.granting_body == "Ministerio de Ciencia e Innovacion"
        assert item1.granting_body_id == "S2826001E"

    def test_extracts_amount(self, sample_concesiones: dict) -> None:
        """Should extract awarded amounts."""
        items = parse_concesiones(sample_concesiones)
        items_by_id = {item.source_id: item for item in items}

        assert items_by_id["CON-2026-001"].amount == Decimal("150000.00")
        assert items_by_id["CON-2026-002"].amount == Decimal("200000.00")
        assert items_by_id["CON-2026-003"].amount == Decimal("25000")

    def test_stores_raw_data(self, sample_concesiones: dict) -> None:
        """Should store raw data."""
        items = parse_concesiones(sample_concesiones)

        for item in items:
            assert item.raw_data is not None
            assert isinstance(item.raw_data, dict)

    def test_empty_data_returns_empty_list(self) -> None:
        """Should return empty list for empty data."""
        items = parse_concesiones({})
        assert items == []


class TestParsedConvocatoria:
    """Tests for ParsedConvocatoria dataclass."""

    def test_dataclass_fields(self) -> None:
        """Should have all expected fields."""
        item = ParsedConvocatoria(
            source_id="TEST-001",
            title="Test Grant",
            summary="Test summary",
            published_at=datetime(2026, 1, 20, tzinfo=UTC),
            deadline_at=datetime(2026, 3, 31, tzinfo=UTC),
            url_official="https://example.com",
            granting_body="Test Body",
            granting_body_id="A12345678",
            budget=Decimal("1000000"),
            currency="EUR",
            sector="Technology",
            geographic_scope="National",
            beneficiary_types=["Companies", "Research centers"],
            raw_data={"id": "TEST-001"},
        )

        assert item.source_id == "TEST-001"
        assert item.budget == Decimal("1000000")
        assert len(item.beneficiary_types) == 2


class TestParsedConcesion:
    """Tests for ParsedConcesion dataclass."""

    def test_dataclass_fields(self) -> None:
        """Should have all expected fields."""
        item = ParsedConcesion(
            source_id="CON-001",
            convocatoria_id="CONV-001",
            title="Test Grant Award",
            awarded_at=datetime(2026, 1, 20, tzinfo=UTC),
            beneficiary_name="Test Company",
            beneficiary_id="B12345678",
            granting_body="Test Body",
            granting_body_id="A12345678",
            amount=Decimal("50000"),
            currency="EUR",
            raw_data={"id": "CON-001"},
        )

        assert item.source_id == "CON-001"
        assert item.amount == Decimal("50000")
