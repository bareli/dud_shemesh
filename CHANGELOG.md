# Changelog

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
