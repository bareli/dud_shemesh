# Dud Shemesh Smart Scheduler — Project Plan

## What

A Home Assistant **HACS custom integration** that turns any smart switch + temperature sensor into an intelligent solar water heater (Dud Shemesh) controller — same UX as commercial smart-dud devices like Switchee, Brilliant, Sonoff Dud Shemesh.

Target user: Israeli household with solar water tank + electric backup heater. Saves 30–60 % electricity vs always-on or naive schedules.

## Why this exists

- Most Israeli homes have **dud shemesh** = solar tank + electric immersion element on a relay.
- Default control = wall switch turned on for 1–2 h before shower. Wastes electricity if the sun already heated the tank.
- Commercial smart dud controllers cost ₪400–800 and lock you into proprietary apps.
- Existing HACS has nothing built specifically for this; users hack together generic timer integrations.
- This integration replaces the wall switch logic with a polished, visual, water-heater-shaped controller.

## Visual identity — must look like a real smart dud control

UI is the entire product. It must feel like a hardware appliance, not a HA panel.

**Sidebar panel layout (mockup):**

```
┌──────────────────────────────────────────────────┐
│  Dud Shemesh                              ⚙       │
│                                                   │
│        ┌─────────────────────────┐               │
│        │       ╭────────╮         │               │
│        │     ╱           ╲        │               │
│        │   ┃   ┌─────┐    ┃       │   ☀ Solar    │
│        │   ┃   │ 58° │    ┃       │   contributing│
│        │   ┃   │  C  │    ┃       │   +2° / 30min │
│        │   ┃   └─────┘    ┃       │               │
│        │     ╲   READY   ╱        │   🌡 38° → 60°│
│        │       ╰────────╯         │               │
│        │   ████████████░░░░       │   🔥 Off      │
│        │     45°            65°   │               │
│        └─────────────────────────┘               │
│                                                   │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│   │ +30 min │ │ + 1 h   │ │ + 2 h   │   BOOST     │
│   └─────────┘ └─────────┘ └─────────┘            │
│                                                   │
│   ┌──────────────────────────────────┐           │
│   │ Mode: ●Auto  ○Schedule  ○Off     │           │
│   └──────────────────────────────────┘           │
│                                                   │
│   ┌──────────────────────────────────┐           │
│   │ TODAY                            │           │
│   │ 06─────11─────15─────19─────23  │           │
│   │ │░░░░░░│██████│░░░░░░░░│██░░░░│ │           │
│   │   solar   AUTO       schedule   │           │
│   └──────────────────────────────────┘           │
└──────────────────────────────────────────────────┘
```

### Visual elements

1. **Big circular gauge** dominates the panel.
   - SVG dial showing current tank temp in °C inside the ring
   - Ring color gradient: blue (cold <35°) → green (warm 40–55°) → orange (hot 55–65°) → red (>65°)
   - Sub-arc showing current temp position between configured cold/hot setpoints
   - Pulsing animation when heater is ON

2. **Status badge** beneath the dial:
   - `READY` (green) — temp ≥ target, no action needed
   - `HEATING` (orange, pulsing) — electric element on
   - `WAITING` (blue) — scheduled to heat soon, time shown
   - `SOLAR` (yellow sun) — gaining heat from sun, no electric needed
   - `COLD` (red) — below comfort threshold, no plan to heat

3. **Solar status side panel** (live):
   - Sun icon when contributing
   - Temp delta over last 30 min (`+2 °C / 30min`)
   - Predicted peak solar gain today

4. **Boost row**: three big tappable buttons — `+30 min` / `+1 h` / `+2 h`
   - Forces electric ON for chosen duration regardless of mode
   - Visual countdown ring on the active button

5. **Mode toggle**: pill with three states
   - `Auto` — integration decides based on temp + sun + schedule
   - `Schedule` — only follows recurring schedule, no auto reasoning
   - `Off` — manual only, never fires automatically

6. **Today timeline** (horizontal scrub bar):
   - 24-hour ribbon, hour ticks
   - Coloured segments: yellow (solar contributing), green (auto-fired), orange (scheduled heat), grey (idle)
   - Live "now" cursor

7. **Settings drawer** (gear icon):
   - Target temperature (default 55 °C)
   - Comfort window: morning (06:00–08:00), evening (19:00–21:00)
   - Schedule rules
   - Solar prediction source (weather entity)
   - Anti-Legionella weekly cycle (60 °C once/week)
   - Family size / shower count → suggested temp

### Design language

- **Bold, large numbers** — temperature is hero
- **Smooth animations** — gauge fills, ring pulses, timeline cursor moves
- **Material You-ish** — rounded corners, soft shadows, accent color from primary HA theme
- **Hebrew + English** — UI bilingual; auto-RTL when HA language is `he`
- **Mobile-first** — works as a HA dashboard card on phone
- **No HA-flavored UI** — feels like Switchee app, not like Lovelace

## Core features

### MVP (v0.1)

- HA config flow: pick switch entity (electric element relay) + temp sensor entity
- Sidebar panel with the gauge + boost buttons + mode toggle
- Manual boost (`+30/+1h/+2h`)
- Schedule rules: weekly recurring (HH:MM + days + duration OR target-temp)
- Auto-close at target temp OR after duration
- Persistent settings via `Store`

### Smart layer (v0.2)

- **Solar gain estimator**: read temp delta over rolling 30 min window, classify trend (rising / flat / falling)
- **Skip-if-warm**: don't fire schedule if tank already at target
- **Pre-heat for showers**: estimate time-to-target based on past heating rate, fire just-in-time before configured comfort window
- **Weather-aware**: fetch tomorrow's forecast; if expected sunny, push schedule later or skip evening warm-up
- **Anti-Legionella mode**: force 60 °C cycle once per N days (configurable)

### Visibility layer (v0.3)

- **Today timeline** with mode-coloured segments
- **Reports tab**: daily/weekly kWh saved estimate, °C-min over time, cost in ILS based on current IEC tariff
- **Cost calculator**: integrates IEC TOU rates → shows real ₪ cost per heating cycle
- **Notifications**: "Tank is hot enough, your morning shower is ready", "Heater stuck on", "Tank cooled abnormally fast — check insulation"

### Pro-level (v0.4)

- **Multi-tank** support (vacation homes, big families with two heaters)
- **Hot water budget** — set monthly kWh ceiling, integration ensures stays under
- **Historical solar map** — visualize how much solar contributed each day across the year
- **Family shower scheduler** — input "kids shower at 19:00, parents at 22:00" → integration optimizes around that
- **Voice control** via HA Assist: "make sure water is hot by 7 AM"

### Stretch

- Auto-detect tank capacity by observing heating rate over a known idle-to-target cycle
- Vacation mode: keep tank at 30 °C (just above mold range), prepare to full temp on return date
- ML-based shower-prediction from past hot-water draws

## Architecture

Mirrors `schedule_wizard` structure:

```
custom_components/dud_shemesh/
  __init__.py            # entry, services, WS commands, panel registration
  manifest.json
  const.py               # config keys, event names, defaults
  config_flow.py         # initial setup + options
  storage.py             # Store helper for schedules, runs, settings
  scheduler.py           # core decision engine (auto-mode, boost, anti-legionella, solar reasoning)
  sensor.py              # sensors: target_status, solar_contributing, time_to_target
  services.yaml
  strings.json
  translations/{en,he,...}.json
  www/
    panel.js             # custom-element with the gauge UI
    card.js              # Lovelace card (mini gauge for dashboard embedding)
  brand/{icon,icon@2x,logo,logo@2x}.png
```

Tech: same stack as schedule_wizard. Pure Python integration + vanilla-JS panel + SVG gauge.

## Required HA inputs

| What | Required? | Notes |
| ---- | --------- | ----- |
| Heater relay (`switch.*`) | yes | The electric immersion element |
| Tank temperature sensor (`sensor.*` °C) | yes | Most install a DS18B20 on tank or use existing thermistor |
| Outdoor / weather entity | optional | Improves solar prediction |
| Solar PV inverter (if any) | optional | Better solar contribution estimate |
| Cold water inlet sensor | optional | Detect shower events |

If user lacks a tank temp sensor: integration runs in dumb-schedule mode (still useful, no skip-if-warm).

## Sensors created by the integration

- `sensor.dud_shemesh_target_status` — `ready` / `heating` / `waiting` / `solar` / `cold`
- `sensor.dud_shemesh_estimated_minutes_to_target` — int
- `sensor.dud_shemesh_today_kwh` — estimated (relay-on time × element wattage)
- `sensor.dud_shemesh_today_solar_gain` — estimated °C contributed by sun
- `sensor.dud_shemesh_next_heating` — friendly "Wed 06:30"

## Services (planned)

- `dud_shemesh.boost` (minutes: int) — manual override
- `dud_shemesh.cancel_boost`
- `dud_shemesh.set_mode` (mode: auto/schedule/off)
- `dud_shemesh.set_target_temp` (temp: int)
- `dud_shemesh.add_schedule` / `update` / `remove`
- `dud_shemesh.legionella_run_now`
- `dud_shemesh.list_config` (response service)

## Events

- `dud_shemesh_heat_started` — element ON, with reason
- `dud_shemesh_heat_finished` — element OFF, with reason + minutes + estimated kWh
- `dud_shemesh_target_reached` — tank hit configured target
- `dud_shemesh_solar_detected` — measurable solar gain underway
- `dud_shemesh_sensor_anomaly` — tank cooling faster than expected (insulation, leak, broken valve)

## UX rules (don't break)

- Hero is the dial. Always visible without scrolling.
- Boost buttons must be one-tap, large enough for kids and grandparents.
- No HA jargon in default labels. "Heater" not "switch entity".
- Default mode = `Auto`. User shouldn't have to read docs to use it day one.
- Hebrew text right-aligned, mirror layout.
- Dark mode + light mode equally polished.

## Phased roadmap

| Version | Scope                                                                                        |
| ------- | -------------------------------------------------------------------------------------------- |
| v0.1.0  | Manual boost + scheduled mode + gauge UI + persistence                                       |
| v0.2.0  | Auto mode (skip-if-warm, time-to-target estimate, pre-heat windows)                          |
| v0.3.0  | Anti-Legionella + Today timeline + Reports tab + IEC cost calc                               |
| v0.4.0  | Voice/Assist + multi-tank + family-aware optimizer                                           |
| v1.0.0  | Polish, translations, documentation, brand assets, HACS default submission                   |

## Open questions to confirm before coding

1. **Tank temp sensor placement** — top? bottom? mid? Affects accuracy of "ready" status.
2. **Element wattage** — typical Israeli dud is 2–3 kW; user must input for cost calc.
3. **Tariff source** — pull from IEC site (no public API) vs user-entered TOU windows. Probably user-entered for MVP.
4. **Solar gain measurement** — temp-rise during daylight hours = best proxy if no PV inverter data available.
5. **Anti-Legionella default** — recommend 60 °C / 7 days (WHO guideline) — confirm with user community.

## What to NOT build

- Direct heater wiring / hardware mods — out of scope, dangerous, leave to electrician
- Hot-water-flow detection without dedicated flow sensor — too noisy
- HA add-on companion — pure integration is enough; no separate process needed
- Cloud anything — stays local

## First-session task list (for future me)

When kicking this off in a new chat:

1. Read this `PROJECT.md` + `~/.claude/context-management.md` rules.
2. Confirm scope with Bar (it's been 1+ days, may have changed).
3. Scaffold `custom_components/dud_shemesh/` skeleton (manifest, const, __init__, config_flow, scheduler, storage).
4. Write the SVG gauge `panel.js` first — UI sets the bar, everything else follows.
5. Wire one fake config entry → manual boost → see relay turn on/off in dev HA.
6. Iterate from there per phased roadmap.

Reference repo for structure + conventions: `D:\Code\home assistant extensions\schedule_wizard\`.
