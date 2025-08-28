"""Coordinator for Genius Hub System"""

import logging

import aiohttp
from geniushubclient import GeniusHub
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class GeniusCoordinator(DataUpdateCoordinator):
    """Container for geniushub client and data."""

    def __init__(
        self, hass: HomeAssistant, client: GeniusHub, entry: ConfigEntry, hub_uid: str
    ) -> None:
        """Initialize the geniushub client."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.hass = hass
        self.client = client
        self.hub_uid = hub_uid
        self._connect_error = False

    async def _async_update_data(self) -> None:
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

        return self.client

    def make_debug_log_entries(self) -> None:
        """Make any useful debug log entries."""
        _LOGGER.debug(
            "Raw JSON: \n\nclient._zones = %s \n\nclient._devices = %s",
            self.client._zones,  # noqa: SLF001 # pylint: disable=protected-access
            self.client._devices,  # noqa: SLF001 # pylint: disable=protected-access
        )
