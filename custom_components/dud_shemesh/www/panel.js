const PANEL_VERSION = "0.5.0";
const STYLES = `
:host, :root {
  --ds-bg: var(--primary-background-color, #f4f6fa);
  --ds-card: var(--card-background-color, #fff);
  --ds-text: var(--primary-text-color, #1f2933);
  --ds-muted: var(--secondary-text-color, #6b7280);
  --ds-primary: var(--primary-color, #ff7a00);
  --ds-cool: #2196f3;
  --ds-warm: #4caf50;
  --ds-hot: #ff9800;
  --ds-solar: #ffc107;
  --ds-danger: var(--error-color, #e53935);
  --ds-border: var(--divider-color, #e5e7eb);
}
* { box-sizing: border-box; }
.app {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px;
  font-family: var(--paper-font-body1_-_font-family, -apple-system, Roboto, sans-serif);
  color: var(--ds-text);
}
.header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px;
}
.header .brand { display: flex; align-items: baseline; gap: 8px; }
.header h1 { margin: 0; font-size: 24px; font-weight: 500; }
.tank-picker {
  font: inherit; font-size: 14px; padding: 6px 10px; border-radius: 8px;
  border: 1px solid var(--ds-border); background: var(--ds-card); color: var(--ds-text);
  max-width: 200px;
}
.header .ver { opacity: .55; font-size: 11px; }
.icon-btn {
  background: transparent; border: none; cursor: pointer;
  padding: 8px; border-radius: 50%; color: var(--ds-muted);
  font-size: 20px; line-height: 1;
}
.icon-btn:hover { background: var(--ds-border); }
.card {
  background: var(--ds-card);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid var(--ds-border);
}
.gauge-card {
  display: grid;
  grid-template-columns: 1fr 170px;
  gap: 12px;
  align-items: center;
}
@media (max-width: 600px) {
  .gauge-card { grid-template-columns: 1fr; }
  .side { flex-direction: row !important; flex-wrap: wrap; justify-content: center !important; }
  .side-item { flex: 1 1 120px; }
}
.gauge-col { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.gauge-wrap { position: relative; display: flex; justify-content: center; width: 100%; }
.target-row { display: flex; align-items: center; gap: 10px; }
.target-row .tval { font-size: 14px; color: var(--ds-muted); min-width: 92px; text-align: center; }
.round-btn {
  width: 34px; height: 34px; border-radius: 50%;
  border: 1px solid var(--ds-border); background: var(--ds-bg); color: var(--ds-text);
  font-size: 18px; cursor: pointer; font-family: inherit; line-height: 1;
}
.round-btn:hover { background: var(--ds-border); }
.side {
  display: flex; flex-direction: column; gap: 10px;
}
.side-item {
  text-align: center;
  padding: 10px;
  border-radius: 12px;
  background: var(--ds-bg);
  border: 1px solid var(--ds-border);
}
.side-item .label { font-size: 11px; color: var(--ds-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.side-item .value { font-size: 18px; font-weight: 600; margin-top: 4px; }
.next-heat {
  grid-column: 1 / -1;
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: 12px;
  background: rgba(33,150,243,0.08); border: 1px solid rgba(33,150,243,0.25);
  font-size: 14px;
}
.next-heat .ico { font-size: 18px; }
.next-heat .sub { color: var(--ds-muted); font-size: 12px; }
.boost-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 10px;
}
.boost-btn {
  background: var(--ds-primary);
  color: white;
  border: none;
  padding: 18px 10px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.2s;
  box-shadow: 0 4px 12px rgba(255,122,0,0.25);
  font-family: inherit;
}
.boost-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(255,122,0,0.35); }
.boost-btn:active { transform: translateY(0); }
.boost-btn.cancel { background: var(--ds-danger); box-shadow: 0 4px 12px rgba(229,57,53,0.25); grid-column: 1 / -1; }
.boost-btn.extend { background: rgba(255,122,0,0.15); color: var(--ds-primary); box-shadow: none; padding: 12px 8px; }
.mode-toggle {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  background: var(--ds-bg);
  border-radius: 14px;
  padding: 4px;
  border: 1px solid var(--ds-border);
}
.mode-pill {
  text-align: center;
  padding: 10px 6px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  color: var(--ds-muted);
  transition: all 0.2s;
  background: transparent; border: none; font-family: inherit;
}
.mode-pill.active {
  background: var(--ds-card);
  color: var(--ds-text);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.mode-hint { font-size: 12px; color: var(--ds-muted); margin: 8px 4px 0; }
.timeline {
  display: flex;
  height: 24px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--ds-border);
  margin-top: 8px;
  position: relative;
}
.timeline-seg { flex: 1; }
.timeline-seg.idle { background: var(--ds-border); }
.timeline-seg.heating { background: var(--ds-hot); }
.timeline-seg.scheduled { background: var(--ds-cool); }
.timeline-seg.planned {
  background: repeating-linear-gradient(45deg, rgba(33,150,243,0.45) 0 4px, rgba(33,150,243,0.15) 4px 8px);
}
.timeline-now {
  position: absolute;
  top: -4px; bottom: -4px;
  width: 2px;
  background: var(--ds-text);
  pointer-events: none;
}
.timeline-labels {
  display: flex; justify-content: space-between;
  font-size: 11px; color: var(--ds-muted);
  margin-top: 4px;
}
.legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 11px; color: var(--ds-muted); margin-top: 8px; }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-inline-end: 5px; vertical-align: -1px; }
.schedule-card h3, .settings-card h3 { margin: 0 0 12px; font-size: 16px; }
.row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid var(--ds-border);
  border-radius: 10px;
  margin-bottom: 8px;
  background: var(--ds-bg);
}
.row.disabled .name, .row.disabled .sub { opacity: .55; }
.row .name { font-weight: 500; }
.row .sub { font-size: 12px; color: var(--ds-muted); }
.row .next { font-size: 12px; color: var(--ds-cool); margin-top: 2px; }
.row .next.skipped { color: var(--ds-hot); }
.row .actions { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
@media (max-width: 600px) {
  .row { grid-template-columns: auto 1fr; }
  .row .actions { grid-column: 1 / -1; justify-content: flex-start; }
}
.switch { position: relative; width: 38px; height: 22px; flex: none; }
.switch input { opacity: 0; width: 0; height: 0; }
.switch span {
  position: absolute; inset: 0; border-radius: 22px; cursor: pointer;
  background: var(--ds-border); transition: background .2s;
}
.switch span::before {
  content: ""; position: absolute; width: 16px; height: 16px; top: 3px; inset-inline-start: 3px;
  border-radius: 50%; background: white; transition: transform .2s; box-shadow: 0 1px 2px rgba(0,0,0,.3);
}
.switch input:checked + span { background: var(--ds-primary); }
.switch input:checked + span::before { transform: translateX(16px); }
[dir=rtl] .switch input:checked + span::before { transform: translateX(-16px); }
.btn {
  background: var(--ds-card); border: 1px solid var(--ds-border);
  color: var(--ds-text); padding: 6px 12px; border-radius: 8px;
  cursor: pointer; font: inherit; font-size: 13px;
}
.btn.primary { background: var(--ds-primary); border-color: var(--ds-primary); color: white; }
.btn.danger { color: var(--ds-danger); border-color: var(--ds-danger); }
.btn.small { padding: 4px 10px; font-size: 12px; }
.empty { color: var(--ds-muted); font-style: italic; padding: 8px 0; }
.nav-tabs {
  display: flex; gap: 4px; margin-bottom: 14px;
  background: var(--ds-bg); border-radius: 12px; padding: 4px;
  border: 1px solid var(--ds-border);
}
.nav-tab {
  flex: 1; text-align: center; padding: 8px 6px;
  border-radius: 8px; cursor: pointer;
  font-size: 13px; font-weight: 500; color: var(--ds-muted);
  transition: all 0.2s;
  background: transparent; border: none; font-family: inherit;
}
.nav-tab.active {
  background: var(--ds-card); color: var(--ds-text);
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.legionella-pill {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 6px 10px; border-radius: 12px;
  background: rgba(76,175,80,0.1); color: #2e7d32;
  font-size: 11px;
}
.legionella-pill.due { background: rgba(229,57,53,0.15); color: var(--ds-danger); }
.report-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
  gap: 10px; margin-bottom: 12px;
}
.report-tile {
  padding: 14px; border-radius: 12px;
  background: var(--ds-bg); border: 1px solid var(--ds-border);
  text-align: center;
}
.report-tile .v { font-size: 24px; font-weight: 700; color: var(--ds-text); }
.report-tile .l { font-size: 11px; color: var(--ds-muted); text-transform: uppercase; letter-spacing: 0.4px; margin-top: 4px; }
.savings {
  background: linear-gradient(135deg, rgba(255,193,7,0.18), rgba(76,175,80,0.12));
  border-color: rgba(255,193,7,0.4);
}
.savings .big { font-size: 34px; font-weight: 800; }
.savings .sub { color: var(--ds-muted); font-size: 13px; margin-top: 4px; }
.savings .row2 { display: flex; gap: 24px; flex-wrap: wrap; margin-top: 10px; font-size: 13px; }
.section-title { font-size: 14px; font-weight: 600; margin: 12px 0 8px; }
.tariff-link { font-size: 12px; color: var(--ds-muted); }
@keyframes ringPulse {
  0%, 100% { stroke-width: 18; opacity: 1; }
  50%      { stroke-width: 22; opacity: 0.85; }
}
.gauge-arc-active { animation: ringPulse 2s ease-in-out infinite; }
.advanced-toggle {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--ds-border);
}
.advanced-toggle button {
  background: transparent; border: 1px solid var(--ds-border);
  border-radius: 8px; padding: 4px 10px; cursor: pointer;
  font-size: 12px; font-family: inherit; color: var(--ds-text);
}
.field { display: block; margin-bottom: 12px; }
.field > span { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; color: var(--ds-muted); }
.field input:not([type=checkbox]), .field select {
  width: 100%; padding: 8px 10px;
  border: 1px solid var(--ds-border); border-radius: 8px;
  background: var(--ds-card); color: var(--ds-text); font: inherit;
}
.hint { font-size: 11px; color: var(--ds-muted); margin-top: 3px; }
.check { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: 13px; cursor: pointer; }
.check input { width: 16px; height: 16px; margin: 0; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  display: inline-flex; align-items: center; gap: 6px; font-size: 13px;
  padding: 4px 8px; border: 1px solid var(--ds-border); border-radius: 6px; cursor: pointer;
  background: var(--ds-card);
}
.chip input { margin: 0; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: var(--ds-card); border-radius: 16px; padding: 20px;
  max-width: 480px; width: calc(100% - 32px); max-height: 85vh; overflow-y: auto;
}
.modal h3 { margin: 0 0 14px; }
.modal h4 { margin: 16px 0 8px; font-size: 14px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }
.days { display: flex; gap: 4px; flex-wrap: wrap; }
.day-toggle {
  padding: 6px 10px; border: 1px solid var(--ds-border); background: var(--ds-card); color: var(--ds-text);
  border-radius: 6px; cursor: pointer; user-select: none; font-size: 12px; font-family: inherit;
}
.day-toggle.on { background: var(--ds-primary); border-color: var(--ds-primary); color: white; }
.toast {
  position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
  padding: 10px 16px; background: var(--ds-text); color: var(--ds-bg);
  border-radius: 6px; font-size: 13px; z-index: 200;
}
.toast.error { background: var(--ds-danger); color: white; }
.toast.ok { background: var(--ds-warm); color: white; }
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.status-badge.heating { background: rgba(255,152,0,0.15); color: var(--ds-hot); animation: pulse 1.5s infinite; }
.status-badge.ready { background: rgba(76,175,80,0.15); color: var(--ds-warm); }
.status-badge.solar { background: rgba(255,213,79,0.25); color: #f57f17; }
.status-badge.cold { background: rgba(33,150,243,0.15); color: var(--ds-cool); }
.status-badge.waiting { background: var(--ds-border); color: var(--ds-muted); }
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}
button:focus-visible, .nav-tab:focus-visible, .mode-pill:focus-visible { outline: 2px solid var(--ds-primary); outline-offset: 2px; }
`;

function el(tag, attrs = {}, children = []) {
  const n = document.createElement(tag);
  for (const k of Object.keys(attrs)) {
    const v = attrs[k];
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2).toLowerCase(), v);
    else if (v === false || v == null) {}
    else if (v === true) n.setAttribute(k, "");
    else n.setAttribute(k, v);
  }
  (Array.isArray(children) ? children : [children]).forEach(c => {
    if (c == null || c === false) return;
    n.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
  });
  return n;
}

const I18N = {
  en: {
    brand: "Dud Shemesh", tank: "Water heater", control: "Control", reports: "Reports", settings: "Settings",
    target: "Target", target_val: (v, u) => `Target ${v}${u}`, mode: "Mode",
    auto: "Auto", schedule: "Schedule", off: "Off",
    mode_hint_auto: "Heats ahead of your comfort windows and runs your schedules, skipping when the sun is doing the job.",
    mode_hint_schedule: "Runs your schedules at fixed times, skipping when the tank is already warm or the sun is heating it.",
    mode_hint_off: "No automatic heating. Boost buttons still work.",
    st_ready: "Ready", st_heating: "Heating", st_waiting: "Waiting", st_solar: "Solar", st_cold: "Cold",
    src_schedule: "Schedule", src_boost: "Boost", src_manual: "Turned on manually", src_auto: "Pre-heat",
    src_legionella: "Anti-Legionella", src_calendar: "Calendar", src_vacation_hold: "Vacation hold",
    ends_in: "Ends in", to_target: "To target", about_min: (n) => `~${n} min`, status_label: "Status",
    showers: "Showers", showers_val: (n) => `~${n}`,
    boost_min: (n) => `${n} min`, boost_hour: "1 hour", boost_hours: (n) => `${n} hours`,
    extend: (label) => `+${label}`,
    stop_heating: "STOP HEATING",
    next_heat: "Next heat", no_heat_planned: "No heating planned in the next 24 h",
    hot_by: (t) => `Hot by ${t}`, starts: (w) => `starts ${w}`, in_x: (d) => `in ${d}`,
    today_word: "Today", tomorrow_word: "Tomorrow",
    legionella_in: (d) => `🦠 ${d}d to anti-Legionella`, legionella_due: "🦠 Anti-Legionella due",
    vacation_active: (d, t) => `🏖 Vacation — ${d}d left, holding ${t}°C`, vacation_end: "End",
    today: "Today", lg_heated: "Heated", lg_scheduled: "Schedule", lg_planned: "Planned",
    schedules: "Schedules", add: "+ Add", no_schedules: "No schedules yet. Tap + Add to create one.",
    edit_btn: "Edit", delete_confirm: "Delete this schedule?", skip_once: "Skip next", undo_skip: "Undo skip",
    next_run: (w) => `Next: ${w}`, skipped_until: (w) => `Skipping once, then ${w}`, not_scheduled: "Not scheduled",
    sched_default_name: (t) => `Heat ${t}`, enabled: "Enabled",
    add_schedule: "Add schedule", edit_schedule: "Edit schedule", name: "Name", optional: "Optional",
    time: "Time", duration_min: "Duration (min)", target_opt: "Target temp (°C, optional)", days: "Days",
    blank_off: "Blank = time only", pick_day: "Pick at least one day",
    save: "Save", cancel: "Cancel", done: "Done", saved: "Saved", failed_load: "Failed to load: ",
    saved_month: "Saved this month", saved_sub: (kwh) => `${kwh} kWh of electric heating avoided by sun and skips`,
    saved_total: (v) => `All history: ${v}`, skipped_runs: (n) => `${n} runs skipped`,
    last30_chart: "Last 30 days (kWh)", lg_electric: "Electric", lg_avoided: "Avoided",
    last7: "Last 7 days", last30: "Last 30 days", on_time: "On time", energy: "Energy", cost: "Cost",
    tariff_note: (w, t) => `Wattage ${w} W × on-time × ₪${t}/kWh. Adjust in Settings.`,
    heater_health: "Heater health", avg_rate: "Avg heat rate (last 20)", cycles: "Cycles measured",
    descale_hint: "If this number drops over weeks, the element may be scaling. Schedule a descale.",
    temp_chart: "Tank temperature (recent samples)", outcomes: "Run outcomes (history)",
    oc_skipped_warm: "Already warm", oc_skipped_solar: "Solar gaining", oc_skipped_weather: "Sunny",
    oc_skipped_user: "Skipped by you", oc_completed: "Completed", oc_target_reached: "Target reached",
    oc_cancelled: "Cancelled", oc_safety: "Safety stops",
    dur_hm: (h, m) => `${h}h ${String(m).padStart(2, "0")}m`, dur_m: (m) => `${m}m`,
    s_target: "Target temperature (°C)", s_boost: "Boost buttons (min, comma-separated)",
    s_wattage: "Heater wattage (W)", s_tariff: "Tariff (₪/kWh)", s_tank: "Tank volume (L)",
    s_tank_hint: "Used for the showers estimate. 0 = hide.",
    adv_shown: "Advanced (shown)", adv_hidden: "Advanced (hidden)", show: "Show", hide: "Hide",
    h_auto: "Auto mode", s_windows: "Comfort windows (HH:MM-HH:MM, comma-separated)",
    s_margin: "Pre-heat margin (min before window)",
    h_weather: "Weather skip", s_weather_ent: "Weather entity", s_weather_states: "Skip when state is (comma-separated)",
    s_weather_hint: "Never applied between sunset and sunrise.",
    h_solar: "Solar tracking", s_solar_min: "Track window (min)", s_solar_thr: "Rise threshold (°C / 30min)",
    h_safety: "Safety", s_manual_max: "Auto-off after manual turn-on (min, 0 = off)",
    s_max_run: "Maximum run length (min)", s_max_temp: "Over-temperature cutoff (°C)",
    s_stale: "Treat sensor as stale after (min, 0 = never)",
    h_fail: "Fail detection", s_check_after: "Check after (min)", s_min_rise: "Min rise (°C)",
    h_legionella: "Anti-Legionella", s_cycle_temp: "Cycle temp (°C)", s_every_days: "Every N days",
    h_vacation: "Vacation mode",
    vacation_hint: "Until this date/time, schedules and auto-runs are suspended. Tank is held at hold-temp to prevent mold.",
    s_vac_until: "Active until (clear to disable)", s_vac_hold: "Hold temperature (°C)",
    h_notify: "Notifications", notify_hint: "Pick notify services and which events send a push.",
    s_notify_services: "Notify services", s_notify_when: "Send when", no_notify: "No notify.* services detected.",
    ev_heat_start: "Heat started", ev_heat_end: "Heat ended", ev_target_reached: "Target reached",
    ev_heat_not_rising: "Heater fault", ev_skipped_solar: "Skipped (solar)", ev_skipped_weather: "Skipped (weather)",
    ev_legionella_done: "Anti-Legionella done", ev_safety_stop: "Safety stop", ev_sensor_stale: "Sensor offline",
    days_short: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  },
  he: {
    brand: "דוד שמש", tank: "דוד", control: "בקרה", reports: "דוחות", settings: "הגדרות",
    target: "יעד", target_val: (v, u) => `יעד ${v}${u}`, mode: "מצב",
    auto: "אוטומטי", schedule: "לוח זמנים", off: "כבוי",
    mode_hint_auto: "מחמם מראש לפני חלונות הנוחות ומריץ את לוחות הזמנים, ומדלג כשהשמש עושה את העבודה.",
    mode_hint_schedule: "מריץ את לוחות הזמנים בשעות קבועות, ומדלג כשהמים כבר חמים או שהשמש מחממת.",
    mode_hint_off: "ללא חימום אוטומטי. כפתורי ההפעלה המהירה עדיין עובדים.",
    st_ready: "מוכן", st_heating: "מחמם", st_waiting: "ממתין", st_solar: "סולארי", st_cold: "קר",
    src_schedule: "לוח זמנים", src_boost: "הפעלה מהירה", src_manual: "הודלק ידנית", src_auto: "חימום מקדים",
    src_legionella: "חיטוי ליגיונלה", src_calendar: "יומן", src_vacation_hold: "שמירה בחופשה",
    ends_in: "מסתיים בעוד", to_target: "עד היעד", about_min: (n) => `כ-${n} דק׳`, status_label: "מצב",
    showers: "מקלחות", showers_val: (n) => `כ-${n}`,
    boost_min: (n) => `${n} דק׳`, boost_hour: "שעה", boost_hours: (n) => (n === 2 ? "שעתיים" : `${n} שעות`),
    extend: (label) => `עוד ${label}`,
    stop_heating: "הפסק חימום",
    next_heat: "החימום הבא", no_heat_planned: "אין חימום מתוכנן ב-24 השעות הקרובות",
    hot_by: (t) => `חם עד ${t}`, starts: (w) => `מתחיל ${w}`, in_x: (d) => `בעוד ${d}`,
    today_word: "היום", tomorrow_word: "מחר",
    legionella_in: (d) => `🦠 עוד ${d} ימים לחיטוי ליגיונלה`, legionella_due: "🦠 נדרש חיטוי ליגיונלה",
    vacation_active: (d, t) => `🏖 חופשה — עוד ${d} ימים, שמירה על ${t}°C`, vacation_end: "סיום",
    today: "היום", lg_heated: "חומם", lg_scheduled: "לוח זמנים", lg_planned: "מתוכנן",
    schedules: "לוחות זמנים", add: "+ הוספה", no_schedules: "אין עדיין לוחות זמנים. לחצו + הוספה.",
    edit_btn: "עריכה", delete_confirm: "למחוק את לוח הזמנים?", skip_once: "דלג על הבא", undo_skip: "בטל דילוג",
    next_run: (w) => `הבא: ${w}`, skipped_until: (w) => `מדלג פעם אחת, ואז ${w}`, not_scheduled: "לא מתוזמן",
    sched_default_name: (t) => `חימום ${t}`, enabled: "פעיל",
    add_schedule: "הוספת לוח זמנים", edit_schedule: "עריכת לוח זמנים", name: "שם", optional: "רשות",
    time: "שעה", duration_min: "משך (דק׳)", target_opt: "טמפ׳ יעד (°C, רשות)", days: "ימים",
    blank_off: "ריק = לפי זמן בלבד", pick_day: "יש לבחור לפחות יום אחד",
    save: "שמירה", cancel: "ביטול", done: "בוצע", saved: "נשמר", failed_load: "הטעינה נכשלה: ",
    saved_month: "נחסך החודש", saved_sub: (kwh) => `${kwh} קוט״ש של חימום חשמלי נחסכו בזכות השמש והדילוגים`,
    saved_total: (v) => `כל ההיסטוריה: ${v}`, skipped_runs: (n) => `${n} הפעלות דולגו`,
    last30_chart: "30 הימים האחרונים (קוט״ש)", lg_electric: "חשמל", lg_avoided: "נחסך",
    last7: "7 הימים האחרונים", last30: "30 הימים האחרונים", on_time: "זמן פעולה", energy: "אנרגיה", cost: "עלות",
    tariff_note: (w, t) => `הספק ${w} וואט × זמן פעולה × ₪${t} לקוט״ש. ניתן לשנות בהגדרות.`,
    heater_health: "מצב גוף החימום", avg_rate: "קצב חימום ממוצע, 20 אחרונים", cycles: "מחזורים שנמדדו",
    descale_hint: "אם המספר יורד לאורך שבועות, ייתכן שיש אבנית על הגוף. כדאי לתאם ניקוי.",
    temp_chart: "טמפרטורת המיכל (דגימות אחרונות)", outcomes: "תוצאות הפעלות (היסטוריה)",
    oc_skipped_warm: "כבר חם", oc_skipped_solar: "חימום סולארי", oc_skipped_weather: "שמשי",
    oc_skipped_user: "דולג על ידך", oc_completed: "הושלם", oc_target_reached: "הגיע ליעד",
    oc_cancelled: "בוטל", oc_safety: "עצירות בטיחות",
    dur_hm: (h, m) => `${h} ש׳ ${String(m).padStart(2, "0")} ד׳`, dur_m: (m) => `${m} ד׳`,
    s_target: "טמפרטורת יעד (°C)", s_boost: "כפתורי הפעלה מהירה (דק׳, מופרד בפסיקים)",
    s_wattage: "הספק גוף החימום (וואט)", s_tariff: "תעריף (₪ לקוט״ש)", s_tank: "נפח המיכל (ליטר)",
    s_tank_hint: "משמש להערכת מספר המקלחות. 0 = להסתיר.",
    adv_shown: "מתקדם (מוצג)", adv_hidden: "מתקדם (מוסתר)", show: "הצג", hide: "הסתר",
    h_auto: "מצב אוטומטי", s_windows: "חלונות נוחות (HH:MM-HH:MM, מופרד בפסיקים)",
    s_margin: "מרווח חימום מקדים (דק׳ לפני החלון)",
    h_weather: "דילוג לפי מזג אוויר", s_weather_ent: "ישות מזג אוויר", s_weather_states: "דלג כשהמצב הוא (מופרד בפסיקים)",
    s_weather_hint: "לא חל בין השקיעה לזריחה.",
    h_solar: "מעקב סולארי", s_solar_min: "חלון מעקב (דק׳)", s_solar_thr: "סף עלייה (°C ל-30 דק׳)",
    h_safety: "בטיחות", s_manual_max: "כיבוי אוטומטי אחרי הדלקה ידנית (דק׳, 0 = כבוי)",
    s_max_run: "משך הפעלה מקסימלי (דק׳)", s_max_temp: "ניתוק בטמפרטורת יתר (°C)",
    s_stale: "חיישן נחשב לא מעודכן אחרי (דק׳, 0 = אף פעם)",
    h_fail: "זיהוי תקלה", s_check_after: "בדיקה אחרי (דק׳)", s_min_rise: "עלייה מינימלית (°C)",
    h_legionella: "חיטוי ליגיונלה", s_cycle_temp: "טמפ׳ מחזור (°C)", s_every_days: "כל N ימים",
    h_vacation: "מצב חופשה",
    vacation_hint: "עד התאריך הזה לוחות הזמנים והחימום האוטומטי מושהים. המיכל נשמר בטמפ׳ שמירה נגד עובש.",
    s_vac_until: "פעיל עד (ריק = כבוי)", s_vac_hold: "טמפ׳ שמירה (°C)",
    h_notify: "התראות", notify_hint: "בחרו שירותי התראה ואילו אירועים ישלחו התראה.",
    s_notify_services: "שירותי התראה", s_notify_when: "לשלוח כאשר", no_notify: "לא נמצאו שירותי notify.*",
    ev_heat_start: "חימום התחיל", ev_heat_end: "חימום הסתיים", ev_target_reached: "הגיע ליעד",
    ev_heat_not_rising: "תקלה בגוף החימום", ev_skipped_solar: "דולג (שמש)", ev_skipped_weather: "דולג (מזג אוויר)",
    ev_legionella_done: "חיטוי הושלם", ev_safety_stop: "עצירת בטיחות", ev_sensor_stale: "חיישן לא זמין",
    days_short: ["ב׳", "ג׳", "ד׳", "ה׳", "ו׳", "ש׳", "א׳"],
  },
};

function svgEl(tag, attrs = {}, children = []) {
  const n = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const k of Object.keys(attrs)) {
    if (attrs[k] != null) n.setAttribute(k, attrs[k]);
  }
  (Array.isArray(children) ? children : [children]).forEach(c => c && n.appendChild(c));
  return n;
}

// Day bits are Monday-first (backend DAY_BITS); display order may start on Sunday.
const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const DAY_BITS = [1, 2, 4, 8, 16, 32, 64];
const SKIP_STATUSES = new Set(["skipped_warm", "skipped_solar", "skipped_weather"]);

// Minutes the element actually ran for one history row (0 for starts/skips).
// Rows before 0.4.13 have no actual_min; fall back to the planned duration.
function runMinutes(h) {
  const st = String(h.status || "");
  if (st === "started" || st.startsWith("skipped")) return 0;
  if (typeof h.actual_min === "number") return h.actual_min;
  return st === "completed" || st === "target_reached" ? (parseInt(h.duration_min || 0, 10) || 0) : 0;
}

function localDayStart(ts) {
  const d = new Date(ts * 1000);
  return new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime() / 1000;
}

function toLocalInputValue(ts) {
  const d = new Date(ts * 1000);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

function numOr(value, fallback, parse = parseFloat) {
  const n = parse(value);
  return Number.isFinite(n) ? n : fallback;
}

function daysFromMask(mask) {
  return DAYS.filter((_, i) => mask & DAY_BITS[i]);
}

class DudPanel extends HTMLElement {
  constructor() {
    super();
    this._initialized = false;
    this._state = null;
    this._refreshTimer = null;
    this._modalRoot = null;
    this._view = "control";
    this._showAdvanced = false;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) this._init();
    this._maybeRefreshOnHeaterChange();
  }

  _maybeRefreshOnHeaterChange() {
    if (!this._hass || !this._state) return;
    const heaterId = this._state.options && this._state.options.heater_entity;
    if (!heaterId) return;
    const cur = this._hass.states && this._hass.states[heaterId];
    if (!cur) return;
    const last = this._lastHeaterState;
    this._lastHeaterState = cur.state;
    if (last !== undefined && last !== cur.state) {
      this._refresh();
    }
  }
  set narrow(v) { this._narrow = v; }
  set route(v) { this._route = v; }
  set panel(v) { this._panel = v; }

  connectedCallback() {
    if (!this._hass) return;
    if (!this._initialized) {
      this._init();
    } else {
      this._startTimers();
      this._refresh().then(() => this._subscribeHeaterState());
    }
    if (!this._visibilityHandler) {
      this._visibilityHandler = () => {
        if (document.visibilityState === "visible") {
          this._refresh();
          this._tickEndsIn();
        }
      };
      document.addEventListener("visibilitychange", this._visibilityHandler);
    }
  }
  disconnectedCallback() {
    this._stopTimers();
    if (this._heaterUnsub) { try { this._heaterUnsub(); } catch (e) {} this._heaterUnsub = null; }
    if (this._visibilityHandler) {
      document.removeEventListener("visibilitychange", this._visibilityHandler);
      this._visibilityHandler = null;
    }
  }
  _startTimers() {
    if (!this._refreshTimer) this._refreshTimer = setInterval(() => this._refresh(), 5000);
    if (!this._tickTimer) this._tickTimer = setInterval(() => this._tickEndsIn(), 1000);
  }
  _stopTimers() {
    if (this._refreshTimer) { clearInterval(this._refreshTimer); this._refreshTimer = null; }
    if (this._tickTimer) { clearInterval(this._tickTimer); this._tickTimer = null; }
  }

  _init() {
    this._initialized = true;
    const style = el("style"); style.textContent = STYLES;
    this.appendChild(style);
    const lang = (this._hass && (this._hass.language || (this._hass.locale && this._hass.locale.language))) || "en";
    this._lang = lang.toLowerCase().startsWith("he") ? "he" : "en";
    this._app = el("div", { class: "app", dir: this._lang === "he" ? "rtl" : "ltr" });
    this.appendChild(this._app);
    this._modalRoot = el("div", { dir: this._lang === "he" ? "rtl" : "ltr" });
    this.appendChild(this._modalRoot);
    this._loadEntries().then(() => this._refresh()).then(() => this._subscribeHeaterState());
    this._startTimers();
  }

  async _loadEntries() {
    try {
      this._entries = await this._hass.callWS({ type: "dud_shemesh/list_entries" });
    } catch (e) {
      this._entries = [];
    }
    let saved = null;
    try { saved = localStorage.getItem("dud_shemesh_entry"); } catch (e) {}
    const ids = this._entries.map(e => e.entry_id);
    this._entryId = ids.includes(saved) ? saved : (ids[0] || null);
  }

  _withEntry(obj) {
    return this._entryId ? Object.assign({ entry_id: this._entryId }, obj) : obj;
  }

  _selectEntry(id) {
    this._entryId = id;
    try { localStorage.setItem("dud_shemesh_entry", id); } catch (e) {}
    this._state = null;
    this._lastHeaterState = undefined;
    this._refresh().then(() => this._subscribeHeaterState());
  }

  async _subscribeHeaterState() {
    if (this._heaterUnsub) { try { this._heaterUnsub(); } catch (e) {} this._heaterUnsub = null; }
    const heaterId = this._state && this._state.options && this._state.options.heater_entity;
    if (!heaterId || !this._hass || !this._hass.connection) return;
    try {
      this._heaterUnsub = await this._hass.connection.subscribeEvents(
        (ev) => {
          if (!ev || !ev.data) return;
          if (ev.data.entity_id !== heaterId) return;
          const newState = ev.data.new_state && ev.data.new_state.state;
          this._lastHeaterState = newState;
          this._refresh();
        },
        "state_changed"
      );
    } catch (e) {
      // Subscription is an optimisation; the 5 s poll keeps the panel current.
    }
  }

  _t(key, ...args) {
    const dict = I18N[this._lang || "en"] || I18N.en;
    const v = dict[key] != null ? dict[key] : I18N.en[key];
    if (typeof v === "function") return v(...args);
    return v != null ? v : key;
  }

  _locale() { return this._lang === "he" ? "he-IL" : undefined; }

  _fmtDur(minutes) {
    const m = Math.max(0, Math.round(minutes));
    return m >= 60 ? this._t("dur_hm", Math.floor(m / 60), m % 60) : this._t("dur_m", m);
  }

  _fmtTime(ts) {
    return new Date(ts * 1000).toLocaleTimeString(this._locale(), { hour: "2-digit", minute: "2-digit", hour12: false });
  }

  _fmtWhen(ts) {
    const today = localDayStart(this._serverNow());
    const day = localDayStart(ts);
    let d;
    if (day === today) d = this._t("today_word");
    else if (day === today + 86400 || Math.round((day - today) / 86400) === 1) d = this._t("tomorrow_word");
    else d = new Date(ts * 1000).toLocaleDateString(this._locale(), { weekday: "short" });
    return `${d} ${this._fmtTime(ts)}`;
  }

  _sourceLabel(src) {
    const v = this._t("src_" + src);
    return v === "src_" + src ? src : v;
  }

  _firstDaySunday() {
    const fw = this._hass && this._hass.locale && this._hass.locale.first_weekday;
    if (fw && fw !== "language") return fw === "sunday";
    return this._lang === "he";
  }

  // Display order as indexes into DAYS (Monday-first bits).
  _dayOrder() { return this._firstDaySunday() ? [6, 0, 1, 2, 3, 4, 5] : [0, 1, 2, 3, 4, 5, 6]; }

  async _refresh() {
    try {
      this._state = await this._hass.callWS(this._withEntry({ type: "dud_shemesh/get_state" }));
      if (this._state && typeof this._state.now === "number") {
        this._serverOffset = this._state.now - Math.floor(Date.now() / 1000);
      }
      if (this._dragging || this._pendingTargetTimer) return;
      const focused = document.activeElement;
      if (focused && focused.tagName === "INPUT" && this.contains(focused)) return;
      this._render();
    } catch (e) {
      if (this._entryId && e && e.code === "not_loaded") {
        // Remembered tank was removed; fall back to the first one.
        await this._loadEntries();
        if (this._entryId) return this._refresh();
      }
      this._renderError(e);
    }
  }

  _serverNow() {
    return Math.floor(Date.now() / 1000) + (this._serverOffset || 0);
  }

  _formatRemaining(seconds) {
    if (seconds <= 0) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins < 60) return `${mins}:${secs.toString().padStart(2, "0")}`;
    return this._fmtDur(mins);
  }

  _tickEndsIn() {
    if (!this._endsInValueEl || !this._endsInEndsAt) return;
    if (!this._endsInValueEl.isConnected) {
      this._endsInValueEl = null;
      this._endsInEndsAt = 0;
      return;
    }
    const remaining = Math.max(0, this._endsInEndsAt - this._serverNow());
    this._endsInValueEl.textContent = this._formatRemaining(remaining);
    if (remaining === 0 && this._endsRefreshedFor !== this._endsInEndsAt) {
      this._endsRefreshedFor = this._endsInEndsAt;
      setTimeout(() => this._refresh(), 200);
    }
  }

  _renderError(e) {
    this._app.innerHTML = "";
    this._app.appendChild(el("div", { class: "card" }, [
      el("h2", {}, this._t("brand")),
      el("div", { style: "color:var(--ds-danger)" }, this._t("failed_load") + (e.message || "unknown")),
    ]));
  }

  _toast(msg, kind = "") {
    const t = el("div", { class: "toast " + kind }, msg);
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2500);
  }

  async _callService(service, data) {
    try {
      await this._hass.callService("dud_shemesh", service, this._withEntry(data || {}));
      this._toast(this._t("done"), "ok");
      setTimeout(() => this._refresh(), 300);
      return true;
    } catch (e) {
      this._toast(e.message || String(e), "error");
      return false;
    }
  }

  async _saveOptions(patch) {
    try {
      await this._hass.callWS(this._withEntry(Object.assign({ type: "dud_shemesh/update_options" }, patch)));
      this._toast(this._t("saved"), "ok");
      setTimeout(() => this._refresh(), 300);
    } catch (e) {
      this._toast(e.message || String(e), "error");
    }
  }

  _render() {
    if (!this._state) return;
    const opts = this._state.options || {};
    const status = this._state.status || {};
    this._app.innerHTML = "";

    this._app.appendChild(el("div", { class: "header" }, [
      el("div", { class: "brand" }, [
        el("h1", {}, this._t("brand")),
        el("span", { class: "ver", dir: "ltr" }, `v${PANEL_VERSION}`),
      ]),
      el("div", { style: "display:flex;align-items:center;gap:6px;" }, [
        this._renderTankPicker(),
        el("button", { class: "icon-btn", onClick: () => this._openSettings(), title: this._t("settings"), "aria-label": this._t("settings") }, "⚙"),
      ]),
    ]));

    const tabs = el("div", { class: "nav-tabs", role: "tablist" });
    [["control", this._t("control")], ["reports", this._t("reports")]].forEach(([key, label]) => {
      tabs.appendChild(el("button", {
        class: "nav-tab" + (this._view === key ? " active" : ""),
        role: "tab", "aria-selected": this._view === key ? "true" : "false",
        onClick: () => { this._view = key; this._render(); },
      }, label));
    });
    this._app.appendChild(tabs);

    if (this._view === "reports") {
      this._app.appendChild(this._renderReports(this._state.history || []));
      return;
    }

    const vacUntil = parseInt(opts.vacation_until || 0, 10);
    if (vacUntil > this._state.now) {
      const days = Math.ceil((vacUntil - this._state.now) / 86400);
      this._app.appendChild(el("div", {
        class: "card",
        style: "background:rgba(33,150,243,0.08);border-color:rgba(33,150,243,0.3);",
      }, [
        el("div", { style: "display:flex;justify-content:space-between;align-items:center;gap:12px;" }, [
          el("strong", {}, this._t("vacation_active", days, opts.vacation_hold_temp || 30)),
          el("button", {
            class: "boost-btn",
            style: "background:var(--ds-cool);box-shadow:none;padding:8px 14px;",
            onClick: () => this._saveOptions({ vacation_until: 0 }),
          }, this._t("vacation_end")),
        ]),
      ]));
    }

    this._app.appendChild(this._renderGauge(status, opts));
    this._app.appendChild(this._renderBoost(status, opts));
    this._app.appendChild(this._renderModeToggle(opts.mode || "schedule"));
    this._app.appendChild(this._renderTimeline(this._state.history || [], status));
    this._app.appendChild(this._renderSchedules(this._state.schedules || []));
  }

  _renderTankPicker() {
    if (!this._entries || this._entries.length < 2) return null;
    const sel = el("select", { class: "tank-picker", "aria-label": this._t("tank") });
    this._entries.forEach(e => {
      const o = el("option", { value: e.entry_id }, e.title);
      if (e.entry_id === this._entryId) o.selected = true;
      sel.appendChild(o);
    });
    sel.addEventListener("change", () => this._selectEntry(sel.value));
    return sel;
  }

  _renderNextHeat(status) {
    const nxt = status.next_heat;
    if (status.active) return null;
    if (!nxt) {
      return el("div", { class: "next-heat" }, [
        el("span", { class: "ico" }, "🗓"),
        el("div", {}, [el("div", { class: "sub" }, this._t("next_heat")), el("div", {}, this._t("no_heat_planned"))]),
      ]);
    }
    const inSec = Math.max(0, nxt.at - this._serverNow());
    const title = nxt.ready_by
      ? this._t("hot_by", this._fmtWhen(nxt.ready_by))
      : `${nxt.label || this._sourceLabel(nxt.source)} · ${this._fmtWhen(nxt.at)}`;
    const sub = nxt.ready_by
      ? `${this._sourceLabel(nxt.source)} · ${this._t("starts", this._fmtTime(nxt.at))}`
      : `${this._sourceLabel(nxt.source)} · ${this._t("in_x", this._fmtDur(inSec / 60))}`;
    return el("div", { class: "next-heat" }, [
      el("span", { class: "ico" }, "🗓"),
      el("div", {}, [
        el("div", { class: "sub" }, this._t("next_heat")),
        el("div", { style: "font-weight:600;" }, title),
        el("div", { class: "sub" }, sub),
      ]),
    ]);
  }

  _renderGauge(status, opts) {
    const card = el("div", { class: "card gauge-card" });
    const cur = status.current_temp;
    const target = this._pendingTarget != null ? this._pendingTarget : (status.target_temp || opts.target_temp || 55);
    const tempUnit = this._state.temperature_unit || "°C";
    const isHeating = !!status.active;

    const minTemp = 20, maxTemp = 80;
    const clamp = v => Math.max(minTemp, Math.min(maxTemp, v));
    const clamped = cur != null ? clamp(cur) : minTemp;
    const pct = ((clamped - minTemp) / (maxTemp - minTemp));
    const targetPct = ((clamp(target) - minTemp) / (maxTemp - minTemp));

    const startAngle = -210, endAngle = 30;
    const angleSpan = endAngle - startAngle;
    const valueAngle = startAngle + angleSpan * pct;
    const targetAngle = startAngle + angleSpan * targetPct;

    const cx = 130, cy = 130, r = 105, sw = 18;
    const polar = (a, R) => [cx + R * Math.cos(a * Math.PI / 180), cy + R * Math.sin(a * Math.PI / 180)];
    const arcPath = (a1, a2, R) => {
      const [x1, y1] = polar(a1, R);
      const [x2, y2] = polar(a2, R);
      const large = (a2 - a1) > 180 ? 1 : 0;
      return `M ${x1} ${y1} A ${R} ${R} 0 ${large} 1 ${x2} ${y2}`;
    };

    const tempColor = isHeating ? "#ff5722"
      : cur == null ? "#9e9e9e"
      : cur < 35 ? "#2196f3"
      : cur < 45 ? "#4caf50"
      : cur < 60 ? "#ff9800"
      : "#e53935";

    const svg = svgEl("svg", { viewBox: "0 0 260 230", style: "width:100%;max-width:260px;height:auto;direction:ltr;", role: "img",
      "aria-label": `${cur != null ? Math.round(cur) : "—"}${tempUnit}, ${this._t("target_val", target, tempUnit)}` }, [
      svgEl("path", { d: arcPath(startAngle, endAngle, r), fill: "none", stroke: "rgba(0,0,0,0.08)", "stroke-width": sw, "stroke-linecap": "round" }),
      svgEl("path", { d: arcPath(startAngle, valueAngle, r), fill: "none", stroke: tempColor, "stroke-width": sw, "stroke-linecap": "round", class: isHeating ? "gauge-arc-active" : "" }),
      svgEl("circle", {
        cx: polar(targetAngle, r)[0], cy: polar(targetAngle, r)[1], r: 9,
        fill: "var(--ds-text)", stroke: "var(--ds-card)", "stroke-width": "3",
        "data-drag": "target", style: "cursor:grab;",
      }),
      svgEl("text", { x: cx, y: cy - 4, "text-anchor": "middle", "font-size": "48", "font-weight": "700", fill: "var(--ds-text)", "font-family": "inherit" },
        document.createTextNode(cur != null ? `${Math.round(cur)}` : "—")),
      svgEl("text", { x: cx, y: cy + 24, "text-anchor": "middle", "font-size": "16", fill: "var(--ds-muted)", "font-family": "inherit" },
        document.createTextNode(tempUnit)),
    ]);

    const statusKey = (status.status || "waiting").toLowerCase();
    const badgeText = isHeating
      ? `${this._t("st_heating")} · ${this._sourceLabel(status.active.source)}`
      : this._t("st_" + statusKey);
    const targetVal = el("span", { class: "tval" }, this._t("target_val", target, tempUnit));
    const setTarget = (v) => {
      const nv = clamp(v);
      this._pendingTarget = nv;
      targetVal.textContent = this._t("target_val", nv, tempUnit);
      const dot = svg.querySelector('circle[data-drag="target"]');
      const [nx, ny] = polar(startAngle + angleSpan * ((nv - minTemp) / (maxTemp - minTemp)), r);
      if (dot) { dot.setAttribute("cx", nx); dot.setAttribute("cy", ny); }
    };
    const commitSoon = () => {
      clearTimeout(this._pendingTargetTimer);
      this._pendingTargetTimer = setTimeout(() => {
        this._pendingTargetTimer = null;
        const v = this._pendingTarget;
        this._pendingTarget = null;
        if (v != null && v !== (status.target_temp || opts.target_temp)) this._saveOptions({ target_temp: v });
      }, 700);
    };
    const gaugeCol = el("div", { class: "gauge-col" }, [
      el("div", { class: "gauge-wrap" }, svg),
      el("span", { class: "status-badge " + statusKey }, badgeText),
      el("div", { class: "target-row" }, [
        el("button", { class: "round-btn", "aria-label": "−", onClick: () => { setTarget(this._pendingTarget != null ? this._pendingTarget - 1 : target - 1); commitSoon(); } }, "−"),
        targetVal,
        el("button", { class: "round-btn", "aria-label": "+", onClick: () => { setTarget(this._pendingTarget != null ? this._pendingTarget + 1 : target + 1); commitSoon(); } }, "+"),
      ]),
    ]);

    // Drag target marker
    const handleDrag = (clientX, clientY) => {
      const rect = svg.getBoundingClientRect();
      const px = ((clientX - rect.left) / rect.width) * 260;
      const py = ((clientY - rect.top) / rect.height) * 230;
      const dx = px - cx, dy = py - cy;
      let a = Math.atan2(dy, dx) * 180 / Math.PI;
      // Map into [startAngle, startAngle + 360); anything past endAngle is the
      // gap under the gauge, which snaps to whichever end is closer.
      while (a < startAngle) a += 360;
      while (a >= startAngle + 360) a -= 360;
      let normalized = a;
      if (a > endAngle) normalized = (a - endAngle) <= (startAngle + 360 - a) ? endAngle : startAngle;
      setTarget(Math.round(minTemp + ((normalized - startAngle) / angleSpan) * (maxTemp - minTemp)));
    };
    this._dragging = false;
    svg.addEventListener("pointerdown", (ev) => {
      if (ev.target.getAttribute("data-drag") !== "target") return;
      this._dragging = true;
      ev.target.setPointerCapture(ev.pointerId);
      ev.preventDefault();
    });
    svg.addEventListener("pointermove", (ev) => {
      if (!this._dragging) return;
      handleDrag(ev.clientX, ev.clientY);
    });
    const endDrag = (ev, commit) => {
      if (!this._dragging) return;
      this._dragging = false;
      try { ev.target.releasePointerCapture(ev.pointerId); } catch {}
      if (commit) commitSoon();
      else { this._pendingTarget = null; this._render(); }
    };
    svg.addEventListener("pointerup", (ev) => endDrag(ev, true));
    svg.addEventListener("pointercancel", (ev) => endDrag(ev, false));

    const side = el("div", { class: "side" });
    const active = status.active;
    if (active) {
      const remaining = Math.max(0, active.ends_at - this._serverNow());
      const valueEl = el("div", { class: "value", dir: "ltr" }, this._formatRemaining(remaining));
      this._endsInValueEl = valueEl;
      this._endsInEndsAt = active.ends_at;
      side.appendChild(el("div", { class: "side-item" }, [el("div", { class: "label" }, this._t("ends_in")), valueEl]));
    } else if (status.estimated_minutes_to_target != null && status.estimated_minutes_to_target > 0) {
      side.appendChild(el("div", { class: "side-item" }, [
        el("div", { class: "label" }, this._t("to_target")),
        el("div", { class: "value" }, this._t("about_min", status.estimated_minutes_to_target)),
      ]));
    } else {
      side.appendChild(el("div", { class: "side-item" }, [
        el("div", { class: "label" }, this._t("status_label")),
        el("div", { class: "value" }, this._t("st_" + statusKey)),
      ]));
    }
    if (status.showers_available != null) {
      side.appendChild(el("div", { class: "side-item" }, [
        el("div", { class: "label" }, this._t("showers")),
        el("div", { class: "value" }, "🚿 " + this._t("showers_val", status.showers_available)),
      ]));
    }
    side.appendChild(el("div", { class: "side-item" }, [
      el("div", { class: "label" }, this._t("mode")),
      el("div", { class: "value" }, this._t(opts.mode || "schedule")),
    ]));

    if (opts.legionella_enabled && this._state.legionella_next_due) {
      const days = Math.ceil(Math.max(0, this._state.legionella_next_due - this._state.now) / 86400);
      const due = days <= 0;
      side.appendChild(el("div", { class: "legionella-pill" + (due ? " due" : "") },
        due ? this._t("legionella_due") : this._t("legionella_in", days)));
    }

    card.appendChild(gaugeCol);
    card.appendChild(side);
    const next = this._renderNextHeat(status);
    if (next) card.appendChild(next);
    return card;
  }

  _renderReports(history) {
    const opts = this._state.options || {};
    const wattage = parseInt(opts.heater_wattage_w || 2400, 10);
    const tariff = parseFloat(opts.tariff_ils_per_kwh ?? 0.62);
    const now = this._state.now;
    const day = 86400;
    const kwhFromMin = m => +(m * (wattage / 1000) / 60).toFixed(2);
    const ils = kwh => `₪${(kwh * tariff).toFixed(2)}`;

    const sumMinutes = (sinceTs) => Math.round(history
      .filter(h => h.ts >= sinceTs)
      .reduce((a, h) => a + runMinutes(h), 0));
    const avoidedMinutes = (sinceTs) => history
      .filter(h => h.ts >= sinceTs && SKIP_STATUSES.has(h.status))
      .reduce((a, h) => a + (parseInt(h.duration_min || 0, 10) || 0), 0);

    const d = new Date(now * 1000);
    const monthStart = new Date(d.getFullYear(), d.getMonth(), 1).getTime() / 1000;
    const savedMonthKwh = kwhFromMin(avoidedMinutes(monthStart));
    const savedAllKwh = kwhFromMin(avoidedMinutes(0));
    const skippedMonth = history.filter(h => h.ts >= monthStart && SKIP_STATUSES.has(h.status)).length;

    const root = el("div");
    root.appendChild(el("div", { class: "card savings" }, [
      el("div", { class: "section-title", style: "margin-top:0;" }, "☀️ " + this._t("saved_month")),
      el("div", { class: "big" }, ils(savedMonthKwh)),
      el("div", { class: "sub" }, this._t("saved_sub", savedMonthKwh)),
      el("div", { class: "row2" }, [
        el("span", {}, this._t("skipped_runs", skippedMonth)),
        el("span", {}, this._t("saved_total", ils(savedAllKwh))),
      ]),
    ]));

    // 30-day bars: electric vs avoided kWh per local day
    const today = localDayStart(now);
    const days = [];
    for (let i = 29; i >= 0; i--) days.push({ start: today - i * day, elec: 0, avoided: 0 });
    history.forEach(h => {
      const idx = days.findIndex(x => h.ts >= x.start && h.ts < x.start + day);
      if (idx < 0) return;
      days[idx].elec += kwhFromMin(runMinutes(h));
      if (SKIP_STATUSES.has(h.status)) days[idx].avoided += kwhFromMin(parseInt(h.duration_min || 0, 10) || 0);
    });
    const maxK = Math.max(0.5, ...days.map(x => Math.max(x.elec, x.avoided)));
    const W = 600, H = 130, pad = 18, bw = (W - pad * 2) / 30;
    const bars = [];
    days.forEach((x, i) => {
      const x0 = pad + i * bw;
      const hE = (x.elec / maxK) * (H - pad * 2), hA = (x.avoided / maxK) * (H - pad * 2);
      bars.push(svgEl("rect", { x: x0 + 1, y: H - pad - hE, width: bw / 2 - 1.5, height: hE, rx: 1.5, fill: "var(--ds-hot)" }));
      bars.push(svgEl("rect", { x: x0 + bw / 2, y: H - pad - hA, width: bw / 2 - 1.5, height: hA, rx: 1.5, fill: "var(--ds-solar)" }));
    });
    bars.push(svgEl("line", { x1: pad, x2: W - pad, y1: H - pad, y2: H - pad, stroke: "var(--ds-border)" }));
    bars.push(svgEl("text", { x: pad, y: 12, "font-size": "11", fill: "var(--ds-muted)" }, document.createTextNode(`${maxK.toFixed(1)} kWh`)));
    root.appendChild(el("div", { class: "card" }, [
      el("div", { class: "section-title", style: "margin-top:0;" }, this._t("last30_chart")),
      svgEl("svg", { viewBox: `0 0 ${W} ${H}`, style: "width:100%;height:auto;direction:ltr;" }, bars),
      el("div", { class: "legend" }, [
        el("span", {}, [el("i", { style: "background:var(--ds-hot)" }), this._t("lg_electric")]),
        el("span", {}, [el("i", { style: "background:var(--ds-solar)" }), this._t("lg_avoided")]),
      ]),
    ]));

    const minToday = sumMinutes(today);
    const min7 = sumMinutes(now - 7 * day);
    const min30 = sumMinutes(now - 30 * day);
    const tiles = (mins) => el("div", { class: "report-grid" }, [
      el("div", { class: "report-tile" }, [el("div", { class: "v" }, this._fmtDur(mins)), el("div", { class: "l" }, this._t("on_time"))]),
      el("div", { class: "report-tile" }, [el("div", { class: "v", dir: "ltr" }, `${kwhFromMin(mins)} kWh`), el("div", { class: "l" }, this._t("energy"))]),
      el("div", { class: "report-tile" }, [el("div", { class: "v" }, ils(kwhFromMin(mins))), el("div", { class: "l" }, this._t("cost"))]),
    ]);
    root.appendChild(el("div", { class: "card" }, [
      el("div", { class: "section-title", style: "margin-top:0;" }, this._t("today")), tiles(minToday),
      el("div", { class: "section-title" }, this._t("last7")), tiles(min7),
      el("div", { class: "section-title" }, this._t("last30")), tiles(min30),
      el("p", { class: "tariff-link" }, this._t("tariff_note", wattage, tariff)),
    ]));

    const rates = history
      .filter(h => h.status === "completed" || h.status === "target_reached")
      .filter(h => typeof h.starting_temp === "number" && typeof h.ending_temp === "number" && runMinutes(h) > 0)
      .slice(0, 20)
      .map(h => Math.max(0, (h.ending_temp - h.starting_temp) / Math.max(1, runMinutes(h))));
    if (rates.length) {
      const avgRate = +(rates.reduce((a, b) => a + b, 0) / rates.length).toFixed(3);
      root.appendChild(el("div", { class: "card" }, [
        el("div", { class: "section-title", style: "margin-top:0;" }, this._t("heater_health")),
        el("div", { class: "report-grid" }, [
          el("div", { class: "report-tile" }, [el("div", { class: "v", dir: "ltr" }, `${avgRate} °C/min`), el("div", { class: "l" }, this._t("avg_rate"))]),
          el("div", { class: "report-tile" }, [el("div", { class: "v" }, String(rates.length)), el("div", { class: "l" }, this._t("cycles"))]),
        ]),
        el("p", { class: "tariff-link" }, this._t("descale_hint")),
      ]));
    }

    const samples = (this._state.temp_samples || []).slice(-200);
    if (samples.length >= 2) {
      const w = 600, h = 140, p = 24;
      const xs = samples.map(s => s[0]);
      const ys = samples.map(s => s[1]);
      const minX = Math.min(...xs), maxX = Math.max(...xs);
      const minY = Math.min(...ys) - 1, maxY = Math.max(...ys) + 1;
      const sx = t => p + ((t - minX) / Math.max(1, maxX - minX)) * (w - p * 2);
      const sy = v => h - p - ((v - minY) / Math.max(0.1, maxY - minY)) * (h - p * 2);
      const dPath = samples.map(([t, v], i) => `${i ? "L" : "M"} ${sx(t).toFixed(1)} ${sy(v).toFixed(1)}`).join(" ");
      root.appendChild(el("div", { class: "card" }, [
        el("div", { class: "section-title", style: "margin-top:0;" }, this._t("temp_chart")),
        svgEl("svg", { viewBox: `0 0 ${w} ${h}`, style: "width:100%;height:140px;direction:ltr;" }, [
          svgEl("path", { d: dPath, fill: "none", stroke: "var(--ds-primary)", "stroke-width": "2", "stroke-linejoin": "round" }),
          svgEl("text", { x: p, y: 14, "font-size": "11", fill: "var(--ds-muted)" },
            document.createTextNode(`${minY.toFixed(0)}–${maxY.toFixed(0)}°C`)),
        ]),
      ]));
    }

    const counts = {};
    history.forEach(hh => { counts[hh.status] = (counts[hh.status] || 0) + 1; });
    const safety = (counts.safety_overtemp || 0);
    const grid = el("div", { class: "report-grid" });
    [
      ["skipped_warm", "oc_skipped_warm"], ["skipped_solar", "oc_skipped_solar"], ["skipped_weather", "oc_skipped_weather"],
      ["skipped_user", "oc_skipped_user"], ["completed", "oc_completed"], ["target_reached", "oc_target_reached"],
      ["cancelled", "oc_cancelled"],
    ].forEach(([k, label]) => grid.appendChild(el("div", { class: "report-tile" }, [
      el("div", { class: "v" }, String(counts[k] || 0)), el("div", { class: "l" }, this._t(label)),
    ])));
    grid.appendChild(el("div", { class: "report-tile" }, [el("div", { class: "v" }, String(safety)), el("div", { class: "l" }, this._t("oc_safety"))]));
    root.appendChild(el("div", { class: "card" }, [el("div", { class: "section-title", style: "margin-top:0;" }, this._t("outcomes")), grid]));
    return root;
  }

  _boostLabel(mins) {
    if (mins === 60) return this._t("boost_hour");
    if (mins > 60 && mins % 60 === 0) return this._t("boost_hours", mins / 60);
    return this._t("boost_min", mins);
  }

  _renderBoost(status, opts) {
    const card = el("div", { class: "card" });
    const row = el("div", { class: "boost-row" });
    const buttons = this._parseBoostButtons(opts);
    if (status.active) {
      row.appendChild(el("button", {
        class: "boost-btn cancel",
        onClick: () => this._callService("cancel_boost", {}),
      }, this._t("stop_heating")));
      buttons.forEach(mins => row.appendChild(el("button", {
        class: "boost-btn extend",
        onClick: () => this._callService("boost", { minutes: mins }),
      }, this._t("extend", this._boostLabel(mins)))));
    } else {
      buttons.forEach(mins => row.appendChild(el("button", {
        class: "boost-btn",
        onClick: () => this._callService("boost", { minutes: mins }),
      }, this._boostLabel(mins))));
    }
    card.appendChild(row);
    return card;
  }

  _parseBoostButtons(opts) {
    const raw = (opts && opts.boost_buttons) || "30,60,120";
    const arr = String(raw).split(",")
      .map(s => parseInt(s.trim(), 10))
      .filter(n => !isNaN(n) && n > 0 && n <= 720);
    return arr.length ? arr : [30, 60, 120];
  }

  _renderModeToggle(mode) {
    const card = el("div", { class: "card", style: "padding:8px;" });
    const wrap = el("div", { class: "mode-toggle", role: "radiogroup", "aria-label": this._t("mode") });
    ["auto", "schedule", "off"].forEach(key => {
      wrap.appendChild(el("button", {
        class: "mode-pill" + (mode === key ? " active" : ""),
        role: "radio", "aria-checked": mode === key ? "true" : "false",
        onClick: () => this._saveOptions({ mode: key }),
      }, this._t(key)));
    });
    card.appendChild(wrap);
    card.appendChild(el("div", { class: "mode-hint" }, this._t("mode_hint_" + mode)));
    return card;
  }

  _renderTimeline(history, status) {
    const card = el("div", { class: "card" });
    card.appendChild(el("h3", { style: "margin:0;" }, this._t("today")));
    const segs = new Array(48).fill("idle"); // 30-min slots × 24h
    const now = new Date(this._state.now * 1000);
    const dayStart = localDayStart(this._state.now);
    const paint = (start, end, tone) => {
      const s0 = Math.max(0, Math.floor((start - dayStart) / 1800));
      const s1 = Math.min(48, Math.ceil((end - dayStart) / 1800));
      for (let i = s0; i < s1; i++) segs[i] = tone;
    };
    (status.upcoming || []).forEach(u => paint(u.at, u.at + (u.duration_min || 0) * 60, "planned"));
    // Close rows carry ts = end of run; paint [start, end].
    history.forEach(h => {
      const mins = runMinutes(h);
      if (mins <= 0 || h.ts < dayStart) return;
      const start = typeof h.started_at === "number" ? h.started_at : h.ts - mins * 60;
      paint(start, h.ts, h.source === "schedule" ? "scheduled" : "heating");
    });
    if (status.active) paint(status.active.started_at, status.active.ends_at, "heating");
    // The time axis always reads left to right, also in Hebrew.
    const tl = el("div", { class: "timeline", dir: "ltr" });
    segs.forEach(t => tl.appendChild(el("div", { class: "timeline-seg " + t })));
    const nowPct = ((now.getHours() * 60 + now.getMinutes()) / 1440) * 100;
    tl.appendChild(el("div", { class: "timeline-now", style: `left:${nowPct}%;` }));
    card.appendChild(tl);
    card.appendChild(el("div", { class: "timeline-labels", dir: "ltr" }, [
      el("span", {}, "00"), el("span", {}, "06"), el("span", {}, "12"), el("span", {}, "18"), el("span", {}, "24"),
    ]));
    card.appendChild(el("div", { class: "legend" }, [
      el("span", {}, [el("i", { style: "background:var(--ds-hot)" }), this._t("lg_heated")]),
      el("span", {}, [el("i", { style: "background:var(--ds-cool)" }), this._t("lg_scheduled")]),
      el("span", {}, [el("i", { style: "background:repeating-linear-gradient(45deg,rgba(33,150,243,.45) 0 3px,rgba(33,150,243,.15) 3px 6px)" }), this._t("lg_planned")]),
    ]));
    return card;
  }

  _daysLabel(mask) {
    const names = this._t("days_short");
    return this._dayOrder().filter(i => mask & DAY_BITS[i]).map(i => names[i]).join(" ");
  }

  _renderSchedules(schedules) {
    const card = el("div", { class: "card schedule-card" });
    card.appendChild(el("div", { style: "display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;" }, [
      el("h3", { style: "margin:0;" }, this._t("schedules")),
      el("button", { class: "btn primary small", onClick: () => this._openScheduleModal(null) }, this._t("add")),
    ]));
    if (!schedules.length) {
      card.appendChild(el("div", { class: "empty" }, this._t("no_schedules")));
      return card;
    }
    const nextMap = this._state.schedule_next || {};
    const nowTs = this._serverNow();
    schedules.forEach(s => {
      // First-strong isolates keep each segment's digits and units in order under RTL.
      const sub = [s.time_hhmm, this._daysLabel(s.days_mask), this._fmtDur(s.duration_min)]
        .concat(s.target_temp ? [`${this._t("target")} \u2066${s.target_temp}°\u2069`] : [])
        .map(part => `\u2068${part}\u2069`).join(" • ");
      const next = nextMap[s.id];
      const skipping = (s.skip_until || 0) > nowTs;
      let nextLine = null;
      if (s.enabled) {
        nextLine = el("div", { class: "next" + (skipping ? " skipped" : "") },
          next ? (skipping ? this._t("skipped_until", this._fmtWhen(next)) : this._t("next_run", this._fmtWhen(next))) : this._t("not_scheduled"));
      }
      const toggle = el("input", { type: "checkbox", "aria-label": this._t("enabled") });
      toggle.checked = !!s.enabled;
      toggle.addEventListener("change", () => this._callService("update_schedule", { schedule_id: s.id, enabled: toggle.checked }));
      const actions = [];
      if (s.enabled && (next || skipping)) {
        actions.push(el("button", {
          class: "btn small",
          onClick: () => this._callService("update_schedule", { schedule_id: s.id, skip_until: skipping ? 0 : next + 60 }),
        }, skipping ? this._t("undo_skip") : this._t("skip_once")));
      }
      actions.push(el("button", { class: "btn small", onClick: () => this._openScheduleModal(s) }, this._t("edit_btn")));
      actions.push(el("button", {
        class: "btn danger small", "aria-label": "delete",
        onClick: () => {
          if (!confirm(this._t("delete_confirm"))) return;
          this._callService("remove_schedule", { schedule_id: s.id });
        },
      }, "✕"));
      card.appendChild(el("div", { class: "row" + (s.enabled ? "" : " disabled") }, [
        el("label", { class: "switch" }, [toggle, el("span")]),
        el("div", {}, [
          el("div", { class: "name" }, s.name || this._t("sched_default_name", s.time_hhmm)),
          el("div", { class: "sub" }, sub),
          nextLine,
        ]),
        el("div", { class: "actions" }, actions),
      ]));
    });
    return card;
  }

  _openScheduleModal(existing) {
    let name = existing ? existing.name : "";
    let time = existing ? existing.time_hhmm : "06:00";
    let dur = existing ? existing.duration_min : 60;
    let mask = existing ? existing.days_mask : 127;
    let target = existing && existing.target_temp != null ? existing.target_temp : "";
    let enabled = existing ? !!existing.enabled : true;

    const nameInput = el("input", { type: "text", value: name, placeholder: this._t("optional") });
    nameInput.addEventListener("input", () => { name = nameInput.value; });
    const timeInput = el("input", { type: "time", value: time, dir: "ltr" });
    timeInput.addEventListener("input", () => { time = timeInput.value; });
    const durInput = el("input", { type: "number", min: "1", max: "720", value: String(dur) });
    durInput.addEventListener("input", () => { dur = parseInt(durInput.value, 10) || 60; });
    const targetInput = el("input", { type: "number", min: "20", max: "80", placeholder: this._t("blank_off"), value: target });
    targetInput.addEventListener("input", () => { target = targetInput.value; });
    const enabledInput = el("input", { type: "checkbox" });
    enabledInput.checked = enabled;
    enabledInput.addEventListener("change", () => { enabled = enabledInput.checked; });

    const names = this._t("days_short");
    const days = el("div", { class: "days" });
    this._dayOrder().forEach(i => {
      const tog = el("button", { type: "button", class: "day-toggle" + ((mask & DAY_BITS[i]) ? " on" : ""),
        "aria-pressed": (mask & DAY_BITS[i]) ? "true" : "false" }, names[i]);
      tog.addEventListener("click", () => {
        mask ^= DAY_BITS[i];
        const on = !!(mask & DAY_BITS[i]);
        tog.classList.toggle("on", on);
        tog.setAttribute("aria-pressed", on ? "true" : "false");
      });
      days.appendChild(tog);
    });

    const fields = [
      el("label", { class: "field" }, [el("span", {}, this._t("name")), nameInput]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, this._t("time")), timeInput]),
        el("label", { class: "field" }, [el("span", {}, this._t("duration_min")), durInput]),
      ]),
      el("label", { class: "field" }, [el("span", {}, this._t("target_opt")), targetInput]),
      el("div", { class: "field" }, [el("span", {}, this._t("days")), days]),
      el("label", { class: "check" }, [enabledInput, this._t("enabled")]),
    ];

    this._showModal(existing ? this._t("edit_schedule") : this._t("add_schedule"), fields, async () => {
      if (!mask) { this._toast(this._t("pick_day"), "error"); return false; }
      const payload = { time, days: daysFromMask(mask), duration_minutes: dur, name, enabled };
      if (target !== "" && target != null) payload.target_temp = parseInt(target, 10);
      if (existing) {
        return await this._callService("update_schedule", Object.assign({ schedule_id: existing.id }, payload));
      }
      return await this._callService("add_schedule", payload);
    });
  }

  _openSettings() {
    const opts = this._state.options || {};
    const t = (k, ...a) => this._t(k, ...a);
    const num = (value, attrs = {}) => el("input", Object.assign({ type: "number", value: String(value) }, attrs));
    const field = (label, input, hint) => el("label", { class: "field" }, [el("span", {}, label), input, hint ? el("div", { class: "hint" }, hint) : null]);
    const check = (label, input) => el("label", { class: "check" }, [input, label]);
    const box = (checked) => { const c = el("input", { type: "checkbox" }); c.checked = !!checked; return c; };

    const target = num(opts.target_temp ?? 55, { min: "20", max: "80" });
    const wattage = num(opts.heater_wattage_w ?? 2400, { min: "500", max: "10000", step: "100" });
    const tariff = num(opts.tariff_ils_per_kwh ?? 0.62, { min: "0", max: "10", step: "0.01" });
    const tank = num(opts.tank_volume_l ?? 0, { min: "0", max: "1000", step: "10" });
    const boostBtns = el("input", { type: "text", value: String(opts.boost_buttons || "30,60,120"), placeholder: "30,60,120", dir: "ltr" });

    const comfort = el("input", { type: "text", value: String(opts.auto_comfort_windows || ""), placeholder: "06:30-08:00,19:00-21:00", dir: "ltr" });
    const preMargin = num(opts.auto_pre_heat_margin_min ?? 5, { min: "0", max: "60" });
    const weatherEnt = el("input", { type: "text", value: String(opts.weather_entity || ""), placeholder: "weather.forecast_home", dir: "ltr" });
    const weatherStates = el("input", { type: "text", value: String(opts.weather_skip_states || "sunny"), dir: "ltr" });
    const solarMin = num(opts.solar_track_minutes ?? 30, { min: "5", max: "180" });
    const solarThr = num(opts.solar_rise_threshold ?? 1.0, { min: "0.1", max: "10", step: "0.1" });
    const manualMax = num(opts.manual_on_max_min ?? 60, { min: "0", max: "720" });
    const maxRun = num(opts.max_run_min ?? 180, { min: "30", max: "720" });
    const maxTemp = num(opts.max_tank_temp ?? 75, { min: "50", max: "90" });
    const stale = num(opts.sensor_stale_min ?? 120, { min: "0", max: "1440" });
    const failEn = box(opts.fail_detection_enabled);
    const failMin = num(opts.fail_detection_minutes ?? 8, { min: "1", max: "60" });
    const failRise = num(opts.fail_detection_rise ?? 1.0, { min: "0.1", max: "10", step: "0.1" });
    const legEnabled = box(opts.legionella_enabled);
    const legTemp = num(opts.legionella_temp ?? 60, { min: "55", max: "80" });
    const legDays = num(opts.legionella_days ?? 7, { min: "1", max: "30" });

    const vacationUntilTs = parseInt(opts.vacation_until || 0, 10);
    const vacInput = el("input", { type: "datetime-local", dir: "ltr",
      value: vacationUntilTs ? toLocalInputValue(vacationUntilTs) : "" });
    const vacHold = num(opts.vacation_hold_temp ?? 30, { min: "20", max: "50" });

    const availableTargets = this._state.notify_services || [];
    const availableEvents = this._state.notify_events || [];
    const toSet = v => new Set(Array.isArray(v) ? v : (v ? String(v).split(",").map(s => s.trim()).filter(Boolean) : []));
    const currentTargets = toSet(opts.notify_targets);
    const currentEvents = toSet(opts.notify_events);
    const chip = (label, set, key) => {
      const cb = el("input", { type: "checkbox" });
      cb.checked = set.has(key);
      cb.addEventListener("change", () => { cb.checked ? set.add(key) : set.delete(key); });
      return el("label", { class: "chip" }, [cb, label]);
    };
    const targetsWrap = el("div", { class: "chips", dir: "ltr" });
    if (!availableTargets.length) targetsWrap.appendChild(el("div", { class: "empty" }, t("no_notify")));
    availableTargets.forEach(name => targetsWrap.appendChild(chip(name, currentTargets, name)));
    const eventsWrap = el("div", { class: "chips" });
    availableEvents.forEach(ev => eventsWrap.appendChild(chip(t("ev_" + ev), currentEvents, ev)));

    const advancedSection = el("div", { style: this._showAdvanced ? "" : "display:none;" }, [
      el("h4", {}, t("h_safety")),
      field(t("s_manual_max"), manualMax),
      el("div", { class: "field-row" }, [field(t("s_max_run"), maxRun), field(t("s_max_temp"), maxTemp)]),
      field(t("s_stale"), stale),
      el("h4", {}, t("h_auto")),
      field(t("s_windows"), comfort),
      field(t("s_margin"), preMargin),
      el("h4", {}, t("h_weather")),
      field(t("s_weather_ent"), weatherEnt),
      field(t("s_weather_states"), weatherStates, t("s_weather_hint")),
      el("h4", {}, t("h_solar")),
      el("div", { class: "field-row" }, [field(t("s_solar_min"), solarMin), field(t("s_solar_thr"), solarThr)]),
      el("h4", {}, t("h_fail")),
      check(t("enabled"), failEn),
      el("div", { class: "field-row" }, [field(t("s_check_after"), failMin), field(t("s_min_rise"), failRise)]),
      el("h4", {}, t("h_legionella")),
      check(t("enabled"), legEnabled),
      el("div", { class: "field-row" }, [field(t("s_cycle_temp"), legTemp), field(t("s_every_days"), legDays)]),
      el("h4", {}, t("h_vacation")),
      el("div", { class: "hint", style: "margin-bottom:8px;" }, t("vacation_hint")),
      field(t("s_vac_until"), vacInput),
      field(t("s_vac_hold"), vacHold),
      el("h4", {}, t("h_notify")),
      el("div", { class: "hint", style: "margin-bottom:8px;" }, t("notify_hint")),
      el("div", { class: "field" }, [el("span", {}, t("s_notify_services")), targetsWrap]),
      el("div", { class: "field" }, [el("span", {}, t("s_notify_when")), eventsWrap]),
    ]);

    const advLabel = el("strong", {}, this._showAdvanced ? t("adv_shown") : t("adv_hidden"));
    const advBtn = el("button", { type: "button" }, this._showAdvanced ? t("hide") : t("show"));
    advBtn.addEventListener("click", () => {
      this._showAdvanced = !this._showAdvanced;
      advancedSection.style.display = this._showAdvanced ? "" : "none";
      advLabel.textContent = this._showAdvanced ? t("adv_shown") : t("adv_hidden");
      advBtn.textContent = this._showAdvanced ? t("hide") : t("show");
    });

    const fields = [
      field(t("s_target"), target),
      field(t("s_boost"), boostBtns),
      el("div", { class: "field-row" }, [field(t("s_wattage"), wattage), field(t("s_tariff"), tariff)]),
      field(t("s_tank"), tank, t("s_tank_hint")),
      el("div", { class: "advanced-toggle" }, [advLabel, advBtn]),
      advancedSection,
    ];

    this._showModal(t("settings"), fields, async () => {
      await this._saveOptions({
        target_temp: numOr(target.value, 55, parseInt),
        heater_wattage_w: numOr(wattage.value, 2400, parseInt),
        tariff_ils_per_kwh: numOr(tariff.value, 0.62),
        tank_volume_l: numOr(tank.value, 0, parseInt),
        boost_buttons: boostBtns.value.trim() || "30,60,120",
        auto_comfort_windows: comfort.value.trim(),
        auto_pre_heat_margin_min: numOr(preMargin.value, 5, parseInt),
        weather_entity: weatherEnt.value.trim(),
        weather_skip_states: weatherStates.value.trim(),
        manual_on_max_min: numOr(manualMax.value, 60, parseInt),
        max_run_min: numOr(maxRun.value, 180, parseInt),
        max_tank_temp: numOr(maxTemp.value, 75, parseInt),
        sensor_stale_min: numOr(stale.value, 120, parseInt),
        fail_detection_enabled: failEn.checked,
        fail_detection_minutes: numOr(failMin.value, 8, parseInt),
        fail_detection_rise: numOr(failRise.value, 1.0),
        solar_track_minutes: numOr(solarMin.value, 30, parseInt),
        solar_rise_threshold: numOr(solarThr.value, 1.0),
        legionella_enabled: legEnabled.checked,
        legionella_temp: numOr(legTemp.value, 60, parseInt),
        legionella_days: numOr(legDays.value, 7, parseInt),
        vacation_until: vacInput.value ? Math.floor(new Date(vacInput.value).getTime() / 1000) : 0,
        vacation_hold_temp: numOr(vacHold.value, 30, parseInt),
        notify_targets: Array.from(currentTargets),
        notify_events: Array.from(currentEvents),
      });
      return true;
    });
  }

  _showModal(title, fields, onSave) {
    this._modalRoot.innerHTML = "";
    const modal = el("div", { class: "modal", role: "dialog", "aria-modal": "true", "aria-label": title }, [el("h3", {}, title)]);
    fields.forEach(f => modal.appendChild(f));
    const cancelBtn = el("button", { class: "btn", onClick: () => { this._modalRoot.innerHTML = ""; } }, this._t("cancel"));
    const saveBtn = el("button", { class: "btn primary", onClick: async () => {
      saveBtn.disabled = true;
      try {
        const ok = await onSave();
        if (ok) this._modalRoot.innerHTML = "";
      } finally { saveBtn.disabled = false; }
    } }, this._t("save"));
    modal.appendChild(el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]));
    const overlay = el("div", { class: "modal-overlay" }, modal);
    overlay.addEventListener("click", e => { if (e.target === overlay) this._modalRoot.innerHTML = ""; });
    this._modalRoot.appendChild(overlay);
  }
}

if (!customElements.get("dud-shemesh-panel")) {
  customElements.define("dud-shemesh-panel", DudPanel);
}
