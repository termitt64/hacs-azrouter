"""Sensor platform for azrouter_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity

from .entity import AZRouterIntegrationEntity
from .entity_description import create_entity_factory

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AZRouterDataUpdateCoordinator
    from .data import AZRouterIntegrationConfigEntry
    from .sensor_specs import RawValueInterpreter, SensorSpec


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
    """Sensor entity for an AZRouter data point read from coordinator data."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AZRouterDataUpdateCoordinator,
        spec: SensorSpec,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, spec.device_info, spec.path)
        self.entity_description = spec.description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{spec.description.key}"
        )
        self._interpreter: RawValueInterpreter | None = spec.get_value_interpreter()

    @property
    def native_value(self) -> str | None:
        """Return the sensor value, translated by the spec if applicable."""
        return (
            self._interpreter.interpret(self.raw_value)
            if self._interpreter
            else self.raw_value
        )
