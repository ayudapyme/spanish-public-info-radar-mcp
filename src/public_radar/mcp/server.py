"""MCP Server for Spanish Public Data.

This module provides the MCP server that exposes tools for querying
Spanish government open data APIs (BDNS, BOE, INE) on-the-fly.
"""

import json
import logging
import os
import sys
import time
from datetime import date, datetime, timedelta
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import GetPromptResult, Prompt, TextContent, Tool
from pydantic import BaseModel, ConfigDict, Field

# Configure logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Input Schemas for MCP Tools
# =============================================================================


class StrictModel(BaseModel):
    """Base model with strict validation (no extra fields allowed)."""

    model_config = ConfigDict(extra="forbid")


class SearchGrantsInput(StrictModel):
    """Input schema for search_grants tool."""

    date_from: str | None = Field(
        default=None,
        description="Start date for filtering (YYYY-MM-DD format)",
    )
    date_to: str | None = Field(
        default=None,
        description="End date for filtering (YYYY-MM-DD format)",
    )
    granting_body: str | None = Field(
        default=None,
        description="Filter by granting body/organization code",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum results to return",
    )


class SearchGrantAwardsInput(StrictModel):
    """Input schema for search_grant_awards tool."""

    date_from: str | None = Field(
        default=None,
        description="Start date for filtering (YYYY-MM-DD format)",
    )
    date_to: str | None = Field(
        default=None,
        description="End date for filtering (YYYY-MM-DD format)",
    )
    beneficiary_nif: str | None = Field(
        default=None,
        description="Filter by beneficiary NIF/CIF (Spanish tax ID)",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum results to return",
    )


class GetGrantDetailsInput(StrictModel):
    """Input schema for get_grant_details tool."""

    grant_id: str = Field(description="Grant call ID from BDNS")


class SearchLegislationInput(StrictModel):
    """Input schema for search_legislation tool."""

    query: str = Field(description="Search query text")
    date_from: str | None = Field(
        default=None,
        description="Start date for filtering (YYYY-MM-DD format)",
    )
    date_to: str | None = Field(
        default=None,
        description="End date for filtering (YYYY-MM-DD format)",
    )
    title: str | None = Field(
        default=None,
        description="Filter by title (partial match)",
    )
    department_code: str | None = Field(
        default=None,
        description="Filter by department code (use get_departments_table to get codes)",
    )
    legal_range_code: str | None = Field(
        default=None,
        description="Filter by legal range code: Ley, Real Decreto, etc. (use get_legal_ranges_table to get codes)",
    )
    matter_code: str | None = Field(
        default=None,
        description="Filter by matter/subject code (use get_matters_table to get codes)",
    )
    include_derogated: bool = Field(
        default=False,
        description="Include repealed/derogated legislation in results",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip (for pagination)",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum results to return",
    )


class GetLegislationDetailsInput(StrictModel):
    """Input schema for get_legislation_details tool."""

    legislation_id: str = Field(description="Legislation ID from BOE")
    include_analysis: bool = Field(
        default=False,
        description="Include legal analysis (references, modifications, related laws)",
    )


class FindRelatedLawsInput(StrictModel):
    """Input schema for find_related_laws tool."""

    legislation_id: str = Field(description="Legislation ID from BOE (e.g., BOE-A-2015-10566)")
    relation_type: str | None = Field(
        default=None,
        description="Filter by relation type: 'modifies', 'modified_by', 'repeals', 'repealed_by', 'references', 'referenced_by'. If not specified, returns all relations.",
    )


class SearchRecentBoeInput(StrictModel):
    """Input schema for search_recent_boe tool."""

    days_back: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Number of days to search back from today (1-30)",
    )
    search_terms: str | None = Field(
        default=None,
        description="Search terms to filter items by title (case-insensitive, partial match)",
    )
    section_filter: str | None = Field(
        default=None,
        description="Filter by section (e.g., '1', '2A', '2B', '3', '4', '5', 'T')",
    )
    max_items: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum total items to return across all days",
    )


class GetLegislationTextInput(StrictModel):
    """Input schema for get_legislation_text tool."""

    legislation_id: str = Field(description="Legislation ID from BOE")


class GetLegislationBlockInput(StrictModel):
    """Input schema for get_legislation_block tool."""

    legislation_id: str = Field(description="Legislation ID from BOE (e.g., BOE-A-2015-10566)")
    block_id: str = Field(
        description="Block identifier (e.g., 'a1' for article 1, 'a2' for article 2, 'dd' for derogation disposition)"
    )


class GetLegislationStructureInput(StrictModel):
    """Input schema for get_legislation_structure tool."""

    legislation_id: str = Field(description="Legislation ID from BOE (e.g., BOE-A-2015-10566)")


class GetDepartmentsTableInput(StrictModel):
    """Input schema for get_departments_table tool."""

    pass  # No parameters needed


class GetLegalRangesTableInput(StrictModel):
    """Input schema for get_legal_ranges_table tool."""

    pass  # No parameters needed


class GetMattersTableInput(StrictModel):
    """Input schema for get_matters_table tool."""

    pass  # No parameters needed


class GetBoeSummaryInput(StrictModel):
    """Input schema for get_boe_summary tool."""

    date: str | None = Field(
        default=None,
        description="Date to fetch BOE summary for (YYYY-MM-DD). Defaults to today.",
    )
    section_filter: str | None = Field(
        default=None,
        description="Filter by section (e.g., '1', '2A', '2B', '3', '4', '5', 'T')",
    )
    department_filter: str | None = Field(
        default=None,
        description="Filter by department name (partial match, case-insensitive)",
    )
    max_items: int | None = Field(
        default=None,
        ge=1,
        le=500,
        description="Maximum number of items to return (default: all items)",
    )


class GetBormeSummaryInput(StrictModel):
    """Input schema for get_borme_summary tool."""

    date: str | None = Field(
        default=None,
        description="Date to fetch BORME summary for (YYYY-MM-DD). Defaults to most recent weekday.",
    )
    province_filter: str | None = Field(
        default=None,
        description="Filter by province name (partial match, case-insensitive)",
    )
    max_items: int | None = Field(
        default=None,
        ge=1,
        le=500,
        description="Maximum number of items to return (default: all items)",
    )


# INE Input Schemas


class GetIneOperationsInput(StrictModel):
    """Input schema for get_ine_operations tool."""

    pass  # No parameters needed


class GetIneOperationInput(StrictModel):
    """Input schema for get_ine_operation tool."""

    operation_id: str = Field(
        description="Operation ID or code (e.g., 'IPC', 'EPA', '25')",
    )


class GetIneTableDataInput(StrictModel):
    """Input schema for get_ine_table_data tool."""

    table_id: str = Field(description="Table ID from INE")
    nult: int | None = Field(
        default=12,
        ge=1,
        le=100,
        description="Number of last periods to return (default: 12)",
    )


class GetIneSeriesDataInput(StrictModel):
    """Input schema for get_ine_series_data tool."""

    series_code: str = Field(description="Series code from INE")
    nult: int | None = Field(
        default=12,
        ge=1,
        le=100,
        description="Number of last periods to return (default: 12)",
    )


class SearchIneTablesInput(StrictModel):
    """Input schema for search_ine_tables tool."""

    operation_id: str = Field(
        description="Operation ID or code to search tables for (e.g., 'IPC', 'EPA')",
    )


class GetIneVariablesInput(StrictModel):
    """Input schema for get_ine_variables tool."""

    operation_id: str | None = Field(
        default=None,
        description="Optional operation ID to filter variables. If not provided, returns all variables.",
    )


# datos.gob.es Input Schemas


class SearchOpenDataInput(StrictModel):
    """Input schema for search_open_data tool."""

    query: str | None = Field(
        default=None,
        description="Search query text (searches title, description, keywords)",
    )
    theme: str | None = Field(
        default=None,
        description="Filter by theme code (e.g., 'medio-ambiente', 'economia', 'salud')",
    )
    publisher: str | None = Field(
        default=None,
        description="Filter by publisher/organization ID",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum results to return",
    )


class GetOpenDataDetailsInput(StrictModel):
    """Input schema for get_open_data_details tool."""

    dataset_id: str = Field(
        description="Dataset identifier (e.g., 'e05068001-mapas-estrategicos-de-ruido')",
    )


class ListOpenDataThemesInput(StrictModel):
    """Input schema for list_open_data_themes tool."""

    pass  # No parameters needed


class ListOpenDataPublishersInput(StrictModel):
    """Input schema for list_open_data_publishers tool."""

    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum results to return",
    )


# =============================================================================
# Schema Helper
# =============================================================================


def _flatten_schema(schema: dict) -> dict:
    """Fix Pydantic v2 anyOf/oneOf from Optional fields for n8n compatibility.

    Pydantic v2 generates {"anyOf": [{"type": "string"}, {"type": "null"}]}
    for Optional[str] fields. n8n cannot render anyOf and crashes with
    'cannot access property inputType'. This function flattens those to
    a simple {"type": "string"} keeping the original default and description.
    Also handles int | None -> integer.
    """
    schema = dict(schema)
    props = schema.get("properties")
    if not props:
        return schema

    new_props = {}
    for key, val in props.items():
        val = dict(val)
        if "anyOf" in val:
            # Find the non-null type
            non_null = [t for t in val["anyOf"] if t.get("type") != "null"]
            if non_null:
                # Merge: keep description, default, constraints; replace anyOf with type
                merged = {k: v for k, v in val.items() if k != "anyOf"}
                merged["type"] = non_null[0]["type"]
                # Carry over constraints from the non-null type (ge/le become minimum/maximum)
                for constraint_key in ("minimum", "maximum", "minLength", "maxLength", "enum"):
                    if constraint_key in non_null[0]:
                        merged[constraint_key] = non_null[0][constraint_key]
                val = merged
        new_props[key] = val

    schema["properties"] = new_props
    return schema


# =============================================================================
# Server Factory
# =============================================================================


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("spanish-public-data")

    @server.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
    async def list_tools() -> list[Tool]:
        """List available tools for querying Spanish public data."""
        return [
            # System info
            Tool(
                name="get_system_info",
                description="Get overview of available data sources and tools. Call this first to understand what data is available.",
                inputSchema={"type": "object", "properties": {}},
            ),
            # BDNS tools (Grants)
            Tool(
                name="search_grants",
                description="Search grant calls (convocatorias) from BDNS. Filter by date range and granting body.",
                inputSchema=_flatten_schema(SearchGrantsInput.model_json_schema()),
            ),
            Tool(
                name="search_grant_awards",
                description="Search awarded grants (concesiones) from BDNS. Filter by date range and beneficiary NIF.",
                inputSchema=_flatten_schema(SearchGrantAwardsInput.model_json_schema()),
            ),
            Tool(
                name="get_grant_details",
                description="Get detailed information about a specific grant call by ID.",
                inputSchema=_flatten_schema(GetGrantDetailsInput.model_json_schema()),
            ),
            # BOE tools (Legislation)
            Tool(
                name="search_legislation",
                description="Search consolidated Spanish legislation. Filter by query, dates, title, department, legal range (Ley, Real Decreto, etc.), matter, and include/exclude repealed laws.",
                inputSchema=_flatten_schema(SearchLegislationInput.model_json_schema()),
            ),
            Tool(
                name="get_legislation_details",
                description="Get metadata and details of a specific law or regulation.",
                inputSchema=_flatten_schema(GetLegislationDetailsInput.model_json_schema()),
            ),
            Tool(
                name="get_legislation_text",
                description="Get the full consolidated text of a law or regulation.",
                inputSchema=_flatten_schema(GetLegislationTextInput.model_json_schema()),
            ),
            Tool(
                name="get_legislation_structure",
                description="Get the structure/index of a law showing all its blocks (articles, dispositions, annexes). Use this to discover block IDs before fetching specific blocks.",
                inputSchema=_flatten_schema(GetLegislationStructureInput.model_json_schema()),
            ),
            Tool(
                name="get_legislation_block",
                description="Get a specific block (article, disposition, annex) from a law. Use get_legislation_structure first to discover available block IDs.",
                inputSchema=_flatten_schema(GetLegislationBlockInput.model_json_schema()),
            ),
            Tool(
                name="get_departments_table",
                description="Get the list of government departments with their codes. Use these codes with search_legislation's department_code filter.",
                inputSchema=_flatten_schema(GetDepartmentsTableInput.model_json_schema()),
            ),
            Tool(
                name="get_legal_ranges_table",
                description="Get the list of legal norm types (Ley, Real Decreto, Orden, etc.) with their codes. Use these codes with search_legislation's legal_range_code filter.",
                inputSchema=_flatten_schema(GetLegalRangesTableInput.model_json_schema()),
            ),
            Tool(
                name="get_matters_table",
                description="Get the list of subject matters/topics with their codes. Use these codes with search_legislation's matter_code filter.",
                inputSchema=_flatten_schema(GetMattersTableInput.model_json_schema()),
            ),
            Tool(
                name="find_related_laws",
                description="Find laws related to a given legislation (modifications, repeals, references). Use this to understand what a law modifies, what modifies it, and related legislation.",
                inputSchema=_flatten_schema(FindRelatedLawsInput.model_json_schema()),
            ),
            Tool(
                name="search_recent_boe",
                description="Search BOE publications from the last N days. Useful for finding recent legislative activity. Supports filtering by section and search terms.",
                inputSchema=_flatten_schema(SearchRecentBoeInput.model_json_schema()),
            ),
            Tool(
                name="get_boe_summary",
                description="Get the daily BOE (Official Gazette) summary for a specific date. Supports filtering by section (1, 2A, 2B, 3, 4, 5, T) and department.",
                inputSchema=_flatten_schema(GetBoeSummaryInput.model_json_schema()),
            ),
            # BORME tools (Company Registry)
            Tool(
                name="get_borme_summary",
                description="Get the daily BORME (Company Registry) summary with company acts for a specific date. Supports filtering by province. Defaults to most recent weekday.",
                inputSchema=_flatten_schema(GetBormeSummaryInput.model_json_schema()),
            ),
            # INE tools (Statistics)
            Tool(
                name="get_ine_operations",
                description="Get list of all available INE statistical operations (IPC, EPA, PIB, etc.).",
                inputSchema=_flatten_schema(GetIneOperationsInput.model_json_schema()),
            ),
            Tool(
                name="get_ine_operation",
                description="Get details of a specific INE statistical operation by ID or code.",
                inputSchema=_flatten_schema(GetIneOperationInput.model_json_schema()),
            ),
            Tool(
                name="get_ine_table_data",
                description="Get statistical data from a specific INE table.",
                inputSchema=_flatten_schema(GetIneTableDataInput.model_json_schema()),
            ),
            Tool(
                name="get_ine_series_data",
                description="Get time series data from INE by series code.",
                inputSchema=_flatten_schema(GetIneSeriesDataInput.model_json_schema()),
            ),
            Tool(
                name="search_ine_tables",
                description="Search for tables within a specific INE operation.",
                inputSchema=_flatten_schema(SearchIneTablesInput.model_json_schema()),
            ),
            Tool(
                name="get_ine_variables",
                description="Get available variables, optionally filtered by operation.",
                inputSchema=_flatten_schema(GetIneVariablesInput.model_json_schema()),
            ),
            # datos.gob.es tools
            Tool(
                name="search_open_data",
                description="Search datasets in the Spanish national open data catalog (datos.gob.es). Filter by theme (medio-ambiente, economia, salud, etc.) or publisher.",
                inputSchema=_flatten_schema(SearchOpenDataInput.model_json_schema()),
            ),
            Tool(
                name="get_open_data_details",
                description="Get detailed information about a specific dataset from datos.gob.es including distributions (download formats).",
                inputSchema=_flatten_schema(GetOpenDataDetailsInput.model_json_schema()),
            ),
            Tool(
                name="list_open_data_themes",
                description="List available themes/categories in datos.gob.es (e.g., medio-ambiente, economia, salud, educacion).",
                inputSchema=_flatten_schema(ListOpenDataThemesInput.model_json_schema()),
            ),
            Tool(
                name="list_open_data_publishers",
                description="List publishers/organizations in datos.gob.es (government agencies that publish datasets).",
                inputSchema=_flatten_schema(ListOpenDataPublishersInput.model_json_schema()),
            ),
        ]

    @server.call_tool()  # type: ignore[untyped-decorator]
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls and return results."""
        from public_radar.mcp.logging import log_tool_call

        start_time = time.perf_counter()
        result: dict[str, Any] = {}
        success = True
        error_msg: str | None = None

        try:
            logger.debug("Tool call: %s with args: %s", name, arguments)

            if name == "get_system_info":
                result = _get_system_info()
            elif name == "search_grants":
                result = await _search_grants(SearchGrantsInput(**arguments))
            elif name == "search_grant_awards":
                result = await _search_grant_awards(SearchGrantAwardsInput(**arguments))
            elif name == "get_grant_details":
                result = await _get_grant_details(GetGrantDetailsInput(**arguments))
            elif name == "search_legislation":
                result = await _search_legislation(SearchLegislationInput(**arguments))
            elif name == "get_legislation_details":
                result = await _get_legislation_details(GetLegislationDetailsInput(**arguments))
            elif name == "get_legislation_text":
                result = await _get_legislation_text(GetLegislationTextInput(**arguments))
            elif name == "get_legislation_structure":
                result = await _get_legislation_structure(GetLegislationStructureInput(**arguments))
            elif name == "get_legislation_block":
                result = await _get_legislation_block(GetLegislationBlockInput(**arguments))
            elif name == "get_departments_table":
                result = await _get_departments_table()
            elif name == "get_legal_ranges_table":
                result = await _get_legal_ranges_table()
            elif name == "get_matters_table":
                result = await _get_matters_table()
            elif name == "find_related_laws":
                result = await _find_related_laws(FindRelatedLawsInput(**arguments))
            elif name == "search_recent_boe":
                result = await _search_recent_boe(SearchRecentBoeInput(**arguments))
            elif name == "get_boe_summary":
                result = await _get_boe_summary(GetBoeSummaryInput(**arguments))
            elif name == "get_borme_summary":
                result = await _get_borme_summary(GetBormeSummaryInput(**arguments))
            elif name == "get_ine_operations":
                result = await _get_ine_operations()
            elif name == "get_ine_operation":
                result = await _get_ine_operation(GetIneOperationInput(**arguments))
            elif name == "get_ine_table_data":
                result = await _get_ine_table_data(GetIneTableDataInput(**arguments))
            elif name == "get_ine_series_data":
                result = await _get_ine_series_data(GetIneSeriesDataInput(**arguments))
            elif name == "search_ine_tables":
                result = await _search_ine_tables(SearchIneTablesInput(**arguments))
            elif name == "get_ine_variables":
                result = await _get_ine_variables(GetIneVariablesInput(**arguments))
            elif name == "search_open_data":
                result = await _search_open_data(SearchOpenDataInput(**arguments))
            elif name == "get_open_data_details":
                result = await _get_open_data_details(GetOpenDataDetailsInput(**arguments))
            elif name == "list_open_data_themes":
                result = await _list_open_data_themes()
            elif name == "list_open_data_publishers":
                result = await _list_open_data_publishers(ListOpenDataPublishersInput(**arguments))
            else:
                result = {"error": f"Unknown tool: {name}"}
                success = False

            if "error" in result:
                success = False
                error_msg = result["error"]

            return [TextContent(type="text", text=_to_json(result))]

        except Exception as e:
            logger.exception("Error calling tool %s", name)
            result = {"error": str(e)}
            success = False
            error_msg = str(e)
            return [TextContent(type="text", text=json.dumps(result))]

        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_tool_call(
                tool=name,
                input_data=arguments,
                output_data=result,
                duration_ms=duration_ms,
                success=success,
                error=error_msg,
            )

    @server.list_prompts()  # type: ignore[no-untyped-call, untyped-decorator]
    async def list_prompts() -> list[Prompt]:
        """List available prompts for common queries."""
        from public_radar.prompts import ALL_PROMPTS

        return list(ALL_PROMPTS.values())

    @server.get_prompt()  # type: ignore[no-untyped-call, untyped-decorator]
    async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
        """Get a specific prompt by name with optional arguments."""
        from public_radar.prompts import ALL_PROMPTS
        from public_radar.prompts.bdns import BDNS_PROMPTS, get_bdns_prompt_content
        from public_radar.prompts.boe import BOE_PROMPTS, get_boe_prompt_content
        from public_radar.prompts.combined import COMBINED_PROMPTS, get_combined_prompt_content
        from public_radar.prompts.datos_gob import DATOS_GOB_PROMPTS, get_datos_gob_prompt_content
        from public_radar.prompts.ine import INE_PROMPTS, get_ine_prompt_content

        if name not in ALL_PROMPTS:
            raise ValueError(f"Unknown prompt: {name}. Available prompts: {list(ALL_PROMPTS.keys())}")

        if name in BDNS_PROMPTS:
            return get_bdns_prompt_content(name, arguments)
        elif name in BOE_PROMPTS:
            return get_boe_prompt_content(name, arguments)
        elif name in INE_PROMPTS:
            return get_ine_prompt_content(name, arguments)
        elif name in DATOS_GOB_PROMPTS:
            return get_datos_gob_prompt_content(name, arguments)
        elif name in COMBINED_PROMPTS:
            return get_combined_prompt_content(name, arguments)
        else:
            raise ValueError(f"Prompt {name} not found in any category")

    return server


# =============================================================================
# Tool Implementations
# =============================================================================


def _get_system_info() -> dict[str, Any]:
    """Get system overview and available tools."""
    return {
        "name": "Spanish Public Data MCP Server",
        "description": "Query Spanish government open data: grants (BDNS), legislation (BOE), company registry (BORME), statistics (INE), and open datasets (datos.gob.es)",
        "architecture": "On-the-fly queries to official APIs (no database)",
        "data_sources": [
            {
                "id": "bdns",
                "name": "BDNS (Base de Datos Nacional de Subvenciones)",
                "description": "Spanish National Grants Database - subsidies and public grants",
                "tools": ["search_grants", "search_grant_awards", "get_grant_details"],
            },
            {
                "id": "boe",
                "name": "BOE (Boletín Oficial del Estado)",
                "description": "Spanish Official Gazette - consolidated legislation",
                "tools": [
                    "search_legislation",
                    "get_legislation_details",
                    "get_legislation_text",
                    "get_legislation_structure",
                    "get_legislation_block",
                    "get_departments_table",
                    "get_legal_ranges_table",
                    "get_matters_table",
                    "find_related_laws",
                    "search_recent_boe",
                    "get_boe_summary",
                ],
            },
            {
                "id": "borme",
                "name": "BORME (Boletín Oficial del Registro Mercantil)",
                "description": "Spanish Company Registry Gazette - company acts and events",
                "tools": ["get_borme_summary"],
            },
            {
                "id": "ine",
                "name": "INE (Instituto Nacional de Estadística)",
                "description": "Spanish National Statistics Institute - GDP, CPI, unemployment, demographics",
                "tools": [
                    "get_ine_operations",
                    "get_ine_operation",
                    "get_ine_table_data",
                    "get_ine_series_data",
                    "search_ine_tables",
                    "get_ine_variables",
                ],
            },
            {
                "id": "datos_gob",
                "name": "datos.gob.es (Spanish Open Data Portal)",
                "description": "National open data catalog with 40,000+ datasets from Spanish public administrations",
                "tools": [
                    "search_open_data",
                    "get_open_data_details",
                    "list_open_data_themes",
                    "list_open_data_publishers",
                ],
            },
        ],
        "tips": [
            "Use search_grants to find funding opportunities",
            "Use search_grant_awards with a NIF to see what grants an entity received",
            "Use search_legislation to find relevant laws and regulations",
            "Use get_borme_summary to see recent company registry events",
            "Use get_ine_operations to discover available statistics (IPC, EPA, PIB)",
            "Use get_ine_table_data or get_ine_series_data to fetch actual statistical data",
            "Use search_open_data to explore 40,000+ open datasets from Spanish government",
            "Use list_open_data_themes to see available categories (medio-ambiente, economia, salud, etc.)",
        ],
    }


async def _search_grants(params: SearchGrantsInput) -> dict[str, Any]:
    """Search grant calls from BDNS API."""
    from public_radar.common.dates import parse_date
    from public_radar.sources.bdns import BdnsClient

    logger.info("Searching grants: date_from=%s, date_to=%s, limit=%d", params.date_from, params.date_to, params.limit)

    try:
        fecha_desde = parse_date(params.date_from) if params.date_from else None
        fecha_hasta = parse_date(params.date_to) if params.date_to else None

        with BdnsClient() as client:
            data = client.fetch_convocatorias(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                organo=params.granting_body,
                page_size=params.limit,
            )

        items: list[dict[str, Any]] = data.get("items", []) if data else []
        if not items:
            return {"count": 0, "grants": [], "message": "No grants found for the given criteria"}

        return {
            "count": len(items),
            "grants": [
                {
                    "id": str(item.get("codigoBdns", item.get("id", ""))),
                    "title": item.get("titulo"),
                    "description": item.get("descripcion"),
                    "granting_body": item.get("organo"),
                    "amount": item.get("presupuesto") or item.get("importeTotal"),
                    "start_date": item.get("fechaInicio"),
                    "end_date": item.get("fechaFin"),
                    "url": item.get("urlBases"),
                }
                for item in items[: params.limit]
            ],
        }
    except Exception as e:
        logger.exception("Error searching grants")
        return {"error": f"Failed to search grants: {str(e)}"}


async def _search_grant_awards(params: SearchGrantAwardsInput) -> dict[str, Any]:
    """Search awarded grants from BDNS API."""
    from public_radar.common.dates import parse_date
    from public_radar.sources.bdns import BdnsClient

    logger.info(
        "Searching grant awards: date_from=%s, date_to=%s, nif=%s",
        params.date_from,
        params.date_to,
        params.beneficiary_nif,
    )

    try:
        fecha_desde = parse_date(params.date_from) if params.date_from else None
        fecha_hasta = parse_date(params.date_to) if params.date_to else None

        with BdnsClient() as client:
            data = client.fetch_concesiones(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                nif_beneficiario=params.beneficiary_nif,
                page_size=params.limit,
            )

        items: list[dict[str, Any]] = data.get("items", []) if data else []
        if not items:
            return {"count": 0, "awards": [], "message": "No grant awards found for the given criteria"}

        return {
            "count": len(items),
            "awards": [
                {
                    "id": str(item.get("idConcesion", "")),
                    "grant_id": str(item.get("codigoBdns", item.get("idConvocatoria", ""))),
                    "beneficiary": item.get("beneficiario"),
                    "beneficiary_nif": item.get("nifBeneficiario"),
                    "amount": item.get("importe"),
                    "date": item.get("fechaConcesion"),
                }
                for item in items[: params.limit]
            ],
        }
    except Exception as e:
        logger.exception("Error searching grant awards")
        return {"error": f"Failed to search grant awards: {str(e)}"}


async def _get_grant_details(params: GetGrantDetailsInput) -> dict[str, Any]:
    """Get details of a specific grant call."""
    from public_radar.sources.bdns import BdnsClient

    logger.info("Getting grant details: id=%s", params.grant_id)

    try:
        with BdnsClient() as client:
            data = client.fetch_convocatoria_by_id(params.grant_id)

        if not data:
            return {"error": f"Grant not found: {params.grant_id}"}

        return {
            "id": str(data.get("idConvocatoria", "")),
            "title": data.get("titulo"),
            "description": data.get("descripcion"),
            "granting_body": data.get("organo"),
            "amount": data.get("importeTotal"),
            "start_date": data.get("fechaInicio"),
            "end_date": data.get("fechaFin"),
            "url": data.get("urlBases"),
            "raw_data": data,
        }
    except Exception as e:
        logger.exception("Error getting grant details")
        return {"error": f"Failed to get grant details: {str(e)}"}


async def _search_legislation(params: SearchLegislationInput) -> dict[str, Any]:
    """Search consolidated legislation from BOE API."""
    from public_radar.common.dates import parse_date
    from public_radar.common.http import HttpClientError
    from public_radar.sources.boe import BoeClient, parse_legislation_search

    logger.info("Searching legislation: query=%s, limit=%d", params.query, params.limit)

    try:
        date_from = parse_date(params.date_from) if params.date_from else None
        date_to = parse_date(params.date_to) if params.date_to else None

        with BoeClient() as client:
            data = client.search_legislation(
                query=params.query,
                date_from=date_from,
                date_to=date_to,
                title=params.title,
                department_code=params.department_code,
                legal_range_code=params.legal_range_code,
                matter_code=params.matter_code,
                include_derogated=params.include_derogated,
                offset=params.offset,
                limit=params.limit,
            )

        if not data:
            return {"count": 0, "legislation": [], "message": "No legislation found for the given criteria"}

        parsed = parse_legislation_search(data)

        return {
            "count": len(parsed),
            "legislation": [
                {
                    "id": item.id,
                    "title": item.title,
                    "department": item.department,
                    "rang": item.rang,
                    "publication_date": item.publication_date,
                    "effective_date": item.effective_date,
                    "status": item.status,
                    "url_pdf": item.url_pdf,
                    "url_html": item.url_html,
                }
                for item in parsed
            ],
        }
    except HttpClientError as e:
        logger.exception("Error searching legislation")
        error_msg = str(e)
        if "500" in error_msg or "Internal Server Error" in error_msg:
            return {
                "error": f"BOE API error: {error_msg}",
                "warning": "The BOE API has a known bug where text search (query parameter) often returns HTTP 500 errors.",
                "suggestions": [
                    "Try using get_legislation_details with a specific legislation ID (e.g., BOE-A-2018-16673 for LOPDGDD)",
                    "Try using search_recent_boe to find recent publications",
                    "Use date filters (date_from, date_to) without text query",
                    "Common legislation IDs: BOE-A-2018-16673 (LOPDGDD), BOE-A-2015-10565 (Ley 39/2015), BOE-A-1978-31229 (Constitution)",
                ],
            }
        return {"error": f"Failed to search legislation: {error_msg}"}
    except Exception as e:
        logger.exception("Error searching legislation")
        return {"error": f"Failed to search legislation: {str(e)}"}


async def _get_legislation_details(params: GetLegislationDetailsInput) -> dict[str, Any]:
    """Get legislation details from BOE API."""
    from public_radar.sources.boe import BoeClient

    logger.info(
        "Getting legislation details: id=%s, include_analysis=%s", params.legislation_id, params.include_analysis
    )

    try:
        with BoeClient() as client:
            data = client.fetch_legislation_by_id(params.legislation_id)

            if not data:
                return {"error": f"Legislation not found: {params.legislation_id}"}

            result: dict[str, Any] = {
                "id": data.get("id", data.get("identificador", params.legislation_id)),
                "title": data.get("titulo", data.get("title")),
                "department": data.get("departamento"),
                "rang": data.get("rango"),
                "publication_date": data.get("fecha_publicacion"),
                "effective_date": data.get("fecha_vigencia"),
                "status": data.get("estado_consolidacion"),
                "url_pdf": data.get("url_pdf"),
                "url_html": data.get("url_html"),
                "url_epub": data.get("url_epub"),
            }

            if params.include_analysis:
                analysis = client.fetch_legislation_analysis(params.legislation_id)
                if analysis:
                    result["analysis"] = {
                        "references": analysis.get("referencias", []),
                        "notes": analysis.get("notas", []),
                        "matters": analysis.get("materias", []),
                        "modifies": analysis.get("modifica", []),
                        "modified_by": analysis.get("modificado_por", []),
                        "repeals": analysis.get("deroga", []),
                        "repealed_by": analysis.get("derogado_por", []),
                    }

            return result
    except Exception as e:
        logger.exception("Error getting legislation details")
        return {"error": f"Failed to get legislation details: {str(e)}"}


async def _get_legislation_text(params: GetLegislationTextInput) -> dict[str, Any]:
    """Get full legislation text from BOE API."""
    from public_radar.sources.boe import BoeClient

    logger.info("Getting legislation text: id=%s", params.legislation_id)

    try:
        with BoeClient() as client:
            data = client.fetch_legislation_text(params.legislation_id)

        if not data:
            return {"error": f"Legislation text not found: {params.legislation_id}"}

        return {
            "id": params.legislation_id,
            "text": data.get("texto", data.get("text", data)),
            "raw_data": data,
        }
    except Exception as e:
        logger.exception("Error getting legislation text")
        return {"error": f"Failed to get legislation text: {str(e)}"}


async def _get_legislation_structure(params: GetLegislationStructureInput) -> dict[str, Any]:
    """Get legislation structure/index from BOE API."""
    from public_radar.sources.boe import BoeClient

    logger.info("Getting legislation structure: id=%s", params.legislation_id)

    try:
        with BoeClient() as client:
            data = client.fetch_legislation_index(params.legislation_id)

        if not data:
            return {"error": f"Legislation structure not found: {params.legislation_id}"}

        blocks = data.get("bloque", [])
        if not isinstance(blocks, list):
            blocks = [blocks] if blocks else []

        return {
            "id": params.legislation_id,
            "block_count": len(blocks),
            "blocks": [
                {
                    "id": block.get("@id", block.get("id", "")),
                    "title": block.get("titulo", block.get("@titulo", "")),
                    "type": block.get("tipo", block.get("@tipo", "")),
                }
                for block in blocks
            ],
            "raw_data": data,
        }
    except Exception as e:
        logger.exception("Error getting legislation structure")
        return {"error": f"Failed to get legislation structure: {str(e)}"}


async def _get_legislation_block(params: GetLegislationBlockInput) -> dict[str, Any]:
    """Get a specific block from legislation from BOE API."""
    from public_radar.sources.boe import BoeClient

    logger.info("Getting legislation block: id=%s, block=%s", params.legislation_id, params.block_id)

    try:
        with BoeClient() as client:
            data = client.fetch_legislation_block(params.legislation_id, params.block_id)

        if not data:
            return {"error": f"Legislation block not found: {params.legislation_id}/{params.block_id}"}

        text_content = ""
        if "texto" in data:
            texto = data["texto"]
            if isinstance(texto, dict):
                text_content = texto.get("text") or texto.get("contenido") or str(texto)
            else:
                text_content = str(texto)
        elif "text" in data:
            text_content = str(data["text"])

        return {
            "legislation_id": params.legislation_id,
            "block_id": params.block_id,
            "title": data.get("titulo", data.get("@titulo", "")),
            "text": text_content,
            "raw_data": data,
        }
    except Exception as e:
        logger.exception("Error getting legislation block")
        return {"error": f"Failed to get legislation block: {str(e)}"}


async def _get_departments_table() -> dict[str, Any]:
    """Get government departments table from BOE API."""
    from public_radar.sources.boe import BoeClient

    logger.info("Getting departments table")

    try:
        with BoeClient() as client:
            data = client.fetch_auxiliary_table("departamentos")

        if not data:
            return {"count": 0, "departments": [], "message": "No departments found"}

        return {
            "count": len(data),
            "departments": [
                {
                    "code": item.get("codigo", item.get("id", "")),
                    "name": item.get("nombre", item.get("texto", "")),
                }
                for item in data
            ],
        }
    except Exception as e:
        logger.exception("Error getting departments table")
        return {"error": f"Failed to get departments table: {str(e)}"}


async def _get_legal_ranges_table() -> dict[str, Any]:
    """Get legal ranges table from BOE API."""
    from public_radar.sources.boe import BoeClient

    logger.info("Getting legal ranges table")

    try:
        with BoeClient() as client:
            data = client.fetch_auxiliary_table("rangos")

        if not data:
            return {"count": 0, "legal_ranges": [], "message": "No legal ranges found"}

        return {
            "count": len(data),
            "legal_ranges": [
                {
                    "code": item.get("codigo", item.get("id", "")),
                    "name": item.get("nombre", item.get("texto", "")),
                }
                for item in data
            ],
        }
    except Exception as e:
        logger.exception("Error getting legal ranges table")
        return {"error": f"Failed to get legal ranges table: {str(e)}"}


async def _get_matters_table() -> dict[str, Any]:
    """Get matters/subjects table from BOE API."""
    from public_radar.sources.boe import BoeClient

    logger.info("Getting matters table")

    try:
        with BoeClient() as client:
            data = client.fetch_auxiliary_table("materias")

        if not data:
            return {"count": 0, "matters": [], "message": "No matters found"}

        return {
            "count": len(data),
            "matters": [
                {
                    "code": item.get("codigo", item.get("id", "")),
                    "name": item.get("nombre", item.get("texto", "")),
                }
                for item in data
            ],
        }
    except Exception as e:
        logger.exception("Error getting matters table")
        return {"error": f"Failed to get matters table: {str(e)}"}


async def _find_related_laws(params: FindRelatedLawsInput) -> dict[str, Any]:
    """Find laws related to a given legislation."""
    from public_radar.sources.boe import BoeClient

    logger.info("Finding related laws: id=%s, relation_type=%s", params.legislation_id, params.relation_type)

    try:
        with BoeClient() as client:
            analysis = client.fetch_legislation_analysis(params.legislation_id)

        if not analysis:
            return {"error": f"No analysis found for legislation: {params.legislation_id}"}

        relations: dict[str, Any] = {
            "legislation_id": params.legislation_id,
            "modifies": analysis.get("modifica", []),
            "modified_by": analysis.get("modificado_por", []),
            "repeals": analysis.get("deroga", []),
            "repealed_by": analysis.get("derogado_por", []),
            "references": analysis.get("referencias", []),
            "referenced_by": analysis.get("referenciado_por", []),
        }

        if params.relation_type:
            relation_key = params.relation_type.lower().replace("-", "_")
            if relation_key in relations:
                return {
                    "legislation_id": params.legislation_id,
                    "relation_type": params.relation_type,
                    "count": len(relations[relation_key]),
                    "related_laws": relations[relation_key],
                }
            else:
                return {
                    "error": f"Invalid relation_type: {params.relation_type}. Valid types: modifies, modified_by, repeals, repealed_by, references, referenced_by"
                }

        total_count = sum(len(v) for k, v in relations.items() if k != "legislation_id" and isinstance(v, list))
        return {
            "legislation_id": params.legislation_id,
            "total_relations": total_count,
            "relations": {
                "modifies": {"count": len(relations["modifies"]), "laws": relations["modifies"]},
                "modified_by": {"count": len(relations["modified_by"]), "laws": relations["modified_by"]},
                "repeals": {"count": len(relations["repeals"]), "laws": relations["repeals"]},
                "repealed_by": {"count": len(relations["repealed_by"]), "laws": relations["repealed_by"]},
                "references": {"count": len(relations["references"]), "laws": relations["references"]},
                "referenced_by": {"count": len(relations["referenced_by"]), "laws": relations["referenced_by"]},
            },
        }
    except Exception as e:
        logger.exception("Error finding related laws")
        return {"error": f"Failed to find related laws: {str(e)}"}


async def _search_recent_boe(params: SearchRecentBoeInput) -> dict[str, Any]:
    """Search BOE publications from the last N days."""
    from public_radar.sources.boe import BoeClient, parse_boe_summary

    logger.info("Searching recent BOE: days_back=%d, search_terms=%s", params.days_back, params.search_terms)

    try:
        all_items: list[dict[str, Any]] = []
        days_checked = 0
        days_with_data = 0

        with BoeClient() as client:
            for i in range(params.days_back):
                target_date = date.today() - timedelta(days=i)

                if target_date.weekday() >= 5:
                    continue

                days_checked += 1
                data = client.fetch_boe_summary(target_date)

                if not data:
                    continue

                days_with_data += 1
                parsed = parse_boe_summary(data)

                for item in parsed:
                    item_dict = {
                        "date": target_date.isoformat(),
                        "id": item.id,
                        "title": item.title,
                        "section": item.section,
                        "department": item.department,
                        "epigraph": item.epigraph,
                        "url_pdf": item.url_pdf,
                        "url_html": item.url_html,
                    }

                    if params.section_filter:
                        if not item.section or params.section_filter.upper() not in item.section.upper():
                            continue

                    if params.search_terms:
                        search_lower = params.search_terms.lower()
                        title_lower = (item.title or "").lower()
                        if search_lower not in title_lower:
                            continue

                    all_items.append(item_dict)

                    if len(all_items) >= params.max_items:
                        break

                if len(all_items) >= params.max_items:
                    break

        return {
            "days_back": params.days_back,
            "days_checked": days_checked,
            "days_with_data": days_with_data,
            "search_terms": params.search_terms,
            "section_filter": params.section_filter,
            "count": len(all_items),
            "items": all_items,
        }
    except Exception as e:
        logger.exception("Error searching recent BOE")
        return {"error": f"Failed to search recent BOE: {str(e)}"}


async def _get_boe_summary(params: GetBoeSummaryInput) -> dict[str, Any]:
    """Get daily BOE summary from BOE API."""
    from public_radar.common.dates import parse_date
    from public_radar.sources.boe import BoeClient, parse_boe_summary

    requested_date = parse_date(params.date) if params.date else date.today()
    target_date = requested_date
    logger.info("Getting BOE summary for date: %s", target_date)

    try:
        with BoeClient() as client:
            data = client.fetch_boe_summary(target_date)

            fallback_used = False
            original_date = target_date
            max_attempts = 7

            if not data:
                for i in range(1, max_attempts + 1):
                    target_date = original_date - timedelta(days=i)
                    if target_date.weekday() >= 5:
                        continue
                    data = client.fetch_boe_summary(target_date)
                    if data:
                        fallback_used = True
                        break

        if not data:
            return {
                "date": requested_date.isoformat(),
                "count": 0,
                "items": [],
                "message": f"No BOE published for {requested_date} or recent days (may be extended holiday period)",
                "warning": "Could not find any BOE in the last 7 days",
            }

        parsed = parse_boe_summary(data)

        filtered = parsed
        if params.section_filter:
            section_upper = params.section_filter.upper()
            filtered = [item for item in filtered if item.section and section_upper in item.section.upper()]
        if params.department_filter:
            dept_lower = params.department_filter.lower()
            filtered = [item for item in filtered if item.department and dept_lower in item.department.lower()]
        if params.max_items:
            filtered = filtered[: params.max_items]

        result: dict[str, Any] = {
            "date": target_date.isoformat(),
            "count": len(filtered),
            "total_unfiltered": len(parsed),
            "filters_applied": {
                "section": params.section_filter,
                "department": params.department_filter,
                "max_items": params.max_items,
            },
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "section": item.section,
                    "department": item.department,
                    "epigraph": item.epigraph,
                    "url_pdf": item.url_pdf,
                    "url_html": item.url_html,
                }
                for item in filtered
            ],
        }

        if fallback_used:
            result["requested_date"] = requested_date.isoformat()
            result["warning"] = (
                f"No BOE published for {requested_date.isoformat()} (weekend/holiday). Showing data from {target_date.isoformat()} instead."
            )

        return result
    except Exception as e:
        logger.exception("Error getting BOE summary")
        return {"error": f"Failed to get BOE summary: {str(e)}"}


async def _get_borme_summary(params: GetBormeSummaryInput) -> dict[str, Any]:
    """Get daily BORME summary from BOE API."""
    from public_radar.common.dates import parse_date
    from public_radar.sources.boe import BoeClient, parse_borme_summary

    if params.date:
        target_date = parse_date(params.date)
    else:
        target_date = _latest_weekday(date.today())

    logger.info("Getting BORME summary for date: %s", target_date)

    try:
        with BoeClient() as client:
            data = client.fetch_borme_summary(target_date)

        if not data:
            return {
                "date": target_date.isoformat(),
                "count": 0,
                "items": [],
                "message": f"No BORME published for {target_date} (may be weekend/holiday)",
            }

        parsed = parse_borme_summary(data)

        filtered = parsed
        if params.province_filter:
            prov_lower = params.province_filter.lower()
            filtered = [item for item in filtered if item.province and prov_lower in item.province.lower()]
        if params.max_items:
            filtered = filtered[: params.max_items]

        return {
            "date": target_date.isoformat(),
            "count": len(filtered),
            "total_unfiltered": len(parsed),
            "filters_applied": {
                "province": params.province_filter,
                "max_items": params.max_items,
            },
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "section": item.section,
                    "province": item.province,
                    "act_type": item.act_type,
                    "company_name": item.company_name,
                    "url_pdf": item.url_pdf,
                }
                for item in filtered
            ],
        }
    except Exception as e:
        logger.exception("Error getting BORME summary")
        return {"error": f"Failed to get BORME summary: {str(e)}"}


async def _get_ine_operations() -> dict[str, Any]:
    """Get list of available INE statistical operations."""
    from public_radar.sources.ine import IneClient, parse_operations

    logger.info("Getting INE operations")

    try:
        with IneClient() as client:
            data = client.fetch_operations()

        if not data:
            return {"count": 0, "operations": [], "message": "No operations found"}

        parsed = parse_operations(data)

        return {
            "count": len(parsed),
            "operations": [
                {
                    "id": op.id,
                    "code": op.code,
                    "name": op.name,
                    "url": op.url,
                }
                for op in parsed[:100]
            ],
        }
    except Exception as e:
        logger.exception("Error getting INE operations")
        return {"error": f"Failed to get INE operations: {str(e)}"}


async def _get_ine_operation(params: GetIneOperationInput) -> dict[str, Any]:
    """Get details of a specific INE operation."""
    from public_radar.sources.ine import IneClient

    logger.info("Getting INE operation: %s", params.operation_id)

    try:
        with IneClient() as client:
            data = client.fetch_operation(params.operation_id)

        if not data:
            return {"error": f"Operation not found: {params.operation_id}"}

        return {
            "id": str(data.get("Id", data.get("Cod_IOE", ""))),
            "code": data.get("Cod_IOE", ""),
            "name": data.get("Nombre", ""),
            "url": data.get("Url", ""),
            "raw_data": data,
        }
    except Exception as e:
        logger.exception("Error getting INE operation")
        return {"error": f"Failed to get INE operation: {str(e)}"}


async def _get_ine_table_data(params: GetIneTableDataInput) -> dict[str, Any]:
    """Get data from a specific INE table."""
    from public_radar.sources.ine import IneClient

    logger.info("Getting INE table data: table_id=%s, nult=%s", params.table_id, params.nult)

    try:
        with IneClient() as client:
            data = client.fetch_table_data(params.table_id, nult=params.nult)

        if not data:
            return {"error": f"Table not found or no data: {params.table_id}"}

        series_list = []
        for item in data:
            series_code = item.get("COD", item.get("Codigo", ""))
            series_name = item.get("Nombre", "")
            data_points = item.get("Data", [])

            points = []
            for point in data_points:
                value = point.get("Valor")
                if value is not None:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        value = None
                points.append(
                    {
                        "period": point.get("Fecha", point.get("T3_Periodo", "")),
                        "value": value,
                    }
                )

            series_list.append(
                {
                    "series_code": series_code,
                    "series_name": series_name,
                    "data_points": points[:50],
                }
            )

        return {
            "table_id": params.table_id,
            "series_count": len(series_list),
            "series": series_list[:100],
        }
    except Exception as e:
        logger.exception("Error getting INE table data")
        return {"error": f"Failed to get INE table data: {str(e)}"}


async def _get_ine_series_data(params: GetIneSeriesDataInput) -> dict[str, Any]:
    """Get data for a specific INE time series."""
    from public_radar.sources.ine import IneClient

    logger.info("Getting INE series data: series_code=%s, nult=%s", params.series_code, params.nult)

    try:
        with IneClient() as client:
            data = client.fetch_series_data(params.series_code, nult=params.nult)

        if not data:
            return {"error": f"Series not found or no data: {params.series_code}"}

        series_name = ""
        data_points = []

        for item in data:
            if not series_name:
                series_name = item.get("Nombre", "")
            item_data = item.get("Data", [item])
            if not isinstance(item_data, list):
                item_data = [item_data]

            for point in item_data:
                value = point.get("Valor")
                if value is not None:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        value = None
                data_points.append(
                    {
                        "period": point.get("Fecha", point.get("T3_Periodo", "")),
                        "value": value,
                    }
                )

        return {
            "series_code": params.series_code,
            "series_name": series_name,
            "count": len(data_points),
            "data_points": data_points,
        }
    except Exception as e:
        logger.exception("Error getting INE series data")
        return {"error": f"Failed to get INE series data: {str(e)}"}


async def _search_ine_tables(params: SearchIneTablesInput) -> dict[str, Any]:
    """Search for tables within an INE operation."""
    from public_radar.sources.ine import IneClient, parse_tables

    logger.info("Searching INE tables for operation: %s", params.operation_id)

    try:
        with IneClient() as client:
            data = client.fetch_tables_by_operation(params.operation_id)

        if not data:
            return {"count": 0, "tables": [], "message": f"No tables found for operation: {params.operation_id}"}

        parsed = parse_tables(data)

        return {
            "operation_id": params.operation_id,
            "count": len(parsed),
            "tables": [
                {
                    "id": table.id,
                    "name": table.name,
                }
                for table in parsed
            ],
        }
    except Exception as e:
        logger.exception("Error searching INE tables")
        return {"error": f"Failed to search INE tables: {str(e)}"}


async def _get_ine_variables(params: GetIneVariablesInput) -> dict[str, Any]:
    """Get available INE variables, optionally filtered by operation."""
    from public_radar.sources.ine import IneClient, parse_variables

    logger.info("Getting INE variables: operation_id=%s", params.operation_id)

    try:
        with IneClient() as client:
            if params.operation_id:
                data = client.fetch_variables_by_operation(params.operation_id)
            else:
                data = client.fetch_variables()

        if not data:
            return {"count": 0, "variables": [], "message": "No variables found"}

        parsed = parse_variables(data)

        return {
            "operation_id": params.operation_id,
            "count": len(parsed),
            "variables": [
                {
                    "id": var.id,
                    "name": var.name,
                    "code": var.code,
                }
                for var in parsed[:100]
            ],
        }
    except Exception as e:
        logger.exception("Error getting INE variables")
        return {"error": f"Failed to get INE variables: {str(e)}"}


# =============================================================================
# datos.gob.es Tool Implementations
# =============================================================================


async def _search_open_data(params: SearchOpenDataInput) -> dict[str, Any]:
    """Search datasets in the datos.gob.es catalog."""
    from public_radar.sources.datos_gob import DatosGobClient, parse_datasets

    logger.info(
        "Searching open data: query=%s, theme=%s, publisher=%s, limit=%d",
        params.query,
        params.theme,
        params.publisher,
        params.limit,
    )

    try:
        with DatosGobClient() as client:
            data = client.search_datasets(
                query=params.query,
                theme=params.theme,
                publisher=params.publisher,
                page_size=params.limit,
            )

        if not data:
            return {"count": 0, "datasets": [], "message": "No datasets found"}

        parsed = parse_datasets(data)

        return {
            "count": len(parsed),
            "filters": {
                "query": params.query,
                "theme": params.theme,
                "publisher": params.publisher,
            },
            "datasets": [
                {
                    "id": ds.identifier,
                    "title": ds.title,
                    "description": (
                        ds.description[:200] + "..." if ds.description and len(ds.description) > 200 else ds.description
                    ),
                    "publisher_id": ds.publisher_id,
                    "themes": ds.themes,
                    "keywords": ds.keywords[:5] if ds.keywords else [],
                    "formats": [d.format for d in ds.distributions if d.format],
                    "modified": ds.modified.isoformat() if ds.modified else None,
                    "url": ds.url,
                }
                for ds in parsed
            ],
        }
    except Exception as e:
        logger.exception("Error searching open data")
        return {"error": f"Failed to search open data: {str(e)}"}


async def _get_open_data_details(params: GetOpenDataDetailsInput) -> dict[str, Any]:
    """Get detailed information about a specific dataset."""
    from public_radar.sources.datos_gob import DatosGobClient, _parse_dataset

    logger.info("Getting open data details: dataset_id=%s", params.dataset_id)

    try:
        with DatosGobClient() as client:
            data = client.get_dataset(params.dataset_id)

        if not data:
            return {"error": f"Dataset not found: {params.dataset_id}"}

        primary = data.get("primaryTopic", data)
        parsed = _parse_dataset(primary)

        if not parsed:
            return {"error": f"Could not parse dataset: {params.dataset_id}"}

        return {
            "id": parsed.identifier,
            "title": parsed.title,
            "description": parsed.description,
            "publisher_id": parsed.publisher_id,
            "themes": parsed.themes,
            "keywords": parsed.keywords,
            "license": parsed.license,
            "issued": parsed.issued.isoformat() if parsed.issued else None,
            "modified": parsed.modified.isoformat() if parsed.modified else None,
            "language": parsed.language,
            "spatial": parsed.spatial,
            "url": parsed.url,
            "distributions": [
                {
                    "url": d.url,
                    "format": d.format,
                    "title": d.title,
                }
                for d in parsed.distributions
            ],
        }
    except Exception as e:
        logger.exception("Error getting open data details")
        return {"error": f"Failed to get dataset details: {str(e)}"}


async def _list_open_data_themes() -> dict[str, Any]:
    """List available themes in datos.gob.es."""
    from public_radar.sources.datos_gob import DatosGobClient, parse_themes

    logger.info("Listing open data themes")

    try:
        with DatosGobClient() as client:
            data = client.list_themes()

        if not data:
            return {"count": 0, "themes": [], "message": "No themes found"}

        parsed = parse_themes(data)

        return {
            "count": len(parsed),
            "themes": [
                {
                    "code": t.code,
                    "label": t.label,
                }
                for t in parsed
            ],
        }
    except Exception as e:
        logger.exception("Error listing open data themes")
        return {"error": f"Failed to list themes: {str(e)}"}


async def _list_open_data_publishers(params: ListOpenDataPublishersInput) -> dict[str, Any]:
    """List publishers in datos.gob.es."""
    from public_radar.sources.datos_gob import DatosGobClient, parse_publishers

    logger.info("Listing open data publishers: limit=%d", params.limit)

    try:
        with DatosGobClient() as client:
            data = client.list_publishers(page_size=params.limit)

        if not data:
            return {"count": 0, "publishers": [], "message": "No publishers found"}

        parsed = parse_publishers(data)

        return {
            "count": len(parsed),
            "publishers": [
                {
                    "code": p.code,
                    "name": p.name,
                }
                for p in parsed
            ],
        }
    except Exception as e:
        logger.exception("Error listing open data publishers")
        return {"error": f"Failed to list publishers: {str(e)}"}


# =============================================================================
# Utilities
# =============================================================================


def _latest_weekday(target: date) -> date:
    """Get the most recent weekday (Monday-Friday)."""
    weekday = target.weekday()
    if weekday == 5:  # Saturday
        return target - timedelta(days=1)
    elif weekday == 6:  # Sunday
        return target - timedelta(days=2)
    return target


def _json_serializer(obj: Any) -> Any:
    """JSON serializer for special types."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _to_json(data: dict[str, Any]) -> str:
    """Convert data to JSON string with standard settings."""
    return json.dumps(data, default=_json_serializer, ensure_ascii=False)


# =============================================================================
# Server Entry Points
# =============================================================================


async def run_server() -> None:
    """Run the MCP server using stdio transport."""
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


async def run_sse_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Run the MCP server using SSE (HTTP) transport."""
    import uvicorn
    from mcp.server.sse import SseServerTransport

    host = os.environ.get("MCP_HOST", host)
    port = int(os.environ.get("MCP_PORT", port))

    mcp_server = create_server()
    sse = SseServerTransport("/messages")

    async def app(scope: dict[str, Any], receive: Any, send: Any) -> None:
        """ASGI application for MCP SSE server."""
        if scope["type"] != "http":
            return

        path = scope["path"]
        method = scope.get("method", "GET")

        if path == "/health":
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"application/json"]],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b'{"status":"healthy","service":"spanish-public-data-mcp"}',
                }
            )

        elif path == "/sse":
            async with sse.connect_sse(scope, receive, send) as streams:
                await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

        elif path == "/messages" and method == "POST":
            await sse.handle_post_message(scope, receive, send)

        else:
            await send(
                {
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [[b"content-type", b"application/json"]],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b'{"error":"Not found"}',
                }
            )

    logger.info("Starting Spanish Public Data MCP Server (SSE) on http://%s:%d", host, port)

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()
