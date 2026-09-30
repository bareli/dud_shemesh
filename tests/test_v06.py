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


# 46
async def test_ws_list_entries_and_entry_scoped_state(hass, hass_ws_client):
    await setup_heater(hass, "dud", "dud2")
    e1 = make_entry(hass)
    e2 = make_entry(hass, heater="input_boolean.dud2", target_temp=48)
    await setup_entry(hass, e1)
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "dud_shemesh/list_entries"})
    msg = await ws.receive_json()
    assert [e["entry_id"] for e in msg["result"]] == [e1.entry_id, e2.entry_id]
    await ws.send_json({"id": 2, "type": "dud_shemesh/get_state", "entry_id": e2.entry_id})
    msg = await ws.receive_json()
    assert msg["result"]["entry_id"] == e2.entry_id and msg["result"]["status"]["target_temp"] == 48


# 33
def _capture_notify(hass, name):
    calls = []

    async def handler(call):
        calls.append(dict(call.data))

    hass.services.async_register("notify", name, handler)
    return calls


async def test_actionable_notifications_and_action_handling(hass, freezer):
    await setup_heater(hass)
    mobile = _capture_notify(hass, "mobile_app_phone")
    other = _capture_notify(hass, "telegram")
    entry = make_entry(hass, notify_targets=["mobile_app_phone", "telegram"],
                       notify_events=["heat_not_rising", "manual_on"],
                       fail_detection_enabled=True, fail_detection_minutes=5)
    data = await setup_entry(hass, entry)
    sch = data["scheduler"]
    await sch.async_boost(60)
    await _advance(hass, freezer, 6 * 60)  # temp did not rise -> fault notification

    assert mobile and other
    actions = mobile[-1]["data"]["actions"]
    assert actions[0]["action"] == f"DUDSHEMESH:stop:0:{entry.entry_id}"
    assert "data" not in other[-1]  # non mobile_app notifiers get plain text

    hass.bus.async_fire("mobile_app_notification_action", {"action": actions[0]["action"]})
    await hass.async_block_till_done()
    assert sch.active is None

    hass.bus.async_fire("mobile_app_notification_action", {"action": f"DUDSHEMESH:boost:25:{entry.entry_id}"})
    await hass.async_block_till_done()
    assert sch.active and sch.active["duration_min"] == 25


async def test_cold_warning_once_before_window(hass, freezer):
    from homeassistant.util import dt as dt_util
    await setup_heater(hass)
    calls = _capture_notify(hass, "mobile_app_phone")
    ready = (dt_util.now() + timedelta(minutes=50)).replace(second=0, microsecond=0)
    data = await setup_entry(hass, make_entry(
        hass, mode="schedule", auto_comfort_windows=f"{ready:%H:%M}-{ready + timedelta(hours=1):%H:%M}",
        notify_targets=["mobile_app_phone"], notify_events=["cold_warning"],
    ))
    await _advance(hass, freezer, 60)
    await _advance(hass, freezer, 60)
    warnings = [c for c in calls if "won't be hot" in c["message"]]
    assert len(warnings) == 1
    assert warnings[0]["data"]["actions"][0]["action"].startswith("DUDSHEMESH:boost:60:")

    # a planned schedule before the window suppresses the warning
    data["scheduler"]._cold_warned.clear()
    calls.clear()
    at = dt_util.now() + timedelta(minutes=10)
    await data["store"].async_add_schedule("", 127, f"{at:%H:%M}", 30)
    await _advance(hass, freezer, 60)
    assert not [c for c in calls if "won't be hot" in c["message"]]


# security review: settings entities vs everyday controls
async def test_legionella_switch_requires_admin_vacation_does_not(hass, hass_owner_user):
    import pytest
    from homeassistant.core import Context
    from homeassistant.exceptions import Unauthorized
    await setup_heater(hass)
    entry = make_entry(hass)
    await setup_entry(hass, entry)
    family = await hass.auth.async_create_user("Family", group_ids=["system-users"])
    ctx = Context(user_id=family.id)
    assert not family.is_admin
    with pytest.raises(Unauthorized):
        await hass.services.async_call("switch", "turn_on", {"entity_id": _eid(hass, "switch", "_legionella")}, blocking=True, context=ctx)
    await hass.services.async_call("switch", "turn_on", {"entity_id": _eid(hass, "switch", "_legionella")}, blocking=True)
    await hass.async_block_till_done()
    assert entry.options["legionella_enabled"] is True
    await hass.services.async_call("switch", "turn_on", {"entity_id": _eid(hass, "switch", "_vacation")}, blocking=True, context=ctx)
    await hass.async_block_till_done()
    assert entry.options["vacation_until"] > 0


# 32
async def test_forecast_and_solar_entity_skip(hass):
    from homeassistant.core import SupportsResponse
    from homeassistant.util import dt as dt_util
    await setup_heater(hass)
    now = dt_util.utcnow().replace(minute=0, second=0, microsecond=0)
    forecast = [{"datetime": (now + timedelta(hours=h)).isoformat(), "condition": "partlycloudy",
                 "cloud_coverage": c} for h, c in enumerate([10, 20, 90, 30])]

    async def get_forecasts(call):
        return {"weather.home": {"forecast": forecast}}

    hass.services.async_register("weather", "get_forecasts", get_forecasts, supports_response=SupportsResponse.ONLY)
    hass.states.async_set("weather.home", "cloudy")
    hass.states.async_set("sun.sun", "above_horizon")
    data = await setup_entry(hass, make_entry(hass, weather_entity="weather.home", forecast_hours=3))
    sch = data["scheduler"]
    await sch._refresh_forecast()
    assert sch._weather_says_sunny() is True        # 3 of 4 slots <= 40 % cloud

    forecast[:] = [dict(f, cloud_coverage=80) for f in forecast]
    await sch._refresh_forecast()
    assert sch._weather_says_sunny() is False

    sch.options["solar_forecast_entity"] = "sensor.solar_next_hour"
    sch.options["solar_forecast_min"] = 1.5
    hass.states.async_set("sensor.solar_next_hour", "2.1")
    assert sch._weather_says_sunny() is True
    hass.states.async_set("sun.sun", "below_horizon")
    assert sch._weather_says_sunny() is False


# 34
async def test_time_of_use_price_cost_and_cheapest_start(hass, freezer):
    from homeassistant.util import dt as dt_util
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(
        hass, heater_wattage_w=3000, tariff_ils_per_kwh=0.62, tariff_windows="23:00-07:00@0.40",
    ))
    sch = data["scheduler"]
    evening = dt_util.now().replace(hour=20, minute=0, second=0, microsecond=0)
    freezer.move_to(evening)
    day2 = evening + timedelta(days=1)
    ts = lambda h, m=0: int(day2.replace(hour=h, minute=m).timestamp())  # noqa: E731

    assert sch.price_at(ts(2)) == 0.40 and sch.price_at(ts(12)) == 0.62
    assert abs(sch.run_cost(ts(6, 30), ts(7, 30)) - (0.5 * 3 * 0.40 + 0.5 * 3 * 0.62)) < 1e-6

    # ready 06:30: latest start 05:30 is already cheap -> keep it
    assert sch.plan_preheat_start(ts(6, 30), 60) == ts(5, 30)
    # ready 08:00: finish in the cheap window instead (06:00-07:00)
    assert sch.plan_preheat_start(ts(8), 60) == ts(6)
    sch.options["prefer_cheap"] = False
    assert sch.plan_preheat_start(ts(8), 60) == ts(7)


async def test_close_record_has_cost(hass, freezer):
    await setup_heater(hass)
    data = await setup_entry(hass, make_entry(hass, heater_wattage_w=2000, tariff_ils_per_kwh=0.5))
    await data["scheduler"].async_boost(60)
    freezer.tick(timedelta(minutes=30))
    await data["scheduler"].async_stop_heat()
    assert abs(data["store"].history[0]["cost"] - 0.5) < 0.01
