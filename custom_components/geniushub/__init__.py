"""Support for a Genius Hub system."""

from __future__ import annotations

import logging

import aiohttp
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

from .const import (
    DOMAIN,
    PLATFORMS,
)
from .coordinator import GeniusCoordinator

_LOGGER = logging.getLogger(__name__)


type GeniusHubConfigEntry = ConfigEntry[GeniusCoordinator]


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

    # setup_service_functions(hass)

    _create_hub_devices(hass, entry, unique_id, api, coordinator.client.zone_by_id[0])

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


# @callback
# def setup_service_functions(hass: HomeAssistant):
#     """Set up the service functions."""

#     @verify_domain_control(hass, DOMAIN)
#     async def set_zone_mode(call: ServiceCall) -> None:
#         """Set the system mode."""
#         entity_id = call.data[ATTR_ENTITY_ID]

#         registry = er.async_get(hass)
#         registry_entry = registry.async_get(entity_id)

#         if registry_entry is None or registry_entry.platform != DOMAIN:
#             raise ValueError(f"'{entity_id}' is not a known {DOMAIN} entity")

#         if registry_entry.domain != "climate":
#             raise ValueError(f"'{entity_id}' is not an {DOMAIN} zone")

#         payload = {
#             "unique_id": registry_entry.unique_id,
#             "service": call.service,
#             "data": call.data,
#         }

#         async_dispatcher_send(hass, DOMAIN, payload)

#     hass.services.async_register(
#         DOMAIN, SVC_SET_ZONE_MODE, set_zone_mode, schema=SET_ZONE_MODE_SCHEMA
#     )
#     hass.services.async_register(
#         DOMAIN, SVC_SET_ZONE_OVERRIDE, set_zone_mode, schema=SET_ZONE_OVERRIDE_SCHEMA
#     )


def _create_hub_devices(
    hass: HomeAssistant, entry: GeniusHubConfigEntry, hub_uid: str, api: str, zone0: any
):
    device_registry = dr.async_get(hass)
    hub_identifiers = (DOMAIN, hub_uid)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={hub_identifiers},
        name=hub_uid,
        manufacturer="Genius Hub",
        model=f"{api} API",
    )
    if zone0.id == 0:
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, f"zone-{zone0.id}")},
            via_device=hub_identifiers,
            name=zone0.name,
            manufacturer="Genius Hub",
            model=zone0.name,
        )
