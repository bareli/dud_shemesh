"""Binary sensors: heating, solar gaining, temperature sensor problem."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import DudEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([
        DudHeatingBinary(hass, entry, "heating_active"),
        DudSolarBinary(hass, entry, "solar_gaining"),
        DudSensorProblem(hass, entry, "sensor_problem"),
    ])


class DudHeatingBinary(DudEntity, BinarySensorEntity):
    _attr_translation_key = "heating_active"
    _attr_device_class = BinarySensorDeviceClass.HEAT

    @property
    def is_on(self) -> bool:
        return bool(self.scheduler.active)


class DudSolarBinary(DudEntity, BinarySensorEntity):
    _attr_translation_key = "solar_gaining"
    _attr_icon = "mdi:solar-power"
    _attr_should_poll = True  # rolling temperature window, no event of its own

    @property
    def is_on(self) -> bool:
        return self.scheduler.now_status().get("solar_gaining", False)


class DudSensorProblem(DudEntity, BinarySensorEntity):
    _attr_translation_key = "sensor_problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = True  # staleness grows with time, not with events

    @property
    def available(self) -> bool:
        return bool(self.cfg.get("temp_sensor"))

    @property
    def is_on(self) -> bool:
        return self.scheduler.now_status().get("current_temp") is None
