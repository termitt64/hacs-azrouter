"""Enumerations for azrouter_integration."""

from enum import Enum


class ChargeStatus(Enum):
    """Charge status codes reported by the AZ Charger."""

    Disconnected = 0
    Waiting = 1
    Charging = 2
    Overheated = 3
    Error = 4
    Unavailable = 5
