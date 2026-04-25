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
    CONF_FAIL_DETECTION_ENABLED,
    CONF_FAIL_DETECTION_MINUTES,
    CONF_FAIL_DETECTION_RISE,
    CONF_HEATER_ENTITY,
    CONF_HEATER_WATTAGE,
    CONF_LEGIONELLA_DAYS,
    CONF_LEGIONELLA_ENABLED,
    CONF_LEGIONELLA_TEMP,
    CONF_MODE,
    CONF_SOLAR_RISE_THRESHOLD,
    CONF_SOLAR_TRACK_MINUTES,
    CONF_TARIFF_ILS_PER_KWH,
    CONF_TARGET_TEMP,
    CONF_TEMP_SENSOR,
    CONF_WEATHER_ENTITY,
    CONF_WEATHER_SKIP_STATES,
    DEFAULT_AUTO_PRE_HEAT_MARGIN_MIN,
    DEFAULT_BOOST_BUTTONS,
    DEFAULT_FAIL_DETECTION_MINUTES,
    DEFAULT_FAIL_DETECTION_RISE,
    DEFAULT_HEATER_WATTAGE,
    DEFAULT_LEGIONELLA_DAYS,
    DEFAULT_LEGIONELLA_TEMP,
    DEFAULT_MODE,
    DEFAULT_SOLAR_RISE_THRESHOLD,
    DEFAULT_SOLAR_TRACK_MINUTES,
    DEFAULT_TARIFF_ILS_PER_KWH,
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
from .scheduler import DudScheduler
from .storage import DudStore

LOG = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

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
    store = DudStore(hass)
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
    }

    scheduler = DudScheduler(hass, store, options)
    await scheduler.async_start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "store": store,
        "scheduler": scheduler,
        "options": options,
    }

    async def _svc_boost(call: ServiceCall) -> None:
        minutes = int(call.data.get("minutes", 60))
        try:
            await scheduler.async_boost(minutes)
        except Exception as e:
            raise HomeAssistantError(str(e)) from e

    async def _svc_cancel_boost(call: ServiceCall) -> None:
        await scheduler.async_stop_heat(reason="cancelled")

    async def _svc_set_mode(call: ServiceCall) -> None:
        mode = call.data["mode"]
        new_options = dict(entry.options)
        new_options[CONF_MODE] = mode
        hass.config_entries.async_update_entry(entry, options=new_options)

    async def _svc_set_target(call: ServiceCall) -> None:
        new_options = dict(entry.options)
        new_options[CONF_TARGET_TEMP] = int(call.data["temp"])
        hass.config_entries.async_update_entry(entry, options=new_options)

    async def _svc_add_schedule(call: ServiceCall) -> ServiceResponse:
        sched = await store.async_add_schedule(
            name=call.data.get("name", ""),
            days_mask=_days_to_mask(call.data["days"]),
            time_hhmm=call.data["time"],
            duration_min=int(call.data.get("duration_minutes", 60)),
            target_temp=call.data.get("target_temp"),
            enabled=bool(call.data.get("enabled", True)),
        )
        return {"schedule": sched}

    async def _svc_update_schedule(call: ServiceCall) -> ServiceResponse:
        fields: dict[str, Any] = {}
        for k_in, k_out in [
            ("name", "name"), ("time", "time_hhmm"),
            ("duration_minutes", "duration_min"),
            ("target_temp", "target_temp"),
            ("enabled", "enabled"),
        ]:
            if k_in in call.data:
                fields[k_out] = call.data[k_in]
        if "days" in call.data:
            fields["days_mask"] = _days_to_mask(call.data["days"])
        sched = await store.async_update_schedule(call.data["schedule_id"], **fields)
        if sched is None:
            raise HomeAssistantError("schedule not found")
        return {"schedule": sched}

    async def _svc_remove_schedule(call: ServiceCall) -> None:
        await store.async_remove_schedule(call.data["schedule_id"])

    async def _svc_legionella_now(call: ServiceCall) -> None:
        target = int(options.get("legionella_temp", DEFAULT_LEGIONELLA_TEMP))
        await scheduler.async_start_heat(
            source="legionella", duration_min=120, target_temp=target,
            note="manual anti-legionella",
        )

    async def _svc_list(call: ServiceCall) -> ServiceResponse:
        return {
            "schedules": store.schedules,
            "active": scheduler.active,
            "history": store.history[:50],
            "options": options,
            "status": scheduler.now_status(),
        }

    SCHEMA_BOOST = vol.Schema({
        vol.Optional("minutes", default=60): vol.All(int, vol.Range(min=1, max=720)),
    })
    SCHEMA_NO_ARGS = vol.Schema({})
    SCHEMA_SET_MODE = vol.Schema({
        vol.Required("mode"): vol.In([MODE_AUTO, MODE_SCHEDULE, MODE_OFF]),
    })
    SCHEMA_SET_TARGET = vol.Schema({
        vol.Required("temp"): vol.All(int, vol.Range(min=20, max=80)),
    })
    SCHEMA_ADD_SCHEDULE = vol.Schema({
        vol.Required("time"): _hhmm,
        vol.Required("days"): vol.All(cv.ensure_list, [vol.In(DAY_NAMES)]),
        vol.Optional("duration_minutes", default=60): vol.All(int, vol.Range(min=1, max=720)),
        vol.Optional("target_temp"): vol.All(int, vol.Range(min=20, max=80)),
        vol.Optional("name", default=""): cv.string,
        vol.Optional("enabled", default=True): cv.boolean,
    })
    SCHEMA_UPDATE_SCHEDULE = vol.Schema({
        vol.Required("schedule_id"): cv.string,
        vol.Optional("time"): _hhmm,
        vol.Optional("days"): vol.All(cv.ensure_list, [vol.In(DAY_NAMES)]),
        vol.Optional("duration_minutes"): vol.All(int, vol.Range(min=1, max=720)),
        vol.Optional("target_temp"): vol.All(int, vol.Range(min=20, max=80)),
        vol.Optional("name"): cv.string,
        vol.Optional("enabled"): cv.boolean,
    })
    SCHEMA_REMOVE_SCHEDULE = vol.Schema({
        vol.Required("schedule_id"): cv.string,
    })

    hass.services.async_register(DOMAIN, SERVICE_BOOST, _svc_boost, schema=SCHEMA_BOOST)
    hass.services.async_register(DOMAIN, SERVICE_CANCEL_BOOST, _svc_cancel_boost, schema=SCHEMA_NO_ARGS)
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
    hass.services.async_register(DOMAIN, SERVICE_LEGIONELLA_NOW, _svc_legionella_now, schema=SCHEMA_NO_ARGS)
    hass.services.async_register(
        DOMAIN, SERVICE_LIST, _svc_list, supports_response=SupportsResponse.ONLY
    )

    _async_register_ws_commands(hass)
    await _async_register_panel(hass)
    await _async_register_card_resource(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


def _async_register_ws_commands(hass: HomeAssistant) -> None:
    if hass.data.get(WS_REGISTERED_KEY):
        return

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get_state"})
    @websocket_api.async_response
    async def _ws_get_state(hass_inner, connection, msg):
        domain_data = hass_inner.data.get(DOMAIN, {})
        if not domain_data:
            connection.send_error(msg["id"], "not_loaded", "integration not loaded")
            return
        entry_id = next(iter(domain_data))
        data = domain_data[entry_id]
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
        connection.send_result(msg["id"], {
            "schedules": store.schedules,
            "history": store.history[:500],
            "active": scheduler.active,
            "options": options,
            "status": scheduler.now_status(),
            "temperature_unit": temp_unit,
            "last_legionella": store.last_legionella,
            "legionella_next_due": legionella_next,
            "now": int(time.time()),
        })

    @websocket_api.websocket_command({
        vol.Required("type"): f"{DOMAIN}/update_options",
        vol.Optional(CONF_TARGET_TEMP): vol.Any(int, float, None),
        vol.Optional(CONF_MODE): vol.In([MODE_AUTO, MODE_SCHEDULE, MODE_OFF]),
        vol.Optional(CONF_HEATER_WATTAGE): vol.Any(int, float, None),
        vol.Optional(CONF_LEGIONELLA_ENABLED): cv.boolean,
        vol.Optional(CONF_LEGIONELLA_TEMP): vol.Any(int, float, None),
        vol.Optional(CONF_LEGIONELLA_DAYS): vol.Any(int, None),
        vol.Optional(CONF_WEATHER_ENTITY): vol.Any(str, None),
        vol.Optional(CONF_WEATHER_SKIP_STATES): vol.Any(str, None),
        vol.Optional(CONF_AUTO_COMFORT_WINDOWS): vol.Any(str, None),
        vol.Optional(CONF_AUTO_PRE_HEAT_MARGIN_MIN): vol.Any(int, float, None),
        vol.Optional(CONF_FAIL_DETECTION_ENABLED): cv.boolean,
        vol.Optional(CONF_FAIL_DETECTION_MINUTES): vol.Any(int, float, None),
        vol.Optional(CONF_FAIL_DETECTION_RISE): vol.Any(int, float, None),
        vol.Optional(CONF_SOLAR_TRACK_MINUTES): vol.Any(int, float, None),
        vol.Optional(CONF_SOLAR_RISE_THRESHOLD): vol.Any(int, float, None),
        vol.Optional(CONF_BOOST_BUTTONS): vol.Any(str, None),
        vol.Optional(CONF_TARIFF_ILS_PER_KWH): vol.Any(int, float, None),
    })
    @websocket_api.async_response
    async def _ws_update_options(hass_inner, connection, msg):
        domain_data = hass_inner.data.get(DOMAIN, {})
        if not domain_data:
            connection.send_error(msg["id"], "not_loaded", "integration not loaded")
            return
        entry_id = next(iter(domain_data))
        entry = hass_inner.config_entries.async_get_entry(entry_id)
        if not entry:
            connection.send_error(msg["id"], "no_entry", "entry not found")
            return
        new_options = dict(entry.options)
        for key in (CONF_TARGET_TEMP, CONF_MODE, CONF_HEATER_WATTAGE,
                    CONF_LEGIONELLA_ENABLED, CONF_LEGIONELLA_TEMP, CONF_LEGIONELLA_DAYS,
                    CONF_WEATHER_ENTITY, CONF_WEATHER_SKIP_STATES,
                    CONF_AUTO_COMFORT_WINDOWS, CONF_AUTO_PRE_HEAT_MARGIN_MIN,
                    CONF_FAIL_DETECTION_ENABLED, CONF_FAIL_DETECTION_MINUTES, CONF_FAIL_DETECTION_RISE,
                    CONF_SOLAR_TRACK_MINUTES, CONF_SOLAR_RISE_THRESHOLD,
                    CONF_BOOST_BUTTONS, CONF_TARIFF_ILS_PER_KWH):
            if key in msg:
                new_options[key] = msg[key]
        hass_inner.config_entries.async_update_entry(entry, options=new_options)
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
        for svc in (
            SERVICE_BOOST, SERVICE_CANCEL_BOOST, SERVICE_SET_MODE, SERVICE_SET_TARGET,
            SERVICE_ADD_SCHEDULE, SERVICE_UPDATE_SCHEDULE, SERVICE_REMOVE_SCHEDULE,
            SERVICE_LEGIONELLA_NOW, SERVICE_LIST,
        ):
            if hass.services.has_service(DOMAIN, svc):
                hass.services.async_remove(DOMAIN, svc)
        if hass.data.pop(PANEL_REGISTERED_KEY, False):
            with suppress(Exception):
                async_remove_panel(hass, PANEL_URL_PATH)
    return True
