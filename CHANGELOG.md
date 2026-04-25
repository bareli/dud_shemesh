# Changelog

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
