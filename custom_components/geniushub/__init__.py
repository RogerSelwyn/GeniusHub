"""Support for a Genius Hub system."""

from __future__ import annotations

import logging

import aiohttp
import homeassistant
from geniushubclient import GeniusHub
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import ATTR_MANUFACTURER, DOMAIN, IDENTIFIER_ZONE, PLATFORMS, SERIAL_NO
from .coordinator import GeniusCoordinator
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)


type GeniusHubConfigEntry = ConfigEntry[GeniusCoordinator]


async def async_setup(hass: homeassistant, config: ConfigType) -> bool:  # pylint: disable=unused-argument
    """Setup for Geniushub."""
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: GeniusHubConfigEntry) -> bool:
    """Create a Genius Hub system."""
    if CONF_TOKEN in entry.data and CONF_MAC in entry.data:
        entity_registry = er.async_get(hass)
        registry_entries = er.async_entries_for_config_entry(
            entity_registry, entry.entry_id
        )
        for reg_entry in registry_entries:
            if reg_entry.unique_id.startswith(entry.data[CONF_MAC]):
                entity_registry.async_update_entity(
                    reg_entry.entity_id,
                    new_unique_id=reg_entry.unique_id.replace(
                        entry.data[CONF_MAC], entry.entry_id
                    ),
                )

    session = async_get_clientsession(hass)
    if CONF_HOST in entry.data:
        api = "Local"
        client = GeniusHub(
            entry.data[CONF_HOST],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            session=session,
        )
    else:
        api = "Cloud"
        client = GeniusHub(entry.data[CONF_TOKEN], session=session)

    unique_id = entry.unique_id or entry.entry_id

    coordinator = entry.runtime_data = GeniusCoordinator(hass, client, entry, unique_id)

    try:
        await coordinator.async_config_entry_first_refresh()
    except aiohttp.ClientResponseError as err:
        _LOGGER.error("Setup failed, check your configuration, %s", err)
        return False
    coordinator.make_debug_log_entries()

    _create_hub_devices(hass, entry, unique_id, api, coordinator.client.zone_by_id[0])

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: GeniusHubConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _create_hub_devices(
    hass: HomeAssistant, entry: GeniusHubConfigEntry, hub_uid: str, api: str, zone0: any
):
    device_registry = dr.async_get(hass)
    hub_identifiers = (DOMAIN, hub_uid)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={hub_identifiers},
        name=hub_uid,
        manufacturer=ATTR_MANUFACTURER,
        model=f"{api} API",
    )
    if zone0.id == 0:
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, IDENTIFIER_ZONE.format(zone0.id))},
            via_device=hub_identifiers,
            name=zone0.name,
            manufacturer=ATTR_MANUFACTURER,
            model=zone0.name,
            serial_number=SERIAL_NO.format("Zone", zone0.id),
        )
