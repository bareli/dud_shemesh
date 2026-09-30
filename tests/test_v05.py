"""v0.5 features: weather at night, safety guard, upcoming, energy, skip-once."""
from __future__ import annotations

import time
from datetime import timedelta

from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.dud_shemesh.const import DOMAIN

from .conftest import HEATER, TEMP, make_entry, setup_entry, setup_heater


async def _advance(hass, freezer, seconds: int) -> None:
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


# 24
async def test_weather_skip_ignored_at_night_and_legacy_default_migrated(hass):
    await setup_heater(hass)
    entry = make_entry(hass, weather_entity="weather.home", weather_skip_states="sunny,clear-night")
    data = await setup_entry(hass, entry)
    assert entry.options["weather_skip_states"] == "sunny"

    sch = data["scheduler"]
    sch.options["weather_skip_states"] = "sunny,clear-night"
    hass.states.async_set("weather.home", "clear-night")
    hass.states.async_set("sun.sun", "below_horizon")
    assert sch._weather_says_sunny() is False
    hass.states.async_set("weather.home", "sunny")
    hass.states.async_set("sun.sun", "above_horizon")
    assert sch._weather_says_sunny() is True


# 27
async def test_manual_turn_on_is_adopted_and_turned_off(hass, freezer):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass, manual_on_max_min=30))
    await hass.services.async_call("input_boolean", "turn_on", {"entity_id": HEATER}, blocking=True)
    await hass.async_block_till_done()
    sch = data["scheduler"]
    assert sch.active and sch.active["source"] == "manual"

    await _advance(hass, freezer, 31 * 60)
    assert hass.states.get(HEATER).state == "off"
    assert data["store"].history[0]["status"] == "completed"


async def test_manual_guard_disabled_with_zero(hass):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass, manual_on_max_min=0))
    await hass.services.async_call("input_boolean", "turn_on", {"entity_id": HEATER}, blocking=True)
    await hass.async_block_till_done()
    assert data["scheduler"].active is None


async def test_max_run_caps_start_and_boost_extension(hass):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass, max_run_min=90))
    sch = data["scheduler"]
    await sch.async_boost(120)
    assert sch.active["duration_min"] == 90
    await sch.async_stop_heat()
    await sch.async_boost(60)
    await sch.async_boost(60)
    assert sch.active["ends_at"] - sch.active["started_at"] == 90 * 60


async def test_overtemp_stops_run(hass, freezer):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass, max_tank_temp=70, target_temp=80))
    await data["scheduler"].async_boost(60)
    hass.states.async_set(TEMP, "71")
    await _advance(hass, freezer, 60)
    assert data["scheduler"].active is None
    assert data["store"].history[0]["status"] == "safety_overtemp"


async def test_stale_sensor_reads_as_none(hass, freezer):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass, sensor_stale_min=10))
    assert data["scheduler"]._read_temp() == 40.0
    freezer.tick(timedelta(minutes=11))
    assert data["scheduler"]._read_temp() is None


# 26
async def test_upcoming_schedule_window_and_showers(hass):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(
        hass, mode="auto", tank_volume_l=150, auto_comfort_windows="23:59-23:59",
    ))
    sch = data["scheduler"]
    nxt = (dt_util.now() + timedelta(hours=2)).strftime("%H:%M")
    await data["store"].async_add_schedule("Shower", 127, nxt, 30)
    up = sch.upcoming()
    assert {"schedule", "auto"} <= {u["source"] for u in up}
    assert up == sorted(up, key=lambda u: u["at"])
    # 150 L at 40 °C: not above shower temp -> 0; at 60 °C: 150*40/20/50 = 6
    assert sch.showers_available() == 0
    hass.states.async_set(TEMP, "60")
    assert sch.showers_available() == 6

    sch.options["mode"] = "off"
    assert sch.upcoming() == []


# 38
async def test_skip_once(hass, freezer):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass))
    sch = data["scheduler"]
    at = (dt_util.now() + timedelta(minutes=2)).replace(second=0, microsecond=0)
    sched = await data["store"].async_add_schedule("", 127, at.strftime("%H:%M"), 30)
    first = sch.next_schedule_run(sched)
    await hass.services.async_call(
        DOMAIN, "update_schedule", {"schedule_id": sched["id"], "skip_until": first + 60}, blocking=True,
    )
    sched = data["store"].get_schedule(sched["id"])
    assert sch.next_schedule_run(sched) == first + 86400

    freezer.move_to(at)
    async_fire_time_changed(hass, at)
    await hass.async_block_till_done()
    assert sch.active is None
    assert data["store"].history[0]["status"] == "skipped_user"


# 29
async def test_energy_accumulates_and_persists(hass, freezer):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass, heater_wattage_w=3000))
    sch = data["scheduler"]
    await sch.async_boost(60)
    freezer.tick(timedelta(minutes=30))
    assert abs(sch.energy_total_kwh() - 1.5) < 0.01
    await sch.async_stop_heat()
    assert abs(data["store"].energy_kwh_total - 1.5) < 0.01
    assert abs(sch.energy_total_kwh() - 1.5) < 0.01

    energy = [s for s in hass.states.async_all("sensor") if s.attributes.get("device_class") == "energy"]
    assert energy and energy[0].attributes["state_class"] == "total_increasing"
    assert time.time()  # keep freezer import path honest
