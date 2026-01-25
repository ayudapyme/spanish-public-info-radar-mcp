"""INE (Instituto Nacional de Estadística) client and parser.

Fetches statistical data from INE's JSON API.
Documentation: https://www.ine.es/dyngs/DataLab/manual.html?cid=45
API Reference: https://www.ine.es/dyngs/DAB/index.htm?cid=1100
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

from public_radar.common.http import create_http_client, fetch_with_retry

logger = logging.getLogger(__name__)

# API Base URL
# Format: https://servicios.ine.es/wstempus/js/{language}/{function}/{input}[?params]
INE_API_BASE = "https://servicios.ine.es/wstempus/js"
DEFAULT_LANGUAGE = "ES"


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class ParsedOperation:
    """Parsed INE statistical operation."""

    id: str
    code: str
    name: str
    url: str | None = None


@dataclass
class ParsedVariable:
    """Parsed INE variable."""

    id: str
    code: str
    name: str


@dataclass
class ParsedTable:
    """Parsed INE table."""

    id: str
    name: str
    operation_id: str | None = None


@dataclass
class ParsedSeries:
    """Parsed INE time series."""

    code: str
    name: str
    operation_id: str | None = None
    periodicity: str | None = None


@dataclass
class ParsedDataPoint:
    """Parsed INE data point."""

    period: str
    value: float | None
    status: str | None = None


# =============================================================================
# Client
# =============================================================================


class IneClient:
    """Client for fetching data from INE API.

    The INE API provides access to Spanish statistical data including:
    - Economic indicators (GDP, CPI, unemployment)
    - Demographics (population, births, deaths, migration)
    - Social statistics (education, health, housing)

    :param language: Language for responses (ES, EN, FR, CA). Defaults to ES.
    :type language: str
    :param http_client: Optional HTTP client to use.
    :type http_client: httpx.Client | None

    Example::

        >>> with IneClient() as client:
        ...     operations = client.fetch_operations()
        ...     print(f"Found {len(operations)} operations")
    """

    def __init__(
        self,
        language: str = DEFAULT_LANGUAGE,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._language = language
        self._http_client = http_client
        self._owns_client = http_client is None

    @property
    def http_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = create_http_client()
        return self._http_client

    def close(self) -> None:
        """Close the HTTP client if we own it."""
        if self._owns_client and self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def __enter__(self) -> "IneClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _build_url(self, function: str, input_param: str | None = None) -> str:
        """Build API URL for a given function.

        :param function: INE API function name (e.g., OPERACIONES_DISPONIBLES).
        :type function: str
        :param input_param: Optional input parameter for the function.
        :type input_param: str | None
        :return: Full API URL.
        :rtype: str
        """
        if input_param:
            return f"{INE_API_BASE}/{self._language}/{function}/{input_param}"
        return f"{INE_API_BASE}/{self._language}/{function}"

    def _fetch_json(
        self,
        function: str,
        input_param: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        """Fetch JSON data from INE API.

        :param function: INE API function name.
        :type function: str
        :param input_param: Optional input parameter.
        :type input_param: str | None
        :param params: Optional query parameters.
        :type params: dict[str, Any] | None
        :return: Parsed JSON response.
        :rtype: list[dict[str, Any]] | dict[str, Any] | None
        """
        url = self._build_url(function, input_param)
        logger.info("Fetching INE data: %s", url)

        try:
            response = fetch_with_retry(
                self.http_client,
                url,
                params=params,
                headers={"Accept": "application/json"},
                raise_for_status=True,
            )
            # Handle empty responses
            if not response.content or response.content.strip() == b"":
                logger.warning("INE returned empty response: %s", url)
                return None
            result: list[dict[str, Any]] | dict[str, Any] = response.json()
            return result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("INE resource not found: %s", url)
                return None
            raise
        except ValueError as e:
            # JSON decode error - likely empty or invalid response
            logger.warning("INE returned invalid JSON: %s - %s", url, e)
            return None
        except Exception as e:
            logger.exception("Error fetching INE data: %s", e)
            raise

    # -------------------------------------------------------------------------
    # Operations
    # -------------------------------------------------------------------------

    def fetch_operations(self) -> list[dict[str, Any]]:
        """Fetch all available statistical operations.

        :return: List of operations with id, code, name.
        :rtype: list[dict[str, Any]]

        Example::

            >>> client.fetch_operations()
            [{'Id': 1, 'Cod_IOE': 'IPC', 'Nombre': 'Índice de Precios de Consumo'}, ...]
        """
        result = self._fetch_json("OPERACIONES_DISPONIBLES")
        return result if isinstance(result, list) else []

    def fetch_operation(self, operation_id: str) -> dict[str, Any] | None:
        """Fetch details for a specific operation.

        :param operation_id: Operation ID or code (e.g., 'IPC', '25').
        :type operation_id: str
        :return: Operation details or None if not found.
        :rtype: dict[str, Any] | None
        """
        result = self._fetch_json("OPERACION", operation_id)
        return result if isinstance(result, dict) else None

    # -------------------------------------------------------------------------
    # Tables
    # -------------------------------------------------------------------------

    def fetch_tables_by_operation(self, operation_id: str) -> list[dict[str, Any]]:
        """Fetch tables for a specific operation.

        :param operation_id: Operation ID or code.
        :type operation_id: str
        :return: List of tables.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("TABLAS_OPERACION", operation_id)
        return result if isinstance(result, list) else []

    def fetch_table_data(
        self,
        table_id: str,
        nult: int | None = None,
        date_range: tuple[date, date] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch data from a specific table.

        :param table_id: Table ID.
        :type table_id: str
        :param nult: Number of last periods to return.
        :type nult: int | None
        :param date_range: Date range (start, end) for filtering.
        :type date_range: tuple[date, date] | None
        :return: Table data.
        :rtype: list[dict[str, Any]]
        """
        params: dict[str, Any] = {}
        if nult:
            params["nult"] = nult
        if date_range:
            start, end = date_range
            params["date"] = f"{start.strftime('%Y%m%d')}:{end.strftime('%Y%m%d')}"

        result = self._fetch_json("DATOS_TABLA", table_id, params=params or None)
        return result if isinstance(result, list) else []

    def fetch_table_groups(self, table_id: str) -> list[dict[str, Any]]:
        """Fetch groups/combos for a table.

        :param table_id: Table ID.
        :type table_id: str
        :return: List of groups.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("GRUPOS_TABLA", table_id)
        return result if isinstance(result, list) else []

    # -------------------------------------------------------------------------
    # Series
    # -------------------------------------------------------------------------

    def fetch_series_by_operation(self, operation_id: str) -> list[dict[str, Any]]:
        """Fetch all series for an operation.

        :param operation_id: Operation ID or code.
        :type operation_id: str
        :return: List of series.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("SERIES_OPERACION", operation_id)
        return result if isinstance(result, list) else []

    def fetch_series_by_table(self, table_id: str) -> list[dict[str, Any]]:
        """Fetch all series in a table.

        :param table_id: Table ID.
        :type table_id: str
        :return: List of series.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("SERIES_TABLA", table_id)
        return result if isinstance(result, list) else []

    def fetch_series_data(
        self,
        series_code: str,
        nult: int | None = None,
        date_range: tuple[date, date] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch data for a specific series.

        :param series_code: Series code.
        :type series_code: str
        :param nult: Number of last periods to return.
        :type nult: int | None
        :param date_range: Date range (start, end) for filtering.
        :type date_range: tuple[date, date] | None
        :return: Series data points.
        :rtype: list[dict[str, Any]]
        """
        params: dict[str, Any] = {}
        if nult:
            params["nult"] = nult
        if date_range:
            start, end = date_range
            params["date"] = f"{start.strftime('%Y%m%d')}:{end.strftime('%Y%m%d')}"

        result = self._fetch_json("DATOS_SERIE", series_code, params=params or None)
        return result if isinstance(result, list) else []

    def fetch_series(self, series_code: str) -> dict[str, Any] | None:
        """Fetch series metadata.

        :param series_code: Series code.
        :type series_code: str
        :return: Series metadata or None if not found.
        :rtype: dict[str, Any] | None
        """
        result = self._fetch_json("SERIE", series_code)
        return result if isinstance(result, dict) else None

    def search_series_metadata(
        self,
        operation_id: str,
        filters: dict[str, str] | None = None,
        periodicity: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search series by metadata filters.

        :param operation_id: Operation ID or code.
        :type operation_id: str
        :param filters: Variable:value filters (e.g., {'3': '1', '70': '18'}).
        :type filters: dict[str, str] | None
        :param periodicity: Periodicity ID filter.
        :type periodicity: str | None
        :return: Matching series.
        :rtype: list[dict[str, Any]]
        """
        params: dict[str, Any] = {}
        if filters:
            # Convert filters to g1, g2, g3... format
            for i, (var_id, value) in enumerate(filters.items(), 1):
                params[f"g{i}"] = f"{var_id}:{value}"
        if periodicity:
            params["p"] = periodicity

        result = self._fetch_json("SERIE_METADATAOPERACION", operation_id, params=params or None)
        return result if isinstance(result, list) else []

    # -------------------------------------------------------------------------
    # Variables
    # -------------------------------------------------------------------------

    def fetch_variables(self) -> list[dict[str, Any]]:
        """Fetch all available variables.

        :return: List of variables.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("VARIABLES")
        return result if isinstance(result, list) else []

    def fetch_variables_by_operation(self, operation_id: str) -> list[dict[str, Any]]:
        """Fetch variables for a specific operation.

        :param operation_id: Operation ID or code.
        :type operation_id: str
        :return: List of variables.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("VARIABLES_OPERACION", operation_id)
        return result if isinstance(result, list) else []

    def fetch_variable_values(self, variable_id: str) -> list[dict[str, Any]]:
        """Fetch all values for a variable.

        :param variable_id: Variable ID.
        :type variable_id: str
        :return: List of variable values.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("VALORES_VARIABLE", variable_id)
        return result if isinstance(result, list) else []

    def fetch_variable_values_by_operation(self, variable_id: str, operation_id: str) -> list[dict[str, Any]]:
        """Fetch values for a variable within an operation context.

        :param variable_id: Variable ID.
        :type variable_id: str
        :param operation_id: Operation ID or code.
        :type operation_id: str
        :return: List of variable values.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("VALORES_VARIABLEOPERACION", f"{variable_id}/{operation_id}")
        return result if isinstance(result, list) else []

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    def fetch_periodicities(self) -> list[dict[str, Any]]:
        """Fetch available periodicities.

        :return: List of periodicities (monthly, quarterly, annual, etc.).
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("PERIODICIDADES")
        return result if isinstance(result, list) else []

    def fetch_publications(self) -> list[dict[str, Any]]:
        """Fetch available publications.

        :return: List of INE publications.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("PUBLICACIONES")
        return result if isinstance(result, list) else []

    def fetch_publications_by_operation(self, operation_id: str) -> list[dict[str, Any]]:
        """Fetch publications for a specific operation.

        :param operation_id: Operation ID or code.
        :type operation_id: str
        :return: List of publications.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("PUBLICACIONES_OPERACION", operation_id)
        return result if isinstance(result, list) else []

    def fetch_classifications(self) -> list[dict[str, Any]]:
        """Fetch available classifications.

        :return: List of classifications.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("CLASIFICACIONES")
        return result if isinstance(result, list) else []

    def fetch_classifications_by_operation(self, operation_id: str) -> list[dict[str, Any]]:
        """Fetch classifications for a specific operation.

        :param operation_id: Operation ID or code.
        :type operation_id: str
        :return: List of classifications.
        :rtype: list[dict[str, Any]]
        """
        result = self._fetch_json("CLASIFICACIONES_OPERACION", operation_id)
        return result if isinstance(result, list) else []


# =============================================================================
# Parsers
# =============================================================================


def parse_operations(data: list[dict[str, Any]]) -> list[ParsedOperation]:
    """Parse operations response into dataclass objects.

    :param data: Raw API response.
    :type data: list[dict[str, Any]]
    :return: List of parsed operations.
    :rtype: list[ParsedOperation]
    """
    operations = []
    for item in data:
        operations.append(
            ParsedOperation(
                id=str(item.get("Id", "")),
                code=item.get("Cod_IOE", ""),
                name=item.get("Nombre", ""),
                url=item.get("Url", None),
            )
        )
    return operations


def parse_variables(data: list[dict[str, Any]]) -> list[ParsedVariable]:
    """Parse variables response into dataclass objects.

    :param data: Raw API response.
    :type data: list[dict[str, Any]]
    :return: List of parsed variables.
    :rtype: list[ParsedVariable]
    """
    variables = []
    for item in data:
        variables.append(
            ParsedVariable(
                id=str(item.get("Id", "")),
                code=item.get("Codigo", item.get("Cod", "")),
                name=item.get("Nombre", ""),
            )
        )
    return variables


def parse_tables(data: list[dict[str, Any]]) -> list[ParsedTable]:
    """Parse tables response into dataclass objects.

    :param data: Raw API response.
    :type data: list[dict[str, Any]]
    :return: List of parsed tables.
    :rtype: list[ParsedTable]
    """
    tables = []
    for item in data:
        tables.append(
            ParsedTable(
                id=str(item.get("Id", "")),
                name=item.get("Nombre", ""),
                operation_id=str(item.get("Id_Operacion", "")) or None,
            )
        )
    return tables


def parse_series(data: list[dict[str, Any]]) -> list[ParsedSeries]:
    """Parse series response into dataclass objects.

    :param data: Raw API response.
    :type data: list[dict[str, Any]]
    :return: List of parsed series.
    :rtype: list[ParsedSeries]
    """
    series = []
    for item in data:
        series.append(
            ParsedSeries(
                code=item.get("COD", item.get("Codigo", "")),
                name=item.get("Nombre", ""),
                operation_id=str(item.get("Id_Operacion", "")) or None,
                periodicity=item.get("Periodicidad", None),
            )
        )
    return series


def parse_data_points(data: list[dict[str, Any]]) -> list[ParsedDataPoint]:
    """Parse data points from series/table data.

    :param data: Raw API response with Data field.
    :type data: list[dict[str, Any]]
    :return: List of parsed data points.
    :rtype: list[ParsedDataPoint]
    """
    points = []
    for item in data:
        # Data can be nested in different structures
        data_list = item.get("Data", [item])
        if not isinstance(data_list, list):
            data_list = [data_list]

        for point in data_list:
            value = point.get("Valor", None)
            if value is not None:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = None

            points.append(
                ParsedDataPoint(
                    period=point.get("Fecha", point.get("T3_Periodo", "")),
                    value=value,
                    status=point.get("Secreto", None),
                )
            )
    return points
