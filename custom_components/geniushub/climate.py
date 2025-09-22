"""Support for Genius Hub climate devices."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.climate import (
    PRESET_ACTIVITY,
    PRESET_BOOST,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import GeniusHubConfigEntry
from .const import (
    GH_HVAC_TO_HA,
    GH_PRESET_TO_HA,
    GH_ZONES,
    HA_HVAC_TO_GH,
    HA_PRESET_TO_GH,
    SET_ZONE_MODE_SCHEMA,
    SET_ZONE_OVERRIDE_SCHEMA,
    SVC_SET_ZONE_MODE,
    SVC_SET_ZONE_OVERRIDE,
)
from .entity import GeniusHeatingZone


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: GeniusHubConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Genius Hub climate entities."""

    coordinator = entry.runtime_data

    await _async_register_services()
    async_add_entities(
        GeniusClimateZone(coordinator, z)
        for z in coordinator.client.zone_objs
        if z.data.get("type") in GH_ZONES
    )


async def _async_register_services():
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SVC_SET_ZONE_MODE,
        SET_ZONE_MODE_SCHEMA,
        f"async_{SVC_SET_ZONE_MODE}",
    )
    platform.async_register_entity_service(
        SVC_SET_ZONE_OVERRIDE,
        SET_ZONE_OVERRIDE_SCHEMA,
        f"async_{SVC_SET_ZONE_OVERRIDE}",
    )


class GeniusClimateZone(GeniusHeatingZone, ClimateEntity):
    """Representation of a Genius Hub climate device."""

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )

    def __init__(self, coordinator, zone) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator, zone)

        self._max_temp = 28.0
        self._min_temp = 4.0

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend UI."""
        return "mdi:radiator"

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode."""
        return GH_HVAC_TO_HA.get(self._zone.data["mode"], HVACMode.AUTO)

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available hvac operation modes."""
        return list(HA_HVAC_TO_GH)

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation if supported."""
        if "_state" in self._zone.data:  # only for v3 API
            if self._zone.data["mode"] == "off":
                return HVACAction.OFF
            if self._zone.data["output"] == 1:
                return HVACAction.HEATING
            # if not self._zone.data["_state"].get("bIsActive"):
            return HVACAction.IDLE

        return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode, e.g., home, away, temp."""
        return GH_PRESET_TO_HA.get(self._zone.data["mode"])

    @property
    def preset_modes(self) -> list[str] | None:
        """Return a list of available preset modes."""
        if "occupied" in self._zone.data:  # if has a movement sensor
            return [PRESET_ACTIVITY, PRESET_BOOST]
        return [PRESET_BOOST]

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set a new hvac mode."""
        await self._zone.set_mode(HA_HVAC_TO_GH.get(hvac_mode))

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set a new preset mode."""
        await self._zone.set_mode(HA_PRESET_TO_GH.get(preset_mode, "timer"))

    async def async_set_zone_mode(self, mode):
        """Set a new zone mode."""
        if mode == "footprint" and not self._zone._has_pir:  # noqa: SLF001 # pylint: disable=protected-access
            raise ServiceValidationError(
                f"'{self.entity_id}' cannot support footprint mode (it has no PIR)"
            )

        await self._zone.set_mode(mode)

    async def async_set_zone_override(self, temperature, duration=timedelta(hours=1)):
        """Set a new zone override."""
        await self._zone.set_override(temperature, int(duration.total_seconds()))

    def set_fan_mode(self, _) -> None:
        """Not implemented."""
        raise NotImplementedError("Service not implemented for this entity")
