"""Custom types for azrouter_integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import AZRouterIntegrationApiClient
    from .coordinator import BlueprintDataUpdateCoordinator


type AZRouterIntegrationConfigEntry = ConfigEntry[AZRouterIntegrationData]


@dataclass
class AZRouterIntegrationData:
    """Data for the Blueprint integration."""

    client: AZRouterIntegrationApiClient
    coordinator: BlueprintDataUpdateCoordinator
    integration: Integration
