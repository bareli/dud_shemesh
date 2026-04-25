# Dud Shemesh — Project Context

Stay current here. Future-me reads this first.

## What this is

HACS custom integration: smart controller for Israeli solar water heater (dud shemesh) electric backup. Looks and feels like a commercial smart-dud appliance.

- Repo: https://github.com/bareli/dud_shemesh
- HACS default PR (pending review): https://github.com/hacs/default/pull/7259
- Latest version: **v0.4.1** (2026-04-25)
- Branches: `main` (primary, GitHub default) + `master` (force-pushed mirror for legacy validators)

## Owner

Bar Eli (Victor). bareli@gmail.com. Caesarea, Israel. Hebrew-first user.

## File map

```
dud_shemesh/
├── custom_components/dud_shemesh/
│   ├── __init__.py        # entry, services, WS, panel + card resource registration, intent registration
│   ├── manifest.json      # version, deps (http, lovelace, panel_custom, websocket_api)
│   ├── const.py           # all CONF_*, EVENT_*, SERVICE_*, NOTIFY_EVENTS, defaults
│   ├── config_flow.py     # config + options flow (multi-instance allowed since v0.4.0)
│   ├── storage.py         # DudStore: schedules, history (cap 500), active_boost, last_legionella
│   ├── scheduler.py       # cron loop, calendar poll, boost (extend), auto pre-heat, solar tracking, weather skip, fail check, anti-Legionella, vacation hold, notify
│   ├── sensor.py          # status / tank_temperature / minutes_to_target sensors
│   ├── services.yaml      # selectors for all services
│   ├── intents.yaml       # DudShemeshBoost / DudShemeshStop intent metadata
│   ├── strings.json       # config flow + options flow + service strings
│   ├── translations/{en,he}.json
│   ├── brand/             # icon.png + icon@2x.png + logo.png + logo@2x.png (placeholder "DS" 256/512)
│   └── www/
│       ├── panel.js       # sidebar custom element: gauge w/ drag-target, boost row, mode toggle, today timeline, schedules, Reports tab, Settings drawer (basic/advanced), partial Hebrew RTL
│       └── card.js        # Lovelace custom:dud-shemesh-card (mini gauge + boost + mode)
├── PROJECT.md             # original product spec / roadmap
├── README.md              # user-facing: features, install, services, events, sensors
├── CHANGELOG.md           # full history v0.1.0 → v0.4.1
├── LICENSE                # MIT
├── hacs.json              # min HA 2024.7.0
├── info.md                # HACS info page
├── .gitignore
├── .github/workflows/validate.yml  # HACS + hassfest CI
└── CLAUDE.md              # this file
```

## Major decisions baked in

- **panel_custom** ES module web component, cache-busted via `?v=<version>`.
- **Lovelace card auto-registered** as Lovelace `module` resource via `lovelace.resources` collection. Stale URLs deleted on each setup.
- **Storage** = HA `Store` helper (JSON file at `<config>/.storage/dud_shemesh.data`). History capped at 500.
- **Single config flow** until v0.3.x, **multi-instance** from v0.4.0 (single-instance check removed). Each entry runs an independent scheduler. Panel UI still shows the first entry — multi-tank picker UI deferred to v0.5.
- **Modes**: `auto` (predictive pre-heat for comfort windows), `schedule` (fire fixed cron rules), `off` (manual only).
- **Skip-if-warm**: cron schedule with `target_temp` skips if tank already at target.
- **Solar gain detection**: rolling 30-min temp delta; skips electric runs while sun is gaining.
- **Weather-aware**: optional weather entity; skip cron when state in `weather_skip_states` (default `sunny,clear-night`).
- **Boost = extend**: pressing +30 / +1 h while heating adds time to current `ends_at` instead of restarting.
- **Heat-not-rising detection**: optional safety check; verify tank temperature rises by ≥N °C within M minutes after element-on.
- **Vacation mode**: `vacation_until` Unix timestamp in options. Suspends schedules + auto-runs; holds tank at `vacation_hold_temp` (default 30 °C anti-mold).
- **Calendar-driven one-off heat**: optional HA calendar entity. Events whose summary matches a configured keyword (default `dud,water,חם,מים,דוד`) trigger a heat run. Description parses `Nm` for minutes and `Nc` for target temp.
- **Voice via HA Assist**: `DudShemeshBoost` (slot `minutes`, default 60) and `DudShemeshStop` intents registered via `intent.async_register`. User adds Assist sentence triggers.
- **Anti-Legionella**: optional. Daily 03:00 check; if N days since `last_legionella`, fire 60 °C+ cycle. Records timestamp on completion.
- **Cost calc**: configurable wattage + ₪/kWh tariff. Reports tab computes today / 7d / 30d energy + ₪.
- **Heat-rate trend**: avg °C/min over last 20 completions. Drop over time = element scaling.
- **Notifications**: list of `notify.*` services + list of event types (`heat_start`, `heat_end`, `target_reached`, `heat_not_rising`, `skipped_solar`, `skipped_weather`, `legionella_done`). Fire-and-forget.
- **Hebrew RTL**: detect `hass.language`/`hass.locale.language` starts with `he` → set `dir=rtl` on root + I18N strings dict (partial: tabs, mode pills, vacation banner, Legionella indicator translated; Settings modal + Reports tab still English — full pass planned for v0.5).
- **Drag-target**: SVG circle on gauge with `data-drag="target"`; pointer events translate angle → temperature → save via WS `update_options`.

## Conventions

- Version format: SemVer. Patch for bug fixes, minor for features. Currently 0.x.
- Each release: bump `manifest.json` `version` → update `CHANGELOG.md` → `git add -A` → commit → tag `vX.Y.Z` → push tag + main → force-push `main:master` → publish GitHub Release via Chrome browser automation.
- Memory rule: **always ask "anything else for this version?" before tag + release**.
- All replies in caveman mode (full level). Code stays normal.

## Outstanding work / roadmap

**Promised but not yet built:**
- Full Hebrew translation pass (Settings modal, Reports tab, schedule modal, side-pill labels, status badge).
- Multi-tank picker UI on panel (currently single-tank view even when multiple entries).
- Real brand icons (need user logo file).
- Voice via Assist sentence triggers documented in README.

**Deferred features (post-v0.5):**
- Multi-tank panel with per-tank dropdown + per-tank stats.
- Full RTL polish for Hebrew users.
- Advanced reports: per-month kWh/cost charts, heating-rate degradation alerts.
- HA blueprint pack ("schedule water heater", "boost when guests arrive") for one-click automation.
- Brand asset PR to home-assistant/brands (not needed since 2026.3 — local `brand/` folder is supported).

## Known limits / caveats

- Multi-instance works for scheduler logic but UI shows entry #0 only.
- Hebrew RTL only partial — most UI strings still English.
- Calendar one-off heat requires `calendar.get_events` service available (HA 2024.6+, already covered by min HA version).
- Voice intents require user to add Assist sentence triggers manually — README should document this in v0.5.
- Brand icons are placeholder PNGs ("DS" on orange).

## Bug history (avoid repeating)

- **YAML `off` parsed as boolean false** (v0.4.1): in `services.yaml`, `set_mode` selector options had unquoted `off`. YAML 1.1 maps to Python `False`. Hassfest validator caught it. Fix: quote string literals in selectors that look like YAML 1.1 booleans (`on`, `off`, `yes`, `no`).
- **Race when adding to `_active`** (carried over from schedule_wizard learning): with HA 2024.7+ `async_create_task` running eagerly, **always populate state dict BEFORE creating tasks that read from it**. Same pattern applies here for active_boost.
- **Blocking `open()` in event loop** (carried over): never `open()` synchronously in async paths. Use `hass.async_add_executor_job`. Cached `_INTEGRATION_VERSION_CACHE` for manifest version reads.
- **Stale frontend cache**: `?v=<version>` cache-bust on `module_url` and Lovelace resource URLs.
- **Default branch on GitHub initialized as `main`** here (different from schedule_wizard which started `master`). Keep `main` and force-push to `master` to match HACS default convention if needed.

## Sister projects

- **schedule_wizard** — see `D:\Code\home assistant extensions\schedule_wizard\CLAUDE.md`. Current version v0.7.3. HACS default PR #7239 pending.
- **WhatsApp HA Bridge** — discussed; not yet scoped/started.

## Quick "where am I" checks for next session

```bash
# Current version
grep version "D:/Code/home assistant extensions/dud_shemesh/custom_components/dud_shemesh/manifest.json"

# Latest tag on remote
git ls-remote --tags https://github.com/bareli/dud_shemesh.git | tail -3

# Pending HACS PR status (if gh CLI installed):
# https://github.com/hacs/default/pull/7259
```

## Memory file references

- `~/.claude/projects/D--Code-home-assistant-extensions-schedule-wizard/memory/feedback_release_confirm.md` — ask before each version close (applies project-wide for HA work).
- `~/.claude/CLAUDE.md` — global preferences (Hebrew, no em-dashes, metric, etc).
- `~/.claude/context/identity.md` — Bar profile, projects.
