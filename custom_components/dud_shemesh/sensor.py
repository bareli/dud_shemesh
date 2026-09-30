"""Sensor entities for Dud Shemesh."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfTemperature, UnitOfTime
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

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
        DudEnergySensor(entry.entry_id, data["scheduler"]),
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
        nxt = s.get("next_heat") or {}
        return {
            "current_temp": s.get("current_temp"),
            "target_temp": s.get("target_temp"),
            "active": s.get("active"),
            "next_heat_at": dt_util.utc_from_timestamp(nxt["at"]).isoformat() if nxt else None,
            "next_heat_source": nxt.get("source"),
            "next_heat_label": nxt.get("label"),
            "hot_by": dt_util.utc_from_timestamp(nxt["ready_by"]).isoformat() if nxt.get("ready_by") else None,
            "showers_available": s.get("showers_available"),
        }


class DudTempSensor(_BaseSensor):
    _attr_name = "Tank temperature"
    _attr_icon = "mdi:thermometer"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

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
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, entry_id, scheduler):
        super().__init__(entry_id, scheduler)
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_minutes_to_target"
        self._attr_should_poll = True

    @property
    def native_value(self):
        return self._scheduler.estimate_minutes_to_target()


class DudEnergySensor(_BaseSensor):
    """Element energy for the HA Energy dashboard (on-time x configured wattage)."""

    _attr_name = "Energy"
    _attr_icon = "mdi:lightning-bolt"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 2

    def __init__(self, entry_id, scheduler):
        super().__init__(entry_id, scheduler)
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_energy"
        self._attr_should_poll = True  # climbs while the element is on

    @property
    def native_value(self):
        return self._scheduler.energy_total_kwh()
