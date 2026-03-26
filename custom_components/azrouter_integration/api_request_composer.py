"""Utilities for composing and executing API write requests."""

import copy
from abc import abstractmethod
from typing import Any

from .api import AZRouterApiClientProtocol
from .data_value_accessor import DataValueWriter


class ValueConverter:
    """Abstract base for value converters applied before API payload injection."""

    @abstractmethod
    def convert(self, value: Any) -> Any:
        """Convert value to the API-expected type."""


class TypedConverter[_FromType, _ToType](ValueConverter):
    """Generic typed converter with explicit input and output types."""

    @abstractmethod
    def convert(self, value: _FromType) -> _ToType:
        """Convert a value of _FromType to _ToType."""


class BoolToNumConverter(TypedConverter[bool, int]):
    """Converts a Python bool to an integer (True→1, False→0)."""

    def convert(self, value: bool) -> int:
        """Return 1 for True, 0 for False."""
        return 1 if value else 0


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
        value_converter: ValueConverter | None = None,
        payload_base: dict | None = None,
    ) -> None:
        """Initialize with the API resource, payload path, and optional base dict."""
        self._resource = resource
        self._payload_writer = DataValueWriter(payload_path)
        self._converter = value_converter
        self._payload_base: dict = payload_base or {}

    def prepare_payload(self, value: Any) -> dict:
        """Build the JSON payload by injecting the converted value into a copy of the base dict."""
        payload = copy.deepcopy(self._payload_base)
        self._payload_writer.inject(
            payload, self._converter.convert(value) if self._converter else value
        )
        return payload

    async def async_execute(
        self, client: AZRouterApiClientProtocol, value: Any
    ) -> None:
        """Prepare payload and send it via the client."""
        await client.async_post(self._resource, self.prepare_payload(value))
