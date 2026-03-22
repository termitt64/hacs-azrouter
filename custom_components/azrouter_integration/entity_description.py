"""Centralised entity description factory for azrouter_integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

from .data_value_accessor import ApiRequestComposer, DataValueWriter  # noqa: TC001
from .device import AZCharger, AZDeviceBase, AZDeviceFactory, AZRouter

if TYPE_CHECKING:
    from homeassistant.helpers.device_registry import DeviceInfo

    from .coordinator import AZRouterDataUpdateCoordinator


# ── Spec dataclasses ──────────────────────────────────────────────────────────


@dataclass
class SensorSpec:
    """Bundles a SensorEntityDescription with its data path and device."""

    description: SensorEntityDescription
    path: str
    device_info: DeviceInfo | None = field(default=None)


@dataclass
class BinarySensorSpec:
    """Bundles a BinarySensorEntityDescription with its data path and device."""

    description: BinarySensorEntityDescription
    path: str
    device_info: DeviceInfo | None = field(default=None)


@dataclass
class SwitchSpec:
    """Bundles a SwitchEntityDescription with its accessor, request composer, and device."""

    description: SwitchEntityDescription
    accessor: DataValueWriter
    request: ApiRequestComposer
    device_info: DeviceInfo | None = field(default=None)


# ── Per-device-type description providers ─────────────────────────────────────


class _DeviceDescriptionProvider:
    """Base provider — returns empty lists; subclasses override what they need."""

    def sensor_specs(self) -> list[SensorSpec]:
        """Return sensor specs for this device."""
        return []

    def binary_sensor_specs(self) -> list[BinarySensorSpec]:
        """Return binary sensor specs for this device."""
        return []

    def switch_specs(self) -> list[SwitchSpec]:
        """Return switch specs for this device."""
        return []


class _RouterDescriptions(_DeviceDescriptionProvider):
    """Description provider for the AZ Router device."""

    def __init__(self, device: AZRouter) -> None:
        self._di: DeviceInfo = device.get_device_info()

    def sensor_specs(self) -> list[SensorSpec]:
        """Return router sensor specs."""
        return [
            SensorSpec(
                description=SensorEntityDescription(
                    key="router_uptime",
                    name="Uptime",
                    icon="mdi:timer-outline",
                    device_class=SensorDeviceClass.DURATION,
                    native_unit_of_measurement=UnitOfTime.MILLISECONDS,
                    suggested_unit_of_measurement=UnitOfTime.DAYS,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                ),
                path="status.system.uptime",
                device_info=self._di,
            ),
            SensorSpec(
                description=SensorEntityDescription(
                    key="router_temperature",
                    name="Temperature",
                    icon="mdi:thermometer",
                    device_class=SensorDeviceClass.TEMPERATURE,
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    state_class=SensorStateClass.MEASUREMENT,
                ),
                path="status.system.temperature",
                device_info=self._di,
            ),
            SensorSpec(
                description=SensorEntityDescription(
                    key="active_device_max_power",
                    name="Active Device Max Power",
                    icon="mdi:lightning-bolt",
                    device_class=SensorDeviceClass.POWER,
                    native_unit_of_measurement=UnitOfPower.WATT,
                    state_class=SensorStateClass.MEASUREMENT,
                ),
                path="status.activeDevice.maxPower",
                device_info=self._di,
            ),
        ]

    def binary_sensor_specs(self) -> list[BinarySensorSpec]:
        """Return router binary sensor specs."""
        return [
            BinarySensorSpec(
                description=BinarySensorEntityDescription(
                    key="cloud_reachable",
                    name="Cloud",
                    device_class=BinarySensorDeviceClass.CONNECTIVITY,
                ),
                path="status.cloud.reachable",
                device_info=self._di,
            ),
            BinarySensorSpec(
                description=BinarySensorEntityDescription(
                    key="hdo_active",
                    name="HDO",
                    icon="mdi:transmission-tower",
                ),
                path="status.system.hdo",
                device_info=self._di,
            ),
        ]

    def switch_specs(self) -> list[SwitchSpec]:
        """Return router switch specs."""
        return [
            SwitchSpec(
                description=SwitchEntityDescription(
                    key="master_boost",
                    name="Master Boost",
                    icon="mdi:rocket-launch",
                ),
                accessor=DataValueWriter("status.system.masterBoost"),
                request=ApiRequestComposer(
                    resource="system/boost",
                    payload_path="data.boost",
                ),
                device_info=self._di,
            ),
        ]


class _ChargerDescriptions(_DeviceDescriptionProvider):
    """Description provider for an AZ Charger device."""

    def __init__(self, device: AZCharger, charger_index: int) -> None:
        self._di: DeviceInfo = device.get_device_info()
        self._i = charger_index  # position in coordinator data["devices"] array
        self._device_id: int = device._raw_data["common"]["id"]

    def sensor_specs(self) -> list[SensorSpec]:
        """Return charger sensor specs."""
        i = self._i
        return [
            SensorSpec(
                description=SensorEntityDescription(
                    key=f"charger_{i}_total_power",
                    name="Charging Power",
                    icon="mdi:ev-station",
                    device_class=SensorDeviceClass.POWER,
                    native_unit_of_measurement=UnitOfPower.WATT,
                    state_class=SensorStateClass.MEASUREMENT,
                ),
                path=f"devices.{i}.charge.totalPower",
                device_info=self._di,
            ),
            SensorSpec(
                description=SensorEntityDescription(
                    key=f"charger_{i}_signal",
                    name="WiFi Signal",
                    icon="mdi:wifi",
                    device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                    native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
                    state_class=SensorStateClass.MEASUREMENT,
                ),
                path=f"devices.{i}.common.signal",
                device_info=self._di,
            ),
            SensorSpec(
                description=SensorEntityDescription(
                    key=f"charger_{i}_boost_source",
                    name="Boost Source",
                    icon="mdi:rocket-launch-outline",
                    state_class=SensorStateClass.MEASUREMENT,
                ),
                path=f"devices.{i}.charge.boostSource",
                device_info=self._di,
            ),
        ]

    def switch_specs(self) -> list[SwitchSpec]:
        """Return charger switch specs."""
        i = self._i
        return [
            SwitchSpec(
                description=SwitchEntityDescription(
                    key=f"charger_{i}_boost",
                    name="Boost",
                    icon="mdi:rocket-launch",
                ),
                accessor=DataValueWriter(f"devices.{i}.charge.boost"),
                request=ApiRequestComposer(
                    resource="device/boost",
                    payload_path="data.boost",
                    payload_base={"data": {"device": {"common": {"id": self._device_id}}}},
                ),
                device_info=self._di,
            ),
        ]


# ── Factory ───────────────────────────────────────────────────────────────────


def create_entity_factory(
    coordinator: AZRouterDataUpdateCoordinator,
) -> EntityDescriptionFactory:
    """Build an EntityDescriptionFactory from coordinator data."""
    return EntityDescriptionFactory(AZDeviceFactory(coordinator).create_devices())


class EntityDescriptionFactory:
    """Aggregates entity specs from per-device-type description providers."""

    def __init__(self, device_list: list[AZDeviceBase]) -> None:
        """Build providers from the given device list."""
        self._providers = self._build_providers(device_list)

    @staticmethod
    def _build_providers(
        device_list: list[AZDeviceBase],
    ) -> list[_DeviceDescriptionProvider]:
        providers: list[_DeviceDescriptionProvider] = []
        charger_index = 0
        for device in device_list:
            if isinstance(device, AZRouter):
                providers.append(_RouterDescriptions(device))
            elif isinstance(device, AZCharger):
                providers.append(_ChargerDescriptions(device, charger_index))
                charger_index += 1
        return providers

    def sensor_descriptions(self) -> list[SensorSpec]:
        """Return all sensor specs across all devices."""
        return [spec for p in self._providers for spec in p.sensor_specs()]

    def binary_sensor_descriptions(self) -> list[BinarySensorSpec]:
        """Return all binary sensor specs across all devices."""
        return [spec for p in self._providers for spec in p.binary_sensor_specs()]

    def switch_descriptions(self) -> list[SwitchSpec]:
        """Return all switch specs across all devices."""
        return [spec for p in self._providers for spec in p.switch_specs()]
