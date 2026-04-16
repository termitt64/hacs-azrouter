"""Spec dataclasses and value interpreters for azrouter_integration entities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription

from .api_request_composer import ApiRequestComposer
from .data_value_accessor import DataValueAccessor

if TYPE_CHECKING:
    from homeassistant.helpers.device_registry import DeviceInfo


# ── Value interpreters ────────────────────────────────────────────────────────


class RawValueInterpreter:
    """Converts a raw coordinator value into a sensor native value."""

    def interpret(self, raw: Any) -> Any:
        """Return the native value for the given raw value."""
        return raw


class EnumValueInterpreter[EnumT: Enum](RawValueInterpreter):
    """Interprets a raw int as the name of the matching member of EnumT."""

    def __init__(self, enum_class: type[EnumT]) -> None:
        """Store the enum class used for interpretation."""
        self._enum_class = enum_class

    def interpret(self, raw: Any) -> str | None:
        """Return the enum member name for the given int value, or None if unknown."""
        try:
            return self._enum_class(raw).name
        except (ValueError, TypeError):
            return None


# ── Spec dataclasses ──────────────────────────────────────────────────────────


@dataclass
class SensorSpec:
    """Bundles a SensorEntityDescription with its data path and device."""

    description: SensorEntityDescription
    path: str
    device_info: DeviceInfo

    def get_value_interpreter(self) -> RawValueInterpreter | None:
        return None


@dataclass
class EnumSensorSpec(SensorSpec):
    """SensorSpec that pairs a raw int sensor with an enum-based interpreter."""

    value_interpreter: RawValueInterpreter

    def get_value_interpreter(self) -> RawValueInterpreter:
        return self.value_interpreter


@dataclass
class BinarySensorSpec:
    """Bundles a BinarySensorEntityDescription with its data path and device."""

    description: BinarySensorEntityDescription
    path: str
    device_info: DeviceInfo


@dataclass
class SwitchSpec:
    """Bundles a SwitchEntityDescription with its accessor, request, and device info."""

    description: SwitchEntityDescription
    reader: DataValueAccessor
    writer: ApiRequestComposer
    device_info: DeviceInfo
