"""Base entity for Geniushub."""

from datetime import datetime
from typing import Any

from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import DOMAIN
from .const import (
    ATTR_DURATION,
    ATTR_MANUFACTURER,
    GH_DEVICE_ATTRS,
    GH_ZONE_ATTRS,
    IDENTIFIER_DEVICE,
    IDENTIFIER_ZONE,
)


class GeniusEntity(CoordinatorEntity):
    """Base for all Genius Hub entities."""

    _attr_should_poll = False

    def __init__(self, coordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._unique_id: str | None = None

    def _handle_coordinator_update(self) -> None:
        """Process any signals."""
        self.async_schedule_update_ha_state(force_refresh=True)

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        return self._unique_id


class GeniusDevice(GeniusEntity):
    """Base for all Genius Hub devices."""

    def __init__(self, coordinator, device) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)

        self._device = device
        self._unique_id = f"{coordinator.hub_uid}_device_{device.id}"
        self._last_comms: datetime | None = None
        self._state_attr = None
        self._hub = coordinator

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the device state attributes."""
        attrs = {"assigned_zone": self._device.data["assignedZones"][0]["name"]}
        if self._last_comms:
            attrs["last_comms"] = self._last_comms.isoformat()

        state = dict(self._device.data["state"])
        if "_state" in self._device.data:  # only via v3 API
            state |= self._device.data["_state"]

        attrs["state"] = {
            GH_DEVICE_ATTRS[k]: v for k, v in state.items() if k in GH_DEVICE_ATTRS
        }

        return attrs

    @property
    def device_info(self) -> DeviceInfo:
        """Entity device info"""

        if self._device.assigned_zone:
            via_device = IDENTIFIER_ZONE.format(self._device.assigned_zone.id)
        else:
            via_device = self._hub.hub_uid

        if self._device.type:
            name = f"{self._device.type.title()} {self._device.id}"
            model = self._device.type
        else:
            name = f"Electric Switch {self._device.id}"
            model = "Electric Switch"

        return DeviceInfo(
            identifiers={(DOMAIN, IDENTIFIER_DEVICE.format(self._device.id))},
            via_device=(DOMAIN, via_device),
            name=name,
            manufacturer=ATTR_MANUFACTURER,
            model=model,
        )

    async def async_update(self) -> None:
        """Update an entity's state data."""
        if (
            "_state" in self._device.data
            and self._device.data["_state"]["lastComms"] is not None
        ):  # only via v3 API
            self._last_comms = dt_util.utc_from_timestamp(
                self._device.data["_state"]["lastComms"]
            )


class GeniusZone(GeniusEntity):
    """Base for all Genius Hub zones."""

    def __init__(self, coordinator, zone) -> None:
        """Initialize the Zone."""
        super().__init__(coordinator)

        self._zone = zone
        self._unique_id = f"{coordinator.hub_uid}_zone_{zone.id}"
        self._hub = coordinator

    @property
    def name(self) -> str:
        """Return the name of the climate device."""
        return self._zone.name

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the device state attributes."""
        status = {k: v for k, v in self._zone.data.items() if k in GH_ZONE_ATTRS}
        return {"status": status}


class GeniusHeatingZone(GeniusZone):
    """Base for Genius Heating Zones."""

    _max_temp: float
    _min_temp: float

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._zone.data.get("temperature")

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self._zone.data["setpoint"]

    @property
    def min_temp(self) -> float:
        """Return max valid temperature that can be set."""
        return self._min_temp

    @property
    def max_temp(self) -> float:
        """Return max valid temperature that can be set."""
        return self._max_temp

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    async def async_set_temperature(self, **kwargs) -> None:
        """Set a new target temperature for this zone."""
        await self._zone.set_override(
            kwargs[ATTR_TEMPERATURE], kwargs.get(ATTR_DURATION, 3600)
        )
