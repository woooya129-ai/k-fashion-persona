# SPDX-License-Identifier: AGPL-3.0-only
"""Base interfaces for public-data API connectors."""

from __future__ import annotations

from typing import Protocol


class AuthAdapter(Protocol):
    """Apply provider-specific authentication to URL and params."""

    def apply(self, url: str, params: dict[str, str]) -> tuple[str, dict[str, str]]:
        """Return a request URL and params with auth applied."""


class KosisAuthAdapter:
    """KOSIS statisticsData style auth adapter."""

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key.strip()

    def apply(self, url: str, params: dict[str, str]) -> tuple[str, dict[str, str]]:
        applied = dict(params)
        if self.api_key:
            applied["apiKey"] = self.api_key
        applied.setdefault("format", "json")
        return url, applied


class DataGoKrAuthAdapter:
    """공공데이터포털 serviceKey style auth adapter."""

    def __init__(self, service_key: str = "") -> None:
        self.service_key = service_key.strip()

    def apply(self, url: str, params: dict[str, str]) -> tuple[str, dict[str, str]]:
        applied = dict(params)
        if self.service_key:
            applied["serviceKey"] = self.service_key
        applied.setdefault("type", "json")
        return url, applied


class SgisAccessTokenAuthAdapter:
    """SGIS S-Open API accessToken style auth adapter."""

    def __init__(self, access_token: str = "") -> None:
        self.access_token = access_token.strip()

    def apply(self, url: str, params: dict[str, str]) -> tuple[str, dict[str, str]]:
        applied = dict(params)
        if self.access_token:
            applied["accessToken"] = self.access_token
        return url, applied


class KmaApiHubAuthAdapter:
    """KMA API Hub authKey style auth adapter."""

    def __init__(self, auth_key: str = "") -> None:
        self.auth_key = auth_key.strip()

    def apply(self, url: str, params: dict[str, str]) -> tuple[str, dict[str, str]]:
        applied = dict(params)
        if self.auth_key:
            applied["authKey"] = self.auth_key
        return url, applied
