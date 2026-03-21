"""Binary sensor platform for azrouter_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import AZRouterIntegrationEntity
from .entity_description import EntityDescriptionFactory

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo
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
    factory = EntityDescriptionFactory(coordinator)

    async_add_entities(
        AZRouterIntegrationBinarySensor(coordinator, spec.description, spec.path, spec.device_info)
        for spec in factory.binary_sensor_descriptions()
    )


class AZRouterIntegrationBinarySensor(AZRouterIntegrationEntity, BinarySensorEntity):
    """azrouter_integration binary_sensor class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AZRouterDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
        path: str,
        device_info: DeviceInfo | None = None,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, path, device_info)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return bool(self.raw_value)
