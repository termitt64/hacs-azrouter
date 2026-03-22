"""AZRouterEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.device_registry import DeviceInfo

from .const import ATTRIBUTION
from .coordinator import AZRouterDataUpdateCoordinator
from .data_value_accessor import DataValueAccessor


class AZRouterIntegrationEntity(CoordinatorEntity[AZRouterDataUpdateCoordinator]):
    """AZRouterEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: AZRouterDataUpdateCoordinator,
        device_info: DeviceInfo,
        path: str = "",
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = device_info

        self._value_accessor = DataValueAccessor(path) if path else None

    @property
    def raw_value(self) -> Any:
        """Get value from Coordinator.data by given Path."""
        if self._value_accessor:
            return self._value_accessor.extract(self.coordinator.data)

        return None
