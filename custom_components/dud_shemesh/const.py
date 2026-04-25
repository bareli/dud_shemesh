"""Constants for Dud Shemesh."""
from __future__ import annotations

DOMAIN = "dud_shemesh"

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.data"

CONF_HEATER_ENTITY = "heater_entity"
CONF_TEMP_SENSOR = "temp_sensor"
CONF_TARGET_TEMP = "target_temp"
CONF_HEATER_WATTAGE = "heater_wattage_w"
CONF_MODE = "mode"
CONF_LEGIONELLA_ENABLED = "legionella_enabled"
CONF_LEGIONELLA_TEMP = "legionella_temp"
CONF_LEGIONELLA_DAYS = "legionella_days"

DEFAULT_TARGET_TEMP = 55
DEFAULT_HEATER_WATTAGE = 2400
DEFAULT_LEGIONELLA_TEMP = 60
DEFAULT_LEGIONELLA_DAYS = 7

MODE_AUTO = "auto"
MODE_SCHEDULE = "schedule"
MODE_OFF = "off"
DEFAULT_MODE = MODE_SCHEDULE

DAY_BITS = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32, 6: 64}

SIGNAL_STATE_CHANGED = f"{DOMAIN}_state_changed"

EVENT_HEAT_STARTED = f"{DOMAIN}_heat_started"
EVENT_HEAT_FINISHED = f"{DOMAIN}_heat_finished"
EVENT_TARGET_REACHED = f"{DOMAIN}_target_reached"

SERVICE_BOOST = "boost"
SERVICE_CANCEL_BOOST = "cancel_boost"
SERVICE_SET_MODE = "set_mode"
SERVICE_SET_TARGET = "set_target_temp"
SERVICE_ADD_SCHEDULE = "add_schedule"
SERVICE_UPDATE_SCHEDULE = "update_schedule"
SERVICE_REMOVE_SCHEDULE = "remove_schedule"
SERVICE_LEGIONELLA_NOW = "legionella_run_now"
SERVICE_LIST = "list_config"
