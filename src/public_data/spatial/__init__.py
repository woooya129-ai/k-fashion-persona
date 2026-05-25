# SPDX-License-Identifier: AGPL-3.0-only
"""SGIS spatial context connector."""

from src.public_data.spatial.connector import (
    SGIS_SPATIAL_API_URL_VAR,
    build_spatial_context,
    fetch_sgis_access_token,
    fetch_sgis_spatial_rows,
)

__all__ = [
    "SGIS_SPATIAL_API_URL_VAR",
    "build_spatial_context",
    "fetch_sgis_access_token",
    "fetch_sgis_spatial_rows",
]
