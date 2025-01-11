"""DataUpdateCoordinator for azrouter_integration."""

from __future__ import annotations

import json
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AZRouterIntegrationApiClientAuthenticationError,
    AZRouterIntegrationApiClientError,
)
from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import AZRouterIntegrationConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class AZRouterDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: AZRouterIntegrationConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            client = self.config_entry.runtime_data.client
            data = {
                "cloud/status": await client.async_get_cloud_status(),
                "status": await client.async_get_status(),
                "power": await client.async_get_power(),
                "devices": await client.async_get_devices(),
            }
            LOGGER.debug("Got AZRouter data:\n%s", json.dumps(data))
            return data

        except AZRouterIntegrationApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except AZRouterIntegrationApiClientError as exception:
            raise UpdateFailed(exception) from exception
