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
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

from .device import AZDeviceFactory

if TYPE_CHECKING:
    from homeassistant.helpers.device_registry import DeviceInfo

    from .coordinator import AZRouterDataUpdateCoordinator


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


class EntityDescriptionFactory:
    """Build entity descriptions from live coordinator data."""

    def __init__(self, coordinator: AZRouterDataUpdateCoordinator) -> None:
        """Initialise factory and resolve device infos."""
        self._coordinator = coordinator
        devices = AZDeviceFactory(coordinator).create_devices()
        self._router_device: DeviceInfo = devices[0].get_device_info()
        self._charger_device: DeviceInfo | None = (
            devices[1].get_device_info() if len(devices) > 1 else None
        )

    def sensor_descriptions(self) -> list[SensorSpec]:
        """Return sensor specs for all platforms."""
        specs: list[SensorSpec] = [
            # ── Router ────────────────────────────────────────────────
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
                device_info=self._router_device,
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
                device_info=self._router_device,
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
                device_info=self._router_device,
            ),
        ]

        if self._charger_device is not None:
            specs += [
                # ── AZ Charger ────────────────────────────────────────
                SensorSpec(
                    description=SensorEntityDescription(
                        key="charger_total_power",
                        name="Charging Power",
                        icon="mdi:ev-station",
                        device_class=SensorDeviceClass.POWER,
                        native_unit_of_measurement=UnitOfPower.WATT,
                        state_class=SensorStateClass.MEASUREMENT,
                    ),
                    path="devices.0.charge.totalPower",
                    device_info=self._charger_device,
                ),
                SensorSpec(
                    description=SensorEntityDescription(
                        key="charger_signal",
                        name="WiFi Signal",
                        icon="mdi:wifi",
                        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
                        state_class=SensorStateClass.MEASUREMENT,
                    ),
                    path="devices.0.common.signal",
                    device_info=self._charger_device,
                ),
            ]

        return specs

    def binary_sensor_descriptions(self) -> list[BinarySensorSpec]:
        """Return binary sensor specs for all platforms."""
        return [
            BinarySensorSpec(
                description=BinarySensorEntityDescription(
                    key="cloud_reachable",
                    name="Cloud",
                    device_class=BinarySensorDeviceClass.CONNECTIVITY,
                ),
                path="status.cloud.reachable",
                device_info=self._router_device,
            ),
            BinarySensorSpec(
                description=BinarySensorEntityDescription(
                    key="hdo_active",
                    name="HDO",
                    icon="mdi:transmission-tower",
                ),
                path="status.system.hdo",
                device_info=self._router_device,
            ),
        ]
