"""BDNS (National Grants Database) client and parser.

Fetches and parses grants data from the BDNS Open Data API.
API Documentation: https://www.infosubvenciones.es/bdnstrans/doc/swagger
"""

import logging
from collections.abc import Generator
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any, cast

import httpx

from public_radar.common.dates import format_date_spanish, parse_date
from public_radar.common.http import NotFoundError, create_http_client, fetch_with_retry

logger = logging.getLogger(__name__)

BDNS_API_BASE = "https://www.infosubvenciones.es/bdnstrans/api"
DEFAULT_PAGE_SIZE = 100


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class ParsedConvocatoria:
    """Parsed BDNS grant call (convocatoria) ready for storage."""

    source_id: str
    title: str
    summary: str | None
    published_at: datetime | None
    deadline_at: datetime | None
    url_official: str | None
    granting_body: str | None
    granting_body_id: str | None
    budget: Decimal | None
    currency: str | None
    sector: str | None
    geographic_scope: str | None
    beneficiary_types: list[str] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedConcesion:
    """Parsed BDNS grant award (concesion) ready for storage."""

    source_id: str
    convocatoria_id: str | None
    title: str
    awarded_at: datetime | None
    beneficiary_name: str | None
    beneficiary_id: str | None
    granting_body: str | None
    granting_body_id: str | None
    amount: Decimal | None
    currency: str | None
    raw_data: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Client
# =============================================================================


class BdnsClient:
    """Client for fetching BDNS grants and subsidies data."""

    def __init__(self, http_client: httpx.Client | None = None) -> None:
        self._http_client = http_client
        self._owns_client = http_client is None

    @property
    def http_client(self) -> httpx.Client:
        if self._http_client is None:
            self._http_client = create_http_client()
        return self._http_client

    def close(self) -> None:
        if self._owns_client and self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def __enter__(self) -> "BdnsClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def fetch_convocatorias(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        organo: str | None = None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        """Fetch grant calls (convocatorias) from BDNS.

        Uses /convocatorias/busqueda for filtered queries or /convocatorias/ultimas for latest.
        """
        # Use /busqueda endpoint if filters are provided, otherwise /ultimas
        if fecha_desde or fecha_hasta or organo:
            url = f"{BDNS_API_BASE}/convocatorias/busqueda"
        else:
            url = f"{BDNS_API_BASE}/convocatorias/ultimas"

        params: dict[str, Any] = {"page": page, "pageSize": page_size}

        if fecha_desde:
            params["fechaDesde"] = format_date_spanish(fecha_desde)
        if fecha_hasta:
            params["fechaHasta"] = format_date_spanish(fecha_hasta)
        if organo:
            params["organo"] = organo

        logger.info("Fetching BDNS convocatorias page %d from %s", page, url)

        response = fetch_with_retry(
            self.http_client,
            url,
            params=params,
            headers={"Accept": "application/json"},
            raise_for_status=True,
        )

        data = response.json()
        # New API returns 'content' instead of 'items'
        items = data.get("content", data.get("items", []))
        logger.info("Fetched %d convocatorias (page %d)", len(items), page)
        # Normalize response to have 'items' key for backward compatibility
        if "content" in data and "items" not in data:
            data["items"] = data["content"]
        return cast(dict[str, Any], data)

    def fetch_convocatorias_paginated(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        organo: str | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
        max_pages: int | None = None,
    ) -> Generator[list[dict[str, Any]], None, None]:
        """Fetch all grant calls with automatic pagination."""
        page = 1
        while True:
            if max_pages and page > max_pages:
                break

            data = self.fetch_convocatorias(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                organo=organo,
                page=page,
                page_size=page_size,
            )

            items = data.get("items", data.get("content", []))
            if not items:
                break

            yield items

            # New API uses totalElements, old used total
            total = data.get("totalElements", data.get("total", 0))
            if page * page_size >= total:
                break

            page += 1

    def fetch_concesiones(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        nif_beneficiario: str | None = None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        """Fetch grant awards (concesiones) from BDNS.

        Uses /concesiones/busqueda endpoint.
        """
        url = f"{BDNS_API_BASE}/concesiones/busqueda"
        params: dict[str, Any] = {"page": page, "pageSize": page_size}

        if fecha_desde:
            params["fechaDesde"] = format_date_spanish(fecha_desde)
        if fecha_hasta:
            params["fechaHasta"] = format_date_spanish(fecha_hasta)
        if nif_beneficiario:
            params["nifBeneficiario"] = nif_beneficiario

        logger.info("Fetching BDNS concesiones page %d from %s", page, url)

        response = fetch_with_retry(
            self.http_client,
            url,
            params=params,
            headers={"Accept": "application/json"},
            raise_for_status=True,
        )

        data = response.json()
        # New API returns 'content' instead of 'items'
        items = data.get("content", data.get("items", []))
        logger.info("Fetched %d concesiones (page %d)", len(items), page)
        # Normalize response to have 'items' key for backward compatibility
        if "content" in data and "items" not in data:
            data["items"] = data["content"]
        return cast(dict[str, Any], data)

    def fetch_concesiones_paginated(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        nif_beneficiario: str | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
        max_pages: int | None = None,
    ) -> Generator[list[dict[str, Any]], None, None]:
        """Fetch all grant awards with automatic pagination."""
        page = 1
        while True:
            if max_pages and page > max_pages:
                break

            data = self.fetch_concesiones(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                nif_beneficiario=nif_beneficiario,
                page=page,
                page_size=page_size,
            )

            items = data.get("items", data.get("content", []))
            if not items:
                break

            yield items

            # New API uses totalElements, old used total
            total = data.get("totalElements", data.get("total", 0))
            if page * page_size >= total:
                break

            page += 1

    def fetch_convocatoria_by_id(self, convocatoria_id: str) -> dict[str, Any] | None:
        """Fetch a specific grant call by ID."""
        url = f"{BDNS_API_BASE}/convocatorias/{convocatoria_id}"
        logger.info("Fetching BDNS convocatoria %s", convocatoria_id)

        try:
            response = fetch_with_retry(
                self.http_client,
                url,
                headers={"Accept": "application/json"},
                raise_for_status=True,
            )
            return cast(dict[str, Any], response.json())
        except NotFoundError:
            logger.info("Convocatoria %s not found", convocatoria_id)
            return None


# =============================================================================
# Parser
# =============================================================================


def parse_convocatorias(data: dict[str, Any] | list[dict[str, Any]]) -> list[ParsedConvocatoria]:
    """Parse BDNS convocatorias response into items."""
    items: list[ParsedConvocatoria] = []

    if not data:
        return items

    # Handle both list and dict responses
    if isinstance(data, list):
        raw_items = data
    else:
        raw_items = data.get("items", [])
        if not raw_items:
            return items

    for raw_item in raw_items:
        parsed = _parse_convocatoria(raw_item)
        if parsed:
            items.append(parsed)

    logger.info("Parsed %d convocatorias from BDNS response", len(items))
    return items


def _parse_convocatoria(item: dict[str, Any]) -> ParsedConvocatoria | None:
    """Parse a single convocatoria item."""
    source_id = item.get("codigoBdns") or item.get("codigo") or item.get("id")
    if not source_id:
        logger.debug("Skipping convocatoria without ID")
        return None

    source_id = str(source_id)
    title = item.get("titulo") or item.get("descripcion") or ""

    published_at = _parse_datetime(item.get("fechaPublicacion") or item.get("fechaInicio"))
    deadline_at = _parse_datetime(item.get("fechaFin") or item.get("plazoSolicitud"))

    organo = item.get("organo", {})
    if isinstance(organo, dict):
        granting_body = organo.get("nombre") or organo.get("descripcion")
        granting_body_id = organo.get("nif") or organo.get("cif")
    else:
        granting_body = str(organo) if organo else None
        granting_body_id = None

    budget = None
    currency = "EUR"
    presupuesto = item.get("presupuesto") or item.get("importeTotal")
    if presupuesto:
        try:
            budget = Decimal(str(presupuesto))
        except (ValueError, TypeError):
            pass

    url_official = item.get("urlBases") or item.get("url")

    beneficiary_types = []
    tipos = item.get("tiposBeneficiarios", [])
    if isinstance(tipos, list):
        for tipo in tipos:
            if isinstance(tipo, dict):
                beneficiary_types.append(tipo.get("descripcion", str(tipo)))
            else:
                beneficiary_types.append(str(tipo))

    sector = item.get("sector") or item.get("finalidad")
    if isinstance(sector, dict):
        sector = sector.get("descripcion")

    geographic_scope = item.get("ambitoGeografico")
    if isinstance(geographic_scope, dict):
        geographic_scope = geographic_scope.get("descripcion")

    return ParsedConvocatoria(
        source_id=source_id,
        title=title,
        summary=item.get("descripcion") if item.get("titulo") else None,
        published_at=published_at,
        deadline_at=deadline_at,
        url_official=url_official,
        granting_body=granting_body,
        granting_body_id=granting_body_id,
        budget=budget,
        currency=currency if budget else None,
        sector=sector,
        geographic_scope=geographic_scope,
        beneficiary_types=beneficiary_types,
        raw_data=item,
    )


def parse_concesiones(data: dict[str, Any] | list[dict[str, Any]]) -> list[ParsedConcesion]:
    """Parse BDNS concesiones response into items."""
    items: list[ParsedConcesion] = []

    if not data:
        return items

    # Handle both list and dict responses
    if isinstance(data, list):
        raw_items = data
    else:
        raw_items = data.get("items", [])
        if not raw_items:
            return items

    for raw_item in raw_items:
        parsed = _parse_concesion(raw_item)
        if parsed:
            items.append(parsed)

    logger.info("Parsed %d concesiones from BDNS response", len(items))
    return items


def _parse_concesion(item: dict[str, Any]) -> ParsedConcesion | None:
    """Parse a single concesion item."""
    source_id = item.get("idConcesion") or item.get("id") or item.get("codigo")
    if not source_id:
        logger.debug("Skipping concesion without ID")
        return None

    source_id = str(source_id)
    convocatoria_id = item.get("codigoBdns") or item.get("convocatoriaId")
    if convocatoria_id:
        convocatoria_id = str(convocatoria_id)

    title = item.get("tituloConvocatoria") or item.get("titulo") or ""
    awarded_at = _parse_datetime(item.get("fechaConcesion") or item.get("fechaResolucion") or item.get("fecha"))

    beneficiario = item.get("beneficiario", {})
    if isinstance(beneficiario, dict) and beneficiario:
        beneficiary_name = beneficiario.get("nombre") or beneficiario.get("descripcion")
        beneficiary_id = beneficiario.get("nif") or beneficiario.get("cif")
    else:
        beneficiary_name = item.get("nombreBeneficiario")
        beneficiary_id = item.get("nifBeneficiario")

    organo = item.get("organo", {})
    if isinstance(organo, dict) and organo:
        granting_body = organo.get("nombre") or organo.get("descripcion")
        granting_body_id = organo.get("nif") or organo.get("cif")
    else:
        granting_body = item.get("nombreOrgano")
        granting_body_id = item.get("nifOrgano")

    amount = None
    currency = "EUR"
    importe = item.get("importe") or item.get("importeConcedido")
    if importe:
        try:
            amount = Decimal(str(importe))
        except (ValueError, TypeError):
            pass

    return ParsedConcesion(
        source_id=source_id,
        convocatoria_id=convocatoria_id,
        title=title,
        awarded_at=awarded_at,
        beneficiary_name=beneficiary_name,
        beneficiary_id=beneficiary_id,
        granting_body=granting_body,
        granting_body_id=granting_body_id,
        amount=amount,
        currency=currency if amount else None,
        raw_data=item,
    )


def _parse_datetime(value: Any) -> datetime | None:
    """Parse datetime from various formats, preserving time if present.

    Supports formats:
    - ISO 8601: "2024-01-15T10:30:00", "2024-01-15T10:30:00Z"
    - Date only: "2024-01-15", "15/01/2024"
    - Spanish: "15-01-2024"
    """
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    value_str = str(value).strip()

    # Try ISO 8601 datetime formats first (to preserve time)
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]:
        try:
            dt = datetime.strptime(value_str, fmt)
            return dt.replace(tzinfo=UTC)
        except ValueError:
            continue

    # Fall back to date-only parsing
    parsed_date = parse_date(value_str)
    if parsed_date:
        return datetime.combine(parsed_date, datetime.min.time(), tzinfo=UTC)

    return None
