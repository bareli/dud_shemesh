"""Dud Shemesh scheduler — boost, schedule, anti-legionella."""
from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timedelta
from typing import Optional

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_change,
    async_track_time_interval,
)
from homeassistant.helpers.start import async_at_started
from homeassistant.util import dt as dt_util

from .const import (
    DAY_BITS,
    DEFAULT_FAIL_DETECTION_MINUTES,
    DEFAULT_FAIL_DETECTION_RISE,
    DEFAULT_LEGIONELLA_DAYS,
    DEFAULT_LEGIONELLA_TEMP,
    DEFAULT_AUTO_PRE_HEAT_MARGIN_MIN,
    DEFAULT_SOLAR_RISE_THRESHOLD,
    DEFAULT_SOLAR_TRACK_MINUTES,
    DEFAULT_TARGET_TEMP,
    DEFAULT_WEATHER_SKIP_STATES,
    EVENT_AUTO_PREHEAT_PLANNED,
    EVENT_BOOST_EXTENDED,
    EVENT_HEAT_FINISHED,
    EVENT_HEAT_NOT_RISING,
    EVENT_HEAT_STARTED,
    EVENT_TARGET_REACHED,
    MODE_AUTO,
    MODE_OFF,
    MODE_SCHEDULE,
    SIGNAL_STATE_CHANGED,
)
from .storage import DudStore

LOG = logging.getLogger(__name__)

ON_STATES = {"on", "open", "active"}
OFF_STATES = {"off", "closed"}

CALENDAR_TEMP_MIN, CALENDAR_TEMP_MAX = 20, 80
CALENDAR_DUR_MIN, CALENDAR_DUR_MAX = 1, 720
RE_CAL_DURATION = re.compile(r"(\d{1,3})\s*(?:m|min|minutes?)\b")
RE_CAL_TEMP = re.compile(r"(\d{2,3})\s*°?\s*c\b")


class DudScheduler:
    def __init__(self, hass: HomeAssistant, store: DudStore, options: dict):
        self.hass = hass
        self.store = store
        self.options = options
        self._unsub_minute = None
        self._unsub_calendar = None
        self._unsub_heater_state = None
        self._unsub_started = None
        self._unsub_temp_check = None
        self._unsub_close = None
        self._unsub_fail_check = None
        self._calendar_unsubs: dict = {}                  # key -> unsub
        self._known_calendar_keys: dict[str, int] = {}  # key -> start_ts
        self._active = None
        self._last_minute_fired: Optional[str] = None
        self._temp_samples: list[tuple[int, float]] = []  # rolling (ts, temp)
        self._planned_preheats: dict[str, int] = {}       # window_key -> end_at_ts

    @property
    def active(self) -> Optional[dict]:
        return dict(self._active) if self._active else None

    async def async_start(self) -> None:
        self._unsub_minute = async_track_time_change(self.hass, self._on_minute, second=0)
        self._unsub_calendar = async_track_time_interval(
            self.hass, self._on_calendar_poll, timedelta(seconds=60)
        )
        heater = (self.options.get("heater_entity") or "").strip()
        if heater:
            self._unsub_heater_state = async_track_state_change_event(
                self.hass, [heater], self._on_heater_state_change
            )
        # Heater entity may not exist yet during HA startup; restore once started.
        self._unsub_started = async_at_started(self.hass, self._on_ha_started)
        LOG.info("dud_shemesh scheduler started")

    async def _on_ha_started(self, _hass) -> None:
        self._unsub_started = None
        await self._restore_active_boost()

    @callback
    def _on_heater_state_change(self, event) -> None:
        if not self._active:
            return
        new_state = event.data.get("new_state")
        if not new_state:
            return
        if new_state.state in OFF_STATES or new_state.state == "unavailable":
            LOG.info("heater turned off externally — closing active session")
            self.hass.async_create_task(self._async_close("external_stop"))

    async def async_stop(self) -> None:
        for attr in (
            "_unsub_minute", "_unsub_calendar", "_unsub_heater_state", "_unsub_started",
        ):
            unsub = getattr(self, attr)
            if unsub:
                unsub()
                setattr(self, attr, None)
        for unsub in self._calendar_unsubs.values():
            unsub()
        self._calendar_unsubs = {}
        self._cancel_run_timers()
        self._active = None

    def _cancel_run_timers(self) -> None:
        for attr in ("_unsub_close", "_unsub_temp_check", "_unsub_fail_check"):
            unsub = getattr(self, attr)
            if unsub:
                unsub()
                setattr(self, attr, None)

    def _arm_run_timers(self) -> None:
        """(Re)arm close, target-check and fail-check timers for the active run."""
        self._cancel_run_timers()
        if not self._active:
            return
        now = int(time.time())
        self._unsub_close = async_call_later(
            self.hass, max(1, int(self._active["ends_at"]) - now), self._on_close_timer
        )
        self._unsub_temp_check = async_track_time_change(
            self.hass, self._on_temp_check, second=15
        )
        if self.options.get("fail_detection_enabled"):
            check_after = int(self.options.get("fail_detection_minutes", DEFAULT_FAIL_DETECTION_MINUTES)) * 60
            due = int(self._active.get("started_at", now)) + check_after - now
            if due > 0:
                self._unsub_fail_check = async_call_later(self.hass, due, self._on_fail_check)

    async def _restore_active_boost(self) -> None:
        boost = self.store.active_boost
        if not boost:
            return
        ends_at = int(boost.get("ends_at", 0))
        if ends_at <= int(time.time()):
            self._active = boost
            await self._async_close("expired_during_downtime")
            return
        heater = self.options.get("heater_entity")
        state = self.hass.states.get(heater) if heater else None
        if state and state.state in OFF_STATES:
            await self.store.async_set_active_boost(None)
            return
        # Heater on, unknown or unavailable: keep the run so the close timer
        # still turns it off at ends_at.
        self._active = boost
        self._arm_run_timers()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    @callback
    def _on_minute(self, now: datetime) -> None:
        local = dt_util.as_local(now)
        key = local.strftime("%Y-%m-%d %H:%M")
        if key == self._last_minute_fired:
            return
        self._last_minute_fired = key

        # Always sample for solar tracking, regardless of mode
        self._track_temp_sample()

        mode = self.options.get("mode", MODE_SCHEDULE)
        if mode == MODE_OFF:
            return

        if self._vacation_active():
            cur = self._read_temp()
            hold = float(self.options.get("vacation_hold_temp") or 30)
            if cur is not None and cur < hold - 2 and not self._active:
                LOG.info("vacation hold: heating to %.0f°C", hold)
                self.hass.async_create_task(self.async_start_heat(
                    source="vacation_hold", duration_min=60, target_temp=int(hold),
                    note="vacation anti-mold",
                ))
            return

        # Only one run may start per minute tick; _active is set inside the task.
        started = False
        if mode == MODE_AUTO:
            started = self._evaluate_auto_preheat(local)

        bit = DAY_BITS[local.weekday()]
        hhmm = local.strftime("%H:%M")
        for sched in self.store.schedules:
            if not sched.get("enabled"):
                continue
            if not (int(sched.get("days_mask", 0)) & bit):
                continue
            if sched.get("time_hhmm") != hhmm:
                continue
            if self._active or started:
                LOG.debug("skip schedule %s: heater already running", sched["id"])
                continue
            if self._is_solar_gaining():
                LOG.info("skip schedule %s: solar gaining", sched["id"])
                self.hass.async_create_task(self.store.async_record_run(
                    "schedule", int(sched.get("duration_min", 60)), "skipped_solar",
                    starting_temp=self._read_temp(), note=f"schedule:{sched['id']}",
                ))
                self.hass.async_create_task(self._notify(
                    "skipped_solar", "Dud Shemesh", "Scheduled heating skipped: solar gain detected",
                ))
                continue
            if self._weather_says_sunny():
                LOG.info("skip schedule %s: weather sunny", sched["id"])
                self.hass.async_create_task(self.store.async_record_run(
                    "schedule", int(sched.get("duration_min", 60)), "skipped_weather",
                    starting_temp=self._read_temp(), note=f"schedule:{sched['id']}",
                ))
                self.hass.async_create_task(self._notify(
                    "skipped_weather", "Dud Shemesh", "Scheduled heating skipped: sunny weather",
                ))
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
            started = True
            self.hass.async_create_task(self.async_start_heat(
                source="schedule",
                duration_min=int(sched.get("duration_min", 60)),
                target_temp=target_temp,
                note=f"schedule:{sched['id']}",
                schedule_id=sched["id"],
            ))

        # Anti-Legionella check, run once per day at 03:00 local
        if hhmm == "03:00" and not started:
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

    def _track_temp_sample(self) -> None:
        # Samples taken while the element is on would read as solar gain afterwards.
        if self._active:
            self._temp_samples = []
            return
        cur = self._read_temp()
        if cur is None:
            return
        now_ts = int(time.time())
        self._temp_samples.append((now_ts, cur))
        track_min = int(self.options.get("solar_track_minutes", DEFAULT_SOLAR_TRACK_MINUTES))
        cutoff = now_ts - track_min * 60
        self._temp_samples = [(ts, t) for (ts, t) in self._temp_samples if ts >= cutoff]

    def _solar_rise_per_30min(self) -> Optional[float]:
        if len(self._temp_samples) < 3:
            return None
        oldest_ts, oldest_t = self._temp_samples[0]
        newest_ts, newest_t = self._temp_samples[-1]
        elapsed = max(1, newest_ts - oldest_ts)
        return (newest_t - oldest_t) * (1800.0 / elapsed)

    def _is_solar_gaining(self) -> bool:
        if self._active:
            return False
        rise = self._solar_rise_per_30min()
        if rise is None:
            return False
        threshold = float(self.options.get("solar_rise_threshold", DEFAULT_SOLAR_RISE_THRESHOLD))
        return rise >= threshold

    def _weather_says_sunny(self) -> bool:
        ent = (self.options.get("weather_entity") or "").strip()
        if not ent:
            return False
        s = self.hass.states.get(ent)
        if not s:
            return False
        states = [x.strip() for x in str(self.options.get("weather_skip_states", DEFAULT_WEATHER_SKIP_STATES)).split(",") if x.strip()]
        return s.state in states

    async def _on_calendar_poll(self, _now) -> None:
        now_ts = int(time.time())
        self._known_calendar_keys = {
            k: ts for k, ts in self._known_calendar_keys.items() if ts >= now_ts - 86400
        }
        if self._active or self._vacation_active() or self.options.get("mode") == MODE_OFF:
            return
        cal = (self.options.get("calendar_entity") or "").strip()
        if not cal:
            return
        lookahead = int(self.options.get("calendar_lookahead_min", 10))
        try:
            response = await self.hass.services.async_call(
                "calendar", "get_events",
                {"entity_id": cal, "duration": {"minutes": lookahead}},
                blocking=True, return_response=True,
            )
        except Exception as e:
            LOG.warning("calendar get_events failed: %s", e)
            return
        cal_data = (response or {}).get(cal) or {}
        events = cal_data.get("events", [])
        if not events:
            return
        keywords_raw = self.options.get("calendar_keywords") or "dud,water"
        keywords = [k.strip().lower() for k in str(keywords_raw).split(",") if k.strip()]
        now_ts = int(time.time())
        for ev in events:
            summary = (ev.get("summary") or "").strip().lower()
            if not summary:
                continue
            if keywords and not any(k in summary for k in keywords):
                continue
            start_str = ev.get("start", "")
            try:
                start_ts = self._parse_calendar_time(start_str)
            except Exception:
                continue
            if start_ts > now_ts + lookahead * 60:
                continue
            if start_ts < now_ts - 60:
                continue
            key = f"{summary}|{start_str}"
            if key in self._known_calendar_keys:
                continue
            self._known_calendar_keys[key] = start_ts

            description = (ev.get("description") or "").strip().lower()
            duration_min = 60
            target = None
            m_dur = RE_CAL_DURATION.search(description)
            if m_dur:
                duration_min = max(CALENDAR_DUR_MIN, min(CALENDAR_DUR_MAX, int(m_dur.group(1))))
            m_t = RE_CAL_TEMP.search(description)
            if m_t:
                target = max(CALENDAR_TEMP_MIN, min(CALENDAR_TEMP_MAX, int(m_t.group(1))))

            delay = max(0, start_ts - now_ts)
            if delay == 0:
                self.hass.async_create_task(self.async_start_heat(
                    source="calendar", duration_min=duration_min,
                    target_temp=target, note=key,
                ))
            else:
                self._calendar_unsubs[key] = async_call_later(
                    self.hass, delay, self._make_calendar_callback(duration_min, target, key)
                )

    def _make_calendar_callback(self, duration_min, target, key):
        async def _fire(_now):
            self._calendar_unsubs.pop(key, None)
            if self._active:
                return
            await self.async_start_heat(
                source="calendar", duration_min=duration_min,
                target_temp=target, note=key,
            )
        return _fire

    @staticmethod
    def _parse_calendar_time(value: str) -> int:
        if not value:
            raise ValueError("empty")
        v = value.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(v)
        except ValueError:
            dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
        if dt.tzinfo is None:
            tz = getattr(dt_util, "get_default_time_zone", None)
            tz = tz() if callable(tz) else getattr(dt_util, "DEFAULT_TIME_ZONE", None)
            if tz is None:
                from datetime import timezone as _tz
                tz = _tz.utc
            dt = dt.replace(tzinfo=tz)
        return int(dt.timestamp())

    def _vacation_active(self) -> int:
        until = int(self.options.get("vacation_until") or 0)
        if until <= 0 or until <= int(time.time()):
            return 0
        return until

    async def _notify(self, event: str, title: str, message: str) -> None:
        events = self.options.get("notify_events") or []
        if isinstance(events, str):
            events = [e.strip() for e in events.split(",") if e.strip()]
        if event not in events:
            return
        targets = self.options.get("notify_targets") or []
        if isinstance(targets, str):
            targets = [t.strip() for t in targets.split(",") if t.strip()]
        for t in targets:
            if not t:
                continue
            try:
                await self.hass.services.async_call(
                    "notify", t,
                    {"title": title, "message": message},
                    blocking=False,
                )
            except Exception as e:
                LOG.warning("notify %s failed: %s", t, e)

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

        starting_temp = self._read_temp()
        now = int(time.time())
        # Claim the run before the first await so concurrent starts see it.
        self._active = {
            "source": source,
            "started_at": now,
            "ends_at": now + max(60, int(duration_min) * 60),
            "duration_min": int(duration_min),
            "target_temp": target_temp,
            "starting_temp": starting_temp,
            "schedule_id": schedule_id,
            "note": note,
        }
        active = self._active
        try:
            await self._call_heater(heater, on=True)
        except Exception:
            if self._active is active:
                self._active = None
            raise
        if self._active is not active:
            # Stopped while the turn-on call was in flight; the stop's turn-off
            # may have landed before our turn-on, so switch off again.
            if self._active is None:
                try:
                    await self._call_heater(heater, on=False)
                except Exception as e:
                    LOG.error("dud_shemesh: failed to turn off heater %s: %s", heater, e)
            return

        await self.store.async_set_active_boost(self._active)
        await self.store.async_record_run(
            source, int(duration_min), "started",
            starting_temp=starting_temp, note=note, started_at=now,
        )
        self.hass.bus.async_fire(EVENT_HEAT_STARTED, {
            "source": source, "duration_min": int(duration_min),
            "target_temp": target_temp, "starting_temp": starting_temp,
            "note": note,
        })
        self.hass.async_create_task(self._notify(
            "heat_start", "Dud Shemesh",
            f"Heating started ({source}, target {target_temp}°C, {duration_min} min)",
        ))
        self._arm_run_timers()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    async def _on_close_timer(self, _now) -> None:
        self._unsub_close = None
        await self._async_close("completed")

    async def _on_fail_check(self, _now) -> None:
        self._unsub_fail_check = None
        if not self._active:
            return
        starting = self._active.get("starting_temp")
        cur = self._read_temp()
        rise_threshold = float(self.options.get("fail_detection_rise", DEFAULT_FAIL_DETECTION_RISE))
        if starting is None or cur is None:
            return
        if (cur - starting) < rise_threshold:
            LOG.error(
                "dud_shemesh: heat-not-rising detected (start=%.1f cur=%.1f need>=%.1f)",
                starting, cur, rise_threshold,
            )
            self.hass.bus.async_fire(EVENT_HEAT_NOT_RISING, {
                "starting_temp": starting,
                "current_temp": cur,
                "elapsed_min": int((time.time() - self._active.get("started_at", time.time())) / 60),
                "source": self._active.get("source"),
            })
            await self._notify(
                "heat_not_rising", "Dud Shemesh — heater issue",
                f"Tank not rising as expected (start {starting:.1f}°C, now {cur:.1f}°C). Check element / breaker.",
            )

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
            self.hass.async_create_task(self._notify(
                "target_reached", "Dud Shemesh",
                f"Target {target}°C reached",
            ))
            self.hass.async_create_task(self._async_close("target_reached"))

    async def async_stop_heat(self, reason: str = "manual_stop") -> None:
        await self._async_close(reason)

    async def _async_close(self, status: str) -> None:
        # Clear state before any await: the heater's own off-transition must not
        # be seen as an external stop, and a failed turn-off must not leave the
        # scheduler stuck in a run.
        active = self._active
        self._active = None
        self._cancel_run_timers()
        heater = self.options.get("heater_entity")
        if heater:
            try:
                await self._call_heater(heater, on=False)
            except Exception as e:
                LOG.error("dud_shemesh: failed to turn off heater %s: %s", heater, e)
        await self.store.async_set_active_boost(None)
        if active:
            now = int(time.time())
            started_at = int(active.get("started_at") or now)
            ended_at = min(now, int(active.get("ends_at") or now))
            actual_min = round(max(0, ended_at - started_at) / 60, 1)
            ending_temp = self._read_temp()
            await self.store.async_record_run(
                active.get("source", "manual"),
                active.get("duration_min", 0),
                status,
                starting_temp=active.get("starting_temp"),
                ending_temp=ending_temp,
                note=active.get("note", ""),
                started_at=started_at,
                actual_min=actual_min,
            )
            self.hass.bus.async_fire(EVENT_HEAT_FINISHED, {
                "source": active.get("source"),
                "status": status,
                "duration_min": active.get("duration_min"),
                "actual_min": actual_min,
                "starting_temp": active.get("starting_temp"),
                "ending_temp": ending_temp,
            })
            await self._notify(
                "heat_end", "Dud Shemesh",
                f"Heating ended ({status}). Tank: {ending_temp if ending_temp is not None else '—'}°C",
            )
            if active.get("source") == "legionella":
                # Only a confirmed target temperature counts as a disinfection.
                if status == "target_reached":
                    await self.store.async_set_last_legionella(now)
                    await self._notify(
                        "legionella_done", "Dud Shemesh",
                        "Anti-Legionella cycle completed",
                    )
                else:
                    LOG.warning(
                        "dud_shemesh: anti-legionella run ended (%s) without reaching target; not recorded",
                        status,
                    )
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    async def async_boost(self, minutes: int) -> None:
        target = int(self.options.get("target_temp") or DEFAULT_TARGET_TEMP)
        if self._active:
            extra_sec = max(60, int(minutes) * 60)
            self._active["ends_at"] = int(self._active.get("ends_at", time.time())) + extra_sec
            self._active["duration_min"] = int(self._active.get("duration_min", 0)) + int(minutes)
            await self.store.async_set_active_boost(self._active)
            if self._unsub_close:
                self._unsub_close()
            remaining = self._active["ends_at"] - int(time.time())
            self._unsub_close = async_call_later(self.hass, max(1, remaining), self._on_close_timer)
            self.hass.bus.async_fire(EVENT_BOOST_EXTENDED, {
                "added_minutes": int(minutes),
                "new_ends_at": self._active["ends_at"],
            })
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
            return
        await self.async_start_heat(
            source="boost", duration_min=int(minutes),
            target_temp=target, note=f"manual+{minutes}m",
        )

    def _evaluate_auto_preheat(self, local: datetime) -> bool:
        """Start a pre-heat run if a comfort window is close. Returns True if started."""
        if self._active:
            return False
        cur = self._read_temp()
        target = int(self.options.get("target_temp") or DEFAULT_TARGET_TEMP)
        if cur is not None and cur >= target:
            return False
        if self._is_solar_gaining():
            return False
        if self._weather_says_sunny():
            return False

        windows_str = (self.options.get("auto_comfort_windows") or "").strip()
        if not windows_str:
            return False
        windows = []
        for chunk in windows_str.split(","):
            chunk = chunk.strip()
            if not chunk or "-" not in chunk:
                continue
            start, _ = chunk.split("-", 1)
            try:
                hh, mm = [int(x) for x in start.split(":")]
                windows.append((hh, mm))
            except Exception:
                continue
        if not windows:
            return False

        margin = int(self.options.get("auto_pre_heat_margin_min", DEFAULT_AUTO_PRE_HEAT_MARGIN_MIN))
        eta = self.estimate_minutes_to_target() or 30

        for hh, mm in windows:
            try:
                window_start = local.replace(hour=hh, minute=mm, second=0, microsecond=0)
            except ValueError:
                continue
            if window_start <= local:
                continue
            minutes_to_window = int((window_start - local).total_seconds() // 60)
            if minutes_to_window <= eta + margin:
                key = f"auto:{window_start.isoformat()}"
                if self._planned_preheats.get(key):
                    continue
                self._planned_preheats[key] = int(window_start.timestamp())
                LOG.info(
                    "auto pre-heat firing for window %02d:%02d (eta %dmin, margin %dmin)",
                    hh, mm, eta, margin,
                )
                self.hass.bus.async_fire(EVENT_AUTO_PREHEAT_PLANNED, {
                    "window_start": window_start.isoformat(),
                    "estimated_eta_min": eta,
                    "margin_min": margin,
                })
                self.hass.async_create_task(self.async_start_heat(
                    source="auto",
                    duration_min=eta + margin,
                    target_temp=target,
                    note=f"auto-preheat:{hh:02d}:{mm:02d}",
                ))
                return True
        return False

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
        rise = self._solar_rise_per_30min()
        return {
            "status": label,
            "current_temp": cur,
            "target_temp": target,
            "active": self.active,
            "estimated_minutes_to_target": self.estimate_minutes_to_target(),
            "solar_rise_per_30min": round(rise, 2) if rise is not None else None,
            "solar_gaining": self._is_solar_gaining(),
            "weather_skip_active": self._weather_says_sunny(),
        }

    def solar_rise_per_30min(self) -> Optional[float]:
        return self._solar_rise_per_30min()
