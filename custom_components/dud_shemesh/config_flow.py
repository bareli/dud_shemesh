"""Config and options flow for Dud Shemesh."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_HEATER_ENTITY,
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


class DudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(
                title="Dud Shemesh",
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
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DudOptionsFlow(config_entry)


class DudOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self._entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        opts = self._entry.options
        schema = vol.Schema({
            vol.Required(
                CONF_HEATER_ENTITY,
                default=opts.get(CONF_HEATER_ENTITY, ""),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean"])
            ),
            vol.Optional(
                CONF_TEMP_SENSOR,
                default=opts.get(CONF_TEMP_SENSOR, ""),
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
        return self.async_show_form(step_id="init", data_schema=schema)
