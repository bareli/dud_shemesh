// Lovelace card — appliance-grade smart-dud control inside a single Lovelace card.
const STYLES = `
:host { display: block; }
.card {
  background: var(--ha-card-background, var(--card-background-color, #fff));
  border-radius: var(--ha-card-border-radius, 18px);
  border: 1px solid var(--ha-card-border-color, var(--divider-color, #e5e7eb));
  padding: 16px 16px 18px;
  color: var(--primary-text-color);
  font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
  box-shadow: var(--ha-card-box-shadow, 0 1px 3px rgba(0,0,0,0.06));
}
.title { font-size: 15px; font-weight: 600; margin: 0 0 4px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.title .status-badge {
  font-size: 10px; font-weight: 600;
  padding: 3px 10px; border-radius: 999px;
  letter-spacing: 0.5px; white-space: nowrap;
}
.status-badge.heating { background: rgba(255,152,0,0.15); color: #f57c00; animation: pulse 1.5s infinite; }
.status-badge.ready   { background: rgba(76,175,80,0.18); color: #2e7d32; }
.status-badge.solar   { background: rgba(255,213,79,0.30); color: #f57f17; }
.status-badge.cold    { background: rgba(33,150,243,0.18); color: #1565c0; }
.status-badge.waiting { background: var(--divider-color); color: var(--secondary-text-color); }
@keyframes pulse {
  0% { opacity: 1; } 50% { opacity: 0.55; } 100% { opacity: 1; }
}
.gauge-row {
  display: grid;
  grid-template-columns: 168px 1fr;
  gap: 14px;
  align-items: center;
  margin: 4px 0 8px;
}
@media (max-width: 420px) {
  .gauge-row { grid-template-columns: 1fr; }
  .side { flex-direction: row !important; flex-wrap: wrap; justify-content: space-around !important; }
}
.gauge-col { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.target-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--secondary-text-color); }
.round-btn {
  width: 28px; height: 28px; border-radius: 50%; line-height: 1;
  border: 1px solid var(--divider-color); background: var(--secondary-background-color, #f4f6fa);
  color: var(--primary-text-color); font-size: 16px; cursor: pointer; font-family: inherit;
}
.side { display: flex; flex-direction: column; gap: 8px; }
.side-pill {
  background: var(--secondary-background-color, #f4f6fa);
  border: 1px solid var(--divider-color);
  border-radius: 10px;
  padding: 8px 10px;
  text-align: center;
}
.side-pill .label { font-size: 10px; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: 0.4px; }
.side-pill .value { font-size: 15px; font-weight: 600; margin-top: 2px; }
.next { font-size: 12px; color: var(--secondary-text-color); margin: 2px 0 6px; }
.next b { color: var(--primary-text-color); font-weight: 600; }
.boost-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));
  gap: 6px;
  margin: 8px 0;
}
.boost-btn {
  background: var(--primary-color, #ff7a00); color: white; border: none;
  padding: 11px 6px; border-radius: 10px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  font-family: inherit;
  box-shadow: 0 2px 6px rgba(255,122,0,0.25);
  transition: transform 0.1s, filter 0.15s;
}
.boost-btn:hover { filter: brightness(1.08); }
.boost-btn:active { transform: translateY(1px); }
.boost-btn.cancel {
  background: var(--error-color, #e53935);
  box-shadow: 0 2px 6px rgba(229,57,53,0.25);
  grid-column: 1 / -1;
}
.boost-btn.extend { background: rgba(255,122,0,0.15); color: var(--primary-color, #ff7a00); box-shadow: none; padding: 8px 6px; }
.mode-toggle {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  background: var(--secondary-background-color, #f4f6fa);
  border-radius: 10px;
  padding: 3px;
  border: 1px solid var(--divider-color);
  margin-top: 4px;
}
.mode-pill {
  text-align: center; padding: 7px 4px; border-radius: 8px; cursor: pointer;
  font-size: 12px; font-weight: 500; color: var(--secondary-text-color);
  transition: all 0.15s; background: transparent; border: none; font-family: inherit;
}
.mode-pill.active {
  background: var(--card-background-color, #fff);
  color: var(--primary-text-color);
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.empty { color: var(--secondary-text-color); font-size: 13px; padding: 8px 0; font-style: italic; }
.error { color: var(--error-color, #e53935); font-size: 12px; margin-top: 8px; }
`;

const I18N = {
  en: {
    brand: "Dud Shemesh", ends_in: "Ends in", to_target: "To target", status: "Status", target: "Target",
    showers: "Showers", about_min: (n) => `~${n} min`, stop: "STOP HEATING",
    boost_min: (n) => `${n} min`, boost_hour: "1 hour", boost_hours: (n) => `${n} hours`, extend: (l) => `+${l}`,
    auto: "Auto", schedule: "Schedule", off: "Off",
    st_ready: "Ready", st_heating: "Heating", st_waiting: "Waiting", st_solar: "Solar", st_cold: "Cold",
    src_schedule: "Schedule", src_boost: "Boost", src_manual: "Manual", src_auto: "Pre-heat",
    src_legionella: "Anti-Legionella", src_calendar: "Calendar", src_vacation_hold: "Vacation",
    next: "Next:", hot_by: "Hot by", today: "today", tomorrow: "tomorrow",
    dur_hm: (h, m) => `${h}h ${String(m).padStart(2, "0")}m`,
    e_title: "Title", e_entry: "Water heater", e_first: "First (default)", e_show_mode: "Show mode switch",
  },
  he: {
    brand: "דוד שמש", ends_in: "מסתיים בעוד", to_target: "עד היעד", status: "מצב", target: "יעד",
    showers: "מקלחות", about_min: (n) => `כ-${n} דק׳`, stop: "הפסק חימום",
    boost_min: (n) => `${n} דק׳`, boost_hour: "שעה", boost_hours: (n) => (n === 2 ? "שעתיים" : `${n} שעות`), extend: (l) => `עוד ${l}`,
    auto: "אוטומטי", schedule: "לוח זמנים", off: "כבוי",
    st_ready: "מוכן", st_heating: "מחמם", st_waiting: "ממתין", st_solar: "סולארי", st_cold: "קר",
    src_schedule: "לוח זמנים", src_boost: "הפעלה מהירה", src_manual: "ידני", src_auto: "חימום מקדים",
    src_legionella: "חיטוי ליגיונלה", src_calendar: "יומן", src_vacation_hold: "חופשה",
    next: "הבא:", hot_by: "חם עד", today: "היום", tomorrow: "מחר",
    dur_hm: (h, m) => `${h} ש׳ ${String(m).padStart(2, "0")} ד׳`,
    e_title: "כותרת", e_entry: "דוד", e_first: "הראשון (ברירת מחדל)", e_show_mode: "הצג בורר מצב",
  },
};

function langOf(hass) {
  const l = (hass && (hass.language || (hass.locale && hass.locale.language))) || "en";
  return l.toLowerCase().startsWith("he") ? "he" : "en";
}

function svgEl(tag, attrs = {}, children = []) {
  const n = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const k of Object.keys(attrs)) {
    if (attrs[k] != null) n.setAttribute(k, attrs[k]);
  }
  (Array.isArray(children) ? children : [children]).forEach(c => c && n.appendChild(c));
  return n;
}

function mk(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
}

class DudCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._state = null;
    this._timer = null;
    this._tickTimer = null;
    this._initialized = false;
    this._heaterUnsub = null;
    this._serverOffset = 0;
    this._endsInValueEl = null;
    this._endsInEndsAt = 0;
    this._config = {};
  }

  static getConfigElement() { return document.createElement("dud-shemesh-card-editor"); }
  static getStubConfig() { return { show_mode: true }; }

  setConfig(config) {
    const prevEntry = this._config && this._config.entry_id;
    this._config = config || {};
    if (this._initialized) {
      if (prevEntry !== this._config.entry_id) this._refresh().then(() => this._subscribeHeaterState());
      else this._render();
    }
  }
  getCardSize() { return 5; }
  set hass(hass) { this._hass = hass; if (!this._initialized) this._init(); }
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

  _t(key, ...args) {
    const dict = I18N[langOf(this._hass)];
    const v = dict[key] != null ? dict[key] : I18N.en[key];
    return typeof v === "function" ? v(...args) : (v != null ? v : key);
  }

  _entryData(extra) {
    return Object.assign(this._config.entry_id ? { entry_id: this._config.entry_id } : {}, extra || {});
  }

  _startTimers() {
    if (!this._timer) this._timer = setInterval(() => this._refresh(), 5000);
    if (!this._tickTimer) this._tickTimer = setInterval(() => this._tickEndsIn(), 1000);
  }
  _stopTimers() {
    if (this._timer) { clearInterval(this._timer); this._timer = null; }
    if (this._tickTimer) { clearInterval(this._tickTimer); this._tickTimer = null; }
  }

  _init() {
    this._initialized = true;
    const style = document.createElement("style");
    style.textContent = STYLES;
    this.shadowRoot.appendChild(style);
    this._root = document.createElement("div");
    this.shadowRoot.appendChild(this._root);
    this._refresh().then(() => this._subscribeHeaterState());
    this._startTimers();
  }

  async _refresh() {
    try {
      this._state = await this._hass.callWS(this._entryData({ type: "dud_shemesh/get_state" }));
      if (this._state && typeof this._state.now === "number") {
        this._serverOffset = this._state.now - Math.floor(Date.now() / 1000);
      }
      if (this._pendingTimer) return;
      this._render();
    } catch (e) {
      this._renderError(e);
    }
  }

  _serverNow() { return Math.floor(Date.now() / 1000) + (this._serverOffset || 0); }

  _formatRemaining(seconds) {
    if (seconds <= 0) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins < 60) return `${mins}:${secs.toString().padStart(2, "0")}`;
    return this._t("dur_hm", Math.floor(mins / 60), mins % 60);
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

  async _subscribeHeaterState() {
    if (this._heaterUnsub) { try { this._heaterUnsub(); } catch (e) {} this._heaterUnsub = null; }
    const heaterId = this._state && this._state.options && this._state.options.heater_entity;
    if (!heaterId || !this._hass || !this._hass.connection) return;
    try {
      this._heaterUnsub = await this._hass.connection.subscribeEvents(
        (ev) => {
          if (!ev || !ev.data) return;
          if (ev.data.entity_id !== heaterId) return;
          this._refresh();
        },
        "state_changed"
      );
    } catch (e) {
      // Subscription is an optimisation; the 5 s poll keeps the card current.
    }
  }

  _renderError(e) {
    const card = mk("div", "card");
    card.appendChild(mk("div", "empty", `${this._t("brand")}: ${(e && e.message) || "not loaded"}`));
    this._root.innerHTML = "";
    this._root.appendChild(card);
  }

  _showError(e) {
    this._error = (e && e.message) || String(e);
    clearTimeout(this._errorTimer);
    this._errorTimer = setTimeout(() => { this._error = null; this._render(); }, 4000);
    this._render();
  }

  async _call(service, data) {
    try {
      await this._hass.callService("dud_shemesh", service, this._entryData(data));
      setTimeout(() => this._refresh(), 300);
    } catch (e) {
      this._showError(e);
    }
  }

  async _saveOptions(patch) {
    try {
      await this._hass.callWS(this._entryData(Object.assign({ type: "dud_shemesh/update_options" }, patch)));
      setTimeout(() => this._refresh(), 300);
    } catch (e) {
      this._showError(e);
    }
  }

  _boostButtons(opts) {
    const arr = String((opts && opts.boost_buttons) || "30,60,120").split(",")
      .map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n > 0 && n <= 720);
    return (arr.length ? arr : [30, 60, 120]).slice(0, 4);
  }

  _boostLabel(mins) {
    if (mins === 60) return this._t("boost_hour");
    if (mins > 60 && mins % 60 === 0) return this._t("boost_hours", mins / 60);
    return this._t("boost_min", mins);
  }

  _fmtWhen(ts) {
    const d = new Date(ts * 1000);
    const now = new Date(this._serverNow() * 1000);
    const dayDiff = Math.round((new Date(d.getFullYear(), d.getMonth(), d.getDate()) - new Date(now.getFullYear(), now.getMonth(), now.getDate())) / 86400000);
    const locale = langOf(this._hass) === "he" ? "he-IL" : undefined;
    const time = d.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit", hour12: false });
    const day = dayDiff === 0 ? this._t("today") : dayDiff === 1 ? this._t("tomorrow")
      : d.toLocaleDateString(locale, { weekday: "short" });
    return `${day} ${time}`;
  }

  _render() {
    if (!this._state) return;
    const s = this._state.status || {};
    const opts = this._state.options || {};
    const tempUnit = this._state.temperature_unit || "°C";
    const cur = s.current_temp;
    const target = this._pendingTarget != null ? this._pendingTarget : (s.target_temp || opts.target_temp || 55);
    const status = (s.status || "waiting").toLowerCase();
    const active = s.active;

    const card = mk("div", "card");
    card.dir = langOf(this._hass) === "he" ? "rtl" : "ltr";

    const title = mk("div", "title");
    title.appendChild(mk("span", null, this._config.title || this._t("brand")));
    const srcKey = active ? "src_" + active.source : null;
    const src = active ? (this._t(srcKey) === srcKey ? active.source : this._t(srcKey)) : null;
    title.appendChild(mk("span", "status-badge " + status, active ? `${this._t("st_heating")} · ${src}` : this._t("st_" + status)));
    card.appendChild(title);

    const gaugeRow = mk("div", "gauge-row");
    const gaugeCol = mk("div", "gauge-col");
    gaugeCol.appendChild(this._buildGauge(cur, target, tempUnit, !!active));
    const targetRow = mk("div", "target-row");
    const minus = mk("button", "round-btn", "−");
    const plus = mk("button", "round-btn", "+");
    const tval = mk("span", null, `${this._t("target")} ${target}${tempUnit}`);
    const bump = (d) => {
      this._pendingTarget = Math.max(20, Math.min(80, target + d));
      clearTimeout(this._pendingTimer);
      this._pendingTimer = setTimeout(() => {
        this._pendingTimer = null;
        const v = this._pendingTarget;
        this._pendingTarget = null;
        this._saveOptions({ target_temp: v });
      }, 700);
      this._render();
    };
    minus.onclick = () => bump(-1);
    plus.onclick = () => bump(1);
    minus.setAttribute("aria-label", "−");
    plus.setAttribute("aria-label", "+");
    targetRow.append(minus, tval, plus);
    gaugeCol.appendChild(targetRow);
    gaugeRow.appendChild(gaugeCol);

    const side = mk("div", "side");
    if (active) {
      const remaining = Math.max(0, active.ends_at - this._serverNow());
      const pill = this._sidePill(this._t("ends_in"), this._formatRemaining(remaining));
      this._endsInValueEl = pill.querySelector(".value");
      this._endsInValueEl.dir = "ltr";
      this._endsInEndsAt = active.ends_at;
      side.appendChild(pill);
    } else if (s.estimated_minutes_to_target != null && s.estimated_minutes_to_target > 0) {
      side.appendChild(this._sidePill(this._t("to_target"), this._t("about_min", s.estimated_minutes_to_target)));
    } else {
      side.appendChild(this._sidePill(this._t("status"), this._t("st_" + status)));
    }
    if (s.showers_available != null) side.appendChild(this._sidePill(this._t("showers"), `🚿 ${s.showers_available}`));
    gaugeRow.appendChild(side);
    card.appendChild(gaugeRow);

    const nxt = s.next_heat;
    if (!active && nxt) {
      const line = mk("div", "next");
      if (nxt.ready_by) {
        line.append(`${this._t("hot_by")} `, mk("b", null, this._fmtWhen(nxt.ready_by)));
      } else {
        line.append(`${this._t("next")} `, mk("b", null, this._fmtWhen(nxt.at)), nxt.label ? ` · ${nxt.label}` : "");
      }
      card.appendChild(line);
    }

    const boostRow = mk("div", "boost-row");
    const buttons = this._boostButtons(opts);
    if (active) {
      const stop = mk("button", "boost-btn cancel", this._t("stop"));
      stop.onclick = () => this._call("cancel_boost");
      boostRow.appendChild(stop);
      buttons.forEach(mins => {
        const b = mk("button", "boost-btn extend", this._t("extend", this._boostLabel(mins)));
        b.onclick = () => this._call("boost", { minutes: mins });
        boostRow.appendChild(b);
      });
    } else {
      buttons.forEach(mins => {
        const b = mk("button", "boost-btn", this._boostLabel(mins));
        b.onclick = () => this._call("boost", { minutes: mins });
        boostRow.appendChild(b);
      });
    }
    card.appendChild(boostRow);

    if (this._config.show_mode !== false) {
      const modeWrap = mk("div", "mode-toggle");
      const mode = (opts.mode || "schedule").toLowerCase();
      ["auto", "schedule", "off"].forEach(key => {
        const pill = mk("button", "mode-pill" + (mode === key ? " active" : ""), this._t(key));
        pill.onclick = () => this._saveOptions({ mode: key });
        modeWrap.appendChild(pill);
      });
      card.appendChild(modeWrap);
    }

    if (this._error) card.appendChild(mk("div", "error", this._error));

    this._root.innerHTML = "";
    this._root.appendChild(card);
  }

  _sidePill(label, value) {
    const wrap = mk("div", "side-pill");
    wrap.append(mk("div", "label", label), mk("div", "value", value));
    return wrap;
  }

  _buildGauge(cur, target, tempUnit, heating) {
    const minTemp = 20, maxTemp = 80;
    const clamped = cur != null ? Math.max(minTemp, Math.min(maxTemp, cur)) : minTemp;
    const pct = (clamped - minTemp) / (maxTemp - minTemp);
    const targetPct = (Math.max(minTemp, Math.min(maxTemp, target)) - minTemp) / (maxTemp - minTemp);
    const startAngle = -210, endAngle = 30;
    const angleSpan = endAngle - startAngle;
    const valueAngle = startAngle + angleSpan * pct;
    const targetAngle = startAngle + angleSpan * targetPct;

    const cx = 90, cy = 90, r = 72, sw = 13;
    const polar = (a, R) => [cx + R * Math.cos(a * Math.PI / 180), cy + R * Math.sin(a * Math.PI / 180)];
    const arcPath = (a1, a2, R) => {
      const [x1, y1] = polar(a1, R);
      const [x2, y2] = polar(a2, R);
      const large = (a2 - a1) > 180 ? 1 : 0;
      return `M ${x1} ${y1} A ${R} ${R} 0 ${large} 1 ${x2} ${y2}`;
    };
    const tempColor = heating ? "#ff5722"
      : cur == null ? "#9e9e9e"
      : cur < 35 ? "#2196f3"
      : cur < 45 ? "#4caf50"
      : cur < 60 ? "#ff9800"
      : "#e53935";
    const [tx, ty] = polar(targetAngle, r);

    return svgEl("svg", { viewBox: "0 0 180 160", style: "width:160px;height:auto;direction:ltr;" }, [
      svgEl("path", { d: arcPath(startAngle, endAngle, r), fill: "none", stroke: "rgba(0,0,0,0.08)", "stroke-width": sw, "stroke-linecap": "round" }),
      svgEl("path", { d: arcPath(startAngle, valueAngle, r), fill: "none", stroke: tempColor, "stroke-width": sw, "stroke-linecap": "round" }),
      svgEl("circle", { cx: tx, cy: ty, r: 5, fill: "var(--primary-text-color)" }),
      svgEl("text", { x: cx, y: cy - 4, "text-anchor": "middle", "font-size": "32", "font-weight": "700", fill: "var(--primary-text-color)", "font-family": "inherit" },
        document.createTextNode(cur != null ? `${Math.round(cur)}` : "—")),
      svgEl("text", { x: cx, y: cy + 16, "text-anchor": "middle", "font-size": "12", fill: "var(--secondary-text-color)", "font-family": "inherit" },
        document.createTextNode(tempUnit)),
    ]);
  }
}

// Visual editor shown in the Lovelace card picker.
class DudCardEditor extends HTMLElement {
  setConfig(config) { this._config = Object.assign({}, config); this._render(); }
  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) this._loadEntries();
  }

  async _loadEntries() {
    try {
      this._entries = (await this._hass.callWS({ type: "config_entries/get", domain: "dud_shemesh" })) || [];
    } catch (e) {
      this._entries = [];
    }
    this._render();
  }

  _t(key) {
    const dict = I18N[langOf(this._hass)];
    return dict[key] != null ? dict[key] : I18N.en[key];
  }

  _emit() {
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this._config }, bubbles: true, composed: true }));
  }

  _render() {
    if (!this._config) return;
    this.innerHTML = "";
    const wrap = mk("div");
    wrap.style.cssText = "display:flex;flex-direction:column;gap:12px;padding:4px 0;";
    const row = (label, input) => {
      const l = mk("label");
      l.style.cssText = "display:flex;flex-direction:column;gap:4px;font-size:13px;";
      l.append(mk("span", null, label), input);
      return l;
    };
    const inputCss = "padding:8px;border:1px solid var(--divider-color);border-radius:6px;background:var(--card-background-color);color:var(--primary-text-color);font:inherit;";

    const title = document.createElement("input");
    title.style.cssText = inputCss;
    title.value = this._config.title || "";
    title.placeholder = this._t("brand");
    title.addEventListener("change", () => {
      if (title.value) this._config.title = title.value; else delete this._config.title;
      this._emit();
    });
    wrap.appendChild(row(this._t("e_title"), title));

    const sel = document.createElement("select");
    sel.style.cssText = inputCss;
    sel.appendChild(new Option(this._t("e_first"), ""));
    (this._entries || []).forEach(e => sel.appendChild(new Option(e.title, e.entry_id)));
    sel.value = this._config.entry_id || "";
    sel.addEventListener("change", () => {
      if (sel.value) this._config.entry_id = sel.value; else delete this._config.entry_id;
      this._emit();
    });
    wrap.appendChild(row(this._t("e_entry"), sel));

    const cbLabel = mk("label");
    cbLabel.style.cssText = "display:flex;align-items:center;gap:8px;font-size:13px;";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = this._config.show_mode !== false;
    cb.addEventListener("change", () => { this._config.show_mode = cb.checked; this._emit(); });
    cbLabel.append(cb, this._t("e_show_mode"));
    wrap.appendChild(cbLabel);

    this.appendChild(wrap);
  }
}

if (!customElements.get("dud-shemesh-card-editor")) {
  customElements.define("dud-shemesh-card-editor", DudCardEditor);
}
if (!customElements.get("dud-shemesh-card")) {
  customElements.define("dud-shemesh-card", DudCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "dud-shemesh-card",
    name: "Dud Shemesh",
    description: "Smart solar water heater control: gauge, boost, mode, next heat.",
    preview: true,
  });
}
