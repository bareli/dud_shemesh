"""Regression tests for issues #1-#23."""
from __future__ import annotations

import asyncio
import time
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.dud_shemesh import scheduler as sched_mod
from custom_components.dud_shemesh.const import DOMAIN

from .conftest import HEATER, TEMP, make_entry, setup_entry, setup_heater


def _closes(store):
    return [h for h in store.history if h["status"] != "started"]


async def _advance(hass: HomeAssistant, freezer, seconds: int) -> None:
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


# 1
async def test_restore_before_heater_exists_still_turns_off(hass, hass_storage, freezer):
    entry = make_entry(hass)
    now = int(time.time())
    hass_storage[f"dud_shemesh.data.{entry.entry_id}"] = {
        "version": 1, "key": f"dud_shemesh.data.{entry.entry_id}",
        "data": {"schedules": [], "history": [], "last_legionella": 0, "active_boost": {
            "source": "boost", "started_at": now - 60, "ends_at": now + 600,
            "duration_min": 11, "target_temp": None, "starting_temp": 40, "note": "",
        }},
    }
    hass.set_state(CoreState.starting)
    data = await setup_entry(hass, entry)
    assert data["scheduler"].active is None  # heater not loaded yet, restore deferred

    await setup_heater(hass, initial=True)  # device came back ON
    hass.set_state(CoreState.running)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()
    assert data["scheduler"].active is not None

    await _advance(hass, freezer, 700)
    assert hass.states.get(HEATER).state == "off"
    assert data["scheduler"].active is None


# 2
async def test_failed_turn_off_clears_run(hass):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass))
    sch = data["scheduler"]
    await sch.async_boost(30)
    assert sch.active

    real = sch._call_heater

    async def failing(entity_id, on):
        if not on:
            raise RuntimeError("unavailable")
        await real(entity_id, on)

    with patch.object(sch, "_call_heater", side_effect=failing):
        await sch.async_stop_heat("manual_stop")
    assert sch.active is None
    assert data["store"].active_boost is None
    assert sch._unsub_close is None


# 3
async def test_options_flow_keeps_panel_keys(hass):
    await setup_heater(hass)
    entry = make_entry(hass, notify_targets=["mobile_app_x"], vacation_until=123, tariff_ils_per_kwh=0.7)
    await setup_entry(hass, entry)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"heater_entity": HEATER, "target_temp": 60, "heater_wattage_w": 2000},
    )
    await hass.async_block_till_done()
    assert entry.options["target_temp"] == 60
    assert entry.options["notify_targets"] == ["mobile_app_x"]
    assert entry.options["vacation_until"] == 123
    assert entry.options["tariff_ils_per_kwh"] == 0.7
    assert entry.options["temp_sensor"] == ""  # cleared field is cleared


# 4
async def test_multi_instance_separate_storage_and_legacy_migration(hass, hass_storage):
    await setup_heater(hass, "dud", "dud2")
    hass_storage["dud_shemesh.data"] = {
        "version": 1, "key": "dud_shemesh.data",
        "data": {"schedules": [{"id": "legacy1", "name": "", "days_mask": 127, "time_hhmm": "06:00",
                                "duration_min": 30, "target_temp": None, "enabled": True, "created_at": 0}],
                 "history": [], "active_boost": None, "last_legionella": 0},
    }
    e1 = make_entry(hass)
    e2 = make_entry(hass, heater="input_boolean.dud2")
    d1 = await setup_entry(hass, e1)  # integration setup loads both entries
    d2 = hass.data[DOMAIN][e2.entry_id]

    assert [s["id"] for s in d1["store"].schedules] == ["legacy1"]
    assert d2["store"].schedules == []
    assert "dud_shemesh.data" not in hass_storage

    await hass.services.async_call(
        DOMAIN, "add_schedule",
        {"entry_id": e2.entry_id, "time": "07:00", "days": ["mon"]}, blocking=True,
    )
    assert len(d2["store"].schedules) == 1
    assert len(d1["store"].schedules) == 1

    await hass.services.async_call(DOMAIN, "boost", {"entry_id": e2.entry_id, "minutes": 10}, blocking=True)
    assert hass.states.get("input_boolean.dud2").state == "on"
    assert hass.states.get(HEATER).state == "off"

    # Unloading one entry keeps services working for the other.
    await hass.config_entries.async_unload(e1.entry_id)
    await hass.async_block_till_done()
    await hass.services.async_call(DOMAIN, "cancel_boost", {}, blocking=True)
    assert hass.states.get("input_boolean.dud2").state == "off"


# 5
@pytest.mark.parametrize(("status", "recorded"), [("completed", False), ("target_reached", True)])
async def test_legionella_only_recorded_on_target(hass, status, recorded):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass))
    sch = data["scheduler"]
    await sch.async_start_heat(source="legionella", duration_min=120, target_temp=60)
    await sch._async_close(status)
    assert bool(data["store"].last_legionella) is recorded


# 6
async def test_target_check_survives_reload(hass, freezer):
    await setup_heater(hass)
    entry = make_entry(hass)
    data = await setup_entry(hass, entry)
    await data["scheduler"].async_boost(60)

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    sch = hass.data[DOMAIN][entry.entry_id]["scheduler"]
    assert sch.active and sch._unsub_temp_check is not None

    hass.states.async_set(TEMP, "56")
    await _advance(hass, freezer, 60)
    assert sch.active is None
    assert _closes(hass.data[DOMAIN][entry.entry_id]["store"])[0]["status"] == "target_reached"


# 7
async def test_no_solar_samples_while_heating(hass):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass))
    sch = data["scheduler"]
    sch._temp_samples = [(1, 40.0), (2, 41.0)]
    await sch.async_boost(30)
    sch._track_temp_sample()
    assert sch._temp_samples == []


# 8
async def test_own_turn_off_records_single_close(hass):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass))
    events = []
    hass.bus.async_listen(f"{DOMAIN}_heat_finished", events.append)
    await data["scheduler"].async_boost(30)
    await data["scheduler"].async_stop_heat("manual_stop")
    await hass.async_block_till_done()
    closes = _closes(data["store"])
    assert [c["status"] for c in closes] == ["manual_stop"]
    assert len(events) == 1
    assert "actual_min" in closes[0] and "started_at" in closes[0]


# 9
async def test_two_schedules_same_minute_start_once(hass, freezer):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass))
    nxt = (dt_util.now() + timedelta(minutes=2)).replace(second=0, microsecond=0)
    hhmm = nxt.strftime("%H:%M")
    for dur in (30, 45):
        await data["store"].async_add_schedule("", 127, hhmm, dur)
    sch = data["scheduler"]
    real = sch._call_heater

    async def network_relay(entity_id, on):
        await asyncio.sleep(0)  # a real (network) relay suspends here
        await real(entity_id, on)

    freezer.move_to(nxt)
    with patch.object(sch, "_call_heater", side_effect=network_relay):
        async_fire_time_changed(hass, nxt)
        await hass.async_block_till_done()
    started = [h for h in data["store"].history if h["status"] == "started"]
    assert len(started) == 1
    assert data["scheduler"].active["duration_min"] == 30


# 10
async def test_stop_cancels_calendar_timers(hass):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass))
    unsub = MagicMock()
    data["scheduler"]._calendar_unsubs["k"] = unsub
    await data["scheduler"].async_stop()
    unsub.assert_called_once()


# 16
async def test_boost_accepts_string_minutes(hass):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass))
    await hass.services.async_call(DOMAIN, "boost", {"minutes": "15"}, blocking=True)
    assert data["scheduler"].active["duration_min"] == 15


# 17
async def test_ws_update_options_validation_and_admin(hass, hass_ws_client, hass_read_only_access_token):
    await setup_heater(hass)
    entry = make_entry(hass)
    await setup_entry(hass, entry)

    admin = await hass_ws_client(hass)
    await admin.send_json({"id": 1, "type": f"{DOMAIN}/update_options", "target_temp": 150})
    assert not (await admin.receive_json())["success"]

    user = await hass_ws_client(hass, hass_read_only_access_token)
    await user.send_json({"id": 1, "type": f"{DOMAIN}/update_options", "heater_wattage_w": 3000})
    msg = await user.receive_json()
    assert not msg["success"] and msg["error"]["code"] == "unauthorized"

    await user.send_json({"id": 2, "type": f"{DOMAIN}/update_options", "mode": "off"})
    assert (await user.receive_json())["success"]
    await hass.async_block_till_done()
    assert entry.options["mode"] == "off"


# 18
def test_calendar_description_clamped():
    m = sched_mod.RE_CAL_TEMP.search("heat to 600c please")
    assert max(sched_mod.CALENDAR_TEMP_MIN, min(sched_mod.CALENDAR_TEMP_MAX, int(m.group(1)))) == 80
    assert sched_mod.RE_CAL_DURATION.search("45 min").group(1) == "45"


# 23
async def test_temperature_sensor_device_class(hass):
    await setup_heater(hass)
    await setup_entry(hass, make_entry(hass))
    states = [s for s in hass.states.async_all("sensor") if s.attributes.get("device_class") == "temperature"]
    assert any(s.attributes.get("state_class") == "measurement" for s in states)
