"""
Enumerations for azrouter_integration.

Read from webserver JavaScript.
"""

from enum import Enum


class DeviceStatus(Enum):
    """Device status codes."""

    Unpaired = 0
    Online = 1
    Offline = 2
    Error = 3
    Active = 4


class DeviceType(Enum):
    """Device type codes."""

    Generic = 0
    Power = 1
    Hdo = 2
    Fire = 3
    Charger = 4
    Inverter = 5


class DeviceBoostMode(Enum):
    """Device boost mode codes."""

    Manual = 0
    Hdo = 1
    Window = 2
    WindowAndHdo = 3


class HdoStatus(Enum):
    """HDO status codes."""

    Off = 0
    On = 1


class Mode(Enum):
    """System mode codes."""

    Summer = 0
    Winter = 1


class SystemStatus(Enum):
    """System status codes."""

    Online = 0
    Offline = 1
    Updating = 2


class PhaseStatus(Enum):
    """Phase status codes."""

    Connected = 0
    Disconnected = 1


class ChargeStatus(Enum):
    """Charge status codes reported by the AZ Charger."""

    Disconnected = 0
    Waiting = 1
    Charging = 2
    Overheated = 3
    Error = 4
    Unavailable = 5


class ChargeMode(Enum):
    """Charge mode codes."""

    Solar = 0
    Manual = 1
    Time = 2
    Hdo = 3


class DeviceTestResult(Enum):
    """Device test result codes."""

    NoResult = 0
    InProgress = 1
    Pass = 2
    Fail = 3
    Timeout = 4


class InverterEmsMode(Enum):
    """Inverter EMS mode codes."""

    Auto = 1
    ChargePv = 2
    DischargePv = 3
    ImportAc = 4
    ExportAc = 5
    Conserve = 6
    OffGrid = 7
    BatteryStandby = 8
    BuyPower = 9
    SellPower = 10
    ChargeBattery = 11
    DischargeBattery = 12
    Stopped = 255
