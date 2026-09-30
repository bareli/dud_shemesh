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
