# Changelog

## 0.6.1 — accessibility (#44)

- Target gauge is a keyboard slider (`role="slider"`): arrows ±1 °C, PgUp/PgDn ±5, Home/End min/max, with a spoken value ("Target 55°C, tank 43°C"). −/+ buttons have real labels.
- Keyboard focus survives the panel's and card's periodic refresh (it used to jump to the page start every 5 s).
- Tabs, mode switch and Settings tabs follow the WAI-ARIA pattern: arrow keys / Home / End, roving tabindex.
- Dialogs: focus moves into the dialog, Tab stays inside, Esc closes, focus returns to the button that opened it.
- Toasts are announced (status / alert), the Today timeline and both charts have text descriptions, schedule switches are `role="switch"` with the schedule name, delete buttons are labelled.
- `lang` set on panel and card so screen readers pronounce Hebrew correctly; visible focus rings on every control; animations off with `prefers-reduced-motion`.

## 0.6.0 — a real appliance in Home Assistant

- **#28 Native entities**: one device per water heater with a `water_heater` entity (target, mode, away = vacation, on/off), boost / stop / anti-Legionella buttons, mode select, heat-now / vacation / anti-Legionella switches, heating / solar / sensor-problem binary sensors. Entity names in English and Hebrew.
- **#31 Learned heat rate**: °C/min learned per tank from clean runs (moving average), physics fallback from tank volume × wattage; drives minutes-to-target, auto pre-heat, "hot by" and Shabbat pre-heat.
- **#46 Tank picker** in the panel header for multi-tank setups (remembered per browser); new `dud_shemesh/list_entries` WS command.
- **#33 Actionable notifications** for companion-app targets (Heat now, Boost 1 h, Keep 30 min, Turn off) and a new **cold warning** 60 min before a comfort window when nothing is planned. Notification texts in Hebrew when HA's language is Hebrew. New events `manual_on`, `cold_warning`.
- **#32 Forecast-based solar skip**: hourly forecast (condition / cloud cover over the next N hours) or a solar production forecast sensor, instead of only the current weather state.
- **#34 Time-of-use tariffs**: price windows, auto pre-heat moves to the cheapest hours that still finish in time (small standby-loss penalty), per-run `cost` in history, TOU-aware Reports and savings.
- **#35 Shabbat mode** (Jewish Calendar integration): pre-heat for candle lighting, optional control lock and quiet notifications until havdalah.
- **#37 Settings rework**: tabbed sections, entity suggestions for weather / calendar / solar sensors, row editors for comfort windows and price windows, calendar settings exposed; config flow asks for tank volume, price and comfort windows with validation. Settings gear shown to admins only.
- **#43 Temperature chart** from HA history (24 h / 7 days) with heating runs shaded.
- **#45 Assist**: ready-made English and Hebrew sentence files (`docs/assist/`), new `DudShemeshStatus` intent ("is there hot water?").
- Permissions: vacation joins mode and target as an everyday control any user may change; the anti-Legionella switch requires an admin when a person uses it.

## 0.5.0 — hot water you can plan on

Bugs
- **#24** Weather skip no longer skips pre-sunrise heating: default skip states are now `sunny` only (old `sunny,clear-night` default is migrated) and weather skip never applies while `sun.sun` is below the horizon.
- **#25** Hebrew: full panel and card translation, fixed RTL garbling (`hours 2+`, `C°`, `70~ min`), timeline always reads 00→24 with the "now" marker in the right place.

Features
- **#26** "Will I have hot water?": next heat line ("Hot by 06:30" / "Morning shower · tomorrow 06:15"), planned runs painted on the Today timeline, showers-available estimate from new tank volume setting. Status sensor gains `next_heat_at`, `next_heat_source`, `next_heat_label`, `hot_by`, `showers_available`.
- **#27** Safety: manual turn-ons are adopted and turned off after `manual_on_max_min` (default 60, 0 = off); `max_run_min` hard cap (default 180) also caps boost extensions; `max_tank_temp` over-temperature cutoff (default 75 °C); stale temperature sensor detection (`sensor_stale_min`, default 120) with `safety_stop` / `sensor_stale` notifications.
- **#29** New Energy sensor (kWh, `total_increasing`) for the HA Energy dashboard.
- **#30** Reports: "Saved this month ₪X", 30-day electric vs avoided kWh chart, human-readable durations (**#42**).
- **#36** Lovelace card parity: extend buttons while heating, configured boost durations, −/+ target, next heat, run source, `entry_id` config, visual editor.
- **#38** Schedules: on/off switch, Sunday-first days (Hebrew / HA first weekday), next-run line, skip next (`update_schedule` `skip_until`).
- **#39** Header version sits next to the title. **#40** Gauge turns orange-red while heating and the badge shows the run source. **#41** Target −/+ buttons.
- Mode explanation under the mode switch; Settings layout fixed (checkboxes, chips) and a new Safety section.
- Heater state events are ignored when they no longer match the heater's current state (prevents a stale ON being adopted, or a stale OFF closing a new run).

## 0.4.13 — bug-fix sweep (#1–#23)

Safety / data
- **#1** Heater no longer left on after an HA restart mid-run: the active run is restored once HA has started (heater entity loaded), and kept even if the heater state is still unknown so the close timer turns it off.
- **#2 / #8** Closing a run clears state before turning the heater off. A failed turn-off is logged instead of leaving the scheduler stuck in "heating", and our own turn-off no longer triggers a second `external_stop` close (duplicate history rows, events, notifications).
- **#3** Options flow merges into existing options instead of replacing them; panel-only settings (notify, vacation, weather, tariff, calendar, ...) survive "Configure".
- **#4** Multi-instance: each entry has its own storage file (`dud_shemesh.data.<entry_id>`); the pre-0.4.13 shared file is migrated to the first entry. Services are registered once and accept an optional `entry_id` (default: first entry); panel/WS/intents use the first entry in config order.
- **#5** Anti-Legionella only recorded as done when the target temperature is reached.

Behaviour
- **#6** Target-reached check and fail detection are re-armed when the entry reloads during a run (any options save).
- **#7** Temperature samples are not collected while the element is on, so a finished electric run is no longer mistaken for solar gain.
- **#9** Only one run can start per minute tick; the run is claimed before the relay call, so network relays can't race two starts.
- **#10** Pending calendar-triggered starts and the fail check are cancelled on stop/reload; seen-event keys are pruned.
- `skipped_solar` / `skipped_weather` notifications are now actually sent.
- **#11** Vacation "active until" no longer shifts by the UTC offset on every Settings save.
- **#12** Dragging the target past 80 °C snaps to the nearest end instead of jumping to 20 °C.
- **#13** Today timeline paints each run from its real start to its end.
- **#14** Reports use actual element on-time (`actual_min`, new on close records) for all stop reasons; "Today" starts at local midnight.

Minor
- **#15** Options flow temp sensor uses `suggested_value` (blank is valid).
- **#16** Service and intent numbers are coerced (`"30"` works).
- **#17** `update_options` WS validates ranges; non-admin users may only change mode and target.
- **#18** Calendar description values clamped (20–80 °C, 1–720 min).
- **#19** Gauge target marker clamped; `0` can be saved for margin/tariff.
- **#20** Periodic refresh no longer interrupts a target drag.
- **#21 / #22** Card error rendering uses `textContent`; `console.*` removed; card shows service errors inline.
- **#23** Tank temperature sensor has `device_class: temperature` and `state_class: measurement`; minutes-to-target is a duration.
- Countdown hitting 0 refreshes once instead of every second.
- New pytest suite (`tests/`) with a regression test per issue, run in CI.

## 0.4.12 — apply panel fixes to the Lovelace card

- The fixes shipped in 0.4.5–0.4.10 only touched the sidebar panel (`panel.js`); the Lovelace card (`card.js`) still polled every 5 s with no live ticker, no `state_changed` subscription, no re-attach handling, and no visibility wake-up. All of the same logic is now ported to the card: per-second `Ends in` countdown with server clock skew correction, immediate refresh on heater entity state change, restart of timers/subscriptions when the card is re-attached to the DOM, and force-refresh when the browser tab returns to foreground.
- Removed the diagnostic `console.log` calls added in 0.4.11 from `panel.js`.

## 0.4.11 — diagnostic logging for state subscription + tick

- Adds `console.log` calls to verify the panel actually subscribes to the heater entity's `state_changed` events and that the 1-second tick handler is firing. Logs prefixed `[dud_shemesh]`. Diagnostic only — will be cleaned up once the upstream issue is identified.

## 0.4.10 — subscribe to raw state_changed events

- Replaced the `subscribe_trigger` WS message (which proved unreliable in `panel_custom`-hosted custom elements) with a direct `subscribeEvents("state_changed")` subscription. The callback filters by `entity_id` and triggers an immediate `_refresh()` whenever the heater entity changes — same mechanism Lovelace cards rely on, so panel state stays in sync with any external toggle.

## 0.4.9 — visibility handling + panel version pill

- Panel registers a `visibilitychange` listener. When the browser tab returns to foreground (after being backgrounded, where browsers throttle `setInterval`), panel forces an immediate `_refresh()` plus a tick of the countdown so UI is current within a frame.
- Header now shows the panel.js version (`v0.4.9` next to the title) so it's possible to verify which build the browser actually loaded — useful when diagnosing cache issues after upgrades.

## 0.4.8 — restart timers and subscriptions on panel re-attach

- Fix: HA detaches and re-attaches the panel custom-element when navigating between sidebar entries. Previous code cleared timers in `disconnectedCallback` but the `_init` guard (`if (!_initialized)`) prevented re-setup on re-attach. Result: no 5 s poll, no 1 s countdown ticker, no heater state subscription — UI froze until full page reload (F5).
- `connectedCallback` now restarts timers and re-subscribes to the heater entity even when already initialized; `_init` is only called the first time.

## 0.4.7 — live "Heating ends in" countdown

- "Heating ends in" pill now ticks every second client-side instead of only refreshing on the 5 s WS poll. Format is `MM:SS` while under an hour, `Hh MMm` above. Server-client clock skew is corrected on every poll. When the timer hits 0, panel refreshes immediately to pick up the heat-finished state.

## 0.4.6 — subscribe to heater state changes via WS trigger

- Panel registers a `subscribe_trigger` WS subscription on the configured heater entity. When the entity changes state, HA pushes a trigger message and the panel calls `_refresh()` 150 ms later. Doesn't depend on `set hass()` semantics or `panel_custom` reactive updates which proved unreliable.

## 0.4.5 — refresh panel on heater entity state change

- Panel watches the configured heater entity directly via `set hass()` (called by HA on every state update). When the entity transitions on↔off, panel triggers an immediate `_refresh()`. Replaces the v0.4.4 event-bus subscription which relied on backend events being dispatched and required an HA restart to pick up; this approach reacts to the entity state itself.

## 0.4.4 — instant panel refresh on heater events

- Panel subscribes to HA event bus (`dud_shemesh_heat_started`, `heat_finished`, `target_reached`, `boost_extended`) and refreshes UI immediately instead of waiting up to 5 s for the next poll. Closes the visible lag where a heater turned off externally still showed "STOP HEATING" until the next tick.

## 0.4.3 — sync with external heater state changes

- Listens to the heater entity's state. When it transitions to off/closed/unavailable while integration thinks it's heating (e.g. user turned it off via a custom button or another automation), the active session is closed cleanly with status `external_stop`. Panel and reports stay in sync.

## 0.4.2 — README screenshots

- Added 4 screenshots to README: panel control, panel reports, settings (advanced expanded), Lovelace card.

## 0.4.1 — fix services.yaml validation

- Quoted `"off"` in set_mode selector options. YAML 1.1 parses unquoted `off` as boolean false, which broke hassfest validation of services.yaml.

## 0.4.0 — notifications, vacation, drag-target, temp graph, calendar, voice, multi-tank, RTL

- **Notifications**: pick one or more `notify.*` services and tick which events to push: heat_start, heat_end, target_reached, heat_not_rising, skipped_solar, skipped_weather, legionella_done.
- **Vacation mode**: pick an "active until" date; integration suspends schedules and auto-runs and holds the tank at a configurable anti-mold temp (default 30°C). Dashboard shows banner with one-tap End button.
- **Drag-target on the gauge**: grab the target marker dot and drag along the arc to set a new target temp without opening Settings.
- **24h tank-temp graph** on Reports tab: smooth SVG line of rolling temperature samples.
- **Calendar-driven one-off heat**: optional HA calendar entity. Events whose summary contains a configured keyword (default `dud,water,חם,מים,דוד`) trigger a heat run. Description can carry minutes (`30m`) and target temperature (`60c`).
- **Voice via Assist**: registers `DudShemeshBoost` and `DudShemeshStop` intents. Add Assist sentence triggers like "boost the water heater" → boost. Slot `minutes` optional.
- **Multi-tank**: removed single-instance restriction. You can add the integration multiple times for vacation homes / two heaters; each entry runs its own scheduler. (Panel UI still shows the first entry; full multi-tank picker UI planned for v0.5.)
- **Hebrew RTL panel**: when HA language is `he`, panel switches to right-to-left layout and translates tab labels, mode pills, vacation banner, and Legionella indicator.

## 0.3.0 — Reports tab + visibility polish

## 0.3.0 — Reports tab + visibility polish

- **Reports tab**: dedicated view with kWh, ₪ cost (configurable IEC tariff), on-time minutes for today / 7 days / 30 days; heater health average heat-rate °C/min trend; entire-history skip-reasons summary.
- **Settings: Basic / Advanced split**. Basic shows target temp, boost-button durations, wattage, tariff. Advanced reveals comfort windows, weather entity, solar tracking, fail detection, anti-Legionella.
- **Configurable boost durations**: comma-separated minutes (default `30,60,120`); also rendered as inline extend buttons while heating.
- **Anti-Legionella next-due indicator**: side-pill on the gauge shows days until next sterilization, turns red when overdue.
- **Pulsing gauge ring** while heating; smooth status transitions.
- **Tariff for cost calc**: configurable ₪/kWh in Settings (default 0.62 reflecting common IEC daytime rate).
- WS state now exposes `last_legionella` and `legionella_next_due` timestamps.

## 0.2.0 — smart layer

- **Real Auto mode**: predictive pre-heat. Configure comfort windows like `06:30-08:00,19:00-21:00`. Integration estimates time-to-target and fires the element just-in-time before each window. Skipped if tank already at target, sun is gaining, or weather forecast is sunny.
- **Solar gain detection**: rolling 30-minute temperature delta. When tank rises above the configured threshold without electric heat, integration reports "solar gaining" and skips the next scheduled run.
- **Boost = extend, not replace**: pressing +30 / +1 h while already heating now adds time to the current run instead of restarting from zero. New event `boost_extended`.
- **Weather-aware skip**: optional weather entity. Schedule mode skips runs when the weather state is in the skip list (default `sunny,clear-night`). New history status `skipped_weather` and `skipped_solar`.
- **Heat-not-rising detection**: optional safety check. After a configured number of minutes from heat start, verify tank temperature has risen by at least N °C. If not → fire `heat_not_rising` event and log error.
- New status fields exposed via WebSocket: `solar_rise_per_30min`, `solar_gaining`, `weather_skip_active`.

## 0.1.1 — appliance-grade Lovelace card

- Lovelace card rebuilt to look like a real smart-dud controller: SVG gauge with target marker, status badge, side pills (ends-in / target), three large boost buttons (+30/+1h/+2h), STOP HEATING button while running, Auto/Schedule/Off mode toggle.
- Cache-busted via existing `?v=<version>` resource URL — restart HA after update for fresh card.

## 0.1.0 — initial scaffold

- HACS custom integration skeleton modeled on schedule_wizard.
- Config flow + options flow (heater entity, temp sensor, target temp, wattage, mode, anti-Legionella).
- Storage helper for schedules / history / active boost / last-Legionella timestamp.
- Scheduler: per-minute cron tick, manual boost, scheduled heat, skip-if-warm, target-temp auto-close, anti-Legionella weekly cycle.
- Services: `boost`, `cancel_boost`, `set_mode`, `set_target_temp`, `add_schedule`, `update_schedule`, `remove_schedule`, `legionella_run_now`, `list_config`.
- Events: `heat_started`, `heat_finished`, `target_reached`.
- Sensors: status, tank temperature, estimated minutes to target.
- Sidebar panel custom-element with circular SVG gauge, status badge, boost row, mode toggle, today timeline, schedule list/editor, settings drawer.
- Companion Lovelace card.
- English + Hebrew translations for config flow and options.
- Brand placeholder PNGs.
