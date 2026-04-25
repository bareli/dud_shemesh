# Changelog

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
