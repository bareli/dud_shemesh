const PANEL_VERSION = "0.4.10";
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
.header h1 { margin: 0; font-size: 24px; font-weight: 500; }
.icon-btn {
  background: transparent; border: none; cursor: pointer;
  padding: 8px; border-radius: 50%; color: var(--ds-muted);
  font-size: 20px;
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
  grid-template-columns: 1fr 160px;
  gap: 12px;
  align-items: center;
}
@media (max-width: 600px) {
  .gauge-card { grid-template-columns: 1fr; }
  .side { order: 2; flex-direction: row !important; justify-content: space-around !important; }
}
.gauge-wrap { position: relative; display: flex; justify-content: center; }
.side {
  display: flex; flex-direction: column; gap: 14px;
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
.boost-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 10px;
  margin-bottom: 14px;
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
.boost-btn.cancel { background: var(--ds-danger); box-shadow: 0 4px 12px rgba(229,57,53,0.25); }
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
}
.mode-pill.active {
  background: var(--ds-card);
  color: var(--ds-text);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
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
.timeline-seg.solar { background: #ffd54f; }
.timeline-seg.scheduled { background: var(--ds-cool); }
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
.schedule-card h3, .settings-card h3 { margin: 0 0 12px; font-size: 16px; }
.row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid var(--ds-border);
  border-radius: 10px;
  margin-bottom: 8px;
  background: var(--ds-bg);
}
.row .name { font-weight: 500; }
.row .sub { font-size: 12px; color: var(--ds-muted); }
.row .actions { display: flex; gap: 6px; }
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
}
.nav-tab.active {
  background: var(--ds-card); color: var(--ds-text);
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.legionella-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 999px;
  background: rgba(76,175,80,0.1); color: #2e7d32;
  font-size: 11px; margin-top: 4px;
}
.legionella-pill.due { background: rgba(229,57,53,0.15); color: var(--ds-danger); }
.report-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px; margin-bottom: 12px;
}
.report-tile {
  padding: 14px; border-radius: 12px;
  background: var(--ds-bg); border: 1px solid var(--ds-border);
  text-align: center;
}
.report-tile .v { font-size: 24px; font-weight: 700; color: var(--ds-text); }
.report-tile .l { font-size: 11px; color: var(--ds-muted); text-transform: uppercase; letter-spacing: 0.4px; margin-top: 4px; }
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
.field span { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; color: var(--ds-muted); }
.field input, .field select {
  width: 100%; padding: 8px 10px;
  border: 1px solid var(--ds-border); border-radius: 8px;
  background: var(--ds-card); color: var(--ds-text); font: inherit;
}
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: var(--ds-card); border-radius: 16px; padding: 20px;
  max-width: 460px; width: calc(100% - 32px); max-height: 85vh; overflow-y: auto;
}
.modal h3 { margin: 0 0 14px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }
.days { display: flex; gap: 4px; flex-wrap: wrap; }
.day-toggle {
  padding: 6px 10px; border: 1px solid var(--ds-border);
  border-radius: 6px; cursor: pointer; user-select: none; font-size: 12px;
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
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 8px;
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
    if (c == null) return;
    n.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
  });
  return n;
}

const I18N = {
  en: {
    control: "Control", reports: "Reports",
    target: "Target", mode: "Mode",
    auto: "Auto", schedule: "Schedule", off: "Off",
    today: "Today", schedules: "Schedules", add: "+ Add",
    no_schedules: "No schedules. Tap + Add to create one.",
    stop_heating: "STOP HEATING",
    legionella_in: (d) => `🦠 ${d}d to anti-Legionella`,
    legionella_due: "🦠 Legionella due",
    vacation_active: (d, t) => `🏖 Vacation mode — ${d}d left, holding ${t}°C`,
    vacation_end: "End",
    ends_in: "Ends in", to_target: "To target", status_label: "Status",
    edit_btn: "Edit", on_btn: "On", off_btn: "Off",
    delete_confirm: "Delete schedule?",
  },
  he: {
    control: "בקרה", reports: "דוחות",
    target: "יעד", mode: "מצב",
    auto: "אוטומטי", schedule: "לוח זמנים", off: "כבוי",
    today: "היום", schedules: "לוחות זמנים", add: "+ הוסף",
    no_schedules: "אין לוחות זמנים. לחצו + הוסף ליצירה.",
    stop_heating: "הפסק חימום",
    legionella_in: (d) => `🦠 ${d} ימים עד טיפול ליגיונלה`,
    legionella_due: "🦠 חיטוי ליגיונלה נדרש",
    vacation_active: (d, t) => `🏖 חופשה — ${d} ימים, שמירה על ${t}°C`,
    vacation_end: "סיים",
    ends_in: "מסתיים בעוד", to_target: "ליעד", status_label: "מצב",
    edit_btn: "עריכה", on_btn: "הפעל", off_btn: "כבה",
    delete_confirm: "למחוק לוח זמנים?",
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

const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const DAY_BITS = [1, 2, 4, 8, 16, 32, 64];

function maskFromDays(days) {
  let mask = 0;
  for (const d of days) {
    const i = DAYS.indexOf(d);
    if (i >= 0) mask |= DAY_BITS[i];
  }
  return mask;
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
    this._modalRoot = el("div");
    this.appendChild(this._modalRoot);
    this._refresh().then(() => this._subscribeHeaterState());
    this._startTimers();
  }

  async _subscribeHeaterState() {
    if (this._heaterUnsub) { try { this._heaterUnsub(); } catch (e) {} this._heaterUnsub = null; }
    const heaterId = this._state && this._state.options && this._state.options.heater_entity;
    if (!heaterId || !this._hass || !this._hass.connection) return;
    try {
      this._heaterUnsub = await this._hass.connection.subscribeEvents(
        (ev) => {
          if (!ev || !ev.data || ev.data.entity_id !== heaterId) return;
          const newState = ev.data.new_state && ev.data.new_state.state;
          this._lastHeaterState = newState;
          this._refresh();
        },
        "state_changed"
      );
    } catch (e) {
      console.warn("[dud_shemesh] heater state subscription failed", e);
    }
  }

  _t(key, ...args) {
    const dict = I18N[this._lang || "en"] || I18N.en;
    const v = dict[key];
    if (typeof v === "function") return v(...args);
    if (v != null) return v;
    return I18N.en[key] || key;
  }

  async _refresh() {
    try {
      this._state = await this._hass.callWS({ type: "dud_shemesh/get_state" });
      if (this._state && typeof this._state.now === "number") {
        this._serverOffset = this._state.now - Math.floor(Date.now() / 1000);
      }
      const focused = document.activeElement;
      if (focused && focused.tagName === "INPUT" && this.contains(focused)) return;
      this._render();
    } catch (e) {
      this._renderError(e);
    }
  }

  _serverNow() {
    return Math.floor(Date.now() / 1000) + (this._serverOffset || 0);
  }

  _formatRemaining(seconds) {
    if (seconds <= 0) return "0 min";
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins < 60) return `${mins}:${secs.toString().padStart(2, "0")}`;
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return `${h}h ${m.toString().padStart(2, "0")}m`;
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
    if (remaining === 0) {
      setTimeout(() => this._refresh(), 200);
    }
  }

  _renderError(e) {
    this._app.innerHTML = "";
    this._app.appendChild(el("div", { class: "card" }, [
      el("h2", {}, "Dud Shemesh"),
      el("div", { style: "color:var(--ds-danger)" }, "Failed to load: " + (e.message || "unknown")),
    ]));
  }

  _toast(msg, kind = "") {
    const t = el("div", { class: "toast " + kind }, msg);
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2500);
  }

  async _callService(service, data) {
    try {
      await this._hass.callService("dud_shemesh", service, data || {});
      this._toast("Done", "ok");
      setTimeout(() => this._refresh(), 300);
      return true;
    } catch (e) {
      this._toast(e.message || String(e), "error");
      return false;
    }
  }

  async _saveOptions(patch) {
    try {
      await this._hass.callWS(Object.assign({ type: "dud_shemesh/update_options" }, patch));
      this._toast("Saved", "ok");
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
      el("h1", {}, "Dud Shemesh"),
      el("span", { style: "opacity:.55;font-size:11px;margin-left:8px;" }, `v${PANEL_VERSION}`),
      el("button", { class: "icon-btn", onClick: () => this._openSettings(), title: "Settings" }, "⚙"),
    ]));

    const tabs = el("div", { class: "nav-tabs" });
    [["control", this._t("control")], ["reports", this._t("reports")]].forEach(([key, label]) => {
      const t = el("div", {
        class: "nav-tab" + (this._view === key ? " active" : ""),
        onClick: () => { this._view = key; this._render(); },
      }, label);
      tabs.appendChild(t);
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
        el("div", { style: "display:flex;justify-content:space-between;align-items:center;" }, [
          el("strong", {}, `🏖 Vacation mode — ${days}d left, holding ${opts.vacation_hold_temp || 30}°C`),
          el("button", {
            class: "boost-btn",
            style: "background:var(--ds-cool);box-shadow:none;padding:8px 14px;",
            onClick: () => this._saveOptions({ vacation_until: 0 }),
          }, "End"),
        ]),
      ]));
    }

    this._app.appendChild(this._renderGauge(status, opts));
    this._app.appendChild(this._renderBoost(status, opts));
    this._app.appendChild(this._renderModeToggle(opts.mode || "schedule"));
    this._app.appendChild(this._renderTimeline(this._state.history || [], status));
    this._app.appendChild(this._renderSchedules(this._state.schedules || []));
  }

  _renderGauge(status, opts) {
    const card = el("div", { class: "card gauge-card" });
    const cur = status.current_temp;
    const target = status.target_temp || opts.target_temp || 55;
    const tempUnit = this._state.temperature_unit || "°C";

    const minTemp = 20, maxTemp = 80;
    const clamped = cur != null ? Math.max(minTemp, Math.min(maxTemp, cur)) : minTemp;
    const pct = ((clamped - minTemp) / (maxTemp - minTemp));
    const targetPct = ((target - minTemp) / (maxTemp - minTemp));

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

    const tempColor = cur == null ? "#9e9e9e"
      : cur < 35 ? "#2196f3"
      : cur < 45 ? "#4caf50"
      : cur < 60 ? "#ff9800"
      : "#e53935";

    const isHeating = !!status.active;
    const svg = svgEl("svg", { viewBox: "0 0 260 260", style: "width:100%;max-width:260px;height:auto;" }, [
      svgEl("path", { d: arcPath(startAngle, endAngle, r), fill: "none", stroke: "rgba(0,0,0,0.08)", "stroke-width": sw, "stroke-linecap": "round" }),
      svgEl("path", { d: arcPath(startAngle, valueAngle, r), fill: "none", stroke: tempColor, "stroke-width": sw, "stroke-linecap": "round", class: isHeating ? "gauge-arc-active" : "" }),
      svgEl("circle", {
        cx: polar(targetAngle, r)[0], cy: polar(targetAngle, r)[1], r: 8,
        fill: "var(--ds-text)", stroke: "var(--ds-card)", "stroke-width": "2",
        "data-drag": "target", style: "cursor:grab;",
      }),
      svgEl("text", { x: cx, y: cy - 8, "text-anchor": "middle", "font-size": "44", "font-weight": "700", fill: "var(--ds-text)", "font-family": "inherit" },
        document.createTextNode(cur != null ? `${Math.round(cur)}` : "—")),
      svgEl("text", { x: cx, y: cy + 22, "text-anchor": "middle", "font-size": "16", fill: "var(--ds-muted)", "font-family": "inherit" },
        document.createTextNode(tempUnit)),
      svgEl("text", { x: cx, y: cy + 50, "text-anchor": "middle", "font-size": "12", fill: "var(--ds-muted)", "font-family": "inherit" },
        document.createTextNode(`Target ${target}${tempUnit}`)),
    ]);

    const wrap = el("div", { class: "gauge-wrap" }, svg);

    // Drag target marker
    const handleDrag = (clientX, clientY) => {
      const rect = svg.getBoundingClientRect();
      const px = ((clientX - rect.left) / rect.width) * 260;
      const py = ((clientY - rect.top) / rect.height) * 260;
      const dx = px - cx, dy = py - cy;
      const ang = Math.atan2(dy, dx) * 180 / Math.PI;
      let normalized = ang;
      while (normalized < startAngle) normalized += 360;
      while (normalized > endAngle) normalized -= 360;
      if (normalized < startAngle) normalized = startAngle;
      if (normalized > endAngle) normalized = endAngle;
      const newPct = (normalized - startAngle) / angleSpan;
      const newTemp = Math.round(minTemp + newPct * (maxTemp - minTemp));
      this._pendingTarget = newTemp;
      const txt = svg.querySelector("text:nth-of-type(3)");
      if (txt) txt.textContent = `Target ${newTemp}${tempUnit}`;
      const dot = svg.querySelector('circle[data-drag="target"]');
      if (dot) {
        const [nx, ny] = polar(normalized, r);
        dot.setAttribute("cx", nx);
        dot.setAttribute("cy", ny);
      }
    };
    let dragging = false;
    svg.addEventListener("pointerdown", (ev) => {
      if (ev.target.getAttribute("data-drag") !== "target") return;
      dragging = true;
      ev.target.setPointerCapture(ev.pointerId);
      ev.preventDefault();
    });
    svg.addEventListener("pointermove", (ev) => {
      if (!dragging) return;
      handleDrag(ev.clientX, ev.clientY);
    });
    svg.addEventListener("pointerup", (ev) => {
      if (!dragging) return;
      dragging = false;
      try { ev.target.releasePointerCapture(ev.pointerId); } catch {}
      if (this._pendingTarget && this._pendingTarget !== target) {
        this._saveOptions({ target_temp: this._pendingTarget });
        this._pendingTarget = null;
      }
    });
    const status_label = (status.status || "waiting").toLowerCase();
    const STATUS_LABELS = { ready: "Ready", heating: "Heating", waiting: "Waiting", solar: "Solar", cold: "Cold" };
    wrap.appendChild(el("div", {
      style: "position:absolute;bottom:-10px;left:50%;transform:translateX(-50%);text-align:center;",
    }, [
      el("span", { class: "status-badge " + status_label }, STATUS_LABELS[status_label] || status_label),
    ]));

    const side = el("div", { class: "side" });
    const active = status.active;
    if (active) {
      const remaining = Math.max(0, active.ends_at - this._serverNow());
      const valueEl = el("div", { class: "value" }, this._formatRemaining(remaining));
      this._endsInValueEl = valueEl;
      this._endsInEndsAt = active.ends_at;
      side.appendChild(el("div", { class: "side-item" }, [
        el("div", { class: "label" }, "Heating ends in"),
        valueEl,
      ]));
    } else if (status.estimated_minutes_to_target != null && status.estimated_minutes_to_target > 0) {
      side.appendChild(el("div", { class: "side-item" }, [
        el("div", { class: "label" }, "To target"),
        el("div", { class: "value" }, `~${status.estimated_minutes_to_target} min`),
      ]));
    } else {
      side.appendChild(el("div", { class: "side-item" }, [
        el("div", { class: "label" }, "Status"),
        el("div", { class: "value" }, STATUS_LABELS[status_label] || status_label),
      ]));
    }
    side.appendChild(el("div", { class: "side-item" }, [
      el("div", { class: "label" }, "Mode"),
      el("div", { class: "value" }, (opts.mode || "schedule").toUpperCase()),
    ]));

    if (opts.legionella_enabled && this._state.legionella_next_due) {
      const days = Math.ceil(Math.max(0, this._state.legionella_next_due - this._state.now) / 86400);
      const due = days <= 0;
      side.appendChild(el("div", {
        class: "legionella-pill" + (due ? " due" : ""),
      }, due ? "🦠 Legionella due" : `🦠 ${days}d to anti-Legionella`));
    }

    card.appendChild(wrap);
    card.appendChild(side);
    return card;
  }

  _renderReports(history) {
    const opts = this._state.options || {};
    const wattage = parseInt(opts.heater_wattage_w || 2400, 10);
    const tariff = parseFloat(opts.tariff_ils_per_kwh || 0.62);
    const now = this._state.now;
    const day = 86400;

    const sumMinutes = (sinceTs) => history
      .filter(h => h.status === "completed" || h.status === "target_reached")
      .filter(h => h.ts >= sinceTs)
      .reduce((a, h) => a + (parseInt(h.duration_min || 0, 10)), 0);

    const min7 = sumMinutes(now - 7 * day);
    const min30 = sumMinutes(now - 30 * day);
    const minToday = sumMinutes(now - day);

    const kwhFromMin = m => +(m * (wattage / 1000) / 60).toFixed(2);
    const ilsFromMin = m => +(kwhFromMin(m) * tariff).toFixed(2);

    const statusCounts = {};
    history.forEach(h => {
      const k = h.status || "unknown";
      statusCounts[k] = (statusCounts[k] || 0) + 1;
    });

    // Heating-rate trend (°C/min averaged over last N completions where rise > 0)
    let avgRate = null;
    const rates = history
      .filter(h => h.status === "completed" || h.status === "target_reached")
      .filter(h => typeof h.starting_temp === "number" && typeof h.ending_temp === "number" && h.duration_min > 0)
      .slice(0, 20)
      .map(h => Math.max(0, (h.ending_temp - h.starting_temp) / Math.max(1, h.duration_min)));
    if (rates.length) {
      avgRate = +(rates.reduce((a, b) => a + b, 0) / rates.length).toFixed(3);
    }

    const root = el("div");
    root.appendChild(el("div", { class: "card" }, [
      el("div", { class: "section-title" }, "Today"),
      el("div", { class: "report-grid" }, [
        el("div", { class: "report-tile" }, [
          el("div", { class: "v" }, `${minToday}m`),
          el("div", { class: "l" }, "On time"),
        ]),
        el("div", { class: "report-tile" }, [
          el("div", { class: "v" }, `${kwhFromMin(minToday)} kWh`),
          el("div", { class: "l" }, "Energy"),
        ]),
        el("div", { class: "report-tile" }, [
          el("div", { class: "v" }, `₪${ilsFromMin(minToday)}`),
          el("div", { class: "l" }, "Cost"),
        ]),
      ]),
      el("div", { class: "section-title" }, "Last 7 days"),
      el("div", { class: "report-grid" }, [
        el("div", { class: "report-tile" }, [
          el("div", { class: "v" }, `${min7}m`),
          el("div", { class: "l" }, "On time"),
        ]),
        el("div", { class: "report-tile" }, [
          el("div", { class: "v" }, `${kwhFromMin(min7)} kWh`),
          el("div", { class: "l" }, "Energy"),
        ]),
        el("div", { class: "report-tile" }, [
          el("div", { class: "v" }, `₪${ilsFromMin(min7)}`),
          el("div", { class: "l" }, "Cost"),
        ]),
      ]),
      el("div", { class: "section-title" }, "Last 30 days"),
      el("div", { class: "report-grid" }, [
        el("div", { class: "report-tile" }, [
          el("div", { class: "v" }, `${min30}m`),
          el("div", { class: "l" }, "On time"),
        ]),
        el("div", { class: "report-tile" }, [
          el("div", { class: "v" }, `${kwhFromMin(min30)} kWh`),
          el("div", { class: "l" }, "Energy"),
        ]),
        el("div", { class: "report-tile" }, [
          el("div", { class: "v" }, `₪${ilsFromMin(min30)}`),
          el("div", { class: "l" }, "Cost"),
        ]),
      ]),
      el("p", { class: "tariff-link" },
        `Wattage ${wattage} W × on-time × ₪${tariff}/kWh. Adjust both in Settings.`),
    ]));

    if (avgRate != null) {
      root.appendChild(el("div", { class: "card" }, [
        el("div", { class: "section-title" }, "Heater health"),
        el("div", { class: "report-grid" }, [
          el("div", { class: "report-tile" }, [
            el("div", { class: "v" }, `${avgRate} °C/min`),
            el("div", { class: "l" }, "Avg heat rate (last 20)"),
          ]),
          el("div", { class: "report-tile" }, [
            el("div", { class: "v" }, String(rates.length)),
            el("div", { class: "l" }, "Cycles measured"),
          ]),
        ]),
        el("p", { class: "tariff-link" },
          "If this number drops over weeks, the element may be scaling. Schedule a descale."),
      ]));
    }

    const samples = (this._state.temp_samples || []).slice(-200);
    if (samples.length >= 2) {
      const w = 600, h = 140, pad = 24;
      const xs = samples.map(s => Array.isArray(s) ? s[0] : s.ts || s[0]);
      const ys = samples.map(s => Array.isArray(s) ? s[1] : s.temp || s[1]);
      const minX = Math.min(...xs), maxX = Math.max(...xs);
      const minY = Math.min(...ys) - 1, maxY = Math.max(...ys) + 1;
      const sx = t => pad + ((t - minX) / Math.max(1, maxX - minX)) * (w - pad * 2);
      const sy = v => h - pad - ((v - minY) / Math.max(0.1, maxY - minY)) * (h - pad * 2);
      let dPath = "";
      samples.forEach(([t, v], i) => {
        const cmd = i === 0 ? "M" : "L";
        dPath += `${cmd} ${sx(t).toFixed(1)} ${sy(v).toFixed(1)} `;
      });
      const graphCard = el("div", { class: "card" }, [el("div", { class: "section-title" }, "Tank temperature (last samples)")]);
      const svg = svgEl("svg", { viewBox: `0 0 ${w} ${h}`, style: "width:100%;height:140px;" }, [
        svgEl("path", { d: dPath, fill: "none", stroke: "var(--ds-primary)", "stroke-width": "2", "stroke-linejoin": "round" }),
        svgEl("text", { x: pad, y: 14, "font-size": "11", fill: "var(--ds-muted)" },
          document.createTextNode(`${minY.toFixed(0)}–${maxY.toFixed(0)}°C`)),
      ]);
      graphCard.appendChild(svg);
      root.appendChild(graphCard);
    }

    const skipsCard = el("div", { class: "card" }, [el("div", { class: "section-title" }, "Skip reasons (entire history)")]);
    const skipGrid = el("div", { class: "report-grid" });
    [
      ["skipped_warm", "Already warm"],
      ["skipped_solar", "Solar gaining"],
      ["skipped_weather", "Sunny"],
      ["completed", "Completed"],
      ["cancelled", "Cancelled"],
      ["target_reached", "Target reached"],
    ].forEach(([key, label]) => {
      skipGrid.appendChild(el("div", { class: "report-tile" }, [
        el("div", { class: "v" }, String(statusCounts[key] || 0)),
        el("div", { class: "l" }, label),
      ]));
    });
    skipsCard.appendChild(skipGrid);
    root.appendChild(skipsCard);

    return root;
  }

  _renderBoost(status, opts) {
    const card = el("div", { class: "card" });
    if (status.active) {
      const row = el("div", { class: "boost-row" });
      const stopBtn = el("button", {
        class: "boost-btn cancel",
        style: "grid-column: 1 / -1;",
        onClick: () => this._callService("cancel_boost", {}),
      }, "STOP HEATING");
      row.appendChild(stopBtn);
      // Allow extending while heating
      const buttons = this._parseBoostButtons(opts);
      buttons.forEach(mins => {
        row.appendChild(el("button", {
          class: "boost-btn",
          style: "background:rgba(255,122,0,0.15);color:var(--ds-primary);box-shadow:none;",
          onClick: () => this._callService("boost", { minutes: mins }),
        }, `+${mins}m`));
      });
      card.appendChild(row);
    } else {
      const row = el("div", { class: "boost-row" });
      const buttons = this._parseBoostButtons(opts);
      buttons.forEach(mins => {
        const label = mins >= 60 && mins % 60 === 0
          ? (mins === 60 ? "+1 hour" : `+${mins / 60} hours`)
          : `+${mins} min`;
        row.appendChild(el("button", {
          class: "boost-btn",
          onClick: () => this._callService("boost", { minutes: mins }),
        }, label));
      });
      card.appendChild(row);
    }
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
    const wrap = el("div", { class: "mode-toggle" });
    [["auto", this._t("auto")], ["schedule", this._t("schedule")], ["off", this._t("off")]].forEach(([key, label]) => {
      const pill = el("div", {
        class: "mode-pill" + (mode === key ? " active" : ""),
        onClick: () => this._saveOptions({ mode: key }),
      }, label);
      wrap.appendChild(pill);
    });
    card.appendChild(wrap);
    return card;
  }

  _renderTimeline(history, status) {
    const card = el("div", { class: "card" });
    card.appendChild(el("h3", {}, "Today"));
    const segs = new Array(48).fill("idle"); // 30-min slots × 24h
    const now = new Date(this._state.now * 1000);
    const dayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0).getTime() / 1000;
    history.forEach(h => {
      if (h.ts < dayStart) return;
      const slotStart = Math.max(0, Math.floor((h.ts - dayStart) / 1800));
      const dur = (h.duration_min || 0) / 30;
      const slotEnd = Math.min(48, Math.ceil(slotStart + dur));
      const tone = h.status === "completed" || h.status === "started" || h.status === "target_reached"
        ? (h.source === "schedule" ? "scheduled" : "heating")
        : "idle";
      for (let i = slotStart; i < slotEnd && i < 48; i++) segs[i] = tone;
    });
    if (status.active) {
      const startSlot = Math.floor((status.active.started_at - dayStart) / 1800);
      const endSlot = Math.min(48, Math.ceil((status.active.ends_at - dayStart) / 1800));
      for (let i = Math.max(0, startSlot); i < endSlot; i++) segs[i] = "heating";
    }
    const tl = el("div", { class: "timeline" });
    segs.forEach(t => tl.appendChild(el("div", { class: "timeline-seg " + t })));
    const nowSlotPct = ((now.getHours() * 60 + now.getMinutes()) / 1440) * 100;
    tl.appendChild(el("div", { class: "timeline-now", style: `left:${nowSlotPct}%;` }));
    card.appendChild(tl);
    card.appendChild(el("div", { class: "timeline-labels" }, [
      el("span", {}, "00"), el("span", {}, "06"), el("span", {}, "12"), el("span", {}, "18"), el("span", {}, "23"),
    ]));
    return card;
  }

  _renderSchedules(schedules) {
    const card = el("div", { class: "card schedule-card" });
    card.appendChild(el("div", { style: "display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;" }, [
      el("h3", { style: "margin:0;" }, "Schedules"),
      el("button", { class: "btn primary small", onClick: () => this._openScheduleModal(null) }, "+ Add"),
    ]));
    if (!schedules.length) {
      card.appendChild(el("div", { class: "empty" }, "No schedules. Tap + Add to create one."));
      return card;
    }
    schedules.forEach(s => {
      const dlabel = DAY_LABELS.filter((_, i) => s.days_mask & DAY_BITS[i]).join(",");
      const sub = `${s.time_hhmm} • ${dlabel} • ${s.duration_min}min` + (s.target_temp ? ` • →${s.target_temp}°` : "");
      card.appendChild(el("div", { class: "row" }, [
        el("div", {}, [
          el("div", { class: "name" }, (s.name || `Heat ${s.time_hhmm}`) + (s.enabled ? "" : " (off)")),
          el("div", { class: "sub" }, sub),
        ]),
        el("div", { class: "actions" }, [
          el("button", { class: "btn small", onClick: () => this._openScheduleModal(s) }, "Edit"),
          el("button", {
            class: "btn small",
            onClick: () => this._callService("update_schedule", { schedule_id: s.id, enabled: !s.enabled }),
          }, s.enabled ? "Off" : "On"),
          el("button", {
            class: "btn danger small",
            onClick: () => {
              if (!confirm("Delete schedule?")) return;
              this._callService("remove_schedule", { schedule_id: s.id });
            },
          }, "✕"),
        ]),
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

    const nameInput = el("input", { type: "text", value: name, placeholder: "Optional" });
    nameInput.addEventListener("input", () => { name = nameInput.value; });
    const timeInput = el("input", { type: "time", value: time });
    timeInput.addEventListener("input", () => { time = timeInput.value; });
    const durInput = el("input", { type: "number", min: "1", max: "720", value: String(dur) });
    durInput.addEventListener("input", () => { dur = parseInt(durInput.value, 10) || 60; });
    const targetInput = el("input", { type: "number", min: "20", max: "80", placeholder: "Off / blank", value: target });
    targetInput.addEventListener("input", () => { target = targetInput.value; });
    const enabledInput = el("input", { type: "checkbox" });
    enabledInput.checked = enabled;
    enabledInput.addEventListener("change", () => { enabled = enabledInput.checked; });

    const days = el("div", { class: "days" });
    DAY_LABELS.forEach((d, i) => {
      const tog = el("div", { class: "day-toggle" + ((mask & DAY_BITS[i]) ? " on" : "") }, d);
      tog.addEventListener("click", () => {
        mask ^= DAY_BITS[i];
        tog.classList.toggle("on", !!(mask & DAY_BITS[i]));
      });
      days.appendChild(tog);
    });

    const fields = [
      el("label", { class: "field" }, [el("span", {}, "Name"), nameInput]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, "Time"), timeInput]),
        el("label", { class: "field" }, [el("span", {}, "Duration (min)"), durInput]),
      ]),
      el("label", { class: "field" }, [el("span", {}, "Target temp (°C, optional)"), targetInput]),
      el("div", { class: "field" }, [el("span", {}, "Days"), days]),
      el("label", { class: "field" }, [el("span", {}, "Enabled"), enabledInput]),
    ];

    this._showModal(existing ? "Edit schedule" : "Add schedule", fields, async () => {
      if (!mask) { this._toast("Pick at least one day", "error"); return false; }
      const payload = {
        time, days: daysFromMask(mask), duration_minutes: dur, name, enabled,
      };
      if (target !== "" && target != null) payload.target_temp = parseInt(target, 10);
      if (existing) {
        return await this._callService("update_schedule", Object.assign({ schedule_id: existing.id }, payload));
      }
      return await this._callService("add_schedule", payload);
    });
  }

  _openSettings() {
    const opts = this._state.options || {};
    const target = el("input", { type: "number", min: "20", max: "80", value: String(opts.target_temp || 55) });
    const wattage = el("input", { type: "number", min: "500", max: "10000", step: "100", value: String(opts.heater_wattage_w || 2400) });
    const tariff = el("input", { type: "number", min: "0", max: "10", step: "0.01", value: String(opts.tariff_ils_per_kwh ?? 0.62) });
    const boostBtns = el("input", { type: "text", value: String(opts.boost_buttons || "30,60,120"), placeholder: "30,60,120" });

    // Advanced
    const comfort = el("input", { type: "text", value: String(opts.auto_comfort_windows || ""), placeholder: "06:30-08:00,19:00-21:00" });
    const preMargin = el("input", { type: "number", min: "0", max: "60", value: String(opts.auto_pre_heat_margin_min || 5) });
    const weatherEnt = el("input", { type: "text", value: String(opts.weather_entity || ""), placeholder: "weather.forecast_home" });
    const weatherStates = el("input", { type: "text", value: String(opts.weather_skip_states || "sunny,clear-night") });
    const failEn = el("input", { type: "checkbox" }); failEn.checked = !!opts.fail_detection_enabled;
    const failMin = el("input", { type: "number", min: "1", max: "60", value: String(opts.fail_detection_minutes || 8) });
    const failRise = el("input", { type: "number", min: "0.1", max: "10", step: "0.1", value: String(opts.fail_detection_rise || 1.0) });
    const solarMin = el("input", { type: "number", min: "5", max: "180", value: String(opts.solar_track_minutes || 30) });
    const solarThr = el("input", { type: "number", min: "0.1", max: "10", step: "0.1", value: String(opts.solar_rise_threshold || 1.0) });

    const legEnabled = el("input", { type: "checkbox" }); legEnabled.checked = !!opts.legionella_enabled;
    const legTemp = el("input", { type: "number", min: "55", max: "80", value: String(opts.legionella_temp || 60) });
    const legDays = el("input", { type: "number", min: "1", max: "30", value: String(opts.legionella_days || 7) });

    // Vacation
    let vacationUntilTs = parseInt(opts.vacation_until || 0, 10);
    const vacInput = el("input", { type: "datetime-local",
      value: vacationUntilTs ? new Date(vacationUntilTs * 1000).toISOString().slice(0, 16) : "" });
    const vacHold = el("input", { type: "number", min: "20", max: "50", value: String(opts.vacation_hold_temp || 30) });

    // Notifications
    const availableTargets = this._state.notify_services || [];
    const availableEvents = this._state.notify_events || [];
    const currentTargets = new Set(Array.isArray(opts.notify_targets) ? opts.notify_targets : (opts.notify_targets ? String(opts.notify_targets).split(",").map(s => s.trim()).filter(Boolean) : []));
    const currentEvents = new Set(Array.isArray(opts.notify_events) ? opts.notify_events : (opts.notify_events ? String(opts.notify_events).split(",").map(s => s.trim()).filter(Boolean) : []));

    const targetsWrap = el("div", { style: "display:flex;flex-wrap:wrap;gap:6px;max-height:140px;overflow:auto;padding:8px;border:1px solid var(--ds-border);border-radius:6px;background:var(--ds-bg);" });
    if (!availableTargets.length) {
      targetsWrap.appendChild(el("div", { class: "empty", style: "padding:4px;" }, "No notify.* services detected."));
    } else {
      availableTargets.forEach(name => {
        const lbl = el("label", { style: "display:flex;gap:6px;align-items:center;font-size:13px;padding:2px 6px;border:1px solid var(--ds-border);border-radius:4px;cursor:pointer;" });
        const cb = el("input", { type: "checkbox" });
        cb.checked = currentTargets.has(name);
        cb.addEventListener("change", () => { cb.checked ? currentTargets.add(name) : currentTargets.delete(name); });
        lbl.appendChild(cb);
        lbl.appendChild(document.createTextNode(name));
        targetsWrap.appendChild(lbl);
      });
    }
    const eventsWrap = el("div", { style: "display:flex;flex-wrap:wrap;gap:6px;" });
    const EVENT_LABELS = {
      heat_start: "Heat started", heat_end: "Heat ended", target_reached: "Target reached",
      heat_not_rising: "Heater fault", skipped_solar: "Skipped (solar)", skipped_weather: "Skipped (weather)",
      legionella_done: "Anti-Legionella done",
    };
    availableEvents.forEach(ev => {
      const lbl = el("label", { style: "display:flex;gap:6px;align-items:center;font-size:13px;padding:2px 6px;border:1px solid var(--ds-border);border-radius:4px;cursor:pointer;" });
      const cb = el("input", { type: "checkbox" });
      cb.checked = currentEvents.has(ev);
      cb.addEventListener("change", () => { cb.checked ? currentEvents.add(ev) : currentEvents.delete(ev); });
      lbl.appendChild(cb);
      lbl.appendChild(document.createTextNode(EVENT_LABELS[ev] || ev));
      eventsWrap.appendChild(lbl);
    });

    const advancedSection = el("div", { style: this._showAdvanced ? "" : "display:none;" }, [
      el("h4", { style: "margin:14px 0 6px;" }, "Auto mode"),
      el("label", { class: "field" }, [
        el("span", {}, "Comfort windows (HH:MM-HH:MM, comma separated)"),
        comfort,
      ]),
      el("label", { class: "field" }, [
        el("span", {}, "Pre-heat margin (min before window)"),
        preMargin,
      ]),
      el("h4", { style: "margin:14px 0 6px;" }, "Weather skip"),
      el("label", { class: "field" }, [el("span", {}, "Weather entity"), weatherEnt]),
      el("label", { class: "field" }, [el("span", {}, "Skip when state is (comma-separated)"), weatherStates]),
      el("h4", { style: "margin:14px 0 6px;" }, "Solar tracking"),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, "Track window (min)"), solarMin]),
        el("label", { class: "field" }, [el("span", {}, "Rise threshold (°C / 30min)"), solarThr]),
      ]),
      el("h4", { style: "margin:14px 0 6px;" }, "Fail detection"),
      el("label", { class: "field" }, [el("span", {}, "Enabled"), failEn]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, "Check after (min)"), failMin]),
        el("label", { class: "field" }, [el("span", {}, "Min rise (°C)"), failRise]),
      ]),
      el("h4", { style: "margin:14px 0 6px;" }, "Anti-Legionella"),
      el("label", { class: "field" }, [el("span", {}, "Enabled"), legEnabled]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, "Cycle temp (°C)"), legTemp]),
        el("label", { class: "field" }, [el("span", {}, "Every N days"), legDays]),
      ]),
      el("h4", { style: "margin:14px 0 6px;" }, "Vacation mode"),
      el("p", { class: "muted small", style: "margin:0 0 8px;font-size:12px;color:var(--ds-muted);" },
        "Until this date/time, all schedules and auto-runs are suspended. Tank is held at hold-temp to prevent mold."),
      el("label", { class: "field" }, [el("span", {}, "Active until (clear to disable)"), vacInput]),
      el("label", { class: "field" }, [el("span", {}, "Hold temperature (°C)"), vacHold]),
      el("h4", { style: "margin:14px 0 6px;" }, "Notifications"),
      el("p", { class: "muted small", style: "margin:0 0 8px;font-size:12px;color:var(--ds-muted);" },
        "Pick one or more notify services and tick which events should send a push."),
      el("label", { class: "field" }, [el("span", {}, "Notify services"), targetsWrap]),
      el("label", { class: "field" }, [el("span", {}, "Send when"), eventsWrap]),
    ]);

    const advToggle = el("div", { class: "advanced-toggle" }, [
      el("strong", {}, this._showAdvanced ? "Advanced (shown)" : "Advanced (hidden)"),
      el("button", {
        onClick: () => {
          this._showAdvanced = !this._showAdvanced;
          advancedSection.style.display = this._showAdvanced ? "" : "none";
          // refresh "shown/hidden" label
          advToggle.firstChild.textContent = this._showAdvanced ? "Advanced (shown)" : "Advanced (hidden)";
        },
      }, this._showAdvanced ? "Hide" : "Show"),
    ]);

    const fields = [
      el("label", { class: "field" }, [el("span", {}, "Target temperature (°C)"), target]),
      el("label", { class: "field" }, [el("span", {}, "Boost button durations (min, comma-separated)"), boostBtns]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, "Heater wattage (W)"), wattage]),
        el("label", { class: "field" }, [el("span", {}, "Tariff (₪/kWh)"), tariff]),
      ]),
      advToggle,
      advancedSection,
    ];

    this._showModal("Settings", fields, async () => {
      await this._saveOptions({
        target_temp: parseInt(target.value, 10) || 55,
        heater_wattage_w: parseInt(wattage.value, 10) || 2400,
        tariff_ils_per_kwh: parseFloat(tariff.value) || 0.62,
        boost_buttons: boostBtns.value.trim() || "30,60,120",
        auto_comfort_windows: comfort.value.trim(),
        auto_pre_heat_margin_min: parseInt(preMargin.value, 10) || 5,
        weather_entity: weatherEnt.value.trim(),
        weather_skip_states: weatherStates.value.trim(),
        fail_detection_enabled: failEn.checked,
        fail_detection_minutes: parseInt(failMin.value, 10) || 8,
        fail_detection_rise: parseFloat(failRise.value) || 1.0,
        solar_track_minutes: parseInt(solarMin.value, 10) || 30,
        solar_rise_threshold: parseFloat(solarThr.value) || 1.0,
        legionella_enabled: legEnabled.checked,
        legionella_temp: parseInt(legTemp.value, 10) || 60,
        legionella_days: parseInt(legDays.value, 10) || 7,
        vacation_until: vacInput.value ? Math.floor(new Date(vacInput.value).getTime() / 1000) : 0,
        vacation_hold_temp: parseInt(vacHold.value, 10) || 30,
        notify_targets: Array.from(currentTargets),
        notify_events: Array.from(currentEvents),
      });
      return true;
    });
  }

  _showModal(title, fields, onSave) {
    this._modalRoot.innerHTML = "";
    const modal = el("div", { class: "modal" }, [el("h3", {}, title)]);
    fields.forEach(f => modal.appendChild(f));
    const cancelBtn = el("button", { class: "btn", onClick: () => { this._modalRoot.innerHTML = ""; } }, "Cancel");
    const saveBtn = el("button", { class: "btn primary", onClick: async () => {
      saveBtn.disabled = true;
      try {
        const ok = await onSave();
        if (ok) this._modalRoot.innerHTML = "";
      } finally { saveBtn.disabled = false; }
    } }, "Save");
    modal.appendChild(el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]));
    const overlay = el("div", { class: "modal-overlay" }, modal);
    overlay.addEventListener("click", e => { if (e.target === overlay) this._modalRoot.innerHTML = ""; });
    this._modalRoot.appendChild(overlay);
  }
}

if (!customElements.get("dud-shemesh-panel")) {
  customElements.define("dud-shemesh-panel", DudPanel);
}
