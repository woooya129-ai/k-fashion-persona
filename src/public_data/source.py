# SPDX-License-Identifier: AGPL-3.0-only
"""Source metadata for public-data sections in reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SourceStatus = Literal["success", "snapshot", "missing_api_key", "failed", "not_used"]


@dataclass(frozen=True)
class SourceMetadata:
    name: str
    source_url: str
    status: SourceStatus
    period: str = ""
    retrieved_at: str = ""
    note: str = ""
