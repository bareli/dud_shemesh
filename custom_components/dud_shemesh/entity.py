"""Shared entity base and helpers for Dud Shemesh platforms."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, SIGNAL_STATE_CHANGED


@callback
def async_update_options(hass: HomeAssistant, entry: ConfigEntry, patch: dict) -> dict:
    """Merge a patch into the entry options (triggers the reload listener)."""
    new_options = {**entry.options, **patch}
    hass.config_entries.async_update_entry(entry, options=new_options)
    return new_options


class DudEntity(Entity):
    """Base: one device per config entry, pushed updates from the scheduler and sensors."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, key: str) -> None:
        self._entry = entry
        self._data = hass.data[DOMAIN][entry.entry_id]
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Dud Shemesh",
            model="Smart solar water heater controller",
        )

    @property
    def scheduler(self):
        return self._data["scheduler"]

    @property
    def cfg(self) -> dict:
        """Integration options (not the enum `options` of sensor/select)."""
        return self._data["options"]

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_STATE_CHANGED, self.async_write_ha_state)
        )
        watched = [e for e in (self.cfg.get("temp_sensor"), self.cfg.get("heater_entity")) if e]
        if watched:
            self.async_on_remove(
                async_track_state_change_event(self.hass, watched, self._on_source_change)
            )

    @callback
    def _on_source_change(self, _event: Event) -> None:
        self.async_write_ha_state()
