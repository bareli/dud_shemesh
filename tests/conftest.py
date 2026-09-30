"""Shared fixtures for Dud Shemesh tests."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.dud_shemesh.const import DOMAIN

HEATER = "input_boolean.dud"
TEMP = "sensor.tank"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def no_frontend():
    """Panel / Lovelace registration needs the real frontend; not under test."""
    with patch(
        "custom_components.dud_shemesh._async_register_panel", return_value=None
    ), patch(
        "custom_components.dud_shemesh._async_register_card_resource", return_value=None
    ):
        yield


async def setup_heater(hass: HomeAssistant, *names: str, initial: bool = False) -> None:
    conf = {n: {"initial": initial} for n in (names or ("dud",))}
    await async_setup_component(hass, "input_boolean", {"input_boolean": conf})
    await async_setup_component(hass, "websocket_api", {})
    hass.states.async_set(TEMP, "40")
    await hass.async_block_till_done()


def make_entry(hass: HomeAssistant, heater: str = HEATER, **options) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dud Shemesh",
        data={},
        options={"heater_entity": heater, "temp_sensor": TEMP, "target_temp": 55, **options},
    )
    entry.add_to_hass(hass)
    return entry


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry):
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return hass.data[DOMAIN][entry.entry_id]
