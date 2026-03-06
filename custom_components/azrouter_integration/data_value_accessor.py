"""Helper object for accessing values from data Json."""

from collections.abc import Mapping
from typing import Any


class DataValueAccessor:
    """Access data within multiple-layered dict (aka JSON)."""

    def __init__(self, path: str) -> None:
        """Initialize Data Value Accessor with dot-separated path."""
        parts = path.split(".", 1)
        self._key = parts[0]
        self._proxy = DataValueAccessor(parts[1]) if len(parts) > 1 else None

    def extract(self, data: Mapping[str, Any]) -> Any:
        """Retrieve value from given data (dict)."""
        value = data.get(self._key)
        return self._proxy.extract(value) if value and self._proxy else value
