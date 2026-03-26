"""
Representation of AZ Router and linked devices.

Main purpose is to ease creation of DeviceInfo.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, LOGGER
from .coordinator import AZRouterDataUpdateCoordinator
from .data_value_accessor import DataValueAccessor

# Registry mapping deviceType strings to device classes.
# Register new device types with @register_device_type("<type>").
_DEVICE_TYPE_REGISTRY: dict[str, type] = {}


def register_device_type(device_type: str) -> Callable[[type], type]:
    """Register a device class for a given deviceType string - Decorator."""

    def decorator(cls: type) -> type:
        _DEVICE_TYPE_REGISTRY[device_type] = cls
        return cls

    return decorator


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
        serial = "{} (mac: {})".format(d["sn"], mac)
        sw = "{}; {}".format(d["fw"], d["www"])
        return DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name="A-Z Router SMART",
            manufacturer="A-Z Traders",
            model="Router SMART",
            serial_number=serial,
            sw_version=sw,
            hw_version=d["hw"],
        )


@register_device_type("4")
class AZCharger(AZDeviceBase):
    """Representation of an AZ Charger device linked to the router."""

    def __init__(self, dev_data: Mapping[str, Any], router_mac: str) -> None:
        """Construct AZCharger device."""
        super().__init__(dev_data)
        self._router_mac = router_mac

    @property
    def device_id(self) -> int:
        """Return the device id."""
        return self._raw_data["common"]["id"]

    def get_device_info(self) -> DeviceInfo:
        """Create HA DeviceInfo object."""
        c = self._raw_data["common"]
        identifier = f"{self._router_mac}_{c['id']}"
        return DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            name=c["name"],
            manufacturer="A-Z Traders",
            model="AZ Charger",
            sw_version=c["fw"],
            hw_version=str(c["hw"]),
            via_device=(DOMAIN, self._router_mac),
        )


class AZDeviceFactory:
    """Factory to create devices."""

    def __init__(self, coordinator: AZRouterDataUpdateCoordinator) -> None:
        """Initialize Factory with Coordinator."""
        self._coordinator = coordinator

    def _extract_data(self, path: str) -> Mapping[str, Any]:
        """Extract a value from coordinator data at the given dot-separated path."""
        return DataValueAccessor(path).extract(self._coordinator.data)

    def create_devices(self) -> list[AZDeviceBase]:
        """Create AZDevice objects from data provided by coordinator."""
        devices: list[AZDeviceBase] = []

        system_data = self._extract_data("status.system")
        router = AZRouter(system_data)
        devices.append(router)

        router_mac = system_data.get("mac", "")
        for dev_data in self._coordinator.data.get("devices", []):
            device_type = str(dev_data.get("deviceType", ""))
            cls = _DEVICE_TYPE_REGISTRY.get(device_type)
            if cls is not None:
                devices.append(cls(dev_data, router_mac))
            else:
                LOGGER.warning("Unknown device type %s — skipping", device_type)

        return devices
