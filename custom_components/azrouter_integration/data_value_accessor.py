"""Helper objects for accessing and writing values within nested JSON data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping


class DataValueAccessor:
    """
    Read-only access to a value inside a nested dict/list structure.

    Path is a dot-separated string, e.g. "devices.0.charge.boost".
    """

    class _ExtractionStrategy(ABC):
        @abstractmethod
        def extract(self, data: Any, key: str) -> Any:
            """Extract the value for key from data."""

    class _ListExtractionStrategy(_ExtractionStrategy):
        def extract(self, data: Any, key: str) -> Any:
            """Return the list item at index key, or None on invalid index."""
            try:
                return data[int(key)]
            except (ValueError, IndexError):
                return None

    class _DictExtractionStrategy(_ExtractionStrategy):
        def extract(self, data: Any, key: str) -> Any:
            """Return the dict value for key, or None if absent."""
            return data.get(key)

    _LIST_STRATEGY = _ListExtractionStrategy()
    _DICT_STRATEGY = _DictExtractionStrategy()

    def __init__(self, path: str) -> None:
        """Initialize with a dot-separated path."""
        parts = path.split(".", 1)
        self._key = parts[0]
        self._proxy: DataValueAccessor | DataValueWriter | None = (
            type(self)(parts[1]) if len(parts) > 1 else None
        )

    def extract(self, data: Mapping[str, Any] | list[Any]) -> Any:
        """Retrieve value from given data (dict or list)."""
        strategy = (
            self._LIST_STRATEGY if isinstance(data, list) else self._DICT_STRATEGY
        )
        value = strategy.extract(data, self._key)
        return (
            self._proxy.extract(value) if value is not None and self._proxy else value
        )


class DataValueWriter(DataValueAccessor):
    """
    Extends DataValueAccessor with in-memory write capability.

    Used both to read the current state from coordinator data and to apply
    an optimistic update after a successful API write.
    """

    class _InjectionStrategy(ABC):
        @abstractmethod
        def inject(self, data: Any, key: str, value: Any) -> None:
            """Set value directly in data at key (leaf operation)."""

        @abstractmethod
        def traverse(self, data: Any, key: str) -> Any:
            """Return the child node at key, creating it if necessary."""

    class _ListInjectionStrategy(_InjectionStrategy):
        def inject(self, data: Any, key: str, value: Any) -> None:
            """Set value at list index key."""
            data[int(key)] = value

        def traverse(self, data: Any, key: str) -> Any:
            """Return the child list item at index key."""
            return data[int(key)]

    class _DictInjectionStrategy(_InjectionStrategy):
        def inject(self, data: Any, key: str, value: Any) -> None:
            """Set value at dict key."""
            data[key] = value

        def traverse(self, data: Any, key: str) -> Any:
            """Return the child dict at key, creating an empty dict if absent."""
            if key not in data:
                data[key] = {}
            return data[key]

    _LIST_INJECT_STRATEGY = _ListInjectionStrategy()
    _DICT_INJECT_STRATEGY = _DictInjectionStrategy()

    def inject(self, data: dict | list, value: Any) -> None:
        """Write value into data (dict or list) at this path."""
        strategy = (
            self._LIST_INJECT_STRATEGY
            if isinstance(data, list)
            else self._DICT_INJECT_STRATEGY
        )
        proxy = self._proxy if isinstance(self._proxy, DataValueWriter) else None
        if proxy is not None:
            proxy.inject(strategy.traverse(data, self._key), value)
        else:
            strategy.inject(data, self._key, value)
