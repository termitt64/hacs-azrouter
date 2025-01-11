"""Sample API Client."""

from __future__ import annotations

import json
import socket
from typing import Any, Final
from urllib.parse import urljoin

import aiohttp
import async_timeout
from .const import LOGGER

API_URL: Final = "/api/v1/"


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
    LOGGER.debug("Got response: %s", response.text)
    response.raise_for_status()


class AZRouterIntegrationApiClient:
    """Sample API Client."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._api_url = urljoin(base_url, API_URL)
        self._session = session
        self._token = None

    async def async_get_status(self) -> Any:
        """Get AZRouter status."""
        return await self._get_resource("status")

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _get_resource(self, resource: str) -> Any:
        """Access resource from REST api, authenticates if not yet authenticated"""
        if self._token is None:
            await self._login()

        response = await self._api_wrapper(
            method="get",
            url=self._get_resource_url(resource),
        )
        return response.json()

    async def _login(self) -> Any:
        """Log in into AZRouter"""
        response = await self._api_wrapper(
            method="post",
            data={"data": {"username": self._username, "password": self._password}},
            url=self._get_resource_url("login"),
        )
        self._token = response.text()

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                LOGGER.debug("Request %s [%s]: %s", method, headers, data)
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return response

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise AZRouterIntegrationApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise AZRouterIntegrationApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise AZRouterIntegrationApiClientError(
                msg,
            ) from exception

    def _get_resource_url(self, resource: str) -> str:
        return urljoin(self._api_url, resource)
