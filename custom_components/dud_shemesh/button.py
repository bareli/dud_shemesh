"""Button entities: one per boost duration, stop, anti-Legionella now."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_LEGIONELLA_TEMP, DOMAIN
from .entity import DudEntity


def boost_minutes(options: dict) -> list[int]:
    out: list[int] = []
    for part in str(options.get("boost_buttons") or "30,60,120").split(","):
        try:
            value = int(part.strip())
        except ValueError:
            continue
        if 0 < value <= 720 and value not in out:
            out.append(value)
    return out or [30, 60, 120]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    options = hass.data[DOMAIN][entry.entry_id]["options"]
    minutes = boost_minutes(options)

    # Boost durations are configurable; drop buttons for durations no longer offered.
    wanted = {f"{DOMAIN}_{entry.entry_id}_boost_{m}" for m in minutes}
    registry = er.async_get(hass)
    for reg in er.async_entries_for_config_entry(registry, entry.entry_id):
        if reg.domain == "button" and "_boost_" in reg.unique_id and reg.unique_id not in wanted:
            registry.async_remove(reg.entity_id)

    entities: list[ButtonEntity] = [DudBoostButton(hass, entry, m) for m in minutes]
    entities += [DudStopButton(hass, entry, "stop"), DudLegionellaButton(hass, entry, "legionella_now")]
    async_add_entities(entities)


class DudBoostButton(DudEntity, ButtonEntity):
    _attr_translation_key = "boost"
    _attr_icon = "mdi:fire"

    def __init__(self, hass, entry, minutes: int) -> None:
        super().__init__(hass, entry, f"boost_{minutes}")
        self._minutes = minutes
        self._attr_translation_placeholders = {"minutes": str(minutes)}

    async def async_press(self) -> None:
        await self.scheduler.async_boost(self._minutes)


class DudStopButton(DudEntity, ButtonEntity):
    _attr_translation_key = "stop"
    _attr_icon = "mdi:stop-circle-outline"

    async def async_press(self) -> None:
        await self.scheduler.async_stop_heat("cancelled")


class DudLegionellaButton(DudEntity, ButtonEntity):
    _attr_translation_key = "legionella_now"
    _attr_icon = "mdi:bacteria-outline"

    async def async_press(self) -> None:
        await self.scheduler.async_start_heat(
            source="legionella", duration_min=120,
            target_temp=int(self.cfg.get("legionella_temp") or DEFAULT_LEGIONELLA_TEMP),
            note="manual anti-legionella",
        )
