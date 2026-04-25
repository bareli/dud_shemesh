# Dud Shemesh

Smart controller for Israeli solar water heater (dud shemesh) electric backup. HACS-installable HA integration with a sidebar UI that looks and feels like a commercial smart-dud appliance.

## Features (v0.1)

- Big circular gauge with current tank temperature, target marker, and live status badge.
- One-tap **+30 min / +1 h / +2 h** boost buttons.
- **Mode toggle**: Auto / Schedule / Off.
- Recurring schedules (HH:MM + days of week + duration, optional target temp).
- **Skip-if-warm**: scheduled run is skipped when the tank is already at target.
- Auto-close at target temperature OR after configured duration.
- Optional **Anti-Legionella** weekly cycle to 60 °C+.
- Today timeline of heater activity.
- 3 sensors: status, tank temperature, estimated minutes to target.
- Companion Lovelace card with quick boost.
- Bilingual (English + Hebrew) config strings.

## Setup

1. HACS → Custom repositories → add repo as Integration.
2. Search "Dud Shemesh" → Download → restart HA.
3. Settings → Devices & Services → + Add Integration → Dud Shemesh.
4. Pick the heater relay (`switch.*`) and a tank temperature sensor (`sensor.*`).
5. Open the **Dud Shemesh** entry in the sidebar.

Smart auto layer (skip-if-warm with predictive pre-heat, solar gain detection, weather-aware scheduling) lands in v0.2.
