"""Support for Genius Hub binary_sensor devices."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import GeniusHubConfigEntry
from .const import (
    GH_BINARY_SENSOR_STATE_ATTR,
    GH_DUAL_CHANNEL_RECEIVER,
    # GH_ELECTRIC_SWITCH_TYPE,
    GH_RECEIVER_TYPE,
)
from .entity import GeniusDevice


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: GeniusHubConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Genius Hub binary sensor entities."""

    coordinator = entry.runtime_data

    async_add_entities(
        GeniusBinarySensor(coordinator, d, GH_BINARY_SENSOR_STATE_ATTR)
        for d in coordinator.client.device_objs
        # if (
        #     GH_RECEIVER_TYPE in d.data["type"]
        #     and d.data["type"] != GH_DUAL_CHANNEL_RECEIVER
        # )
        # or GH_ELECTRIC_SWITCH_TYPE in d.data["type"]
        if (
            d.data.get("type")
            and GH_RECEIVER_TYPE in d.data.get("type")
            and d.data["type"] != GH_DUAL_CHANNEL_RECEIVER
        )
        or (
            not d.data.get("type")
            and GH_BINARY_SENSOR_STATE_ATTR in d.data.get("state")
        )
    )


class GeniusBinarySensor(GeniusDevice, BinarySensorEntity):
    """Representation of a Genius Hub binary_sensor."""

    def __init__(self, coordinator, device, state_attr) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, device)

        self._state_attr = state_attr

        # self._attr_name = f"{device.type} {device.id}"
        if device.type:
            self._attr_name = f"{device.type} {device.id}"
        else:
            self._attr_name = f"Electric Switch {device.id}"

    @property
    def is_on(self) -> bool:
        """Return the status of the sensor."""
        return self._device.data["state"][self._state_attr]
