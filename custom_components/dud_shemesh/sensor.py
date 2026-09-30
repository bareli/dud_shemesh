"""Sensor entities for Dud Shemesh."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .entity import DudEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([
        DudStatusSensor(hass, entry, "status"),
        DudTempSensor(hass, entry, "tank_temp"),
        DudMinutesToTargetSensor(hass, entry, "minutes_to_target"),
        DudEnergySensor(hass, entry, "energy"),
    ])


class DudStatusSensor(DudEntity, SensorEntity):
    _attr_translation_key = "status"
    _attr_icon = "mdi:water-boiler"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["ready", "heating", "waiting", "solar", "cold"]

    @property
    def native_value(self) -> str:
        return self.scheduler.now_status().get("status", "waiting")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        s = self.scheduler.now_status()
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
            "heat_rate_c_per_min": s.get("heat_rate_c_per_min"),
            "heat_rate_source": s.get("heat_rate_source"),
        }


class DudTempSensor(DudEntity, SensorEntity):
    _attr_translation_key = "tank_temperature"
    _attr_icon = "mdi:thermometer"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self):
        return self.scheduler.now_status().get("current_temp")


class DudMinutesToTargetSensor(DudEntity, SensorEntity):
    _attr_translation_key = "minutes_to_target"
    _attr_icon = "mdi:timer-sand"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    @property
    def native_value(self):
        return self.scheduler.estimate_minutes_to_target()


class DudEnergySensor(DudEntity, SensorEntity):
    """Element energy for the HA Energy dashboard (on-time x configured wattage)."""

    _attr_translation_key = "energy"
    _attr_icon = "mdi:lightning-bolt"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 2
    _attr_should_poll = True  # climbs while the element is on

    @property
    def native_value(self):
        return self.scheduler.energy_total_kwh()
