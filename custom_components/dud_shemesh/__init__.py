"""Dud Shemesh integration."""
from __future__ import annotations

import json
import logging
import os
import time
from contextlib import suppress
from typing import Any

import voluptuous as vol

from homeassistant.components import panel_custom, websocket_api
from homeassistant.components.frontend import async_remove_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_AUTO_COMFORT_WINDOWS,
    CONF_AUTO_PRE_HEAT_MARGIN_MIN,
    CONF_BOOST_BUTTONS,
    CONF_CALENDAR_ENTITY,
    CONF_CALENDAR_KEYWORDS,
    CONF_CALENDAR_LOOKAHEAD_MIN,
    CONF_FAIL_DETECTION_ENABLED,
    CONF_NOTIFY_EVENTS,
    CONF_NOTIFY_TARGETS,
    CONF_FAIL_DETECTION_MINUTES,
    CONF_FAIL_DETECTION_RISE,
    CONF_HEATER_ENTITY,
    CONF_HEATER_WATTAGE,
    CONF_LEGIONELLA_DAYS,
    CONF_LEGIONELLA_ENABLED,
    CONF_LEGIONELLA_TEMP,
    CONF_MANUAL_ON_MAX_MIN,
    CONF_MAX_RUN_MIN,
    CONF_MAX_TANK_TEMP,
    CONF_MODE,
    CONF_SENSOR_STALE_MIN,
    CONF_TANK_VOLUME_L,
    CONF_SOLAR_RISE_THRESHOLD,
    CONF_SOLAR_TRACK_MINUTES,
    CONF_TARIFF_ILS_PER_KWH,
    CONF_VACATION_HOLD_TEMP,
    CONF_VACATION_UNTIL,
    CONF_TARGET_TEMP,
    CONF_TEMP_SENSOR,
    CONF_WEATHER_ENTITY,
    CONF_WEATHER_SKIP_STATES,
    DEFAULT_AUTO_PRE_HEAT_MARGIN_MIN,
    DEFAULT_BOOST_BUTTONS,
    DEFAULT_CALENDAR_KEYWORDS,
    DEFAULT_CALENDAR_LOOKAHEAD_MIN,
    DEFAULT_FAIL_DETECTION_MINUTES,
    DEFAULT_FAIL_DETECTION_RISE,
    DEFAULT_HEATER_WATTAGE,
    DEFAULT_LEGIONELLA_DAYS,
    DEFAULT_LEGIONELLA_TEMP,
    DEFAULT_MANUAL_ON_MAX_MIN,
    DEFAULT_MAX_RUN_MIN,
    DEFAULT_MAX_TANK_TEMP,
    DEFAULT_MODE,
    DEFAULT_SENSOR_STALE_MIN,
    DEFAULT_TANK_VOLUME_L,
    LEGACY_WEATHER_SKIP_STATES,
    DEFAULT_SOLAR_RISE_THRESHOLD,
    DEFAULT_SOLAR_TRACK_MINUTES,
    DEFAULT_TARIFF_ILS_PER_KWH,
    DEFAULT_VACATION_HOLD_TEMP,
    NOTIFY_EVENTS,
    DEFAULT_TARGET_TEMP,
    DEFAULT_WEATHER_SKIP_STATES,
    DOMAIN,
    MODE_AUTO,
    MODE_OFF,
    MODE_SCHEDULE,
    SERVICE_ADD_SCHEDULE,
    SERVICE_BOOST,
    SERVICE_CANCEL_BOOST,
    SERVICE_LEGIONELLA_NOW,
    SERVICE_LIST,
    SERVICE_REMOVE_SCHEDULE,
    SERVICE_SET_MODE,
    SERVICE_SET_TARGET,
    SERVICE_UPDATE_SCHEDULE,
)
from .entity import async_update_options
from .scheduler import DudScheduler
from .storage import DudStore

LOG = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]

PANEL_URL_PATH = "dud-shemesh"
PANEL_STATIC_URL = "/dud_shemesh_panel"
PANEL_REGISTERED_KEY = f"{DOMAIN}_panel_registered"
WS_REGISTERED_KEY = f"{DOMAIN}_ws_registered"
CARD_REGISTERED_KEY = f"{DOMAIN}_card_registered"
CARD_RESOURCE_URL = f"{PANEL_STATIC_URL}/card.js"

DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _hhmm(value: str) -> str:
    if not isinstance(value, str) or ":" not in value:
        raise vol.Invalid("time must be HH:MM")
    h, m = value.split(":", 1)
    try:
        hi, mi = int(h), int(m)
    except ValueError:
        raise vol.Invalid("time must be HH:MM")
    if not (0 <= hi < 24 and 0 <= mi < 60):
        raise vol.Invalid("time out of range")
    return f"{hi:02d}:{mi:02d}"


def _days_to_mask(days: list[str]) -> int:
    mask = 0
    for d in days:
        mask |= 1 << DAY_NAMES.index(d)
    return mask


_INTEGRATION_VERSION_CACHE: str | None = None


def _read_version_sync() -> str:
    try:
        with open(os.path.join(os.path.dirname(__file__), "manifest.json"), "r") as f:
            return json.load(f).get("version", "0")
    except Exception:
        return "0"


async def _integration_version(hass: HomeAssistant) -> str:
    global _INTEGRATION_VERSION_CACHE
    if _INTEGRATION_VERSION_CACHE is None:
        _INTEGRATION_VERSION_CACHE = await hass.async_add_executor_job(_read_version_sync)
    return _INTEGRATION_VERSION_CACHE


async def _async_register_panel(hass: HomeAssistant) -> None:
    if hass.data.get(PANEL_REGISTERED_KEY):
        return
    panel_dir = os.path.join(os.path.dirname(__file__), "www")
    if os.path.isdir(panel_dir):
        await hass.http.async_register_static_paths([
            StaticPathConfig(PANEL_STATIC_URL, panel_dir, False)
        ])
    version = await _integration_version(hass)
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name="dud-shemesh-panel",
        frontend_url_path=PANEL_URL_PATH,
        module_url=f"{PANEL_STATIC_URL}/panel.js?v={version}",
        sidebar_title="Dud Shemesh",
        sidebar_icon="mdi:water-boiler",
        require_admin=False,
        config={},
    )
    hass.data[PANEL_REGISTERED_KEY] = True


async def _async_register_card_resource(hass: HomeAssistant) -> None:
    if hass.data.get(CARD_REGISTERED_KEY):
        return
    try:
        from homeassistant.components.lovelace.resources import ResourceStorageCollection
        lovelace = hass.data.get("lovelace")
        if lovelace and getattr(lovelace, "resources", None):
            resources: ResourceStorageCollection = lovelace.resources
            if resources.store and resources.store.key and not resources.loaded:
                await resources.async_load()
            version = await _integration_version(hass)
            target_url = f"{CARD_RESOURCE_URL}?v={version}"
            items = list(resources.async_items())
            stale = [r for r in items if r.get("url", "").startswith(CARD_RESOURCE_URL) and r.get("url") != target_url]
            for r in stale:
                await resources.async_delete_item(r["id"])
            existing = [r for r in resources.async_items() if r.get("url") == target_url]
            if not existing:
                await resources.async_create_item({"res_type": "module", "url": target_url})
    except Exception as e:
        LOG.debug("card resource auto-register skipped: %s", e)
    hass.data[CARD_REGISTERED_KEY] = True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # v0.5: "clear-night" in the old default skipped pre-sunrise heating.
    if entry.options.get(CONF_WEATHER_SKIP_STATES) == LEGACY_WEATHER_SKIP_STATES:
        hass.config_entries.async_update_entry(
            entry, options={**entry.options, CONF_WEATHER_SKIP_STATES: DEFAULT_WEATHER_SKIP_STATES},
        )

    entries = hass.config_entries.async_entries(DOMAIN)
    store = DudStore(
        hass, entry.entry_id,
        claim_legacy=bool(entries) and entries[0].entry_id == entry.entry_id,
    )
    await store.async_load()

    options = {
        CONF_HEATER_ENTITY: entry.options.get(CONF_HEATER_ENTITY, ""),
        CONF_TEMP_SENSOR: entry.options.get(CONF_TEMP_SENSOR, ""),
        CONF_TARGET_TEMP: entry.options.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP),
        CONF_HEATER_WATTAGE: entry.options.get(CONF_HEATER_WATTAGE, DEFAULT_HEATER_WATTAGE),
        CONF_MODE: entry.options.get(CONF_MODE, DEFAULT_MODE),
        CONF_LEGIONELLA_ENABLED: entry.options.get(CONF_LEGIONELLA_ENABLED, False),
        CONF_LEGIONELLA_TEMP: entry.options.get(CONF_LEGIONELLA_TEMP, DEFAULT_LEGIONELLA_TEMP),
        CONF_LEGIONELLA_DAYS: entry.options.get(CONF_LEGIONELLA_DAYS, DEFAULT_LEGIONELLA_DAYS),
        # alias keys for scheduler convenience
        "heater_entity": entry.options.get(CONF_HEATER_ENTITY, ""),
        "temp_sensor": entry.options.get(CONF_TEMP_SENSOR, ""),
        "target_temp": entry.options.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP),
        "heater_wattage_w": entry.options.get(CONF_HEATER_WATTAGE, DEFAULT_HEATER_WATTAGE),
        "mode": entry.options.get(CONF_MODE, DEFAULT_MODE),
        "legionella_enabled": entry.options.get(CONF_LEGIONELLA_ENABLED, False),
        "legionella_temp": entry.options.get(CONF_LEGIONELLA_TEMP, DEFAULT_LEGIONELLA_TEMP),
        "legionella_days": entry.options.get(CONF_LEGIONELLA_DAYS, DEFAULT_LEGIONELLA_DAYS),
        "weather_entity": entry.options.get(CONF_WEATHER_ENTITY, ""),
        "weather_skip_states": entry.options.get(CONF_WEATHER_SKIP_STATES, DEFAULT_WEATHER_SKIP_STATES),
        "auto_comfort_windows": entry.options.get(CONF_AUTO_COMFORT_WINDOWS, ""),
        "auto_pre_heat_margin_min": entry.options.get(CONF_AUTO_PRE_HEAT_MARGIN_MIN, DEFAULT_AUTO_PRE_HEAT_MARGIN_MIN),
        "fail_detection_enabled": entry.options.get(CONF_FAIL_DETECTION_ENABLED, False),
        "fail_detection_minutes": entry.options.get(CONF_FAIL_DETECTION_MINUTES, DEFAULT_FAIL_DETECTION_MINUTES),
        "fail_detection_rise": entry.options.get(CONF_FAIL_DETECTION_RISE, DEFAULT_FAIL_DETECTION_RISE),
        "solar_track_minutes": entry.options.get(CONF_SOLAR_TRACK_MINUTES, DEFAULT_SOLAR_TRACK_MINUTES),
        "solar_rise_threshold": entry.options.get(CONF_SOLAR_RISE_THRESHOLD, DEFAULT_SOLAR_RISE_THRESHOLD),
        "boost_buttons": entry.options.get(CONF_BOOST_BUTTONS, DEFAULT_BOOST_BUTTONS),
        "tariff_ils_per_kwh": entry.options.get(CONF_TARIFF_ILS_PER_KWH, DEFAULT_TARIFF_ILS_PER_KWH),
        "notify_targets": entry.options.get(CONF_NOTIFY_TARGETS, []),
        "notify_events": entry.options.get(CONF_NOTIFY_EVENTS, []),
        "vacation_until": entry.options.get(CONF_VACATION_UNTIL, 0),
        "vacation_hold_temp": entry.options.get(CONF_VACATION_HOLD_TEMP, DEFAULT_VACATION_HOLD_TEMP),
        "calendar_entity": entry.options.get(CONF_CALENDAR_ENTITY, ""),
        "calendar_lookahead_min": entry.options.get(CONF_CALENDAR_LOOKAHEAD_MIN, DEFAULT_CALENDAR_LOOKAHEAD_MIN),
        "calendar_keywords": entry.options.get(CONF_CALENDAR_KEYWORDS, DEFAULT_CALENDAR_KEYWORDS),
        "manual_on_max_min": entry.options.get(CONF_MANUAL_ON_MAX_MIN, DEFAULT_MANUAL_ON_MAX_MIN),
        "max_run_min": entry.options.get(CONF_MAX_RUN_MIN, DEFAULT_MAX_RUN_MIN),
        "max_tank_temp": entry.options.get(CONF_MAX_TANK_TEMP, DEFAULT_MAX_TANK_TEMP),
        "sensor_stale_min": entry.options.get(CONF_SENSOR_STALE_MIN, DEFAULT_SENSOR_STALE_MIN),
        "tank_volume_l": entry.options.get(CONF_TANK_VOLUME_L, DEFAULT_TANK_VOLUME_L),
    }

    scheduler = DudScheduler(hass, store, options)
    await scheduler.async_start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "entry": entry,
        "store": store,
        "scheduler": scheduler,
        "options": options,
    }

    _async_register_services(hass)
    _async_register_ws_commands(hass)
    await _async_register_panel(hass)
    await _async_register_card_resource(hass)
    _async_register_intents(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


def _resolve_entry(hass: HomeAssistant, entry_id: str | None = None) -> dict:
    """Loaded entry data for entry_id, or the first loaded entry in config order."""
    domain_data = hass.data.get(DOMAIN) or {}
    if entry_id:
        data = domain_data.get(entry_id)
        if not data:
            raise HomeAssistantError(f"Dud Shemesh entry {entry_id} is not loaded")
        return data
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.entry_id in domain_data:
            return domain_data[e.entry_id]
    raise HomeAssistantError("Dud Shemesh integration not loaded")


_ENTRY_ID = vol.Optional("entry_id")
_INT_MINUTES = vol.All(vol.Coerce(int), vol.Range(min=1, max=720))
_INT_TEMP = vol.All(vol.Coerce(int), vol.Range(min=20, max=80))

SCHEMA_BOOST = vol.Schema({
    _ENTRY_ID: cv.string,
    vol.Optional("minutes", default=60): _INT_MINUTES,
})
SCHEMA_ENTRY_ONLY = vol.Schema({_ENTRY_ID: cv.string})
SCHEMA_SET_MODE = vol.Schema({
    _ENTRY_ID: cv.string,
    vol.Required("mode"): vol.In([MODE_AUTO, MODE_SCHEDULE, MODE_OFF]),
})
SCHEMA_SET_TARGET = vol.Schema({
    _ENTRY_ID: cv.string,
    vol.Required("temp"): _INT_TEMP,
})
SCHEMA_ADD_SCHEDULE = vol.Schema({
    _ENTRY_ID: cv.string,
    vol.Required("time"): _hhmm,
    vol.Required("days"): vol.All(cv.ensure_list, [vol.In(DAY_NAMES)]),
    vol.Optional("duration_minutes", default=60): _INT_MINUTES,
    vol.Optional("target_temp"): _INT_TEMP,
    vol.Optional("name", default=""): cv.string,
    vol.Optional("enabled", default=True): cv.boolean,
})
SCHEMA_UPDATE_SCHEDULE = vol.Schema({
    _ENTRY_ID: cv.string,
    vol.Required("schedule_id"): cv.string,
    vol.Optional("time"): _hhmm,
    vol.Optional("days"): vol.All(cv.ensure_list, [vol.In(DAY_NAMES)]),
    vol.Optional("duration_minutes"): _INT_MINUTES,
    vol.Optional("target_temp"): _INT_TEMP,
    vol.Optional("name"): cv.string,
    vol.Optional("enabled"): cv.boolean,
    vol.Optional("skip_until"): vol.All(vol.Coerce(int), vol.Range(min=0)),
})
SCHEMA_REMOVE_SCHEDULE = vol.Schema({
    _ENTRY_ID: cv.string,
    vol.Required("schedule_id"): cv.string,
})

ALL_SERVICES = (
    SERVICE_BOOST, SERVICE_CANCEL_BOOST, SERVICE_SET_MODE, SERVICE_SET_TARGET,
    SERVICE_ADD_SCHEDULE, SERVICE_UPDATE_SCHEDULE, SERVICE_REMOVE_SCHEDULE,
    SERVICE_LEGIONELLA_NOW, SERVICE_LIST,
)


def _async_register_services(hass: HomeAssistant) -> None:
    """Register domain services once; each call targets entry_id or the first entry."""
    if hass.services.has_service(DOMAIN, SERVICE_BOOST):
        return

    async def _svc_boost(call: ServiceCall) -> None:
        data = _resolve_entry(hass, call.data.get("entry_id"))
        try:
            await data["scheduler"].async_boost(call.data["minutes"])
        except Exception as e:
            raise HomeAssistantError(str(e)) from e

    async def _svc_cancel_boost(call: ServiceCall) -> None:
        data = _resolve_entry(hass, call.data.get("entry_id"))
        await data["scheduler"].async_stop_heat(reason="cancelled")

    async def _svc_set_mode(call: ServiceCall) -> None:
        data = _resolve_entry(hass, call.data.get("entry_id"))
        async_update_options(hass, data["entry"], {CONF_MODE: call.data["mode"]})

    async def _svc_set_target(call: ServiceCall) -> None:
        data = _resolve_entry(hass, call.data.get("entry_id"))
        async_update_options(hass, data["entry"], {CONF_TARGET_TEMP: call.data["temp"]})

    async def _svc_add_schedule(call: ServiceCall) -> ServiceResponse:
        data = _resolve_entry(hass, call.data.get("entry_id"))
        sched = await data["store"].async_add_schedule(
            name=call.data.get("name", ""),
            days_mask=_days_to_mask(call.data["days"]),
            time_hhmm=call.data["time"],
            duration_min=call.data["duration_minutes"],
            target_temp=call.data.get("target_temp"),
            enabled=call.data.get("enabled", True),
        )
        return {"schedule": sched}

    async def _svc_update_schedule(call: ServiceCall) -> ServiceResponse:
        data = _resolve_entry(hass, call.data.get("entry_id"))
        fields: dict[str, Any] = {}
        for k_in, k_out in [
            ("name", "name"), ("time", "time_hhmm"),
            ("duration_minutes", "duration_min"),
            ("target_temp", "target_temp"),
            ("enabled", "enabled"),
            ("skip_until", "skip_until"),
        ]:
            if k_in in call.data:
                fields[k_out] = call.data[k_in]
        if "days" in call.data:
            fields["days_mask"] = _days_to_mask(call.data["days"])
        sched = await data["store"].async_update_schedule(call.data["schedule_id"], **fields)
        if sched is None:
            raise HomeAssistantError("schedule not found")
        return {"schedule": sched}

    async def _svc_remove_schedule(call: ServiceCall) -> None:
        data = _resolve_entry(hass, call.data.get("entry_id"))
        await data["store"].async_remove_schedule(call.data["schedule_id"])

    async def _svc_legionella_now(call: ServiceCall) -> None:
        data = _resolve_entry(hass, call.data.get("entry_id"))
        target = int(data["options"].get("legionella_temp", DEFAULT_LEGIONELLA_TEMP))
        await data["scheduler"].async_start_heat(
            source="legionella", duration_min=120, target_temp=target,
            note="manual anti-legionella",
        )

    async def _svc_list(call: ServiceCall) -> ServiceResponse:
        data = _resolve_entry(hass, call.data.get("entry_id"))
        return {
            "entry_id": data["entry"].entry_id,
            "schedules": data["store"].schedules,
            "active": data["scheduler"].active,
            "history": data["store"].history[:50],
            "options": data["options"],
            "status": data["scheduler"].now_status(),
        }

    hass.services.async_register(DOMAIN, SERVICE_BOOST, _svc_boost, schema=SCHEMA_BOOST)
    hass.services.async_register(DOMAIN, SERVICE_CANCEL_BOOST, _svc_cancel_boost, schema=SCHEMA_ENTRY_ONLY)
    hass.services.async_register(DOMAIN, SERVICE_SET_MODE, _svc_set_mode, schema=SCHEMA_SET_MODE)
    hass.services.async_register(DOMAIN, SERVICE_SET_TARGET, _svc_set_target, schema=SCHEMA_SET_TARGET)
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_SCHEDULE, _svc_add_schedule,
        schema=SCHEMA_ADD_SCHEDULE,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_SCHEDULE, _svc_update_schedule,
        schema=SCHEMA_UPDATE_SCHEDULE,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_SCHEDULE, _svc_remove_schedule, schema=SCHEMA_REMOVE_SCHEDULE)
    hass.services.async_register(DOMAIN, SERVICE_LEGIONELLA_NOW, _svc_legionella_now, schema=SCHEMA_ENTRY_ONLY)
    hass.services.async_register(
        DOMAIN, SERVICE_LIST, _svc_list, schema=SCHEMA_ENTRY_ONLY,
        supports_response=SupportsResponse.ONLY,
    )


_INTENT_REGISTERED_KEY = f"{DOMAIN}_intent_registered"


def _async_register_intents(hass: HomeAssistant) -> None:
    if hass.data.get(_INTENT_REGISTERED_KEY):
        return
    try:
        from homeassistant.helpers import intent

        class _BoostIntent(intent.IntentHandler):
            intent_type = "DudShemeshBoost"
            slot_schema = {vol.Optional("minutes"): _INT_MINUTES}
            description = "Boost the water heater"
            async def async_handle(self, intent_obj):
                slots = self.async_validate_slots(intent_obj.slots)
                minutes = int(slots.get("minutes", {}).get("value", 60))
                response = intent_obj.create_response()
                try:
                    data = _resolve_entry(hass)
                except HomeAssistantError:
                    response.async_set_speech("Dud Shemesh integration not loaded.")
                    return response
                await data["scheduler"].async_boost(minutes)
                response.async_set_speech(f"Heater boosted for {minutes} minutes")
                return response

        class _StopIntent(intent.IntentHandler):
            intent_type = "DudShemeshStop"
            description = "Stop the water heater"
            async def async_handle(self, intent_obj):
                response = intent_obj.create_response()
                try:
                    data = _resolve_entry(hass)
                except HomeAssistantError:
                    response.async_set_speech("Dud Shemesh integration not loaded.")
                    return response
                await data["scheduler"].async_stop_heat(reason="voice")
                response.async_set_speech("Water heater stopped")
                return response

        intent.async_register(hass, _BoostIntent())
        intent.async_register(hass, _StopIntent())
        hass.data[_INTENT_REGISTERED_KEY] = True
    except Exception as e:
        LOG.debug("intents not registered: %s", e)


def _ws_int(lo: int, hi: int):
    return vol.All(vol.Coerce(int), vol.Range(min=lo, max=hi))


def _ws_float(lo: float, hi: float):
    return vol.All(vol.Coerce(float), vol.Range(min=lo, max=hi))


# Keys any user may change from the panel/card; everything else needs admin.
WS_PUBLIC_OPTION_KEYS = {CONF_MODE, CONF_TARGET_TEMP}

WS_OPTION_SCHEMA = {
    vol.Optional(CONF_TARGET_TEMP): _ws_int(20, 80),
    vol.Optional(CONF_MODE): vol.In([MODE_AUTO, MODE_SCHEDULE, MODE_OFF]),
    vol.Optional(CONF_HEATER_WATTAGE): _ws_int(100, 20000),
    vol.Optional(CONF_LEGIONELLA_ENABLED): cv.boolean,
    vol.Optional(CONF_LEGIONELLA_TEMP): _ws_int(55, 80),
    vol.Optional(CONF_LEGIONELLA_DAYS): _ws_int(1, 30),
    vol.Optional(CONF_WEATHER_ENTITY): vol.Any(None, cv.string),
    vol.Optional(CONF_WEATHER_SKIP_STATES): vol.Any(None, cv.string),
    vol.Optional(CONF_AUTO_COMFORT_WINDOWS): vol.Any(None, cv.string),
    vol.Optional(CONF_AUTO_PRE_HEAT_MARGIN_MIN): _ws_int(0, 180),
    vol.Optional(CONF_FAIL_DETECTION_ENABLED): cv.boolean,
    vol.Optional(CONF_FAIL_DETECTION_MINUTES): _ws_int(1, 120),
    vol.Optional(CONF_FAIL_DETECTION_RISE): _ws_float(0.1, 20),
    vol.Optional(CONF_SOLAR_TRACK_MINUTES): _ws_int(5, 180),
    vol.Optional(CONF_SOLAR_RISE_THRESHOLD): _ws_float(0.1, 20),
    vol.Optional(CONF_BOOST_BUTTONS): vol.Any(None, cv.string),
    vol.Optional(CONF_TARIFF_ILS_PER_KWH): _ws_float(0, 10),
    vol.Optional(CONF_NOTIFY_TARGETS): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_NOTIFY_EVENTS): vol.All(cv.ensure_list, [vol.In(NOTIFY_EVENTS)]),
    vol.Optional(CONF_VACATION_UNTIL): _ws_int(0, 2**31 - 1),
    vol.Optional(CONF_VACATION_HOLD_TEMP): _ws_int(5, 60),
    vol.Optional(CONF_CALENDAR_ENTITY): vol.Any(None, cv.string),
    vol.Optional(CONF_CALENDAR_LOOKAHEAD_MIN): _ws_int(1, 120),
    vol.Optional(CONF_CALENDAR_KEYWORDS): vol.Any(None, cv.string),
    vol.Optional(CONF_MANUAL_ON_MAX_MIN): _ws_int(0, 720),
    vol.Optional(CONF_MAX_RUN_MIN): _ws_int(30, 720),
    vol.Optional(CONF_MAX_TANK_TEMP): _ws_int(50, 90),
    vol.Optional(CONF_SENSOR_STALE_MIN): _ws_int(0, 1440),
    vol.Optional(CONF_TANK_VOLUME_L): _ws_int(0, 1000),
}


def _async_register_ws_commands(hass: HomeAssistant) -> None:
    if hass.data.get(WS_REGISTERED_KEY):
        return

    @websocket_api.websocket_command({
        vol.Required("type"): f"{DOMAIN}/get_state",
        vol.Optional("entry_id"): cv.string,
    })
    @websocket_api.async_response
    async def _ws_get_state(hass_inner, connection, msg):
        try:
            data = _resolve_entry(hass_inner, msg.get("entry_id"))
        except HomeAssistantError as e:
            connection.send_error(msg["id"], "not_loaded", str(e))
            return
        store = data["store"]
        scheduler = data["scheduler"]
        options = data["options"]
        try:
            temp_unit = hass_inner.config.units.temperature_unit
        except Exception:
            temp_unit = "°C"
        legionella_next = 0
        if options.get("legionella_enabled"):
            days = int(options.get("legionella_days", 7))
            last = store.last_legionella
            if last:
                legionella_next = last + days * 86400
        notify_services = sorted(list((hass_inner.services.async_services().get("notify") or {}).keys()))
        connection.send_result(msg["id"], {
            "entry_id": data["entry"].entry_id,
            "schedules": store.schedules,
            "history": store.history[:500],
            "active": scheduler.active,
            "options": options,
            "status": scheduler.now_status(),
            "temperature_unit": temp_unit,
            "last_legionella": store.last_legionella,
            "legionella_next_due": legionella_next,
            "notify_services": notify_services,
            "notify_events": list(NOTIFY_EVENTS),
            "temp_samples": getattr(scheduler, "_temp_samples", []),
            "schedule_next": {s["id"]: scheduler.next_schedule_run(s) for s in store.schedules},
            "energy_kwh_total": scheduler.energy_total_kwh(),
            "now": int(time.time()),
        })

    @websocket_api.websocket_command({
        vol.Required("type"): f"{DOMAIN}/update_options",
        vol.Optional("entry_id"): cv.string,
        **WS_OPTION_SCHEMA,
    })
    @websocket_api.async_response
    async def _ws_update_options(hass_inner, connection, msg):
        try:
            data = _resolve_entry(hass_inner, msg.get("entry_id"))
        except HomeAssistantError as e:
            connection.send_error(msg["id"], "not_loaded", str(e))
            return
        patch = {k.schema: msg[k.schema] for k in WS_OPTION_SCHEMA if k.schema in msg}
        if not connection.user.is_admin and set(patch) - WS_PUBLIC_OPTION_KEYS:
            connection.send_error(msg["id"], "unauthorized", "Only administrators can change these settings")
            return
        new_options = async_update_options(hass_inner, data["entry"], patch)
        connection.send_result(msg["id"], {"options": new_options})

    websocket_api.async_register_command(hass, _ws_get_state)
    websocket_api.async_register_command(hass, _ws_update_options)
    hass.data[WS_REGISTERED_KEY] = True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unloaded:
        return False

    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if data:
        await data["scheduler"].async_stop()

    if not hass.data.get(DOMAIN):
        for svc in ALL_SERVICES:
            if hass.services.has_service(DOMAIN, svc):
                hass.services.async_remove(DOMAIN, svc)
        if hass.data.pop(PANEL_REGISTERED_KEY, False):
            with suppress(Exception):
                async_remove_panel(hass, PANEL_URL_PATH)
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await DudStore(hass, entry.entry_id).async_remove()
