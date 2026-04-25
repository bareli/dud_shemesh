// Minimal Lovelace card placeholder for v0.1. Mirrors the panel's status block.
const STYLES = `
:host { display: block; }
.card { background: var(--ha-card-background, var(--card-background-color, #fff));
  border-radius: var(--ha-card-border-radius, 12px);
  border: 1px solid var(--ha-card-border-color, var(--divider-color, #e5e7eb));
  padding: 14px; color: var(--primary-text-color);
  font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif); }
.row { display: grid; grid-template-columns: auto 1fr auto; gap: 12px; align-items: center; }
.t { font-size: 32px; font-weight: 700; }
.unit { font-size: 14px; color: var(--secondary-text-color); }
.label { font-weight: 500; font-size: 14px; }
.sub { color: var(--secondary-text-color); font-size: 12px; }
.btn { padding: 6px 12px; border: 1px solid var(--divider-color); background: var(--card-background-color);
  color: var(--primary-text-color); border-radius: 8px; cursor: pointer; font: inherit; font-size: 13px; }
.btn.primary { background: var(--primary-color, #ff7a00); color: white; border-color: transparent; }
.actions { display: flex; gap: 6px; flex-wrap: wrap; }
.empty { color: var(--secondary-text-color); font-size: 13px; }
`;

class DudCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._state = null;
    this._timer = null;
    this._initialized = false;
  }
  setConfig(config) { this._config = config || {}; if (this._initialized) this._render(); }
  getCardSize() { return 2; }
  set hass(hass) { this._hass = hass; if (!this._initialized) this._init(); }
  connectedCallback() { if (this._hass && !this._initialized) this._init(); }
  disconnectedCallback() { if (this._timer) clearInterval(this._timer); }

  _init() {
    this._initialized = true;
    const style = document.createElement("style"); style.textContent = STYLES;
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
      this._root.innerHTML = `<div class="card empty">Dud Shemesh not loaded</div>`;
    }
  }
  async _call(service, data) {
    await this._hass.callService("dud_shemesh", service, data || {});
    setTimeout(() => this._refresh(), 300);
  }
  _render() {
    if (!this._state) return;
    const s = this._state.status || {};
    const opts = this._state.options || {};
    const tempUnit = this._state.temperature_unit || "°C";
    const cur = s.current_temp;
    const target = s.target_temp || opts.target_temp || 55;
    const isActive = !!s.active;
    const status = (s.status || "waiting").toUpperCase();
    this._root.innerHTML = "";
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="row">
        <div>
          <div class="t">${cur != null ? Math.round(cur) : "—"}<span class="unit"> ${tempUnit}</span></div>
        </div>
        <div>
          <div class="label">${this._config.title || "Dud Shemesh"}</div>
          <div class="sub">${status} · target ${target}${tempUnit}</div>
        </div>
        <div class="actions" id="acts"></div>
      </div>
    `;
    const acts = card.querySelector("#acts");
    const mkBtn = (label, cls, fn) => {
      const b = document.createElement("button");
      b.className = "btn " + cls;
      b.textContent = label;
      b.onclick = fn;
      acts.appendChild(b);
    };
    if (isActive) {
      mkBtn("Stop", "", () => this._call("cancel_boost"));
    } else {
      mkBtn("+30m", "primary", () => this._call("boost", { minutes: 30 }));
      mkBtn("+1h", "primary", () => this._call("boost", { minutes: 60 }));
    }
    this._root.appendChild(card);
  }
}
if (!customElements.get("dud-shemesh-card")) {
  customElements.define("dud-shemesh-card", DudCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "dud-shemesh-card",
    name: "Dud Shemesh",
    description: "Compact tank temp + boost buttons.",
    preview: false,
  });
}
