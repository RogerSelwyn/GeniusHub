"""Constants for Genius Hub."""

from datetime import timedelta

import voluptuous as vol
from homeassistant.components.climate import (
    PRESET_ACTIVITY,
    PRESET_BOOST,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_USERNAME,
    STATE_OFF,
    Platform,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import VolDictType

DOMAIN = "geniushub"

SCAN_INTERVAL = timedelta(seconds=60)

SENSOR_PREFIX = "Genius"

PLATFORMS = (
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
)

ATTR_MANUFACTURER = "Genius Hub"
IDENTIFIER_ZONE = "zone-{0}"
IDENTIFIER_DEVICE = "device-{0}"

### __init__ Constants Start ###
SCAN_INTERVAL = timedelta(seconds=60)

MAC_ADDRESS_REGEXP = r"^([0-9A-F]{2}:){5}([0-9A-F]{2})$"

ATTR_ZONE_MODE = "mode"
ATTR_DURATION = "duration"

SVC_SET_ZONE_MODE = "set_zone_mode"
SVC_SET_ZONE_OVERRIDE = "set_zone_override"

SET_ZONE_MODE_SCHEMA = {
    vol.Required(ATTR_ZONE_MODE): vol.In(["off", "timer", "footprint"]),
}

SET_ZONE_OVERRIDE_SCHEMA = {
    vol.Required(ATTR_TEMPERATURE): vol.All(
        vol.Coerce(float), vol.Range(min=4, max=28)
    ),
    vol.Optional(ATTR_DURATION): vol.All(
        cv.time_period,
        vol.Range(min=timedelta(minutes=5), max=timedelta(days=1)),
    ),
}
### __init__ Constants End ###

### Entity Constants Start ###
# temperature is repeated here, as it gives access to high-precision temps
GH_ZONE_ATTRS = ["mode", "temperature", "type", "occupied", "override"]
GH_DEVICE_ATTRS = {
    "luminance": "luminance",
    "measuredTemperature": "measured_temperature",
    "occupancyTrigger": "occupancy_trigger",
    "setback": "setback",
    "setTemperature": "set_temperature",
    "wakeupInterval": "wakeup_interval",
}
### Entity Constants Endt ###

### Switch Constants Start ###
GH_ON_OFF_ZONE = "on / off"

SVC_SET_SWITCH_OVERRIDE = "set_switch_override"

SET_SWITCH_OVERRIDE_SCHEMA: VolDictType = {
    vol.Optional(ATTR_DURATION): vol.All(
        cv.time_period,
        vol.Range(min=timedelta(minutes=5), max=timedelta(days=1)),
    ),
}
### Switch Constants End ###

### Climate Constants Start ###
# GeniusHub Zones support: Off, Timer, Override/Boost, Footprint & Linked modes
HA_HVAC_TO_GH = {HVACMode.OFF: "off", HVACMode.HEAT: "timer"}
GH_HVAC_TO_HA = {v: k for k, v in HA_HVAC_TO_GH.items()}

HA_PRESET_TO_GH = {PRESET_ACTIVITY: "footprint", PRESET_BOOST: "override"}
GH_PRESET_TO_HA = {v: k for k, v in HA_PRESET_TO_GH.items()}

GH_ZONES = ["radiator", "wet underfloor"]
### Climate Constants End ###

### Binary Sensor Constants Start ###
GH_BINARY_SENSOR_STATE_ATTR = "outputOnOff"
GH_RECEIVER_TYPE = "Receiver"
### Binary Sensor Constants End ###


### Config_flow Constants Start ###
CLOUD_API_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
    }
)


LOCAL_API_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)
### Config_flow Constants End ###

### Sensor Constants Start ###
GH_STATE_ATTR = "batteryLevel"

GH_LEVEL_MAPPING = {
    "error": "Errors",
    "warning": "Warnings",
    "information": "Information",
}
### Sensor Constants End ###

### Water Heater Constants Start ###
STATE_AUTO = "auto"
STATE_MANUAL = "manual"

# Genius Hub HW zones support only Off, Override/Boost & Timer modes
HA_OPMODE_TO_GH = {STATE_OFF: "off", STATE_AUTO: "timer", STATE_MANUAL: "override"}
GH_STATE_TO_HA = {
    "off": STATE_OFF,
    "timer": STATE_AUTO,
    "footprint": None,
    "away": None,
    "override": STATE_MANUAL,
    "early": None,
    "test": None,
    "linked": None,
    "other": None,
}

GH_HEATERS = ["hot water temperature"]
### Water Heater Constants End ###
