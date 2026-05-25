# SPDX-License-Identifier: AGPL-3.0-only
"""MOIS resident-registration population context."""

from src.public_data.population.connector import (
    DATAGOKR_SERVICE_KEY_VAR,
    MOIS_POPULATION_API_URL_VAR,
    MOIS_POPULATION_SNAPSHOT_PATH,
    MOIS_POPULATION_SOURCE_URL,
    PopulationRow,
    build_population_context,
    fetch_population_api_rows,
    load_population_snapshot,
    parse_population_api_rows,
)

__all__ = [
    "DATAGOKR_SERVICE_KEY_VAR",
    "MOIS_POPULATION_API_URL_VAR",
    "MOIS_POPULATION_SNAPSHOT_PATH",
    "MOIS_POPULATION_SOURCE_URL",
    "PopulationRow",
    "build_population_context",
    "fetch_population_api_rows",
    "load_population_snapshot",
    "parse_population_api_rows",
]
