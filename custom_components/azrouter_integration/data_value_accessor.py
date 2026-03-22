"""Helper objects for accessing and writing values within nested JSON data."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping


class DataValueAccessor:
    """
    Read-only access to a value inside a nested dict/list structure.

    Path is a dot-separated string, e.g. "devices.0.charge.boost".
    """

    def __init__(self, path: str) -> None:
        """Initialize with a dot-separated path."""
        parts = path.split(".", 1)
        self._key = parts[0]
        self._proxy: DataValueAccessor | None = (
            DataValueAccessor(parts[1]) if len(parts) > 1 else None
        )

    def extract(self, data: Mapping[str, Any] | list[Any]) -> Any:
        """Retrieve value from given data (dict or list)."""
        if isinstance(data, list):
            try:
                value = data[int(self._key)]
            except (ValueError, IndexError):
                return None
        else:
            value = data.get(self._key)
        return (
            self._proxy.extract(value) if value is not None and self._proxy else value
        )


class DataValueWriter(DataValueAccessor):
    """
    Extends DataValueAccessor with in-memory write capability.

    Used both to read the current state from coordinator data and to apply
    an optimistic update after a successful API write.
    """

    def set(self, data: dict | list, value: Any) -> None:
        """Set value in given data (dict or list) at this path."""
        if isinstance(data, list):
            idx = int(self._key)
            if self._proxy is None:
                data[idx] = value
            else:
                self._proxy.set(data[idx], value)
        elif self._proxy is None:
            data[self._key] = value
        else:
            if self._key not in data:
                data[self._key] = {}
            self._proxy.set(data[self._key], value)


class ApiRequestComposer:
    """
    Composes and executes an API POST request.

    Builds the JSON payload by deep-copying an optional base dict and then
    writing the target value at payload_path using a DataValueWriter.
    """

    def __init__(
        self,
        resource: str,
        payload_path: str,
        payload_base: dict | None = None,
    ) -> None:
        """Initialize with the API resource, payload path, and optional base dict."""
        self._resource = resource
        self._payload_writer = DataValueWriter(payload_path)
        self._payload_base: dict = payload_base or {}

    async def async_execute(self, client: Any, *, value: bool) -> None:
        """Build payload and POST to the API resource."""
        payload = copy.deepcopy(self._payload_base)
        self._payload_writer.set(payload, int(value))
        await client.async_post(self._resource, payload)
