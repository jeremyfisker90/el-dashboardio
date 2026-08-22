/* emporia-top5-card — neon "top circuits" leaderboard for the Electricity view.
 * Ranks every *_energy_today circuit statistic over a window (day / week / month)
 * using HA's long-term statistics, so week + month are real history, not live state.
 * Config: { period: "day"|"week"|"month", title?: str, exclude?: [entity_id,...] }
 */
class EmporiaTop5Card extends HTMLElement {
  setConfig(config) {
    this._config = config || {};
    this._lastFetch = 0;
    this._busy = false;
  }
  set hass(hass) {
    this._hass = hass;
    if (Date.now() - this._lastFetch > 300000 && !this._busy) this._refresh();
  }
  getCardSize() { return 5; }

  _windowStart() {
    const now = new Date();
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const p = this._config.period || "day";
    if (p === "week") d.setDate(d.getDate() - ((d.getDay() + 6) % 7)); // back to Monday
    if (p === "month") d.setDate(1);
    return d;
  }

  _label(id) {
    const st = this._hass.states[id];
    let n = ((st && st.attributes.friendly_name) || id.replace("sensor.", ""))
      .replace(/energy[ _]?today/i, "").replace(/[_]/g, " ").trim();
    if (/^h ?vac/i.test(n)) n = "HVAC";
    else if (/small appliances/i.test(n)) n = "Small appliances";
    else n = n.replace(/[.,].*$/, "").trim();
    n = n.charAt(0).toUpperCase() + n.slice(1);
    return n.length > 24 ? n.slice(0, 23) + "…" : n;
  }

  async _refresh() {
    if (!this._hass) return;
    this._busy = true;
    this._lastFetch = Date.now();
    try {
      const excl = ["sensor.home_vue_energy_today", "sensor.balance_energy_today"]
        .concat(this._config.exclude || []);
      const ids = Object.keys(this._hass.states)
        .filter(k => /_energy_today$/.test(k) && !excl.includes(k));
      if (!ids.length) { this._paint([], 0); return; }
      const res = await this._hass.callWS({
        type: "recorder/statistics_during_period",
        start_time: this._windowStart().toISOString(),
        statistic_ids: ids,
        period: (this._config.period || "day") === "day" ? "hour" : "day",
        types: ["change"],
      });
      const totals = ids.map(id => ({
        id,
        kwh: (res[id] || []).reduce((a, b) => a + (b.change || 0), 0),
      })).filter(t => t.kwh > 0.0005).sort((a, b) => b.kwh - a.kwh);
      const grand = totals.reduce((a, t) => a + t.kwh, 0);
      this._paint(totals.slice(0, 5), grand);
    } catch (e) {
      this._paint(null, 0, String(e && (e.message || e.code) || e));
    }
    this._busy = false;
  }

  _paint(rows, grand, err) {
    const P = { day: "TODAY", week: "THIS WEEK", month: "THIS MONTH" }[this._config.period || "day"];
    const title = this._config.title || ("TOP CIRCUITS — " + P);
    const fmt = v => v >= 100 ? Math.round(v) : v >= 10 ? v.toFixed(1) : v.toFixed(2);
    let body;
    if (err) {
      body = '<div style="padding:14px;color:#fca5a5;font-size:12px;">' + err + "</div>";
    } else if (!rows || !rows.length) {
      body = '<div style="padding:14px;color:#94a3b8;font-size:12px;font-style:italic;">No usage recorded yet.</div>';
    } else {
      const max = rows[0].kwh;
      body = rows.map((r, i) => {
        const pct = Math.max(4, Math.round(r.kwh / max * 100));
        const share = grand ? Math.round(r.kwh / grand * 100) : 0;
        if (i === 0) {
          return '<div style="padding:10px 12px 6px;">'
            + '<div style="display:flex;align-items:baseline;gap:8px;">'
            + '<span style="font-size:20px;filter:drop-shadow(0 0 6px rgba(250,204,21,.9));">👑</span>'
            + '<span style="font-size:16px;font-weight:900;color:#fde047;text-shadow:0 0 10px rgba(250,204,21,.6);'
            + 'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;flex:1;">' + this._label(r.id) + "</span>"
            + '<span style="font-size:15px;font-weight:900;color:#f8fafc;">' + fmt(r.kwh) + ' <small style="color:#94a3b8;font-weight:700;">kWh · ' + share + "%</small></span></div>"
            + '<div style="height:8px;border-radius:4px;background:rgba(0,0,0,.4);margin-top:5px;overflow:hidden;">'
            + '<div style="height:100%;width:100%;background:linear-gradient(90deg,#f59e0b,#fde047);box-shadow:0 0 10px rgba(250,204,21,.5);"></div></div></div>';
        }
        return '<div style="padding:4px 12px;display:flex;align-items:center;gap:8px;">'
          + '<span style="width:12px;font-size:10px;font-weight:900;color:#64748b;">' + (i + 1) + "</span>"
          + '<span style="flex:1;min-width:0;font-size:12px;font-weight:700;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + this._label(r.id) + "</span>"
          + '<span style="font-size:11.5px;font-weight:800;color:#cbd5e1;">' + fmt(r.kwh) + ' <small style="color:#64748b;">kWh</small></span>'
          + '<span style="flex:0 0 34%;height:6px;border-radius:3px;background:rgba(0,0,0,.4);overflow:hidden;">'
          + '<span style="display:block;height:100%;width:' + pct + '%;background:linear-gradient(90deg,#b45309,#f59e0b);"></span></span></div>';
      }).join("");
      body += '<div style="padding:7px 12px 10px;font-size:10px;color:#64748b;font-weight:700;">'
        + fmt(grand) + " kWh across all circuits</div>";
    }
    this.innerHTML =
      '<ha-card style="background:rgba(8,12,24,.86);border:1px solid rgba(250,204,21,.4);border-radius:16px;'
      + 'box-shadow:0 0 16px rgba(250,204,21,.15),0 8px 20px rgba(0,0,0,.5);overflow:hidden;">'
      + '<div style="padding:7px 12px;background:linear-gradient(180deg,rgba(250,204,21,.30),rgba(250,204,21,.08));'
      + 'border-bottom:2px solid #facc15;font-size:12.5px;font-weight:900;letter-spacing:1.5px;color:#fef9c3;'
      + 'text-shadow:0 0 10px rgba(250,204,21,.7);">⚡ ' + title + "</div>" + body + "</ha-card>";
  }
}
customElements.define("emporia-top5-card", EmporiaTop5Card);
window.customCards = window.customCards || [];
window.customCards.push({ type: "emporia-top5-card", name: "Emporia Top 5", description: "Top energy circuits over a period" });
