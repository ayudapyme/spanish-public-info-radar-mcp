"""MCP Prompts for Spanish Public Data.

This module provides pre-built prompt templates organized by data source.
Each prompt encapsulates a specific use case workflow.
"""

from public_radar.prompts.bdns import BDNS_PROMPTS
from public_radar.prompts.boe import BOE_PROMPTS
from public_radar.prompts.combined import COMBINED_PROMPTS
from public_radar.prompts.datos_gob import DATOS_GOB_PROMPTS
from public_radar.prompts.ine import INE_PROMPTS

# Merge all prompts into a single dictionary
ALL_PROMPTS = {
    **BDNS_PROMPTS,
    **BOE_PROMPTS,
    **INE_PROMPTS,
    **DATOS_GOB_PROMPTS,
    **COMBINED_PROMPTS,
}

__all__ = [
    "ALL_PROMPTS",
    "BDNS_PROMPTS",
    "BOE_PROMPTS",
    "INE_PROMPTS",
    "DATOS_GOB_PROMPTS",
    "COMBINED_PROMPTS",
]
