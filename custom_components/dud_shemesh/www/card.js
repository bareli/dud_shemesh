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
.title { font-size: 15px; font-weight: 600; margin: 0 0 4px; display: flex; align-items: center; justify-content: space-between; }
.title .status-badge {
  font-size: 10px; font-weight: 600;
  padding: 3px 10px; border-radius: 999px;
  text-transform: uppercase; letter-spacing: 0.5px;
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
  .side { flex-direction: row !important; justify-content: space-around !important; }
}
.gauge-wrap { display: flex; justify-content: center; align-items: center; }
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
.boost-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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
  grid-column: span 3;
}
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
  transition: all 0.15s;
}
.mode-pill.active {
  background: var(--card-background-color, #fff);
  color: var(--primary-text-color);
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.empty { color: var(--secondary-text-color); font-size: 13px; padding: 8px 0; font-style: italic; }
`;

const STATUS_LABELS = { ready: "Ready", heating: "Heating", waiting: "Waiting", solar: "Solar", cold: "Cold" };

function svgEl(tag, attrs = {}, children = []) {
  const n = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const k of Object.keys(attrs)) {
    if (attrs[k] != null) n.setAttribute(k, attrs[k]);
  }
  (Array.isArray(children) ? children : [children]).forEach(c => c && n.appendChild(c));
  return n;
}

class DudCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._state = null;
    this._timer = null;
    this._initialized = false;
  }

  setConfig(config) { this._config = config || {}; if (this._initialized) this._render(); }
  getCardSize() { return 4; }
  set hass(hass) { this._hass = hass; if (!this._initialized) this._init(); }
  connectedCallback() { if (this._hass && !this._initialized) this._init(); }
  disconnectedCallback() { if (this._timer) clearInterval(this._timer); }

  _init() {
    this._initialized = true;
    const style = document.createElement("style");
    style.textContent = STYLES;
    this.shadowRoot.appendChild(style);
    this._root = document.createElement("div");
    this.shadowRoot.appendChild(this._root);
    this._refresh();
    this._timer = setInterval(() => this._refresh(), 5000);
  }

  async _refresh() {
    try {
      this._state = await this._hass.callWS({ type: "dud_shemesh/get_state" });
      this._render();
    } catch (e) {
      this._renderError(e);
    }
  }

  _renderError(e) {
    this._root.innerHTML = `<div class="card"><div class="empty">Dud Shemesh: ${e.message || "not loaded"}</div></div>`;
  }

  async _call(service, data) {
    try {
      await this._hass.callService("dud_shemesh", service, data || {});
      setTimeout(() => this._refresh(), 300);
    } catch (e) {
      console.error("dud_shemesh card:", e);
    }
  }

  async _saveOptions(patch) {
    try {
      await this._hass.callWS(Object.assign({ type: "dud_shemesh/update_options" }, patch));
      setTimeout(() => this._refresh(), 300);
    } catch (e) {
      console.error("dud_shemesh card:", e);
    }
  }

  _render() {
    if (!this._state) return;
    const s = this._state.status || {};
    const opts = this._state.options || {};
    const tempUnit = this._state.temperature_unit || "°C";
    const cur = s.current_temp;
    const target = s.target_temp || opts.target_temp || 55;
    const status = (s.status || "waiting").toLowerCase();
    const active = s.active;

    const card = document.createElement("div");
    card.className = "card";

    const title = document.createElement("div");
    title.className = "title";
    const tName = document.createElement("span");
    tName.textContent = this._config.title || "Dud Shemesh";
    const badge = document.createElement("span");
    badge.className = "status-badge " + status;
    badge.textContent = STATUS_LABELS[status] || status;
    title.appendChild(tName);
    title.appendChild(badge);
    card.appendChild(title);

    const gaugeRow = document.createElement("div");
    gaugeRow.className = "gauge-row";

    const gaugeWrap = document.createElement("div");
    gaugeWrap.className = "gauge-wrap";
    gaugeWrap.appendChild(this._buildGauge(cur, target, tempUnit));
    gaugeRow.appendChild(gaugeWrap);

    const side = document.createElement("div");
    side.className = "side";
    if (active) {
      const remaining = Math.max(0, active.ends_at - this._state.now);
      const mins = Math.floor(remaining / 60);
      const sec = String(remaining % 60).padStart(2, "0");
      side.appendChild(this._sidePill("Ends in", `${mins}:${sec}`));
    } else if (s.estimated_minutes_to_target != null && s.estimated_minutes_to_target > 0) {
      side.appendChild(this._sidePill("To target", `~${s.estimated_minutes_to_target} min`));
    } else {
      side.appendChild(this._sidePill("Status", STATUS_LABELS[status] || status));
    }
    side.appendChild(this._sidePill("Target", `${target}${tempUnit}`));
    gaugeRow.appendChild(side);
    card.appendChild(gaugeRow);

    const boostRow = document.createElement("div");
    boostRow.className = "boost-row";
    if (active) {
      const stop = document.createElement("button");
      stop.className = "boost-btn cancel";
      stop.textContent = "STOP HEATING";
      stop.onclick = () => this._call("cancel_boost");
      boostRow.appendChild(stop);
    } else {
      [["+30 min", 30], ["+1 hour", 60], ["+2 hours", 120]].forEach(([label, mins]) => {
        const b = document.createElement("button");
        b.className = "boost-btn";
        b.textContent = label;
        b.onclick = () => this._call("boost", { minutes: mins });
        boostRow.appendChild(b);
      });
    }
    card.appendChild(boostRow);

    if (this._config.show_mode !== false) {
      const modeWrap = document.createElement("div");
      modeWrap.className = "mode-toggle";
      const mode = (opts.mode || "schedule").toLowerCase();
      [["auto", "Auto"], ["schedule", "Schedule"], ["off", "Off"]].forEach(([key, label]) => {
        const pill = document.createElement("div");
        pill.className = "mode-pill" + (mode === key ? " active" : "");
        pill.textContent = label;
        pill.onclick = () => this._saveOptions({ mode: key });
        modeWrap.appendChild(pill);
      });
      card.appendChild(modeWrap);
    }

    this._root.innerHTML = "";
    this._root.appendChild(card);
  }

  _sidePill(label, value) {
    const wrap = document.createElement("div");
    wrap.className = "side-pill";
    const l = document.createElement("div"); l.className = "label"; l.textContent = label;
    const v = document.createElement("div"); v.className = "value"; v.textContent = value;
    wrap.appendChild(l); wrap.appendChild(v);
    return wrap;
  }

  _buildGauge(cur, target, tempUnit) {
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
    const tempColor = cur == null ? "#9e9e9e"
      : cur < 35 ? "#2196f3"
      : cur < 45 ? "#4caf50"
      : cur < 60 ? "#ff9800"
      : "#e53935";
    const [tx, ty] = polar(targetAngle, r);

    return svgEl("svg", { viewBox: "0 0 180 180", style: "width:160px;height:160px;" }, [
      svgEl("path", { d: arcPath(startAngle, endAngle, r), fill: "none", stroke: "rgba(0,0,0,0.08)", "stroke-width": sw, "stroke-linecap": "round" }),
      svgEl("path", { d: arcPath(startAngle, valueAngle, r), fill: "none", stroke: tempColor, "stroke-width": sw, "stroke-linecap": "round" }),
      svgEl("circle", { cx: tx, cy: ty, r: 4.5, fill: "var(--primary-text-color)" }),
      svgEl("text", { x: cx, y: cy - 4, "text-anchor": "middle", "font-size": "32", "font-weight": "700", fill: "var(--primary-text-color)", "font-family": "inherit" },
        document.createTextNode(cur != null ? `${Math.round(cur)}` : "—")),
      svgEl("text", { x: cx, y: cy + 16, "text-anchor": "middle", "font-size": "12", fill: "var(--secondary-text-color)", "font-family": "inherit" },
        document.createTextNode(tempUnit)),
    ]);
  }
}

if (!customElements.get("dud-shemesh-card")) {
  customElements.define("dud-shemesh-card", DudCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "dud-shemesh-card",
    name: "Dud Shemesh",
    description: "Smart solar water heater control: gauge, boost, mode.",
    preview: false,
  });
}
