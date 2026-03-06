"""Sensor platform for azrouter_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from .entity import AZRouterIntegrationEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AZRouterDataUpdateCoordinator
    from .data import AZRouterIntegrationConfigEntry

ENTITY_DESCRIPTIONS = {
    SensorEntityDescription(
        key="router_uptime",
        name="Uptime",
        icon="mdi:timer-outline",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement="ms",
        suggested_unit_of_measurement="d",
    ): "status.system.uptime",
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AZRouterIntegrationConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        AZRouterIntegrationSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            path=path,
        )
        for entity_description, path in ENTITY_DESCRIPTIONS.items()
    )


class AZRouterIntegrationSensor(AZRouterIntegrationEntity, SensorEntity):
    """azrouter_integration Sensor class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AZRouterDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
        path: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, path)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self.raw_value
