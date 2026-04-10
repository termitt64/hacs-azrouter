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
    """Switch entity for an AZRouter controllable boolean setting."""

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
        self._sync_state(coordinator.data)

    def _sync_state(self, data: Any) -> None:
        """Read the switch value from coordinator data and update _attr_is_on."""
        value = self._spec.reader.extract(data)
        if value is not None:
            self._attr_is_on = bool(value)

    def _handle_coordinator_update(self) -> None:
        """Sync _attr_is_on from fresh coordinator data, then notify HA."""
        self._sync_state(self.coordinator.data)
        super()._handle_coordinator_update()

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        await self._async_set_value(turn_on=True)

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        await self._async_set_value(turn_on=False)

    async def _async_set_value(self, turn_on: bool) -> None:  # noqa: FBT001
        """Send the new value to the API and optimistically update the entity state."""
        client = self.coordinator.config_entry.runtime_data.client
        await self._spec.writer.async_execute(client, turn_on)
        self._attr_is_on = turn_on
        self.async_write_ha_state()
