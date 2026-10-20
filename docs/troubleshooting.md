# Troubleshooting

## The heater turned off by itself

Check the run outcomes in Reports and the notification texts. These limits are on by default:

- A heater switched on outside Dud Shemesh is adopted as a run and turned off after **60 minutes** (setting "Auto-off after manual turn-on", `0` disables it).
- A run never exceeds **180 minutes**, boosts included.
- The heater is turned off at **75 °C** (over-temperature cutoff).
- When the tank reaches the target, the run ends with `target_reached`.

## A scheduled run did not start

Reports list the reason for every skipped run:

- **Already warm**: the schedule has a target temperature and the tank was already there.
- **Solar**: the temperature was rising without the element, so the sun is contributing.
- **Weather**: the weather state is in the skip list (default `sunny`). This is never applied between sunset and sunrise.
- **Skipped by you**: "skip next" was used on the schedule.
- The mode is **Off**, or vacation mode is active until a later date.

## "Showers" does not appear

The estimate is hidden while the tank volume is `0`. Set it in Settings → Basics.

## No temperature sensor

The sensor is optional. Without it the integration runs in dumb-schedule mode: it works by time only.

## The sensor is ignored

A temperature sensor that stops reporting for 120 minutes (setting "Treat sensor as stale after") is ignored, runs fall back to time only, and you get a `sensor_stale` notification when that event is enabled.

## Heat-not-rising alert

When fail detection is on, the tank must rise by a minimum amount within a set time after the element turns on. If it does not, you get a `heat_not_rising` alert. Check the element, the breaker and the sensor placement.

## Anti-Legionella is not marked as done

It is recorded as done only when the tank reaches the cycle temperature (default 60 °C). A run that ends earlier, for example at the maximum run length, does not count.

## Assist does not understand me

Copy the sentence file for your language into `<config>/custom_sentences/<language>/dud_shemesh.yaml` and restart Home Assistant. See [Voice (Assist)](examples.md#voice-assist).

## Shabbat mode does nothing

It needs the Jewish Calendar integration. The panel shows a message when the integration is not found.

## The panel or card looks outdated after an update

Restart Home Assistant after updating, then refresh the browser. If the browser still shows the old version, clear the browser cache or remove the Home Assistant service worker for the site. The panel header shows the loaded version.

## I cannot change the settings

The Settings gear is shown to admins only. Mode, target, heat now and vacation are open to every user.

## Which water heater does a service control?

Without `entry_id` a service acts on the first entry. Pass `entry_id` to control another one.

## Still stuck?

Open an issue at [github.com/bareli/dud_shemesh/issues](https://github.com/bareli/dud_shemesh/issues) with your Home Assistant version, the integration version and the relevant log lines.
