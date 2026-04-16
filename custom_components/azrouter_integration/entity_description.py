"""Centralised entity description factory for azrouter_integration."""

from __future__ import annotations

from dataclasses import dataclass
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
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

from .api_request_composer import ApiRequestComposer, BoolToNumConverter
from .data_value_accessor import DataValueAccessor
from .device import AZCharger, AZDeviceBase, AZDeviceFactory, AZRouter
from .enums import ChargeStatus
from .sensor_specs import (
    BinarySensorSpec,
    EnumSensorSpec,
    EnumValueInterpreter,
    SensorSpec,
    SwitchSpec,
)

if TYPE_CHECKING:
    from homeassistant.helpers.device_registry import DeviceInfo

    from .coordinator import AZRouterDataUpdateCoordinator


@dataclass
class _PhaseSensorDef:
    """Parameters for building a set of per-phase sensor specs."""

    key_prefix: str
    name_prefix: str
    icon: str
    device_class: SensorDeviceClass
    native_unit: str
    suggested_unit: str
    path_prefix: str


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
        """Initialize with the AZ Router device."""
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
            SensorSpec(
                description=SensorEntityDescription(
                    key="cloud_status",
                    name="Cloud Status",
                    icon="mdi:cloud-check-outline",
                ),
                path="cloud/status.status",
                device_info=self._di,
            ),
            *self._phase_sensor_specs(
                _PhaseSensorDef(
                    key_prefix="input_power",
                    name_prefix="Input Power",
                    icon="mdi:transmission-tower",
                    device_class=SensorDeviceClass.POWER,
                    native_unit=UnitOfPower.WATT,
                    suggested_unit=UnitOfPower.WATT,
                    path_prefix="power.input.power",
                )
            ),
            *self._phase_sensor_specs(
                _PhaseSensorDef(
                    key_prefix="input_voltage",
                    name_prefix="Input Voltage",
                    icon="mdi:sine-wave",
                    device_class=SensorDeviceClass.VOLTAGE,
                    native_unit=UnitOfElectricPotential.MILLIVOLT,
                    suggested_unit=UnitOfElectricPotential.VOLT,
                    path_prefix="power.input.voltage",
                )
            ),
            *self._phase_sensor_specs(
                _PhaseSensorDef(
                    key_prefix="input_current",
                    name_prefix="Input Current",
                    icon="mdi:current-ac",
                    device_class=SensorDeviceClass.CURRENT,
                    native_unit=UnitOfElectricCurrent.MILLIAMPERE,
                    suggested_unit=UnitOfElectricCurrent.AMPERE,
                    path_prefix="power.input.current",
                )
            ),
            *self._phase_sensor_specs(
                _PhaseSensorDef(
                    key_prefix="output_power",
                    name_prefix="Output Power",
                    icon="mdi:transmission-tower-export",
                    device_class=SensorDeviceClass.POWER,
                    native_unit=UnitOfPower.WATT,
                    suggested_unit=UnitOfPower.WATT,
                    path_prefix="power.output.power",
                )
            ),
            *[
                SensorSpec(
                    description=SensorEntityDescription(
                        key=f"output_energy_{ch}",
                        name=f"Output Energy {ch}",
                        icon="mdi:counter",
                        device_class=SensorDeviceClass.ENERGY,
                        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
                        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
                        state_class=SensorStateClass.TOTAL_INCREASING,
                    ),
                    path=f"power.output.energy.{ch}.value",
                    device_info=self._di,
                )
                for ch in range(4)
            ],
            SensorSpec(
                description=SensorEntityDescription(
                    key="regulation_target_power",
                    name="Regulation Target Power",
                    icon="mdi:target",
                    device_class=SensorDeviceClass.POWER,
                    native_unit_of_measurement=UnitOfPower.WATT,
                    state_class=SensorStateClass.MEASUREMENT,
                ),
                path="settings.regulation.target_power_w",
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
            BinarySensorSpec(
                description=BinarySensorEntityDescription(
                    key="cloud_registered",
                    name="Cloud Registered",
                    icon="mdi:cloud-check",
                ),
                path="status.cloud.registered",
                device_info=self._di,
            ),
        ]

    def _phase_sensor_specs(self, defn: _PhaseSensorDef) -> list[SensorSpec]:
        """Build three per-phase sensor specs (L1, L2, L3)."""
        return [
            SensorSpec(
                description=SensorEntityDescription(
                    key=f"{defn.key_prefix}_l{phase}",
                    name=f"{defn.name_prefix} L{phase}",
                    icon=defn.icon,
                    device_class=defn.device_class,
                    native_unit_of_measurement=defn.native_unit,
                    suggested_unit_of_measurement=defn.suggested_unit,
                    state_class=SensorStateClass.MEASUREMENT,
                ),
                path=f"{defn.path_prefix}.{phase - 1}.value",
                device_info=self._di,
            )
            for phase in (1, 2, 3)
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
                reader=DataValueAccessor("status.system.masterBoost"),
                writer=ApiRequestComposer(
                    resource="system/boost",
                    payload_path="data.boost",
                    value_converter=BoolToNumConverter(),
                ),
                device_info=self._di,
            ),
        ]


class _ChargerDescriptions(_DeviceDescriptionProvider):
    """Description provider for an AZ Charger device."""

    def __init__(self, device: AZCharger, charger_index: int) -> None:
        """Initialize with an AZ Charger device and its index in the devices array."""
        self._di: DeviceInfo = device.get_device_info()
        self._i = charger_index  # position in coordinator data["devices"] array
        self._device_id: int = device.device_id

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
            EnumSensorSpec(
                description=SensorEntityDescription(
                    key=f"charger_{i}_charge_status",
                    name="Charge Status",
                    icon="mdi:ev-plug-type2",
                    device_class=SensorDeviceClass.ENUM,
                    options=[e.name for e in ChargeStatus],
                ),
                path=f"devices.{i}.charge.status",
                device_info=self._di,
                value_interpreter=EnumValueInterpreter(ChargeStatus),
            ),
            SensorSpec(
                description=SensorEntityDescription(
                    key=f"charger_{i}_temperature",
                    name="Temperature",
                    icon="mdi:thermometer",
                    device_class=SensorDeviceClass.TEMPERATURE,
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    state_class=SensorStateClass.MEASUREMENT,
                ),
                path=f"devices.{i}.charge.temperature",
                device_info=self._di,
            ),
            *[
                SensorSpec(
                    description=SensorEntityDescription(
                        key=f"charger_{i}_current_l{phase}",
                        name=f"Current L{phase}",
                        icon="mdi:current-ac",
                        device_class=SensorDeviceClass.CURRENT,
                        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
                        suggested_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                        state_class=SensorStateClass.MEASUREMENT,
                    ),
                    path=f"devices.{i}.charge.current.{phase - 1}",
                    device_info=self._di,
                )
                for phase in (1, 2, 3)
            ],
        ]

    def binary_sensor_specs(self) -> list[BinarySensorSpec]:
        """Return charger binary sensor specs."""
        i = self._i
        return [
            BinarySensorSpec(
                description=BinarySensorEntityDescription(
                    key=f"charger_{i}_connected",
                    name="Connected",
                    device_class=BinarySensorDeviceClass.CONNECTIVITY,
                ),
                path=f"devices.{i}.common.status",
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
                reader=DataValueAccessor(f"devices.{i}.charge.boost"),
                writer=ApiRequestComposer(
                    resource="device/boost",
                    payload_path="data.boost",
                    value_converter=BoolToNumConverter(),
                    payload_base={
                        "data": {"device": {"common": {"id": self._device_id}}}
                    },
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
        """
        Map each device to its description provider.

        Tracking charger index for array paths.
        """
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
