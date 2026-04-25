"""Sensor entities for Dud Shemesh."""
from __future__ import annotations

import time
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_STATE_CHANGED


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DudStatusSensor(entry.entry_id, data["scheduler"]),
        DudTempSensor(entry.entry_id, data["scheduler"]),
        DudMinutesToTargetSensor(entry.entry_id, data["scheduler"]),
    ])


class _BaseSensor(SensorEntity):
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, entry_id: str, scheduler):
        self._scheduler = scheduler
        self._entry_id = entry_id
        self._unsub = None

    async def async_added_to_hass(self) -> None:
        self._unsub = async_dispatcher_connect(self.hass, SIGNAL_STATE_CHANGED, self._handle)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()

    @callback
    def _handle(self) -> None:
        self.async_write_ha_state()


class DudStatusSensor(_BaseSensor):
    _attr_name = "Status"
    _attr_icon = "mdi:water-boiler"

    def __init__(self, entry_id, scheduler):
        super().__init__(entry_id, scheduler)
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_status"

    @property
    def native_value(self) -> str:
        return self._scheduler.now_status().get("status", "unknown")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        s = self._scheduler.now_status()
        return {
            "current_temp": s.get("current_temp"),
            "target_temp": s.get("target_temp"),
            "active": s.get("active"),
        }


class DudTempSensor(_BaseSensor):
    _attr_name = "Tank temperature"
    _attr_icon = "mdi:thermometer"
    _attr_native_unit_of_measurement = "°C"

    def __init__(self, entry_id, scheduler):
        super().__init__(entry_id, scheduler)
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_tank_temp"
        self._attr_should_poll = True

    @property
    def native_value(self):
        return self._scheduler.now_status().get("current_temp")


class DudMinutesToTargetSensor(_BaseSensor):
    _attr_name = "Minutes to target"
    _attr_icon = "mdi:timer-sand"
    _attr_native_unit_of_measurement = "min"

    def __init__(self, entry_id, scheduler):
        super().__init__(entry_id, scheduler)
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_minutes_to_target"
        self._attr_should_poll = True

    @property
    def native_value(self):
        return self._scheduler.estimate_minutes_to_target()
