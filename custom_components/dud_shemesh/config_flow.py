"""Config and options flow for Dud Shemesh."""
from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_AUTO_COMFORT_WINDOWS,
    CONF_HEATER_ENTITY,
    CONF_TANK_VOLUME_L,
    CONF_TARIFF_ILS_PER_KWH,
    DEFAULT_TANK_VOLUME_L,
    DEFAULT_TARIFF_ILS_PER_KWH,
    CONF_HEATER_WATTAGE,
    CONF_LEGIONELLA_DAYS,
    CONF_LEGIONELLA_ENABLED,
    CONF_LEGIONELLA_TEMP,
    CONF_MODE,
    CONF_TARGET_TEMP,
    CONF_TEMP_SENSOR,
    DEFAULT_HEATER_WATTAGE,
    DEFAULT_LEGIONELLA_DAYS,
    DEFAULT_LEGIONELLA_TEMP,
    DEFAULT_MODE,
    DEFAULT_TARGET_TEMP,
    DOMAIN,
    MODE_AUTO,
    MODE_OFF,
    MODE_SCHEDULE,
)


RE_WINDOW = re.compile(r"^([01]?\d|2[0-3]):[0-5]\d-([01]?\d|2[0-3]):[0-5]\d$")


def valid_windows(value: str) -> bool:
    """Empty, or comma-separated HH:MM-HH:MM ranges."""
    parts = [p.strip() for p in str(value or "").split(",") if p.strip()]
    return all(RE_WINDOW.match(p) for p in parts)


def _setup_fields(defaults: dict) -> dict:
    """Tank / price / comfort windows, shared by the config and options flows."""
    return {
        vol.Optional(CONF_TANK_VOLUME_L, default=defaults.get(CONF_TANK_VOLUME_L, DEFAULT_TANK_VOLUME_L)): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=1000, step=10, unit_of_measurement="L", mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Optional(CONF_TARIFF_ILS_PER_KWH, default=defaults.get(CONF_TARIFF_ILS_PER_KWH, DEFAULT_TARIFF_ILS_PER_KWH)): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=10, step=0.01, unit_of_measurement="₪/kWh", mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Optional(
            CONF_AUTO_COMFORT_WINDOWS,
            description={"suggested_value": defaults.get(CONF_AUTO_COMFORT_WINDOWS) or None},
        ): selector.TextSelector(),
    }


class DudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            if not valid_windows(user_input.get(CONF_AUTO_COMFORT_WINDOWS, "")):
                errors[CONF_AUTO_COMFORT_WINDOWS] = "invalid_windows"
            else:
                heater = user_input.get(CONF_HEATER_ENTITY, "")
                label_part = heater.split(".")[-1].replace("_", " ").title() if heater else ""
                title = f"Dud Shemesh — {label_part}" if label_part else "Dud Shemesh"
                return self.async_create_entry(
                    title=title,
                    data={},
                    options=user_input,
                )
        schema = vol.Schema({
            vol.Required(CONF_HEATER_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean"])
            ),
            vol.Optional(CONF_TEMP_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Optional(CONF_TARGET_TEMP, default=DEFAULT_TARGET_TEMP): selector.NumberSelector(
                selector.NumberSelectorConfig(min=20, max=80, step=1, unit_of_measurement="°C")
            ),
            vol.Optional(CONF_HEATER_WATTAGE, default=DEFAULT_HEATER_WATTAGE): selector.NumberSelector(
                selector.NumberSelectorConfig(min=500, max=10000, step=100, unit_of_measurement="W")
            ),
            **_setup_fields(user_input or {}),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DudOptionsFlow(config_entry)


class DudOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self._entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        opts = self._entry.options
        errors: dict[str, str] = {}
        if user_input is not None:
            if not valid_windows(user_input.get(CONF_AUTO_COMFORT_WINDOWS, "")):
                errors[CONF_AUTO_COMFORT_WINDOWS] = "invalid_windows"
            else:
                # Merge: keys set from the panel (notify, vacation, weather, ...) are
                # not part of this form and must survive.
                new_options = {**opts, **user_input}
                for cleared in (CONF_TEMP_SENSOR, CONF_AUTO_COMFORT_WINDOWS):
                    if cleared not in user_input:
                        new_options[cleared] = ""
                return self.async_create_entry(title="", data=new_options)
        schema = vol.Schema({
            vol.Required(
                CONF_HEATER_ENTITY,
                default=opts.get(CONF_HEATER_ENTITY, ""),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean"])
            ),
            vol.Optional(
                CONF_TEMP_SENSOR,
                description={"suggested_value": opts.get(CONF_TEMP_SENSOR) or None},
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Optional(
                CONF_TARGET_TEMP,
                default=opts.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=20, max=80, step=1, unit_of_measurement="°C")
            ),
            vol.Optional(
                CONF_HEATER_WATTAGE,
                default=opts.get(CONF_HEATER_WATTAGE, DEFAULT_HEATER_WATTAGE),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=500, max=10000, step=100, unit_of_measurement="W")
            ),
            **_setup_fields({**opts, **(user_input or {})}),
            vol.Optional(
                CONF_MODE,
                default=opts.get(CONF_MODE, DEFAULT_MODE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[MODE_AUTO, MODE_SCHEDULE, MODE_OFF],
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Optional(
                CONF_LEGIONELLA_ENABLED,
                default=opts.get(CONF_LEGIONELLA_ENABLED, False),
            ): selector.BooleanSelector(),
            vol.Optional(
                CONF_LEGIONELLA_TEMP,
                default=opts.get(CONF_LEGIONELLA_TEMP, DEFAULT_LEGIONELLA_TEMP),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=55, max=80, step=1, unit_of_measurement="°C")
            ),
            vol.Optional(
                CONF_LEGIONELLA_DAYS,
                default=opts.get(CONF_LEGIONELLA_DAYS, DEFAULT_LEGIONELLA_DAYS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=30, step=1, unit_of_measurement="d")
            ),
        })
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
