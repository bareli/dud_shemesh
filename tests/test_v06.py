"""v0.6 features."""
from __future__ import annotations

from datetime import timedelta

from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .conftest import TEMP, make_entry, setup_entry, setup_heater


async def _advance(hass, freezer, seconds: int) -> None:
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


# 31
async def test_heat_rate_fallback_physics_then_learned(hass, freezer):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass, heater_wattage_w=2500))
    sch = data["scheduler"]
    assert sch.heat_rate()[1] == "fallback"
    assert sch.estimate_minutes_to_target() == 90  # 15 °C x 6 min

    sch.options["tank_volume_l"] = 150
    rate, source = sch.heat_rate()
    assert source == "physics" and abs(rate - 2.5 * 60 * 0.95 / (150 * 4.186)) < 1e-9

    for end_temp in ("50", "52"):  # two runs of 20 min: +10 and +12 °C
        hass.states.async_set(TEMP, "40")
        await sch.async_boost(20)
        freezer.tick(timedelta(minutes=20))
        hass.states.async_set(TEMP, end_temp)
        await sch.async_stop_heat("completed")
    rate, source = sch.heat_rate()
    assert source == "learned"
    assert abs(rate - (0.3 * 0.6 + 0.7 * 0.5)) < 1e-3
    hass.states.async_set(TEMP, "45")
    assert sch.estimate_minutes_to_target() == round(10 / rate)


async def test_heat_rate_ignores_short_and_cancelled_runs(hass, freezer):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass))
    sch = data["scheduler"]
    await sch.async_boost(30)
    freezer.tick(timedelta(minutes=5))
    hass.states.async_set(TEMP, "45")
    await sch.async_stop_heat("completed")      # too short
    await sch.async_boost(30)
    freezer.tick(timedelta(minutes=20))
    hass.states.async_set(TEMP, "55")
    await sch.async_stop_heat("cancelled")      # not a clean run
    assert data["store"].heat_rate["samples"] == 0


# 28
def _eid(hass, platform: str, unique_suffix: str) -> str:
    from homeassistant.helpers import entity_registry as er
    reg = er.async_get(hass)
    for e in reg.entities.values():
        if e.domain == platform and e.unique_id.endswith(unique_suffix):
            return e.entity_id
    raise AssertionError(f"no {platform} *{unique_suffix}")


async def test_native_entities(hass):
    await setup_heater(hass)
    entry = make_entry(hass, boost_buttons="15,45")
    data = await setup_entry(hass, entry)
    sch = data["scheduler"]

    wh = _eid(hass, "water_heater", "_water_heater")
    state = hass.states.get(wh)
    assert state.state == "schedule" and state.attributes["current_temperature"] == 40

    await hass.services.async_call("water_heater", "set_temperature", {"entity_id": wh, "temperature": 60}, blocking=True)
    await hass.async_block_till_done()
    assert entry.options["target_temp"] == 60

    await hass.services.async_call("water_heater", "set_operation_mode", {"entity_id": wh, "operation_mode": "auto"}, blocking=True)
    await hass.async_block_till_done()
    assert entry.options["mode"] == "auto"

    await hass.services.async_call("water_heater", "set_away_mode", {"entity_id": wh, "away_mode": True}, blocking=True)
    await hass.async_block_till_done()
    assert entry.options["vacation_until"] > 0
    assert hass.states.get(_eid(hass, "switch", "_vacation")).state == "on"

    sch = hass.data["dud_shemesh"][entry.entry_id]["scheduler"]
    await hass.services.async_call("water_heater", "turn_on", {"entity_id": wh}, blocking=True)
    await hass.async_block_till_done()
    assert sch.active and sch.active["duration_min"] == 15
    assert hass.states.get(_eid(hass, "binary_sensor", "_heating_active")).state == "on"

    await hass.services.async_call("button", "press", {"entity_id": _eid(hass, "button", "_stop")}, blocking=True)
    await hass.async_block_till_done()
    assert sch.active is None

    await hass.services.async_call("button", "press", {"entity_id": _eid(hass, "button", "_boost_45")}, blocking=True)
    assert sch.active["duration_min"] == 45
    await hass.services.async_call("switch", "turn_off", {"entity_id": _eid(hass, "switch", "_heating")}, blocking=True)
    assert sch.active is None

    await hass.services.async_call("select", "select_option", {"entity_id": _eid(hass, "select", "_mode"), "option": "off"}, blocking=True)
    await hass.async_block_till_done()
    assert entry.options["mode"] == "off"


async def test_stale_boost_buttons_removed(hass):
    from homeassistant.helpers import entity_registry as er
    await setup_heater(hass)
    entry = make_entry(hass, boost_buttons="30,60")
    await setup_entry(hass, entry)
    hass.config_entries.async_update_entry(entry, options={**entry.options, "boost_buttons": "60"})
    await hass.async_block_till_done()
    ids = [e.unique_id for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id) if e.domain == "button"]
    assert any(i.endswith("_boost_60") for i in ids)
    assert not any(i.endswith("_boost_30") for i in ids)
