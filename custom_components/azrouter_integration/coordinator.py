"""DataUpdateCoordinator for azrouter_integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import (
    AZRouterApiClientProtocol,
    AZRouterIntegrationApiClientAuthenticationError,
    AZRouterIntegrationApiClientError,
)
from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.core import HomeAssistant

    from .data import AZRouterIntegrationConfigEntry


@dataclass
class _ResourceSchedule:
    """Tracks the fetch function, refresh interval, and cached state for a resource."""

    fetch: Callable[[], Awaitable[Any]]
    interval: timedelta
    cached: Any = field(default=None, init=False)
    last_fetched: datetime | None = field(default=None, init=False)

    def is_due(self, now: datetime) -> bool:
        """Return True if never fetched or if the refresh interval has elapsed."""
        return self.last_fetched is None or now - self.last_fetched >= self.interval

    async def refresh(self, now: datetime) -> None:
        """Fetch and cache a fresh value, recording the fetch time."""
        self.cached = await self.fetch()
        self.last_fetched = now


def _build_schedules(
    client: AZRouterApiClientProtocol,
) -> dict[str, _ResourceSchedule]:
    """Return a resource-key → schedule mapping for the given API client."""
    return {
        "cloud/status": _ResourceSchedule(
            fetch=client.async_get_cloud_status,
            interval=timedelta(seconds=60),
        ),
        "status": _ResourceSchedule(
            fetch=client.async_get_status,
            interval=timedelta(seconds=1),
        ),
        "power": _ResourceSchedule(
            fetch=client.async_get_power,
            interval=timedelta(seconds=1),
        ),
        "devices": _ResourceSchedule(
            fetch=client.async_get_devices,
            interval=timedelta(seconds=1),
        ),
        "settings": _ResourceSchedule(
            fetch=client.async_get_settings,
            interval=timedelta(seconds=60),
        ),
    }


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class AZRouterDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: AZRouterIntegrationConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: AZRouterApiClientProtocol,
    ) -> None:
        """Initialize the coordinator with a 1-second polling interval."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=1),
        )
        self._schedules = _build_schedules(client)

    async def _async_update_data(self) -> Any:
        """Fetch each resource according to its individual refresh interval."""
        try:
            now = dt_util.utcnow()
            for schedule in self._schedules.values():
                if schedule.is_due(now):
                    await schedule.refresh(now)

            data = {key: s.cached for key, s in self._schedules.items()}
        except AZRouterIntegrationApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except AZRouterIntegrationApiClientError as exception:
            raise UpdateFailed(exception) from exception
        else:
            return data
