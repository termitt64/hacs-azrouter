# AZRouter Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

[![Community Forum][forum-shield]][forum]

_Home Assistant integration for the [A-Z Traders Router SMART][hacs-azrouter] — a smart EV charging router that manages connected chargers. Polls the router locally over its REST API._

**This integration sets up the following platforms.**

### Router entities

Platform | Entity | Description
-- | -- | --
`sensor` | Uptime | Router system uptime (reported in days)
`sensor` | Temperature | Router CPU/board temperature in °C
`sensor` | Active Device Max Power | Maximum power of the currently active device in W
`binary_sensor` | Cloud | Whether the router can reach the A-Z cloud (`connectivity`)
`binary_sensor` | HDO | State of the HDO (ripple control) signal
`switch` | Master Boost | Enable/disable global boost mode on the router

### Charger entities (per connected charger)

Platform | Entity | Description
-- | -- | --
`sensor` | Charging Power | Total charging power in W
`sensor` | WiFi Signal | Charger WiFi signal strength in dBm
`sensor` | Boost Source | Source of the active boost command
`switch` | Boost | Enable/disable boost mode on this charger

## Installation

### Option A — HACS (recommended)

1. Make sure [HACS](https://hacs.xyz) is installed in your Home Assistant instance.
1. In the HA UI go to **HACS** → **Integrations**, click the **⋮** menu in the top-right corner, and choose **Custom repositories**.
1. Add `https://github.com/termitt64/hacs-azrouter` as a repository of category **Integration** and click **Add**.
1. Search for **AZRouter Integration** in HACS and click **Download**.
1. Restart Home Assistant.

### Option B — Manual

1. Download the latest release archive from the [Releases](https://github.com/termitt64/hacs-azrouter/releases) page.
1. Unpack the archive and copy the `azrouter_integration` folder into the `custom_components` directory of your HA configuration (the same directory that contains `configuration.yaml`). Create `custom_components` if it does not exist yet.
1. Restart Home Assistant.

## Configuration

The integration is configured entirely through the Home Assistant UI — no `configuration.yaml` edits are needed.

1. In the HA UI go to **Settings** → **Devices & Services** → **Integrations**, click **+ Add Integration**, and search for **AZRouter Integration**.
2. Enter the following details:

   | Field | Description |
   | -- | -- |
   | **URL** | Base URL of the router (e.g. `http://192.168.1.1`) |
   | **Username** | Router admin username |
   | **Password** | Router admin password |

3. HA will verify the credentials by connecting to the router. If successful, the integration is ready.

> Only one instance of this integration can be configured at a time (`single_config_entry`).

Data is polled from the router once per hour.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[hacs-azrouter]: https://github.com/termitt64/hacs-azrouter
[commits-shield]: https://img.shields.io/github/commit-activity/y/termitt64/hacs-azrouter.svg?style=for-the-badge
[commits]: https://github.com/termitt64/hacs-azrouter/commits/main
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/termitt64/hacs-azrouter.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Martin%20Petera-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/termitt64/hacs-azrouter.svg?style=for-the-badge
[releases]: https://github.com/termitt64/hacs-azrouter/releases
