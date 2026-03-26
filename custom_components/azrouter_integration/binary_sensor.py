"""Binary sensor platform for azrouter_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorEntity

from .entity import AZRouterIntegrationEntity
from .entity_description import BinarySensorSpec, create_entity_factory

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
    """Set up the binary_sensor platform."""
    coordinator = entry.runtime_data.coordinator
    factory = create_entity_factory(coordinator)

    async_add_entities(
        AZRouterIntegrationBinarySensor(coordinator, spec)
        for spec in factory.binary_sensor_descriptions()
    )


class AZRouterIntegrationBinarySensor(AZRouterIntegrationEntity, BinarySensorEntity):
    """Binary sensor entity for an AZRouter boolean data point read from coordinator data."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AZRouterDataUpdateCoordinator,
        spec: BinarySensorSpec,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, spec.device_info, spec.path)
        self.entity_description = spec.description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{spec.description.key}"
        )

    @property
    def is_on(self) -> bool:
        """Return True if the coordinator data point is truthy."""
        return bool(self.raw_value)
