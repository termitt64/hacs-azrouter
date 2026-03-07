"""
Representation of AZ Router and linked devices.

Main purpose is to ease creation of DeviceInfo.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo

from custom_components.azrouter_integration.data_value_accessor import DataValueAccessor

from .const import DOMAIN
from .coordinator import AZRouterDataUpdateCoordinator


class AZDeviceBase(ABC):
    """Base class for AZ Devices."""

    def __init__(self, dev_data: Mapping[str, Any]) -> None:
        """Initialize common Device structure (raw_data)."""
        self._raw_data = dev_data

    @abstractmethod
    def get_device_info(self) -> DeviceInfo:
        """Create HA DeviceInfo object."""


class AZRouter(AZDeviceBase):
    """Representation of A-Z Router."""

    def __init__(self, dev_data: Mapping[str, Any]) -> None:
        """Construct root AZRouter device."""
        super().__init__(dev_data)

    def get_device_info(self) -> DeviceInfo:
        """Create HA DeviceInfo object."""
        d = self._raw_data
        mac = d["mac"]
        serial = "{} mac: {}".format(d["sn"], mac)
        sw = d["fw"] + ";" + d["www"]
        return DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name="A-Z Router SMART",
            manufacturer="A-Z Traders",
            model="Router SMART",
            serial_number=serial,
            sw_version=sw,
            hw_version=d["hw"],
        )


class AZDeviceFactory:
    """Factory to create devices."""

    def __init__(self, coordinator: AZRouterDataUpdateCoordinator) -> None:
        """Initialize Factory with Coordinator."""
        self._coordinator = coordinator

    def _extract_data(self, path: str) -> Mapping[str, Any]:
        return DataValueAccessor(path).extract(self._coordinator.data)

    def create_devices(self) -> list[AZDeviceBase]:
        """Create AZDevice objects from data provided by coordinator."""
        devices: list[AZDeviceBase] = []

        # Router
        router = AZRouter(self._extract_data("status.system"))
        devices.append(router)

        return devices
