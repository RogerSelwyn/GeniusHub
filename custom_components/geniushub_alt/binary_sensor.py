"""Support for Genius Hub binary_sensor devices."""

from typing import override

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import GeniusHubConfigEntry
from .const import (
    GH_BINARY_SENSOR_STATE_ATTR,
    GH_DUAL_CHANNEL_RECEIVER,
    GH_ELECTRIC_SWITCH_TYPE,
    GH_RECEIVER_TYPE,
    GH_TYPE,
)
from .coordinator import GeniusCoordinator
from .entity import GeniusDevice


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GeniusHubConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Genius Hub binary sensor entities."""

    coordinator: GeniusCoordinator = entry.runtime_data

    entities = []
    for d in coordinator.client.device_objs:
        if d.data.get(GH_TYPE):
            if (
                GH_RECEIVER_TYPE in d.data[GH_TYPE]
                and d.data[GH_TYPE] != GH_DUAL_CHANNEL_RECEIVER
            ) or GH_ELECTRIC_SWITCH_TYPE in d.data[GH_TYPE]:
                entities.append(
                    GeniusBinarySensor(coordinator, d, GH_BINARY_SENSOR_STATE_ATTR)
                )
        elif d.data["state"].get(GH_BINARY_SENSOR_STATE_ATTR) is not None:
            entities.append(
                GeniusBinarySensor(coordinator, d, GH_BINARY_SENSOR_STATE_ATTR)
            )

    async_add_entities(entities)


class GeniusBinarySensor(GeniusDevice, BinarySensorEntity):
    """Representation of a Genius Hub binary_sensor."""

    def __init__(self, coordinator: GeniusCoordinator, device, state_attr) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, device)

        self._state_attr = state_attr

        if device.type:
            self._attr_name = f"{device.type} {device.id}"
        else:
            self._attr_name = f"Electic Switch {device.id}"

    @property
    @override
    def is_on(self) -> bool:
        """Return the status of the sensor."""
        return self._device.data["state"][self._state_attr]
