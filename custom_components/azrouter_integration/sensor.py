"""Sensor platform for azrouter_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity

from .entity import AZRouterIntegrationEntity
from .entity_description import SensorSpec, create_entity_factory

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AZRouterDataUpdateCoordinator
    from .data import AZRouterIntegrationConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AZRouterIntegrationConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    factory = create_entity_factory(coordinator)

    async_add_entities(
        AZRouterIntegrationSensor(coordinator, spec)
        for spec in factory.sensor_descriptions()
    )


class AZRouterIntegrationSensor(AZRouterIntegrationEntity, SensorEntity):
    """azrouter_integration Sensor class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AZRouterDataUpdateCoordinator,
        spec: SensorSpec,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, spec.path, spec.device_info)
        self.entity_description = spec.description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{spec.description.key}"
        )

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self.raw_value
