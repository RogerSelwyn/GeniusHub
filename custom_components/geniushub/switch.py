"""Support for Genius Hub switch/outlet devices."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import GeniusHubConfigEntry
from .const import (
    ATTR_DURATION,
    ATTR_MANUFACTURER,
    DOMAIN,
    GH_ON_OFF_ZONE,
    IDENTIFIER_ZONE,
    SET_SWITCH_OVERRIDE_SCHEMA,
    SVC_SET_SWITCH_OVERRIDE,
)
from .entity import GeniusZone


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: GeniusHubConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Genius Hub switch entities."""

    coordinator = entry.runtime_data

    async_add_entities(
        GeniusSwitch(coordinator, z)
        for z in coordinator.client.zone_objs
        if z.data.get("type") == GH_ON_OFF_ZONE
    )

    # Register custom services
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SVC_SET_SWITCH_OVERRIDE,
        SET_SWITCH_OVERRIDE_SCHEMA,
        "async_turn_on",
    )


class GeniusSwitch(GeniusZone, SwitchEntity):
    """Representation of a Genius Hub switch."""

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return SwitchDeviceClass.OUTLET

    @property
    def is_on(self) -> bool:
        """Return the current state of the on/off zone.

        The zone is considered 'on' if the mode is either 'override' or 'timer'.
        """
        return (
            self._zone.data["mode"] in ["override", "timer"]
            and self._zone.data["setpoint"]
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Entity device info"""

        return DeviceInfo(
            identifiers={(DOMAIN, IDENTIFIER_ZONE.format(self._zone.id))},
            name=self._zone.name,
            via_device=(DOMAIN, self._hub.hub_uid),
            manufacturer=ATTR_MANUFACTURER,
            model=f"{self._zone.data['type'].title()} Zone",
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Send the zone to Timer mode.

        The zone is deemed 'off' in this mode, although the plugs may actually be on.
        """
        await self._zone.set_mode("timer")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Set the zone to override/on ({'setpoint': true}) for x seconds."""
        await self._zone.set_override(1, kwargs.get(ATTR_DURATION, 3600))

    def turn_off(self, **kwargs: Any) -> None:
        """Not implemented."""
        raise NotImplementedError("Service not implemented for this entity")
