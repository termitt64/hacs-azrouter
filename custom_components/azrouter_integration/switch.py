"""Switch platform for azrouter_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity

from .entity import AZRouterIntegrationEntity
from .entity_description import SwitchSpec, create_entity_factory

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
    """Set up the switch platform."""
    coordinator = entry.runtime_data.coordinator
    factory = create_entity_factory(coordinator)

    async_add_entities(
        AZRouterIntegrationSwitch(coordinator, spec)
        for spec in factory.switch_descriptions()
    )


class AZRouterIntegrationSwitch(AZRouterIntegrationEntity, SwitchEntity):
    """azrouter_integration switch class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AZRouterDataUpdateCoordinator,
        spec: SwitchSpec,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, spec.device_info)
        self.entity_description = spec.description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{spec.description.key}"
        )
        self._spec = spec

    def _handle_coordinator_update(self) -> None:
        """Sync _attr_is_on from fresh coordinator data, then notify HA."""
        self._attr_is_on = bool(self._spec.reader.extract(self.coordinator.data))
        super()._handle_coordinator_update()

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        await self._async_set_value(True)

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        await self._async_set_value(False)

    async def _async_set_value(self, value: bool) -> None:
        client = self.coordinator.config_entry.runtime_data.client
        await self._spec.writer.async_execute(client, value)
        self._attr_is_on = value
        self.async_write_ha_state()
