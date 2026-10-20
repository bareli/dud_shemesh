# Dud Shemesh

A Home Assistant **custom integration** that turns any smart switch and a tank temperature sensor into a controller for an Israeli solar water heater (*dud shemesh*) with an electric backup element.

It adds a sidebar panel with a big gauge, one-tap boost buttons, schedules, an Auto mode that heats ahead of the times you want hot water, reports, and a Lovelace card. It runs entirely inside Home Assistant, on the relay and sensor you already have.

![Panel control](screenshots/panel-control.png)

## What you get

- **Sidebar panel** with a circular gauge (drag the target marker to set the temperature), status badge, "next heat" line, boost buttons, mode switch, today timeline and schedules.
- **Auto mode** that pre-heats for your comfort windows, using the heating speed it learned from finished runs, and skips the electric element when the sun is doing the work.
- **Native entities**: a `water_heater`, buttons, a mode select, switches, binary sensors and sensors, including an energy sensor for the Home Assistant Energy dashboard.
- **Services, events and Assist intents** for your own automations and voice control.
- **Reports** for on-time, energy and cost, and a tank temperature chart.
- **Safety limits**: maximum run length, over-temperature cutoff, stale sensor detection and heat-not-rising detection.
- **Lovelace card** `custom:dud-shemesh-card`.
- English and Hebrew UI, right-to-left layout when Home Assistant runs in Hebrew.

See [Features](features.md) for the details.

![Reports](screenshots/panel-reports.png)

## Requirements

| Requirement | Notes |
| ----------- | ----- |
| Home Assistant **2024.7.0** or newer | Minimum version declared in `hacs.json`. |
| A heater relay | A `switch.*` (or `input_boolean.*`) that controls the electric immersion element. |
| A tank temperature sensor | Optional. A numeric `sensor.*` in °C. Without it the integration runs in dumb-schedule mode (time only). |
| [HACS](https://hacs.xyz) | For the recommended install. A manual install works too. |

Some features use other integrations when you have them: a `weather` entity, a `calendar`, a solar production forecast sensor (for example Forecast.Solar or Solcast), the Jewish Calendar integration, and `notify.*` services. None of them is required.

## Next steps

1. [Install](install.md) the integration and add it in Home Assistant.
2. Go through the [Configuration](configuration.md) options.
3. Copy ideas from the [Examples](examples.md).
