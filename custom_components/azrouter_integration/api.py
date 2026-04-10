"""AZ Router API Client."""

from __future__ import annotations

import socket
from typing import Any, Final, Protocol, runtime_checkable
from urllib.parse import urljoin

import aiohttp
import async_timeout

API_URL: Final = "/api/v1/"


@runtime_checkable
class AZRouterApiClientProtocol(Protocol):
    """Protocol defining the AZ Router API client interface."""

    async def async_get_cloud_status(self) -> Any:
        """Get cloud status."""

    async def async_get_status(self) -> Any:
        """Get system status."""

    async def async_get_power(self) -> Any:
        """Get power data."""

    async def async_get_devices(self) -> Any:
        """Get devices."""

    async def async_post(self, resource: str, data: dict) -> Any:
        """Post data to a resource."""


class AZRouterIntegrationApiClientError(Exception):
    """Exception to indicate a general API error."""


class AZRouterIntegrationApiClientCommunicationError(
    AZRouterIntegrationApiClientError,
):
    """Exception to indicate a communication error."""


class AZRouterIntegrationApiClientAuthenticationError(
    AZRouterIntegrationApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise AZRouterIntegrationApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class AZRouterIntegrationApiClient:
    """HTTP client for the AZ Router REST API."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize with base URL, credentials, and an aiohttp session."""
        self._username = username
        self._password = password
        self._api_url = urljoin(base_url, API_URL)
        self._session = session
        self._token = None

    async def async_get_cloud_status(self) -> Any:
        """Get AZRouter resource: Cloud Status."""
        return await self._get_resource("cloud/status")

    async def async_get_status(self) -> Any:
        """Get AZRouter resource: Status."""
        return await self._get_resource("status")

    async def async_get_power(self) -> Any:
        """Get AZRouter resource: Power."""
        return await self._get_resource("power")

    async def async_get_devices(self) -> Any:
        """Get AZRouter resource: Devices."""
        return await self._get_resource("devices")

    async def async_get_address(self) -> Any:
        """Get AZRouter resource: Address."""
        return await self._get_resource("address")

    async def async_get_settings(self) -> Any:
        """Get AZRouter resource: Settings."""
        return await self._get_resource("settings")

    async def async_post(self, resource: str, data: dict) -> Any:
        """Post data to a resource."""
        return await self._post_resource(resource, data)

    async def _get_resource(self, resource: str) -> Any:
        """Access resource from REST api, authenticates if not yet authenticated."""
        if self._token is None:
            await self._login()

        response = await self._api_wrapper(
            method="get",
            url=self._get_resource_url(resource),
        )
        return await response.json()

    async def _post_resource(self, resource: str, data: dict) -> Any:
        """Post data to a resource, authenticating first if needed."""
        if self._token is None:
            await self._login()

        response = await self._api_wrapper(
            method="post",
            url=self._get_resource_url(resource),
            data=data,
            headers={"Cookie": f"token={self._token}"},
        )
        return await response.text()

    async def _login(self) -> Any:
        """Log in into AZRouter."""
        response = await self._api_wrapper(
            method="post",
            data={"data": {"username": self._username, "password": self._password}},
            url=self._get_resource_url("login"),
        )
        self._token = await response.text()

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Execute an HTTP request, raising typed exceptions on error."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return response

        except TimeoutError as exception:
            msg = f"Timeout error fetching {method.upper()} {url} - {exception}"
            raise AZRouterIntegrationApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching {method.upper()} {url} - {exception}"
            raise AZRouterIntegrationApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Unexpected error fetching {method.upper()} {url} - {exception}"
            raise AZRouterIntegrationApiClientError(
                msg,
            ) from exception

    def _get_resource_url(self, resource: str) -> str:
        """Build the full URL for a given API resource path."""
        return urljoin(self._api_url, resource)
