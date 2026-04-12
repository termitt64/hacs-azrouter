"""Constants for azrouter_integration."""

from logging import Logger, getLogger
from typing import Final

from .enums import InverterEmsMode

LOGGER: Logger = getLogger(__package__)

DOMAIN = "azrouter_integration"
ATTRIBUTION = "Data provided by AZ Router"

SETTINGS_MIN_TARGET_POWER: Final = -10_000  # W
SETTINGS_MAX_TARGET_POWER: Final = 10_000  # W
RECOMMENDED_MIN_TARGET_POWER: Final = 100  # W
RECOMMENDED_MAX_TARGET_POWER: Final = 4_000  # W

# Maps an InverterEmsMode to the label of its configurable power parameter.
# Modes not present here have no associated parameter.
INVERTER_EMS_MODE_PARAMETER_TITLE: Final[dict[InverterEmsMode, str]] = {
    InverterEmsMode.ChargePv: "Max charge power",
    InverterEmsMode.DischargePv: "Max discharge power",
    InverterEmsMode.ImportAc: "Max import power",
    InverterEmsMode.ExportAc: "Max export power",
    InverterEmsMode.BuyPower: "Max buy power",
    InverterEmsMode.SellPower: "Max sell power",
    InverterEmsMode.ChargeBattery: "Max charge power",
    InverterEmsMode.DischargeBattery: "Max discharge power",
}
