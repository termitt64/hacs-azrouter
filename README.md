# AZRouter Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

[![Community Forum][forum-shield]][forum]

_Integration to integrate with [hacs-azrouter][hacs-azrouter]._

**This integration will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from blueprint API.
`switch` | Switch something `True` or `False`.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `azrouter_integration`.
1. Download _all_ the files from the `custom_components/azrouter_integration/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "AZRouter Integration"

## Configuration

TODO: Configuration how to & link
Lorem ipsum ... tbd

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
