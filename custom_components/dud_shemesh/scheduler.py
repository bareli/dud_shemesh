"""Dud Shemesh scheduler — boost, schedule, anti-legionella."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Optional

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_time_change,
)
from homeassistant.util import dt as dt_util

from .const import (
    DAY_BITS,
    DEFAULT_LEGIONELLA_DAYS,
    DEFAULT_LEGIONELLA_TEMP,
    DEFAULT_TARGET_TEMP,
    EVENT_HEAT_FINISHED,
    EVENT_HEAT_STARTED,
    EVENT_TARGET_REACHED,
    MODE_OFF,
    MODE_SCHEDULE,
    SIGNAL_STATE_CHANGED,
)
from .storage import DudStore

LOG = logging.getLogger(__name__)

ON_STATES = {"on", "open", "active"}


class DudScheduler:
    def __init__(self, hass: HomeAssistant, store: DudStore, options: dict):
        self.hass = hass
        self.store = store
        self.options = options
        self._unsub_minute = None
        self._unsub_temp_check = None
        self._unsub_close = None
        self._active = None  # {source, started_at, ends_at, target_temp, schedule_id, starting_temp}
        self._last_minute_fired: Optional[str] = None

    @property
    def active(self) -> Optional[dict]:
        return dict(self._active) if self._active else None

    async def async_start(self) -> None:
        self._unsub_minute = async_track_time_change(self.hass, self._on_minute, second=0)
        await self._restore_active_boost()
        LOG.info("dud_shemesh scheduler started")

    async def async_stop(self) -> None:
        if self._unsub_minute:
            self._unsub_minute()
            self._unsub_minute = None
        if self._unsub_temp_check:
            self._unsub_temp_check()
            self._unsub_temp_check = None
        if self._unsub_close:
            self._unsub_close()
            self._unsub_close = None
        self._active = None

    async def _restore_active_boost(self) -> None:
        boost = self.store.active_boost
        if not boost:
            return
        ends_at = int(boost.get("ends_at", 0))
        if ends_at <= int(time.time()):
            await self._async_close("expired_during_downtime")
            return
        heater = self.options.get("heater_entity")
        state = self.hass.states.get(heater) if heater else None
        if not state or state.state not in ON_STATES:
            await self.store.async_set_active_boost(None)
            return
        self._active = boost
        remaining = ends_at - int(time.time())
        self._unsub_close = async_call_later(self.hass, remaining, self._on_close_timer)
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    @callback
    def _on_minute(self, now: datetime) -> None:
        local = dt_util.as_local(now)
        key = local.strftime("%Y-%m-%d %H:%M")
        if key == self._last_minute_fired:
            return
        if local.second > 30 and self._last_minute_fired is None:
            self._last_minute_fired = key
            return
        self._last_minute_fired = key

        mode = self.options.get("mode", MODE_SCHEDULE)
        if mode == MODE_OFF:
            return

        bit = DAY_BITS[local.weekday()]
        hhmm = local.strftime("%H:%M")
        for sched in self.store.schedules:
            if not sched.get("enabled"):
                continue
            if not (int(sched.get("days_mask", 0)) & bit):
                continue
            if sched.get("time_hhmm") != hhmm:
                continue
            if self._active:
                LOG.debug("skip schedule %s: heater already running", sched["id"])
                continue
            target_temp = sched.get("target_temp")
            current_temp = self._read_temp()
            if target_temp is not None and current_temp is not None and current_temp >= target_temp:
                LOG.info(
                    "skip schedule %s: tank already at %.1f°C (target %d°C)",
                    sched["id"], current_temp, target_temp,
                )
                self.hass.async_create_task(self.store.async_record_run(
                    "schedule", int(sched.get("duration_min", 60)), "skipped_warm",
                    starting_temp=current_temp, note=f"schedule:{sched['id']}",
                ))
                continue
            self.hass.async_create_task(self.async_start_heat(
                source="schedule",
                duration_min=int(sched.get("duration_min", 60)),
                target_temp=target_temp,
                note=f"schedule:{sched['id']}",
                schedule_id=sched["id"],
            ))

        # Anti-Legionella check, run once per day at 03:00 local
        if hhmm == "03:00":
            self._maybe_legionella()

    def _maybe_legionella(self) -> None:
        if not self.options.get("legionella_enabled"):
            return
        days = int(self.options.get("legionella_days", DEFAULT_LEGIONELLA_DAYS))
        last = self.store.last_legionella
        if last and (int(time.time()) - last) < days * 86400:
            return
        if self._active:
            return
        target = int(self.options.get("legionella_temp", DEFAULT_LEGIONELLA_TEMP))
        LOG.info("dud_shemesh: anti-legionella firing, target %d°C", target)
        self.hass.async_create_task(self.async_start_heat(
            source="legionella", duration_min=120, target_temp=target,
            note="anti-legionella",
        ))

    def _read_temp(self) -> Optional[float]:
        sensor = self.options.get("temp_sensor")
        if not sensor:
            return None
        s = self.hass.states.get(sensor)
        if not s:
            return None
        try:
            return float(s.state)
        except (TypeError, ValueError):
            return None

    async def async_start_heat(
        self,
        source: str,
        duration_min: int,
        target_temp: Optional[int] = None,
        note: str = "",
        schedule_id: Optional[str] = None,
    ) -> None:
        heater = self.options.get("heater_entity")
        if not heater:
            raise ValueError("no heater_entity configured")

        if self._active:
            await self.async_stop_heat(reason="superseded")

        await self._call_heater(heater, on=True)

        starting_temp = self._read_temp()
        ends_at = int(time.time()) + max(60, int(duration_min) * 60)
        self._active = {
            "source": source,
            "started_at": int(time.time()),
            "ends_at": ends_at,
            "duration_min": int(duration_min),
            "target_temp": target_temp,
            "starting_temp": starting_temp,
            "schedule_id": schedule_id,
            "note": note,
        }
        await self.store.async_set_active_boost(self._active)
        await self.store.async_record_run(
            source, int(duration_min), "started",
            starting_temp=starting_temp, note=note,
        )
        self.hass.bus.async_fire(EVENT_HEAT_STARTED, {
            "source": source, "duration_min": int(duration_min),
            "target_temp": target_temp, "starting_temp": starting_temp,
            "note": note,
        })
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

        if self._unsub_close:
            self._unsub_close()
        self._unsub_close = async_call_later(
            self.hass, ends_at - int(time.time()), self._on_close_timer
        )

        # Per-minute target temp check while heating
        if self._unsub_temp_check:
            self._unsub_temp_check()
        self._unsub_temp_check = async_track_time_change(
            self.hass, self._on_temp_check, second=15
        )

    async def _on_close_timer(self, _now) -> None:
        await self._async_close("completed")

    @callback
    def _on_temp_check(self, _now) -> None:
        if not self._active:
            if self._unsub_temp_check:
                self._unsub_temp_check()
                self._unsub_temp_check = None
            return
        target = self._active.get("target_temp")
        if target is None:
            return
        cur = self._read_temp()
        if cur is None:
            return
        if cur >= target:
            self.hass.bus.async_fire(EVENT_TARGET_REACHED, {
                "source": self._active.get("source"),
                "temp": cur,
                "target_temp": target,
            })
            self.hass.async_create_task(self._async_close("target_reached"))

    async def async_stop_heat(self, reason: str = "manual_stop") -> None:
        await self._async_close(reason)

    async def _async_close(self, status: str) -> None:
        active = self._active
        heater = self.options.get("heater_entity")
        if heater:
            await self._call_heater(heater, on=False)
        self._active = None
        await self.store.async_set_active_boost(None)
        if self._unsub_close:
            self._unsub_close()
            self._unsub_close = None
        if self._unsub_temp_check:
            self._unsub_temp_check()
            self._unsub_temp_check = None
        if active:
            ending_temp = self._read_temp()
            await self.store.async_record_run(
                active.get("source", "manual"),
                active.get("duration_min", 0),
                status,
                starting_temp=active.get("starting_temp"),
                ending_temp=ending_temp,
                note=active.get("note", ""),
            )
            self.hass.bus.async_fire(EVENT_HEAT_FINISHED, {
                "source": active.get("source"),
                "status": status,
                "duration_min": active.get("duration_min"),
                "starting_temp": active.get("starting_temp"),
                "ending_temp": ending_temp,
            })
            if active.get("source") == "legionella" and status in ("completed", "target_reached"):
                await self.store.async_set_last_legionella(int(time.time()))
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    async def async_boost(self, minutes: int) -> None:
        target = int(self.options.get("target_temp") or DEFAULT_TARGET_TEMP)
        await self.async_start_heat(
            source="boost", duration_min=int(minutes),
            target_temp=target, note=f"manual+{minutes}m",
        )

    async def _call_heater(self, entity_id: str, on: bool) -> None:
        domain = entity_id.split(".")[0]
        if on:
            service = "open_cover" if domain == "cover" else (
                "open_valve" if domain == "valve" else "turn_on"
            )
        else:
            service = "close_cover" if domain == "cover" else (
                "close_valve" if domain == "valve" else "turn_off"
            )
        await self.hass.services.async_call(
            domain, service, {"entity_id": entity_id}, blocking=True
        )

    def estimate_minutes_to_target(self) -> Optional[int]:
        cur = self._read_temp()
        if cur is None:
            return None
        target = int(self.options.get("target_temp") or DEFAULT_TARGET_TEMP)
        if cur >= target:
            return 0
        # Crude estimate: 2 kW heater raises typical 150L tank by ~10°C in ~45 min.
        # Without history of actual rate, fall back to flat 5°C per 30 min.
        delta = target - cur
        return int(round(delta * 6.0))  # ~6 minutes per °C

    def now_status(self) -> dict:
        cur = self._read_temp()
        target = int(self.options.get("target_temp") or DEFAULT_TARGET_TEMP)
        if self._active:
            label = "heating"
        elif cur is not None and cur >= target:
            label = "ready"
        elif cur is not None and cur < (target - 15):
            label = "cold"
        elif self._is_solar_gaining():
            label = "solar"
        else:
            label = "waiting"
        return {
            "status": label,
            "current_temp": cur,
            "target_temp": target,
            "active": self.active,
            "estimated_minutes_to_target": self.estimate_minutes_to_target(),
        }

    def _is_solar_gaining(self) -> bool:
        # MVP placeholder: always False. v0.2 will track temp deltas over rolling window.
        return False
