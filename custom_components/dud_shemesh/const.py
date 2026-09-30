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

DEFAULT_WEATHER_SKIP_STATES = "sunny"
LEGACY_WEATHER_SKIP_STATES = "sunny,clear-night"
DEFAULT_AUTO_PRE_HEAT_MARGIN_MIN = 5
DEFAULT_FAIL_DETECTION_MINUTES = 8
DEFAULT_FAIL_DETECTION_RISE = 1.0
DEFAULT_SOLAR_TRACK_MINUTES = 30
DEFAULT_SOLAR_RISE_THRESHOLD = 1.0

CONF_BOOST_BUTTONS = "boost_buttons"
DEFAULT_BOOST_BUTTONS = "30,60,120"

CONF_TARIFF_ILS_PER_KWH = "tariff_ils_per_kwh"
DEFAULT_TARIFF_ILS_PER_KWH = 0.62

CONF_NOTIFY_TARGETS = "notify_targets"
CONF_NOTIFY_EVENTS = "notify_events"

CONF_VACATION_UNTIL = "vacation_until"
CONF_VACATION_HOLD_TEMP = "vacation_hold_temp"
DEFAULT_VACATION_HOLD_TEMP = 30

CONF_CALENDAR_ENTITY = "calendar_entity"
CONF_CALENDAR_LOOKAHEAD_MIN = "calendar_lookahead_min"
CONF_CALENDAR_KEYWORDS = "calendar_keywords"
DEFAULT_CALENDAR_LOOKAHEAD_MIN = 10
DEFAULT_CALENDAR_KEYWORDS = "dud,water,חם,מים,דוד"

# Safety (v0.5)
CONF_MANUAL_ON_MAX_MIN = "manual_on_max_min"
CONF_MAX_RUN_MIN = "max_run_min"
CONF_MAX_TANK_TEMP = "max_tank_temp"
CONF_SENSOR_STALE_MIN = "sensor_stale_min"
DEFAULT_MANUAL_ON_MAX_MIN = 60   # 0 = don't adopt manual turn-ons
DEFAULT_MAX_RUN_MIN = 180
DEFAULT_MAX_TANK_TEMP = 75
DEFAULT_SENSOR_STALE_MIN = 120   # 0 = never treat the sensor as stale

# Tank model (v0.5) for the showers-available estimate
CONF_TANK_VOLUME_L = "tank_volume_l"
DEFAULT_TANK_VOLUME_L = 0        # 0 = unknown, estimate hidden
COLD_WATER_TEMP = 20.0
SHOWER_TEMP = 40.0
SHOWER_LITRES = 50.0             # ~8 min at 6 L/min, mixed to SHOWER_TEMP

UPCOMING_HORIZON_H = 24

# Learned heat rate (v0.6)
HEAT_RATE_ALPHA = 0.3            # EMA weight of the newest run
HEAT_RATE_MIN_RUN_MIN = 10       # ignore shorter runs
HEAT_RATE_MIN_SAMPLES = 2        # runs needed before the learned rate is trusted
FALLBACK_MIN_PER_C = 6.0         # no data, no tank volume
ELEMENT_EFFICIENCY = 0.95
WATER_KJ_PER_L_C = 4.186

NOTIFY_EVENTS = (
    "heat_start",
    "heat_end",
    "target_reached",
    "heat_not_rising",
    "skipped_solar",
    "skipped_weather",
    "legionella_done",
    "safety_stop",
    "sensor_stale",
    "manual_on",
    "cold_warning",
)

# Forecast-based skipping (v0.6)
CONF_FORECAST_HOURS = "forecast_hours"
CONF_FORECAST_CLOUD_MAX = "forecast_cloud_max"
CONF_SOLAR_FORECAST_ENTITY = "solar_forecast_entity"
CONF_SOLAR_FORECAST_MIN = "solar_forecast_min"
DEFAULT_FORECAST_HOURS = 0       # 0 = use the current weather state only
DEFAULT_FORECAST_CLOUD_MAX = 40  # % cloud cover still counted as sunny
DEFAULT_SOLAR_FORECAST_MIN = 1.0
FORECAST_SUNNY_FRACTION = 0.6
FORECAST_REFRESH_MIN = 30

# Time-of-use tariffs (v0.6)
CONF_TARIFF_WINDOWS = "tariff_windows"     # "23:00-07:00@0.49,..." (₪/kWh)
CONF_PREFER_CHEAP = "prefer_cheap"
DEFAULT_PREFER_CHEAP = True
CHEAP_SHIFT_MAX_H = 8                      # how far ahead auto pre-heat may move
CHEAP_STEP_MIN = 15
STANDBY_PENALTY_PER_H = 0.01               # fraction of run cost per hour waiting

# Actionable notifications (mobile_app): "DUDSHEMESH:<cmd>:<arg>:<entry_id>"
ACTION_PREFIX = "DUDSHEMESH"
COLD_WARNING_LEAD_MIN = 60

# Notification texts, {placeholders} filled by the scheduler.
MESSAGES = {
    "en": {
        "title": "Dud Shemesh",
        "title_safety": "Dud Shemesh — safety",
        "title_fault": "Dud Shemesh — heater issue",
        "title_sensor": "Dud Shemesh — sensor",
        "heat_start": "Heating started ({source}, target {target}°C, {minutes} min)",
        "heat_end": "Heating ended ({status}). Tank: {temp}°C",
        "target_reached": "Target {target}°C reached",
        "skipped_solar": "Scheduled heating skipped: the sun is heating the tank ({temp}°C).",
        "skipped_weather": "Scheduled heating skipped: sunny weather ({temp}°C).",
        "heat_not_rising": "Tank not rising as expected (start {start}°C, now {now}°C). Check element / breaker.",
        "legionella_done": "Anti-Legionella cycle completed",
        "overtemp": "Heater stopped: tank reached {temp}°C (limit {limit}°C).",
        "left_on": "Heater was left on; turned off after {minutes} min.",
        "manual_on": "Heater was switched on manually. It will turn off at {until}.",
        "sensor_stale": "Tank temperature sensor is unavailable or stale. Heating runs by time only until it recovers.",
        "cold_warning": "Tank is {temp}°C and nothing is planned; it won't be hot by {at}.",
        "a_heat_now": "Heat now",
        "a_boost_1h": "Boost 1 h",
        "a_keep_30": "Keep 30 min",
        "a_stop": "Turn off",
        "a_ignore": "Ignore",
    },
    "he": {
        "title": "דוד שמש",
        "title_safety": "דוד שמש — בטיחות",
        "title_fault": "דוד שמש — תקלה בגוף החימום",
        "title_sensor": "דוד שמש — חיישן",
        "heat_start": "החימום התחיל ({source}, יעד {target}°C, {minutes} דק׳)",
        "heat_end": "החימום הסתיים ({status}). במיכל: {temp}°C",
        "target_reached": "הגיע ליעד {target}°C",
        "skipped_solar": "החימום המתוזמן דולג: השמש מחממת את המיכל ({temp}°C).",
        "skipped_weather": "החימום המתוזמן דולג: מזג אוויר שמשי ({temp}°C).",
        "heat_not_rising": "הטמפרטורה לא עולה כמצופה (התחלה {start}°C, עכשיו {now}°C). בדקו את הגוף / המפסק.",
        "legionella_done": "מחזור חיטוי ליגיונלה הושלם",
        "overtemp": "החימום הופסק: המיכל הגיע ל-{temp}°C (מגבלה {limit}°C).",
        "left_on": "הדוד נשאר דולק; כובה אחרי {minutes} דק׳.",
        "manual_on": "הדוד הודלק ידנית. הוא יכבה ב-{until}.",
        "sensor_stale": "חיישן טמפרטורת המיכל לא זמין. החימום יפעל לפי זמן בלבד עד שיחזור.",
        "cold_warning": "המיכל ב-{temp}°C ואין חימום מתוכנן; המים לא יהיו חמים עד {at}.",
        "a_heat_now": "חמם עכשיו",
        "a_boost_1h": "חימום שעה",
        "a_keep_30": "עוד 30 דק׳",
        "a_stop": "כבה",
        "a_ignore": "התעלם",
    },
}


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
