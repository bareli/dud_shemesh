# Install

## With HACS (recommended)

1. Open **HACS** and search for **Dud Shemesh**.
2. Open it, press **Download**, and restart Home Assistant.

!!! note "Not in the HACS search yet?"
    Dud Shemesh is submitted to the HACS default list and the review is pending. Until it shows up in the search, add it as a custom repository:

    1. HACS → ⋮ → **Custom repositories**.
    2. Repository: `https://github.com/bareli/dud_shemesh`, type: **Integration**.
    3. Search **Dud Shemesh** → **Download** → restart Home Assistant.

## Manual install

1. Copy the folder `custom_components/dud_shemesh/` from the repository into `<config>/custom_components/`.
2. Restart Home Assistant.

## Add the integration

1. **Settings → Devices & services → + Add integration → Dud Shemesh**.
2. Fill in the form:

    | Field | Meaning |
    | ----- | ------- |
    | Heater | The relay (`switch.*` or `input_boolean.*`) that powers the electric element. |
    | Tank temperature sensor | Optional. A numeric `sensor.*` in °C. |
    | Target temperature | Default 55 °C. |
    | Element wattage | Default 2400 W. Used for energy and cost. |
    | Tank volume | In litres, `0` = unknown. Used for the showers estimate and for the heating-speed fallback. |
    | Electricity price | In ₪/kWh. Default 0.62. |
    | Hot water needed at | Comfort windows such as `06:30-08:00,19:00-21:00`. Used by Auto mode. |

3. Open **Dud Shemesh** in the sidebar.

Everything else is changed later in the panel Settings. See [Configuration](configuration.md).

The Lovelace card is registered automatically as a Lovelace resource, so there is nothing to add by hand. After an update, restart Home Assistant and refresh the browser to load the new panel and card.

## Add more than one water heater

Add the integration again for a second heater or another home. Each entry has its own scheduler and its own storage file. See [Multiple water heaters](features.md#multiple-water-heaters).
