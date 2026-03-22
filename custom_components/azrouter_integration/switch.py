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

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return bool(self._spec.accessor.extract(self.coordinator.data))

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        client = self.coordinator.config_entry.runtime_data.client
        await self._spec.request.async_execute(client, value=True)
        self._spec.accessor.set(self.coordinator.data, 1)
        self.async_write_ha_state()

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        client = self.coordinator.config_entry.runtime_data.client
        await self._spec.request.async_execute(client, value=False)
        self._spec.accessor.set(self.coordinator.data, 0)
        self.async_write_ha_state()
