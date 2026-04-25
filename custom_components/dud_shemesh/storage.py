"""Persistent storage for Dud Shemesh."""
from __future__ import annotations

import time
import uuid
from typing import Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION

MAX_HISTORY = 500


class DudStore:
    def __init__(self, hass: HomeAssistant):
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {
            "schedules": [],
            "history": [],
            "active_boost": None,
            "last_legionella": 0,
        }

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if data:
            self._data["schedules"] = data.get("schedules", [])
            self._data["history"] = data.get("history", [])
            self._data["active_boost"] = data.get("active_boost")
            self._data["last_legionella"] = int(data.get("last_legionella", 0))

    async def async_save(self) -> None:
        await self._store.async_save(self._data)

    @property
    def schedules(self) -> list[dict]:
        return list(self._data["schedules"])

    @property
    def history(self) -> list[dict]:
        return list(self._data["history"])

    @property
    def active_boost(self) -> Optional[dict]:
        return dict(self._data["active_boost"]) if self._data.get("active_boost") else None

    @property
    def last_legionella(self) -> int:
        return int(self._data.get("last_legionella", 0))

    def get_schedule(self, schedule_id: str) -> Optional[dict]:
        for s in self._data["schedules"]:
            if s["id"] == schedule_id:
                return s
        return None

    async def async_add_schedule(
        self,
        name: str,
        days_mask: int,
        time_hhmm: str,
        duration_min: int,
        target_temp: Optional[int] = None,
        enabled: bool = True,
    ) -> dict:
        sched = {
            "id": uuid.uuid4().hex[:12],
            "name": name,
            "days_mask": int(days_mask),
            "time_hhmm": time_hhmm,
            "duration_min": int(duration_min),
            "target_temp": int(target_temp) if target_temp is not None else None,
            "enabled": bool(enabled),
            "created_at": int(time.time()),
        }
        self._data["schedules"].append(sched)
        await self.async_save()
        return sched

    async def async_update_schedule(self, schedule_id: str, **fields: Any) -> Optional[dict]:
        s = self.get_schedule(schedule_id)
        if not s:
            return None
        for k in ("name", "days_mask", "time_hhmm", "duration_min", "target_temp", "enabled"):
            if k in fields and fields[k] is not None:
                if k in ("days_mask", "duration_min", "target_temp"):
                    s[k] = int(fields[k])
                elif k == "enabled":
                    s[k] = bool(fields[k])
                else:
                    s[k] = fields[k]
        await self.async_save()
        return s

    async def async_remove_schedule(self, schedule_id: str) -> bool:
        before = len(self._data["schedules"])
        self._data["schedules"] = [s for s in self._data["schedules"] if s["id"] != schedule_id]
        if len(self._data["schedules"]) != before:
            await self.async_save()
            return True
        return False

    async def async_set_active_boost(self, payload: Optional[dict]) -> None:
        self._data["active_boost"] = payload
        await self.async_save()

    async def async_set_last_legionella(self, ts: int) -> None:
        self._data["last_legionella"] = int(ts)
        await self.async_save()

    async def async_record_run(
        self,
        source: str,
        duration_min: int,
        status: str,
        starting_temp: Optional[float] = None,
        ending_temp: Optional[float] = None,
        note: str = "",
    ) -> None:
        entry = {
            "ts": int(time.time()),
            "source": source,
            "duration_min": int(duration_min),
            "status": status,
            "starting_temp": starting_temp,
            "ending_temp": ending_temp,
            "note": note,
        }
        self._data["history"].insert(0, entry)
        if len(self._data["history"]) > MAX_HISTORY:
            self._data["history"] = self._data["history"][:MAX_HISTORY]
        await self.async_save()
