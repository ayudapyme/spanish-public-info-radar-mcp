"""BOE (Boletín Oficial del Estado) API client.

This module provides a client for accessing the Spanish Official Gazette
Open Data API, including consolidated legislation and daily summaries.

API Documentation: https://www.boe.es/datosabiertos/api/api.php

Supported endpoints and their formats:
- /legislacion-consolidada (JSON)
- /legislacion-consolidada/id/{id} (XML only)
- /legislacion-consolidada/id/{id}/metadatos (JSON)
- /legislacion-consolidada/id/{id}/analisis (JSON)
- /legislacion-consolidada/id/{id}/texto (XML only)
- /legislacion-consolidada/id/{id}/texto/indice (JSON)
- /legislacion-consolidada/id/{id}/texto/bloque/{block_id} (XML only)
- /boe/sumario/{date} (JSON)
- /borme/sumario/{date} (JSON)
- /tablas-auxiliares/{table} (JSON)
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any, cast
from xml.etree import ElementTree as ET

from public_radar.common.http import (
    HttpClientError,
    NotFoundError,
    create_http_client,
    fetch_with_retry,
)

logger = logging.getLogger(__name__)

# BOE Open Data API base URL
BOE_API_BASE = "https://www.boe.es/datosabiertos/api"


@dataclass
class ParsedLegislation:
    """Parsed legislation item from BOE API."""

    id: str
    title: str
    department: str | None = None
    rang: str | None = None  # Regulatory hierarchy (Ley, Real Decreto, etc.)
    publication_date: str | None = None
    effective_date: str | None = None
    status: str | None = None  # vigente, derogado, etc.
    url_pdf: str | None = None
    url_html: str | None = None
    url_epub: str | None = None


@dataclass
class ParsedBoeSummaryItem:
    """Parsed item from BOE daily summary."""

    id: str
    title: str
    section: str | None = None
    department: str | None = None
    url_pdf: str | None = None
    url_html: str | None = None
    epigraph: str | None = None


@dataclass
class ParsedBormeSummaryItem:
    """Parsed item from BORME daily summary."""

    id: str
    title: str
    section: str | None = None
    province: str | None = None
    url_pdf: str | None = None
    act_type: str | None = None
    company_name: str | None = None


class BoeClient:
    """Client for BOE Open Data API.

    Provides access to:
    - Consolidated legislation search and retrieval
    - Daily BOE summaries
    - Daily BORME summaries

    Example::

        with BoeClient() as client:
            # Search legislation
            results = client.search_legislation("energías renovables")

            # Get BOE summary for a date
            summary = client.fetch_boe_summary(date(2024, 1, 15))

            # Get BORME summary
            borme = client.fetch_borme_summary(date(2024, 1, 15))
    """

    def __init__(self) -> None:
        """Initialize the BOE client."""
        self._client = create_http_client()

    def __enter__(self) -> "BoeClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and close HTTP client."""
        self._client.close()

    def search_legislation(
        self,
        query: str,
        date_from: date | None = None,
        date_to: date | None = None,
        title: str | None = None,
        department_code: str | None = None,
        legal_range_code: str | None = None,
        matter_code: str | None = None,
        include_derogated: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Search consolidated legislation.

        :param query: Search query text.
        :type query: str
        :param date_from: Filter by publication date from.
        :type date_from: date | None
        :param date_to: Filter by publication date to.
        :type date_to: date | None
        :param title: Filter by title (partial match).
        :type title: str | None
        :param department_code: Filter by department code.
        :type department_code: str | None
        :param legal_range_code: Filter by legal range (Ley, Real Decreto, etc.).
        :type legal_range_code: str | None
        :param matter_code: Filter by matter/subject code.
        :type matter_code: str | None
        :param include_derogated: Include repealed legislation in results.
        :type include_derogated: bool
        :param limit: Maximum results to return.
        :type limit: int
        :param offset: Number of results to skip.
        :type offset: int
        :return: List of legislation items.
        :rtype: list[dict[str, Any]]

        Example::

            client = BoeClient()
            results = client.search_legislation(
                query="subvenciones",
                date_from=date(2020, 1, 1),
                legal_range_code="ley",
                limit=10
            )
        """
        logger.info("Searching legislation: query=%s, limit=%d", query, limit)

        url = f"{BOE_API_BASE}/legislacion-consolidada"
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        # Only add query param if not empty (BOE API has a bug that returns 500 with query param)
        if query:
            params["query"] = query

        if date_from:
            params["from"] = date_from.strftime("%Y-%m-%d")
        if date_to:
            params["to"] = date_to.strftime("%Y-%m-%d")
        if title:
            params["titulo"] = title
        if department_code:
            params["departamento"] = department_code
        if legal_range_code:
            params["rango"] = legal_range_code
        if matter_code:
            params["materia"] = matter_code
        try:
            response = fetch_with_retry(self._client, url, params=params, headers={"Accept": "application/json"})
            data = response.json()

            # BOE API returns data in 'data' or 'items' key depending on endpoint
            items = data.get("data", data.get("items", []))
            if isinstance(items, list):
                # Apply client-side filter for estado_consolidacion if needed
                # The BOE API doesn't support this parameter in search
                if not include_derogated:
                    filtered_items = []
                    for item in items:
                        status = item.get("estado_consolidacion", {})
                        if isinstance(status, dict):
                            status_text = status.get("texto", "").lower()
                        else:
                            status_text = str(status).lower() if status else ""
                        # Include only if status is "vigente" or unknown
                        if "derogad" not in status_text:
                            filtered_items.append(item)
                    items = filtered_items
                logger.info("Found %d legislation items", len(items))
                return items
            return []

        except NotFoundError:
            logger.warning("No legislation found for query: %s", query)
            return []
        except HttpClientError as e:
            logger.error("Error searching legislation: %s", e)
            raise

    def fetch_legislation_by_id(self, legislation_id: str) -> dict[str, Any] | None:
        """Fetch legislation details by ID.

        Uses the /metadatos endpoint which supports JSON responses.
        The base /id/{id} endpoint only supports XML.

        :param legislation_id: Legislation identifier.
        :type legislation_id: str
        :return: Legislation details or None if not found.
        :rtype: dict[str, Any] | None

        Example::

            client = BoeClient()
            law = client.fetch_legislation_by_id("BOE-A-2023-12345")
        """
        logger.info("Fetching legislation: id=%s", legislation_id)

        # NOTE: The /id/{id} endpoint only supports XML, not JSON.
        # We use /id/{id}/metadatos which supports JSON and returns the same metadata.
        url = f"{BOE_API_BASE}/legislacion-consolidada/id/{legislation_id}/metadatos"

        try:
            response = fetch_with_retry(self._client, url, headers={"Accept": "application/json"})
            data = response.json()
            # The metadatos endpoint returns data in a list, get first item
            result = data.get("data", data)
            if isinstance(result, list) and len(result) > 0:
                return cast(dict[str, Any], result[0])
            return cast(dict[str, Any], result) if result else None

        except NotFoundError:
            logger.warning("Legislation not found: %s", legislation_id)
            return None
        except HttpClientError as e:
            logger.error("Error fetching legislation: %s", e)
            raise

    def fetch_legislation_text(self, legislation_id: str) -> dict[str, Any] | None:
        """Fetch the consolidated text of a legislation.

        NOTE: The /texto endpoint only supports XML, not JSON.
        This method fetches XML and converts it to a dictionary.

        :param legislation_id: Legislation identifier.
        :type legislation_id: str
        :return: Legislation text data or None if not found.
        :rtype: dict[str, Any] | None

        Example::

            client = BoeClient()
            text = client.fetch_legislation_text("BOE-A-2023-12345")
        """
        logger.info("Fetching legislation text: id=%s", legislation_id)

        url = f"{BOE_API_BASE}/legislacion-consolidada/id/{legislation_id}/texto"

        try:
            # NOTE: The /texto endpoint only supports XML, not JSON
            response = fetch_with_retry(self._client, url, headers={"Accept": "application/xml"})
            # Parse XML response
            result = _parse_xml_response(response.content)
            return result

        except NotFoundError:
            logger.warning("Legislation text not found: %s", legislation_id)
            return None
        except HttpClientError as e:
            logger.error("Error fetching legislation text: %s", e)
            raise

    def fetch_boe_summary(self, target_date: date) -> dict[str, Any] | None:
        """Fetch BOE daily summary for a specific date.

        :param target_date: Date to fetch summary for (format: YYYYMMDD).
        :type target_date: date
        :return: BOE summary data or None if not published.
        :rtype: dict[str, Any] | None

        Example::

            client = BoeClient()
            summary = client.fetch_boe_summary(date(2024, 1, 15))
        """
        date_str = target_date.strftime("%Y%m%d")
        logger.info("Fetching BOE summary for date: %s", date_str)

        url = f"{BOE_API_BASE}/boe/sumario/{date_str}"

        try:
            response = fetch_with_retry(self._client, url, headers={"Accept": "application/json"})
            data = response.json()
            result = data.get("data", data)
            return cast(dict[str, Any], result)

        except NotFoundError:
            logger.warning("No BOE published for date: %s", date_str)
            return None
        except HttpClientError as e:
            logger.error("Error fetching BOE summary: %s", e)
            raise

    def fetch_borme_summary(self, target_date: date) -> dict[str, Any] | None:
        """Fetch BORME daily summary for a specific date.

        :param target_date: Date to fetch summary for (format: YYYYMMDD).
        :type target_date: date
        :return: BORME summary data or None if not published.
        :rtype: dict[str, Any] | None

        Example::

            client = BoeClient()
            borme = client.fetch_borme_summary(date(2024, 1, 15))
        """
        date_str = target_date.strftime("%Y%m%d")
        logger.info("Fetching BORME summary for date: %s", date_str)

        url = f"{BOE_API_BASE}/borme/sumario/{date_str}"

        try:
            response = fetch_with_retry(self._client, url, headers={"Accept": "application/json"})
            data = response.json()
            result = data.get("data", data)
            return cast(dict[str, Any], result)

        except NotFoundError:
            logger.warning("No BORME published for date: %s (likely weekend/holiday)", date_str)
            return None
        except HttpClientError as e:
            logger.error("Error fetching BORME summary: %s", e)
            raise

    def fetch_legislation_analysis(self, legislation_id: str) -> dict[str, Any] | None:
        """Fetch legal analysis for a legislation (references, matters, notes).

        :param legislation_id: Legislation identifier (e.g., BOE-A-2015-10566).
        :type legislation_id: str
        :return: Analysis data or None if not found.
        :rtype: dict[str, Any] | None

        Example::

            client = BoeClient()
            analysis = client.fetch_legislation_analysis("BOE-A-2015-10566")
        """
        logger.info("Fetching legislation analysis: id=%s", legislation_id)

        url = f"{BOE_API_BASE}/legislacion-consolidada/id/{legislation_id}/analisis"

        try:
            response = fetch_with_retry(self._client, url, headers={"Accept": "application/json"})
            data = response.json()
            result = data.get("data", data)
            if isinstance(result, list) and len(result) > 0:
                return cast(dict[str, Any], result[0])
            return cast(dict[str, Any], result) if result else None

        except NotFoundError:
            logger.warning("Legislation analysis not found: %s", legislation_id)
            return None
        except HttpClientError as e:
            logger.error("Error fetching legislation analysis: %s", e)
            raise

    def fetch_legislation_index(self, legislation_id: str) -> dict[str, Any] | None:
        """Fetch the structure/index of a legislation.

        Returns the list of blocks (articles, dispositions, etc.) that make up the law.

        :param legislation_id: Legislation identifier (e.g., BOE-A-2015-10566).
        :type legislation_id: str
        :return: Structure data with list of blocks, or None if not found.
        :rtype: dict[str, Any] | None

        Example::

            client = BoeClient()
            structure = client.fetch_legislation_index("BOE-A-2015-10566")
            for block in structure.get("bloque", []):
                print(f"{block['id']}: {block['titulo']}")
        """
        logger.info("Fetching legislation index: id=%s", legislation_id)

        url = f"{BOE_API_BASE}/legislacion-consolidada/id/{legislation_id}/texto/indice"

        try:
            response = fetch_with_retry(self._client, url, headers={"Accept": "application/json"})
            data = response.json()
            result = data.get("data", data)
            if isinstance(result, list) and len(result) > 0:
                return cast(dict[str, Any], result[0])
            return cast(dict[str, Any], result) if result else None

        except NotFoundError:
            logger.warning("Legislation index not found: %s", legislation_id)
            return None
        except HttpClientError as e:
            logger.error("Error fetching legislation index: %s", e)
            raise

    def fetch_legislation_block(self, legislation_id: str, block_id: str) -> dict[str, Any] | None:
        """Fetch a specific block of legislation text.

        NOTE: This endpoint only supports XML, the response is parsed to dict.

        :param legislation_id: Legislation identifier (e.g., BOE-A-2015-10566).
        :type legislation_id: str
        :param block_id: Block identifier (e.g., "a1" for article 1, "dd" for derogation).
        :type block_id: str
        :return: Block data with versions, or None if not found.
        :rtype: dict[str, Any] | None

        Example::

            client = BoeClient()
            block = client.fetch_legislation_block("BOE-A-2015-10566", "a1")
        """
        logger.info("Fetching legislation block: id=%s, block=%s", legislation_id, block_id)

        url = f"{BOE_API_BASE}/legislacion-consolidada/id/{legislation_id}/texto/bloque/{block_id}"

        try:
            # This endpoint only supports XML
            response = fetch_with_retry(self._client, url, headers={"Accept": "application/xml"})
            return _parse_xml_response(response.content)

        except NotFoundError:
            logger.warning("Legislation block not found: %s/%s", legislation_id, block_id)
            return None
        except HttpClientError as e:
            logger.error("Error fetching legislation block: %s", e)
            raise

    def fetch_auxiliary_table(self, table_name: str) -> list[dict[str, Any]]:
        """Fetch an auxiliary table (departments, legal ranges, matters, etc.).

        Available tables:
        - departamentos: Government departments
        - rangos: Legal norm types (Ley, Real Decreto, etc.)
        - materias: Subject matters vocabulary
        - ambitos: Territorial scopes
        - estados-consolidacion: Consolidation statuses

        :param table_name: Name of the table to fetch.
        :type table_name: str
        :return: List of table entries.
        :rtype: list[dict[str, Any]]

        Example::

            client = BoeClient()
            departments = client.fetch_auxiliary_table("departamentos")
        """
        logger.info("Fetching auxiliary table: %s", table_name)

        url = f"{BOE_API_BASE}/datos-auxiliares/{table_name}"

        try:
            response = fetch_with_retry(self._client, url, headers={"Accept": "application/json"})
            data = response.json()
            result = data.get("data", [])
            if isinstance(result, list):
                return result
            return [result] if result else []

        except NotFoundError:
            logger.warning("Auxiliary table not found: %s", table_name)
            return []
        except HttpClientError as e:
            logger.error("Error fetching auxiliary table: %s", e)
            raise


def parse_legislation_search(data: list[dict[str, Any]]) -> list[ParsedLegislation]:
    """Parse legislation search results.

    :param data: Raw API response items.
    :type data: list[dict[str, Any]]
    :return: List of parsed legislation items.
    :rtype: list[ParsedLegislation]
    """
    results = []
    for item in data:
        # Handle nested dict fields (e.g., departamento.texto, rango.texto)
        dept = item.get("departamento")
        if isinstance(dept, dict):
            dept = dept.get("texto", dept.get("nombre", ""))

        rang = item.get("rango")
        if isinstance(rang, dict):
            rang = rang.get("texto", rang.get("nombre", ""))

        status = item.get("estado_consolidacion")
        if isinstance(status, dict):
            status = status.get("texto", status.get("nombre", ""))

        results.append(
            ParsedLegislation(
                id=item.get("identificador", item.get("id", "")),
                title=item.get("titulo", item.get("title", "")),
                department=dept,
                rang=rang,
                publication_date=item.get("fecha_publicacion"),
                effective_date=item.get("fecha_vigencia"),
                status=status,
                url_pdf=item.get("url_pdf"),
                url_html=item.get("url_html_consolidada", item.get("url_html")),
                url_epub=item.get("url_epub"),
            )
        )
    return results


def parse_boe_summary(data: dict[str, Any]) -> list[ParsedBoeSummaryItem]:
    """Parse BOE daily summary.

    :param data: Raw API response.
    :type data: dict[str, Any]
    :return: List of parsed summary items.
    :rtype: list[ParsedBoeSummaryItem]
    """
    results = []

    # BOE summary structure: sumario -> diario -> seccion -> departamento -> epigrafe -> item
    sumario = data.get("sumario", data)
    if isinstance(sumario, dict):
        diario = sumario.get("diario", [])
        if isinstance(diario, dict):
            diario = [diario]

        for d in diario:
            secciones = d.get("seccion", [])
            if isinstance(secciones, dict):
                secciones = [secciones]

            for seccion in secciones:
                # API uses 'nombre' not '@nombre'
                seccion_nombre = seccion.get("nombre", seccion.get("@nombre", ""))
                departamentos = seccion.get("departamento", [])
                if isinstance(departamentos, dict):
                    departamentos = [departamentos]

                for dept in departamentos:
                    dept_nombre = dept.get("nombre", dept.get("@nombre", ""))
                    epigrafes = dept.get("epigrafe", [])
                    if isinstance(epigrafes, dict):
                        epigrafes = [epigrafes]

                    for epigrafe in epigrafes:
                        epigrafe_nombre = epigrafe.get("nombre", epigrafe.get("@nombre", ""))
                        items = epigrafe.get("item", [])
                        if isinstance(items, dict):
                            items = [items]

                        for item in items:
                            # Extract URL - handle both snake_case and camelCase
                            url_pdf = item.get("url_pdf", item.get("urlPdf"))
                            if isinstance(url_pdf, dict):
                                url_pdf = url_pdf.get("texto")
                            url_html = item.get("url_html", item.get("urlHtml"))

                            results.append(
                                ParsedBoeSummaryItem(
                                    id=item.get("identificador", item.get("@id", "")),
                                    title=item.get("titulo", ""),
                                    section=seccion_nombre,
                                    department=dept_nombre,
                                    epigraph=epigrafe_nombre,
                                    url_pdf=url_pdf,
                                    url_html=url_html,
                                )
                            )

    return results


def parse_borme_summary(data: dict[str, Any]) -> list[ParsedBormeSummaryItem]:
    """Parse BORME daily summary.

    :param data: Raw API response.
    :type data: dict[str, Any]
    :return: List of parsed BORME items.
    :rtype: list[ParsedBormeSummaryItem]
    """
    results: list[ParsedBormeSummaryItem] = []

    # BORME summary structure varies:
    # - Real API: sumario -> diario -> seccion -> item (provinces as items)
    # - Fixtures: sumario -> diario -> seccion -> emisor -> item
    sumario = data.get("sumario", data)
    if isinstance(sumario, dict):
        diario = sumario.get("diario", [])
        if isinstance(diario, dict):
            diario = [diario]

        for d in diario:
            secciones = d.get("seccion", [])
            if isinstance(secciones, dict):
                secciones = [secciones]

            for seccion in secciones:
                seccion_nombre = seccion.get("nombre", seccion.get("@nombre", ""))

                # Handle two possible structures:
                # 1. Items directly in section (real API format)
                # 2. Items in emisor (fixture/XML format)
                emisores = seccion.get("emisor", [])
                if isinstance(emisores, dict):
                    emisores = [emisores]

                if emisores:
                    # Structure with emisor (province as emisor)
                    for emisor in emisores:
                        province = emisor.get("nombre", emisor.get("@nombre", ""))
                        items = emisor.get("item", [])
                        if isinstance(items, dict):
                            items = [items]

                        for item in items:
                            _add_borme_item(results, item, seccion_nombre, province)
                else:
                    # Direct items in section (provinces as items)
                    items = seccion.get("item", [])
                    if isinstance(items, dict):
                        items = [items]

                    for item in items:
                        title = item.get("titulo", "")
                        _add_borme_item(results, item, seccion_nombre, title)

    return results


def _add_borme_item(
    results: list[ParsedBormeSummaryItem],
    item: dict[str, Any],
    section: str,
    province: str,
) -> None:
    """Add a BORME item to results list.

    :param results: List to append to.
    :param item: Item data from API.
    :param section: Section name.
    :param province: Province name.
    """
    title = item.get("titulo", "")
    item_id = item.get("identificador", item.get("@id", ""))

    # Extract URL - handle both snake_case and camelCase
    url_pdf = item.get("url_pdf", item.get("urlPdf"))
    if isinstance(url_pdf, dict):
        url_pdf = url_pdf.get("texto")

    # Parse act type and company name from title (format: "ActType - CompanyName")
    act_type = None
    company_name = None
    if title and " - " in title:
        parts = title.split(" - ", 1)
        act_type = parts[0].strip()
        company_name = parts[1].strip() if len(parts) > 1 else None

    results.append(
        ParsedBormeSummaryItem(
            id=item_id,
            title=title,
            section=section,
            province=province,
            url_pdf=url_pdf,
            act_type=act_type,
            company_name=company_name,
        )
    )


def _parse_xml_response(content: bytes) -> dict[str, Any] | None:
    """Parse XML response from BOE API into a dictionary.

    :param content: Raw XML content from API response.
    :type content: bytes
    :return: Parsed data as dictionary or None if parsing fails.
    :rtype: dict[str, Any] | None
    """
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        logger.error("Failed to parse XML response: %s", e)
        return None

    # Check status
    status_elem = root.find("status")
    if status_elem is not None:
        code_elem = status_elem.find("code")
        if code_elem is not None and code_elem.text != "200":
            logger.warning("BOE API returned error status: %s", code_elem.text)
            return None

    # Parse data element
    data_elem = root.find("data")
    if data_elem is None:
        return None

    return _xml_element_to_dict(data_elem)


def _xml_element_to_dict(element: ET.Element) -> dict[str, Any]:
    """Convert XML element to dictionary recursively.

    Handles attributes with @ prefix and nested elements.

    :param element: XML element to convert.
    :type element: ET.Element
    :return: Dictionary representation of the element.
    :rtype: dict[str, Any]
    """
    result: dict[str, Any] = {}

    # Add attributes with @ prefix
    for key, value in element.attrib.items():
        result[f"@{key}"] = value

    # Process child elements
    children = list(element)
    if children:
        child_dict: dict[str, Any] = {}
        for child in children:
            tag = child.tag
            child_data = _xml_element_to_dict(child)

            if tag in child_dict:
                # Convert to list if multiple elements with same tag
                if not isinstance(child_dict[tag], list):
                    child_dict[tag] = [child_dict[tag]]
                child_dict[tag].append(child_data)
            else:
                child_dict[tag] = child_data

        # If element has both text and children, add text as 'text' key
        if element.text and element.text.strip():
            child_dict["text"] = element.text.strip()

        result.update(child_dict)
    else:
        # Leaf node - return text content or empty string
        text = element.text.strip() if element.text else ""
        if result:  # Has attributes
            if text:
                result["text"] = text
        else:
            return text  # type: ignore[return-value]

    return result
