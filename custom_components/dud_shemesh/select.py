"""Mode select (auto / schedule / off)."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MODE, MODE_AUTO, MODE_OFF, MODE_SCHEDULE
from .entity import DudEntity, async_update_options


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([DudModeSelect(hass, entry, "mode")])


class DudModeSelect(DudEntity, SelectEntity):
    _attr_translation_key = "mode"
    _attr_icon = "mdi:auto-mode"
    _attr_options = [MODE_AUTO, MODE_SCHEDULE, MODE_OFF]

    @property
    def current_option(self) -> str:
        return self.cfg.get("mode") or MODE_SCHEDULE

    async def async_select_option(self, option: str) -> None:
        async_update_options(self.hass, self._entry, {CONF_MODE: option})
