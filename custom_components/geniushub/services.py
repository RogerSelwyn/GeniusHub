"""Setup services for geniushub."""

from __future__ import annotations

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import service

from .const import (
    DOMAIN,
    SET_SWITCH_OVERRIDE_SCHEMA,
    SET_ZONE_MODE_SCHEMA,
    SET_ZONE_OVERRIDE_SCHEMA,
    SVC_SET_SWITCH_OVERRIDE,
    SVC_SET_ZONE_MODE,
    SVC_SET_ZONE_OVERRIDE,
)


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register services."""

    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SVC_SET_ZONE_MODE,
        entity_domain=CLIMATE_DOMAIN,
        schema=SET_ZONE_MODE_SCHEMA,  # pyright: ignore[reportArgumentType]
        func=f"async_{SVC_SET_ZONE_MODE}",
    )
    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SVC_SET_ZONE_OVERRIDE,
        entity_domain=CLIMATE_DOMAIN,
        schema=SET_ZONE_OVERRIDE_SCHEMA,
        func=f"async_{SVC_SET_ZONE_OVERRIDE}",
    )

    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SVC_SET_SWITCH_OVERRIDE,
        entity_domain=SWITCH_DOMAIN,
        schema=SET_SWITCH_OVERRIDE_SCHEMA,
        func="async_turn_on",
    )
