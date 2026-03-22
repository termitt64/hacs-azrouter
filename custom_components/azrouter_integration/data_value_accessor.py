"""Helper object for accessing values from data Json."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping


class DataValueAccessor:
    """Access data within multiple-layered dict (aka JSON)."""

    def __init__(self, path: str) -> None:
        """Initialize Data Value Accessor with dot-separated path."""
        parts = path.split(".", 1)
        self._key = parts[0]
        self._proxy = DataValueAccessor(parts[1]) if len(parts) > 1 else None

    def extract(self, data: Mapping[str, Any] | list[Any]) -> Any:
        """Retrieve value from given data (dict or list)."""
        if self._proxy:
            return self._proxy.extract(data)

        if isinstance(data, list):
            try:
                return data[int(self._key)]
            except (ValueError, IndexError):
                return None
        else:
            return data.get(self._key)

    def set(self, data: dict | list, value: Any) -> None:
        """Set value in given data (dict or list) at this path."""
        if self._proxy:
            self._proxy.set(data, value)

        if isinstance(data, list):
            idx = int(self._key)
            data[idx] = value
        else:
            data[self._key] = value


class DataValueWriter(DataValueAccessor):
    """
    DataValueAccessor extended with API write capability.

    Holds the read path (inherited), the API resource endpoint, a dot-path
    that describes where in the JSON payload to place the written value, and
    an optional base payload dict containing any static fields (e.g. device id).
    """

    def __init__(
        self,
        read_path: str,
        resource: str,
        payload_path: str,
    ) -> None:
        """Initialize with read path, API resource, and payload description."""
        super().__init__(read_path)
        self._resource = resource
        self._payload_accessor = DataValueAccessor(payload_path)

    def set(self, data: dict | list, value: Any) -> None:
        """Set value using payload_accessor."""
        self._payload_accessor.set(data, value)
