"""AZRouterEntity class."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.azrouter_integration.data_value_accessor import DataValueAccessor

from .const import ATTRIBUTION
from .coordinator import AZRouterDataUpdateCoordinator


class AZRouterIntegrationEntity(CoordinatorEntity[AZRouterDataUpdateCoordinator]):
    """AZRouterEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self, coordinator: AZRouterDataUpdateCoordinator, path: str = ""
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        )

        self._value_accessor = DataValueAccessor(path) if path else None

    @property
    def raw_value(self) -> Any:
        """Get value from Coordinator.data by given Path."""
        if self._value_accessor:
            return self._value_accessor.extract(self.coordinator.data)

        return None
