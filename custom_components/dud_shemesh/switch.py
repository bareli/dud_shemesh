"""Switches: heating now, vacation, anti-Legionella."""
from __future__ import annotations

import time
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_LEGIONELLA_ENABLED, CONF_VACATION_UNTIL
from .entity import DudEntity, async_update_options
from .water_heater import AWAY_DEFAULT_DAYS, first_boost_minutes


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([
        DudHeatingSwitch(hass, entry, "heating"),
        DudVacationSwitch(hass, entry, "vacation"),
        DudLegionellaSwitch(hass, entry, "legionella"),
    ])


class DudHeatingSwitch(DudEntity, SwitchEntity):
    """On = heat now for the first boost duration; off = stop."""

    _attr_translation_key = "heating"
    _attr_icon = "mdi:water-boiler"

    @property
    def is_on(self) -> bool:
        return bool(self.scheduler.active)

    async def async_turn_on(self, **kwargs: Any) -> None:
        if not self.scheduler.active:
            await self.scheduler.async_boost(first_boost_minutes(self.cfg))

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.scheduler.async_stop_heat("cancelled")


class DudVacationSwitch(DudEntity, SwitchEntity):
    _attr_translation_key = "vacation"
    _attr_icon = "mdi:bag-suitcase"

    @property
    def is_on(self) -> bool:
        return int(self.cfg.get("vacation_until") or 0) > time.time()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"until": int(self.cfg.get("vacation_until") or 0) or None}

    async def async_turn_on(self, **kwargs: Any) -> None:
        async_update_options(self.hass, self._entry, {CONF_VACATION_UNTIL: int(time.time()) + AWAY_DEFAULT_DAYS * 86400})

    async def async_turn_off(self, **kwargs: Any) -> None:
        async_update_options(self.hass, self._entry, {CONF_VACATION_UNTIL: 0})


class DudLegionellaSwitch(DudEntity, SwitchEntity):
    _attr_translation_key = "legionella"
    _attr_icon = "mdi:bacteria-outline"

    @property
    def is_on(self) -> bool:
        return bool(self.cfg.get("legionella_enabled"))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_require_admin()
        async_update_options(self.hass, self._entry, {CONF_LEGIONELLA_ENABLED: True})

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_require_admin()
        async_update_options(self.hass, self._entry, {CONF_LEGIONELLA_ENABLED: False})
