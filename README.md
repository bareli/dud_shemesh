# Dud Shemesh — Smart solar water heater controller for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Validate](https://github.com/bareli/dud_shemesh/actions/workflows/validate.yml/badge.svg)](https://github.com/bareli/dud_shemesh/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Home Assistant **custom integration** that turns any smart switch + temperature sensor into an intelligent **dud shemesh** (Israeli solar water heater) controller. Same UX as commercial smart-dud appliances, polished and built for the way Israeli families actually use their water heater.

> Why: commercial smart-dud devices cost ₪400–800 and trap you in proprietary apps. This integration lives entirely in Home Assistant, runs on whatever relay + temp sensor you already have, and saves real electricity by skipping heat cycles when the tank is already warm enough.

## Features

**Hero UI**
- Big circular SVG gauge with **drag-to-set** target marker, live color (cool→hot), pulsing ring while heating.
- Live **status badge**: Ready / Heating / Waiting / Solar / Cold.
- Side pills for "Ends in", "Target", and **Anti-Legionella next-due**.

**Control**
- One-tap **boost** buttons; durations are configurable (default `30,60,120` min).
- Boost while heating **extends** the active run instead of restarting it.
- **Mode toggle**: Auto / Schedule / Off.
- Recurring **schedules** (HH:MM + days + duration, optional target temperature).
- Companion Lovelace **`custom:dud-shemesh-card`** with the same look.

**Smart layer**
- **Real Auto mode**: predictive pre-heat for configured comfort windows (`06:30-08:00,19:00-21:00`).
- **Skip-if-warm**: schedule run is skipped when tank already at target.
- **Solar gain detection**: rolling 30-min temperature delta; auto-skips electric when sun is contributing.
- **Weather-aware skip**: optional weather entity; sunny / clear-night → skip schedule.
- **Soil-of-water-heaters style**: anti-Legionella weekly cycle to a configurable temp.

**Reliability**
- **Heat-not-rising detection**: verifies tank actually warms up after element turns on; alerts on element/breaker fault.

**Visibility**
- **Reports tab**: today / 7-day / 30-day on-time minutes, energy (kWh), cost (₪) using configurable IEC tariff. Heater health avg °C/min trend. Skip-reason summary. 24h temperature graph.
- 3 sensors: status, tank temperature, minutes-to-target.

**Triggers & convenience**
- **Vacation mode**: pick an "active until" date; schedules suspended, tank held at anti-mold temp (default 30 °C).
- **Calendar-driven one-off heat**: events on a chosen calendar with summary containing a keyword (`dud,water,חם,מים,דוד` default) fire heat runs. Description sets minutes / target temp.
- **Voice via Assist**: `DudShemeshBoost` and `DudShemeshStop` intents — say "boost the water heater" to your HA Assist.
- **Notifications**: pick `notify.*` services + which events push (heat_start/end, target reached, fail, skips, anti-Legionella).

**Multi-instance**
- Add the integration multiple times for vacation homes or two heaters. Each runs its own scheduler. (Panel UI shows the first entry; multi-tank picker planned for v0.5.)

**i18n**
- English + Hebrew config strings, **right-to-left** panel layout when HA language is `he`.

**Platform**
- Single-instance config flow + options flow with selectors.
- Domain-aware: `switch`, `input_boolean` for the heater relay.
- Persistent storage via HA's `Store` helper.

## Install

### Via HACS

1. HACS → ⋮ → Custom repositories → add `https://github.com/bareli/dud_shemesh` as **Integration**.
2. Search **Dud Shemesh** → Download → restart Home Assistant.
3. Settings → Devices & Services → + Add Integration → **Dud Shemesh**.
4. Pick the heater relay (a `switch.*` controlling the electric immersion element) and the tank temperature sensor (a numeric `sensor.*` in °C).

### Manual

1. Copy `custom_components/dud_shemesh/` into `<config>/custom_components/`.
2. Restart HA.
3. Add the integration from the UI.

Minimum HA version: **2024.7.0**.

## Required entities

| Entity | Required | Notes |
| ------ | -------- | ----- |
| Heater relay (`switch.*`) | yes | The electric immersion element. |
| Tank temperature sensor (`sensor.*` in °C) | optional | A DS18B20 on the tank, or any thermistor exposed as a numeric sensor. Without it the integration runs in dumb-schedule mode. |

## Services

| Service | Purpose |
| ------- | ------- |
| `dud_shemesh.boost` | Start the heater for N minutes (`minutes` parameter). |
| `dud_shemesh.cancel_boost` | Stop the heater immediately. |
| `dud_shemesh.set_mode` | `auto` / `schedule` / `off`. |
| `dud_shemesh.set_target_temp` | Change the target temperature. |
| `dud_shemesh.add_schedule` | Add a recurring schedule (returns the new id). |
| `dud_shemesh.update_schedule` | Patch an existing schedule by id. |
| `dud_shemesh.remove_schedule` | Delete a schedule by id. |
| `dud_shemesh.legionella_run_now` | Force a 60 °C+ heating cycle. |
| `dud_shemesh.list_config` | Returns schedules, history, active run, options, current status (response service). |

## Events

| Event | When | Data |
| ----- | ---- | ---- |
| `dud_shemesh_heat_started` | Heater is turned on | `source`, `duration_min`, `target_temp`, `starting_temp` |
| `dud_shemesh_heat_finished` | Heater turned off | `source`, `status` (`completed` / `target_reached` / `cancelled`), `duration_min`, `starting_temp`, `ending_temp` |
| `dud_shemesh_target_reached` | Tank hit configured target during a heat cycle | `source`, `temp`, `target_temp` |

## Sensors

- `sensor.dud_shemesh_status` — `ready` / `heating` / `waiting` / `solar` / `cold`. Attributes: `current_temp`, `target_temp`, `active`.
- `sensor.dud_shemesh_tank_temperature` — current tank temp in °C.
- `sensor.dud_shemesh_minutes_to_target` — estimated minutes to reach target if heater were on now.

## Roadmap

| Version | Scope |
| ------- | ----- |
| **v0.1.0** | This release. Manual + scheduled heating, skip-if-warm, anti-Legionella, full panel UI. |
| v0.2.0 | Auto mode: solar-gain detection (rolling temperature delta), predictive pre-heat for comfort windows, weather-aware scheduling. |
| v0.3.0 | Today timeline w/ mode-coloured segments. Reports tab: kWh saved, °C·min over time, IEC tariff cost calculation. CSV export. |
| v0.4.0 | Voice / HA Assist integration. Multi-tank. Family-aware shower scheduler. |
| v1.0.0 | Polish, more translations, brand assets, HACS default submission. |

## License

MIT — see [LICENSE](LICENSE).

## Contributing

Issues and PRs welcome at [github.com/bareli/dud_shemesh](https://github.com/bareli/dud_shemesh).
