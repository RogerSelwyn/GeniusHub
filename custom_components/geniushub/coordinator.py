"""Coordinator for Genius Hub System"""

import logging

import aiohttp
from geniushubclient import GeniusHub
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GeniusBroker:
    """Container for geniushub client and data."""

    def __init__(self, hass: HomeAssistant, client: GeniusHub, hub_uid: str) -> None:
        """Initialize the geniushub client."""
        self.hass = hass
        self.client = client
        self.hub_uid = hub_uid
        self._connect_error = False

    async def async_update(self, now, **kwargs) -> None:  # pylint: disable=unused-argument
        """Update the geniushub client's data."""
        try:
            await self.client.update()
            if self._connect_error:
                self._connect_error = False
                _LOGGER.warning("Connection to geniushub re-established")
        except (
            aiohttp.ClientResponseError,
            aiohttp.client_exceptions.ClientConnectorError,
        ) as err:
            if not self._connect_error:
                self._connect_error = True
                _LOGGER.error(
                    "Connection to geniushub failed (unable to update), message is: %s",
                    err,
                )
            return
        self.make_debug_log_entries()

        async_dispatcher_send(self.hass, DOMAIN)

    def make_debug_log_entries(self) -> None:
        """Make any useful debug log entries."""
        _LOGGER.debug(
            "Raw JSON: \n\nclient._zones = %s \n\nclient._devices = %s",
            self.client._zones,  # noqa: SLF001 # pylint: disable=protected-access
            self.client._devices,  # noqa: SLF001 # pylint: disable=protected-access
        )
