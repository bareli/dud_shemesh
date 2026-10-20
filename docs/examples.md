# Examples

## Services

All services live under `dud_shemesh.` and accept an optional `entry_id` (see [Multiple water heaters](features.md#multiple-water-heaters)).

| Service | Purpose |
| ------- | ------- |
| `dud_shemesh.boost` | Start the heater for N minutes (`minutes`, 1 to 720, default 60). |
| `dud_shemesh.cancel_boost` | Stop the heater immediately. |
| `dud_shemesh.set_mode` | `auto`, `schedule` or `off`. |
| `dud_shemesh.set_target_temp` | Change the target temperature (`temp`, 20 to 80 °C). |
| `dud_shemesh.add_schedule` | Add a recurring schedule. Returns the new id. |
| `dud_shemesh.update_schedule` | Patch a schedule by `schedule_id`. |
| `dud_shemesh.remove_schedule` | Delete a schedule by `schedule_id`. |
| `dud_shemesh.legionella_run_now` | Force a 60 °C+ heating cycle. |
| `dud_shemesh.list_config` | Returns schedules, history, active run, options and current status (response service). |

### Boost for 45 minutes

```yaml
action: dud_shemesh.boost
data:
  minutes: 45
```

### Add a weekday morning schedule

```yaml
action: dud_shemesh.add_schedule
data:
  name: Morning shower
  time: "06:00"
  days: [sun, mon, tue, wed, thu]
  duration_minutes: 60
  target_temp: 55
```

`days` takes `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`. `target_temp` is optional; with it, the run is skipped when the tank is already warm.

### Skip the next run once

`skip_until` is a Unix timestamp. Runs that would start before it are skipped. `0` clears it.

```yaml
action: dud_shemesh.update_schedule
data:
  schedule_id: "abc123"
  skip_until: 1790000000
```

### Read the full config

```yaml
action: dud_shemesh.list_config
response_variable: dud
```

## Events

| Event | When | Data |
| ----- | ---- | ---- |
| `dud_shemesh_heat_started` | Heater is turned on | `source`, `duration_min`, `target_temp`, `starting_temp` |
| `dud_shemesh_heat_finished` | Heater turned off | `source`, `status`, `duration_min` (planned), `actual_min` (element on-time), `starting_temp`, `ending_temp` |
| `dud_shemesh_target_reached` | Tank hit the target during a heat cycle | `source`, `temp`, `target_temp` |

`status` is one of `completed`, `target_reached`, `cancelled`, `manual_stop`, `external_stop`, `superseded`, `voice`, `expired_during_downtime`.

The code also fires `dud_shemesh_heat_not_rising`, `dud_shemesh_boost_extended` and `dud_shemesh_auto_preheat_planned`.

### Tell the family the water is hot

```yaml
alias: Hot water ready
triggers:
  - trigger: event
    event_type: dud_shemesh_target_reached
actions:
  - action: notify.notify
    data:
      message: "The water heater reached {{ trigger.event.data.temp }} °C"
```

### Log every finished run

```yaml
triggers:
  - trigger: event
    event_type: dud_shemesh_heat_finished
actions:
  - action: logbook.log
    data:
      name: Dud Shemesh
      message: >
        {{ trigger.event.data.status }}, {{ trigger.event.data.actual_min }} min,
        {{ trigger.event.data.starting_temp }} to {{ trigger.event.data.ending_temp }} °C
```

## Voice (Assist)

The integration registers the intents `DudShemeshBoost`, `DudShemeshStop` and `DudShemeshStatus`. To use them, copy the sentence file for your language and restart Home Assistant:

| Language | File in the repository | Copy to |
| -------- | ---------------------- | ------- |
| English | [`docs/assist/en/dud_shemesh.yaml`](https://github.com/bareli/dud_shemesh/blob/main/docs/assist/en/dud_shemesh.yaml) | `<config>/custom_sentences/en/dud_shemesh.yaml` |
| Hebrew | [`docs/assist/he/dud_shemesh.yaml`](https://github.com/bareli/dud_shemesh/blob/main/docs/assist/he/dud_shemesh.yaml) | `<config>/custom_sentences/he/dud_shemesh.yaml` |

Examples: "boost the water heater for 45 minutes", "is there hot water", "stop the water heater". The `water_heater` entity also works with the built-in turn on and turn off intents.

## Energy dashboard

Add the **Energy** sensor of the water heater as an individual device in **Settings → Dashboards → Energy**. It is a lifetime kWh counter (`total_increasing`).
