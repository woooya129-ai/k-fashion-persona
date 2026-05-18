# SPDX-License-Identifier: AGPL-3.0-only
"""Errors raised by public-data connectors."""


class PublicDataError(RuntimeError):
    """Base public-data connector error."""


class MissingPublicDataKey(PublicDataError):
    """Raised when a connector explicitly requires an API key."""
