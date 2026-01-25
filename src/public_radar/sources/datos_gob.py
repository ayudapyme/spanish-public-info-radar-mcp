"""datos.gob.es (Spanish Open Data Portal) client and parser.

Fetches and parses open datasets from the Spanish national open data catalog.
API Documentation: https://datos.gob.es/apidata
Uses Linked Data API format (v0.2).
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, cast

import httpx

from public_radar.common.http import NotFoundError, create_http_client, fetch_with_retry

logger = logging.getLogger(__name__)

DATOS_GOB_API_BASE = "https://datos.gob.es/apidata/catalog"
DEFAULT_PAGE_SIZE = 20


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class ParsedDistribution:
    """Parsed distribution (download format) for a dataset."""

    url: str
    format: str | None
    title: str | None


@dataclass
class ParsedDataset:
    """Parsed datos.gob.es dataset ready for presentation."""

    identifier: str
    title: str
    description: str | None
    publisher: str | None
    publisher_id: str | None
    themes: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    distributions: list[ParsedDistribution] = field(default_factory=list)
    license: str | None = None
    issued: datetime | None = None
    modified: datetime | None = None
    language: str | None = None
    spatial: str | None = None
    url: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedTheme:
    """Parsed theme/category from datos.gob.es."""

    code: str
    label: str
    url: str | None = None


@dataclass
class ParsedPublisher:
    """Parsed publisher/organization from datos.gob.es."""

    code: str
    name: str | None = None
    url: str | None = None


# =============================================================================
# Client
# =============================================================================


class DatosGobClient:
    """Client for fetching data from datos.gob.es open data portal."""

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

    def __enter__(self) -> "DatosGobClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def search_datasets(
        self,
        query: str | None = None,
        theme: str | None = None,
        publisher: str | None = None,
        page: int = 0,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        """Search datasets in the datos.gob.es catalog.

        :param query: Search query text (searches title, description, keywords).
        :type query: str | None
        :param theme: Filter by theme code (e.g., 'medio-ambiente', 'economia').
        :type theme: str | None
        :param publisher: Filter by publisher ID.
        :type publisher: str | None
        :param page: Page number (0-indexed).
        :type page: int
        :param page_size: Number of results per page.
        :type page_size: int
        :return: API response with items and pagination info.
        :rtype: dict[str, Any]
        """
        url = f"{DATOS_GOB_API_BASE}/dataset.json"
        params: dict[str, Any] = {"_page": page, "_pageSize": page_size}

        if query:
            # The API searches across title/description/keywords
            params["_search"] = query
        if theme:
            # Theme can be a code like 'medio-ambiente' or full URI
            if not theme.startswith("http"):
                params["theme"] = f"http://datos.gob.es/kos/sector-publico/sector/{theme}"
            else:
                params["theme"] = theme
        if publisher:
            # Publisher can be an ID or full URI
            if not publisher.startswith("http"):
                params["publisher"] = f"http://datos.gob.es/recurso/sector-publico/org/Organismo/{publisher}"
            else:
                params["publisher"] = publisher

        logger.info("Searching datos.gob.es datasets page %d with params: %s", page, params)

        response = fetch_with_retry(
            self.http_client,
            url,
            params=params,
            headers={"Accept": "application/json"},
            raise_for_status=True,
        )

        data = response.json()
        result = data.get("result", data)
        items = result.get("items", [])
        logger.info("Found %d datasets (page %d)", len(items), page)

        return cast(dict[str, Any], result)

    def get_dataset(self, dataset_id: str) -> dict[str, Any] | None:
        """Get details of a specific dataset by ID.

        :param dataset_id: Dataset identifier (e.g., 'e05068001-mapas-estrategicos-de-ruido').
        :type dataset_id: str
        :return: Dataset details or None if not found.
        :rtype: dict[str, Any] | None
        """
        url = f"{DATOS_GOB_API_BASE}/dataset/{dataset_id}.json"
        logger.info("Fetching datos.gob.es dataset: %s", dataset_id)

        try:
            response = fetch_with_retry(
                self.http_client,
                url,
                headers={"Accept": "application/json"},
                raise_for_status=True,
            )
            data = response.json()
            return cast(dict[str, Any], data.get("result", data))
        except NotFoundError:
            logger.info("Dataset %s not found", dataset_id)
            return None

    def list_themes(self, page_size: int = 50) -> list[dict[str, Any]]:
        """List available themes/categories.

        :param page_size: Number of themes to fetch.
        :type page_size: int
        :return: List of theme objects.
        :rtype: list[dict[str, Any]]
        """
        url = f"{DATOS_GOB_API_BASE}/theme.json"
        params: dict[str, Any] = {"_pageSize": page_size}

        logger.info("Fetching datos.gob.es themes")

        response = fetch_with_retry(
            self.http_client,
            url,
            params=params,
            headers={"Accept": "application/json"},
            raise_for_status=True,
        )

        data = response.json()
        result = data.get("result", data)
        items = result.get("items", [])
        logger.info("Found %d themes", len(items))

        return cast(list[dict[str, Any]], items)

    def list_publishers(self, page: int = 0, page_size: int = DEFAULT_PAGE_SIZE) -> dict[str, Any]:
        """List publishers/organizations.

        :param page: Page number (0-indexed).
        :type page: int
        :param page_size: Number of results per page.
        :type page_size: int
        :return: API response with publisher items.
        :rtype: dict[str, Any]
        """
        url = f"{DATOS_GOB_API_BASE}/publisher.json"
        params: dict[str, Any] = {"_page": page, "_pageSize": page_size}

        logger.info("Fetching datos.gob.es publishers page %d", page)

        response = fetch_with_retry(
            self.http_client,
            url,
            params=params,
            headers={"Accept": "application/json"},
            raise_for_status=True,
        )

        data = response.json()
        result = data.get("result", data)
        items = result.get("items", [])
        logger.info("Found %d publishers (page %d)", len(items), page)

        return cast(dict[str, Any], result)


# =============================================================================
# Parsers
# =============================================================================


def parse_datasets(data: dict[str, Any]) -> list[ParsedDataset]:
    """Parse datos.gob.es dataset search response.

    :param data: API response from search_datasets.
    :type data: dict[str, Any]
    :return: List of parsed datasets.
    :rtype: list[ParsedDataset]
    """
    items: list[ParsedDataset] = []

    if not data:
        return items

    raw_items = data.get("items", [])
    if not raw_items:
        return items

    for raw_item in raw_items:
        parsed = _parse_dataset(raw_item)
        if parsed:
            items.append(parsed)

    logger.info("Parsed %d datasets from datos.gob.es response", len(items))
    return items


def _parse_dataset(item: dict[str, Any]) -> ParsedDataset | None:
    """Parse a single dataset item."""
    # Get identifier
    identifier = item.get("identifier")
    if not identifier:
        # Try to extract from _about URL
        about = item.get("_about", "")
        if about:
            identifier = about.split("/")[-1]
    if not identifier:
        logger.debug("Skipping dataset without identifier")
        return None

    # Get title (multilingual)
    title = _extract_multilingual_value(item.get("title", []), prefer_lang="es")
    if not title:
        title = str(identifier)

    # Get description (multilingual)
    description = _extract_multilingual_value(item.get("description", []), prefer_lang="es")

    # Get publisher
    publisher_uri = item.get("publisher")
    publisher_id = None
    publisher_name = None
    if publisher_uri:
        if isinstance(publisher_uri, dict):
            publisher_id = publisher_uri.get("_about", "").split("/")[-1]
            publisher_name = publisher_uri.get("name")
        elif isinstance(publisher_uri, str):
            publisher_id = publisher_uri.split("/")[-1]

    # Get themes
    themes: list[str] = []
    raw_themes = item.get("theme", [])
    if not isinstance(raw_themes, list):
        raw_themes = [raw_themes]
    for theme in raw_themes:
        if isinstance(theme, str):
            # Extract theme code from URI
            theme_code = theme.split("/")[-1]
            if theme_code and not theme_code.startswith("http"):
                themes.append(theme_code)
        elif isinstance(theme, dict):
            theme_code = theme.get("_about", "").split("/")[-1]
            if theme_code:
                themes.append(theme_code)

    # Get keywords
    keywords: list[str] = []
    raw_keywords = item.get("keyword", [])
    if not isinstance(raw_keywords, list):
        raw_keywords = [raw_keywords]
    for kw in raw_keywords:
        if isinstance(kw, dict):
            kw_value = kw.get("_value", "")
            if kw_value:
                keywords.append(kw_value)
        elif isinstance(kw, str):
            keywords.append(kw)

    # Get distributions
    distributions: list[ParsedDistribution] = []
    raw_distributions = item.get("distribution", [])
    if not isinstance(raw_distributions, list):
        raw_distributions = [raw_distributions]
    for dist in raw_distributions:
        if isinstance(dist, dict):
            access_url = dist.get("accessURL", "")
            format_info = dist.get("format")
            format_str = None
            if isinstance(format_info, dict):
                format_str = format_info.get("_value") or format_info.get("value")
            elif isinstance(format_info, str):
                format_str = format_info.split("/")[-1] if "/" in format_info else format_info
            dist_title = _extract_multilingual_value(dist.get("title", []), prefer_lang="es")
            if access_url:
                distributions.append(ParsedDistribution(url=access_url, format=format_str, title=dist_title))

    # Get license
    license_uri = item.get("license")
    license_str = None
    if license_uri:
        if isinstance(license_uri, str):
            license_str = license_uri.split("/")[-1]
        elif isinstance(license_uri, dict):
            license_str = license_uri.get("_about", "").split("/")[-1]

    # Get dates
    issued = _parse_date(item.get("issued"))
    modified = _parse_date(item.get("modified"))

    # Get language
    language_raw = item.get("language")
    language_str: str | None = None
    if isinstance(language_raw, list) and language_raw:
        language_raw = language_raw[0]
    if isinstance(language_raw, str):
        language_str = language_raw.split("/")[-1] if "/" in language_raw else language_raw

    # Get spatial coverage
    spatial_raw = item.get("spatial")
    spatial_str: str | None = None
    if isinstance(spatial_raw, str):
        spatial_str = spatial_raw.split("/")[-1] if "/" in spatial_raw else spatial_raw
    elif isinstance(spatial_raw, dict):
        spatial_str = spatial_raw.get("_about", "").split("/")[-1] or None

    # Get URL
    url = item.get("_about")

    return ParsedDataset(
        identifier=str(identifier),
        title=title,
        description=description,
        publisher=publisher_name,
        publisher_id=publisher_id,
        themes=themes,
        keywords=keywords,
        distributions=distributions,
        license=license_str,
        issued=issued,
        modified=modified,
        language=language_str,
        spatial=spatial_str,
        url=url,
        raw_data=item,
    )


def parse_themes(items: list[Any]) -> list[ParsedTheme]:
    """Parse datos.gob.es themes response.

    :param items: List of theme items from API (can be URIs or dicts).
    :type items: list[Any]
    :return: List of parsed themes.
    :rtype: list[ParsedTheme]
    """
    themes: list[ParsedTheme] = []

    for item in items:
        # Handle both string URIs and dict items
        if isinstance(item, str):
            # Item is a URI string
            code = item.split("/")[-1] if item else ""
            if code:
                label = code.replace("-", " ").title()
                themes.append(ParsedTheme(code=code, label=label, url=item))
        elif isinstance(item, dict):
            about = item.get("_about", "")
            code = about.split("/")[-1] if about else ""
            if not code:
                continue

            # Get label (multilingual)
            extracted_label = _extract_multilingual_value(item.get("prefLabel", []), prefer_lang="es")
            label = extracted_label if extracted_label else code.replace("-", " ").title()

            themes.append(ParsedTheme(code=code, label=label, url=about))

    logger.info("Parsed %d themes from datos.gob.es response", len(themes))
    return themes


def parse_publishers(data: dict[str, Any]) -> list[ParsedPublisher]:
    """Parse datos.gob.es publishers response.

    :param data: API response from list_publishers.
    :type data: dict[str, Any]
    :return: List of parsed publishers.
    :rtype: list[ParsedPublisher]
    """
    publishers: list[ParsedPublisher] = []

    items = data.get("items", [])
    for item in items:
        # Items are usually just URIs
        if isinstance(item, str):
            code = item.split("/")[-1]
            if code:
                publishers.append(ParsedPublisher(code=code, url=item))
        elif isinstance(item, dict):
            about = item.get("_about", "")
            code = about.split("/")[-1] if about else ""
            name = item.get("name") or item.get("prefLabel")
            if isinstance(name, list):
                name = _extract_multilingual_value(name, prefer_lang="es")
            if code:
                publishers.append(ParsedPublisher(code=code, name=name, url=about))

    logger.info("Parsed %d publishers from datos.gob.es response", len(publishers))
    return publishers


def _extract_multilingual_value(values: Any, prefer_lang: str = "es") -> str | None:
    """Extract value from multilingual field, preferring specified language.

    :param values: Multilingual value (list of dicts with _value and _lang).
    :param prefer_lang: Preferred language code.
    :return: Extracted string value or None.
    """
    if not values:
        return None

    if isinstance(values, str):
        return values

    if not isinstance(values, list):
        return str(values) if values else None

    # First pass: look for preferred language
    for item in values:
        if isinstance(item, dict):
            lang = item.get("_lang", "")
            if lang == prefer_lang:
                val = item.get("_value")
                return str(val) if val else None
        elif isinstance(item, str):
            return item

    # Second pass: return any value
    for item in values:
        if isinstance(item, dict):
            value = item.get("_value")
            if value:
                return str(value)
        elif isinstance(item, str):
            return item

    return None


def _parse_date(value: Any) -> datetime | None:
    """Parse date from API response.

    :param value: Date value (ISO string or dict with _value).
    :return: Parsed datetime or None.
    """
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    date_str = None
    if isinstance(value, dict):
        date_str = value.get("_value")
    elif isinstance(value, str):
        date_str = value

    if not date_str:
        return None

    # Try ISO formats
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None
