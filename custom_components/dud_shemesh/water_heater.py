"""Native water_heater entity: target temperature, mode, away (vacation), on/off."""
from __future__ import annotations

import time
from typing import Any

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MODE,
    CONF_TARGET_TEMP,
    CONF_VACATION_UNTIL,
    DEFAULT_TARGET_TEMP,
    MODE_AUTO,
    MODE_OFF,
    MODE_SCHEDULE,
)
from .entity import DudEntity, async_update_options

AWAY_DEFAULT_DAYS = 7


def first_boost_minutes(options: dict) -> int:
    for part in str(options.get("boost_buttons") or "60").split(","):
        try:
            value = int(part.strip())
        except ValueError:
            continue
        if 0 < value <= 720:
            return value
    return 60


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([DudWaterHeater(hass, entry, "water_heater")])


class DudWaterHeater(DudEntity, WaterHeaterEntity):
    _attr_name = None  # the device itself
    _attr_translation_key = "dud"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 20
    _attr_max_temp = 80
    _attr_target_temperature_step = 1
    _attr_operation_list = [MODE_AUTO, MODE_SCHEDULE, MODE_OFF]
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.AWAY_MODE
        | WaterHeaterEntityFeature.ON_OFF
    )

    @property
    def current_temperature(self) -> float | None:
        return self.scheduler.now_status().get("current_temp")

    @property
    def target_temperature(self) -> float:
        return float(self.cfg.get("target_temp") or DEFAULT_TARGET_TEMP)

    @property
    def current_operation(self) -> str:
        return self.cfg.get("mode") or MODE_SCHEDULE

    @property
    def is_away_mode_on(self) -> bool:
        return int(self.cfg.get("vacation_until") or 0) > time.time()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        active = self.scheduler.active
        return {
            "heating": bool(active),
            "heating_source": active.get("source") if active else None,
            "heating_ends_at": active.get("ends_at") if active else None,
        }

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is not None:
            async_update_options(self.hass, self._entry, {CONF_TARGET_TEMP: int(round(temp))})

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        async_update_options(self.hass, self._entry, {CONF_MODE: operation_mode})

    async def async_turn_away_mode_on(self) -> None:
        async_update_options(self.hass, self._entry, {CONF_VACATION_UNTIL: int(time.time()) + AWAY_DEFAULT_DAYS * 86400})

    async def async_turn_away_mode_off(self) -> None:
        async_update_options(self.hass, self._entry, {CONF_VACATION_UNTIL: 0})

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Heat now for the first boost duration (extends a running session)."""
        await self.scheduler.async_boost(first_boost_minutes(self.cfg))

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.scheduler.async_stop_heat("cancelled")
