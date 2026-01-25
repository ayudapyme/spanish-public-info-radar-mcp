"""Data source adapters for Spanish Public Data MCP.

Provides clients and parsers for Spanish government open data APIs:
- BDNS: National Grants Database (subsidies and grants)
- BOE: Official Gazette and consolidated legislation
- INE: National Statistics Institute
"""

from public_radar.sources.bdns import (
    BdnsClient,
    ParsedConcesion,
    ParsedConvocatoria,
    parse_concesiones,
    parse_convocatorias,
)
from public_radar.sources.boe import (
    BoeClient,
    ParsedBoeSummaryItem,
    ParsedBormeSummaryItem,
    ParsedLegislation,
    parse_boe_summary,
    parse_borme_summary,
    parse_legislation_search,
)
from public_radar.sources.ine import (
    IneClient,
    ParsedDataPoint,
    ParsedOperation,
    ParsedSeries,
    ParsedTable,
    ParsedVariable,
    parse_data_points,
    parse_operations,
    parse_series,
    parse_tables,
    parse_variables,
)

__all__ = [
    # BDNS
    "BdnsClient",
    "ParsedConvocatoria",
    "ParsedConcesion",
    "parse_convocatorias",
    "parse_concesiones",
    # BOE
    "BoeClient",
    "ParsedLegislation",
    "ParsedBoeSummaryItem",
    "ParsedBormeSummaryItem",
    "parse_legislation_search",
    "parse_boe_summary",
    "parse_borme_summary",
    # INE
    "IneClient",
    "ParsedOperation",
    "ParsedVariable",
    "ParsedTable",
    "ParsedSeries",
    "ParsedDataPoint",
    "parse_operations",
    "parse_variables",
    "parse_tables",
    "parse_series",
    "parse_data_points",
]
