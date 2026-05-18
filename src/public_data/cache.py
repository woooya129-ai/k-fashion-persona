# SPDX-License-Identifier: AGPL-3.0-only
"""Small in-memory cache for public-data responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PublicDataCache:
    _items: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str) -> Any | None:
        return self._items.get(key)

    def set(self, key: str, value: Any) -> Any:
        self._items[key] = value
        return value

    def clear(self) -> None:
        self._items.clear()
