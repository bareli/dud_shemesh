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

CONF_WEATHER_ENTITY = "weather_entity"
CONF_WEATHER_SKIP_STATES = "weather_skip_states"
CONF_AUTO_COMFORT_WINDOWS = "auto_comfort_windows"
CONF_AUTO_PRE_HEAT_MARGIN_MIN = "auto_pre_heat_margin_min"
CONF_FAIL_DETECTION_ENABLED = "fail_detection_enabled"
CONF_FAIL_DETECTION_MINUTES = "fail_detection_minutes"
CONF_FAIL_DETECTION_RISE = "fail_detection_rise"
CONF_SOLAR_TRACK_MINUTES = "solar_track_minutes"
CONF_SOLAR_RISE_THRESHOLD = "solar_rise_threshold"

DEFAULT_WEATHER_SKIP_STATES = "sunny,clear-night"
DEFAULT_AUTO_PRE_HEAT_MARGIN_MIN = 5
DEFAULT_FAIL_DETECTION_MINUTES = 8
DEFAULT_FAIL_DETECTION_RISE = 1.0
DEFAULT_SOLAR_TRACK_MINUTES = 30
DEFAULT_SOLAR_RISE_THRESHOLD = 1.0

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
EVENT_HEAT_NOT_RISING = f"{DOMAIN}_heat_not_rising"
EVENT_BOOST_EXTENDED = f"{DOMAIN}_boost_extended"
EVENT_AUTO_PREHEAT_PLANNED = f"{DOMAIN}_auto_preheat_planned"

SERVICE_BOOST = "boost"
SERVICE_CANCEL_BOOST = "cancel_boost"
SERVICE_SET_MODE = "set_mode"
SERVICE_SET_TARGET = "set_target_temp"
SERVICE_ADD_SCHEDULE = "add_schedule"
SERVICE_UPDATE_SCHEDULE = "update_schedule"
SERVICE_REMOVE_SCHEDULE = "remove_schedule"
SERVICE_LEGIONELLA_NOW = "legionella_run_now"
SERVICE_LIST = "list_config"
