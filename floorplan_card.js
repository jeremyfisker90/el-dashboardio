/* neon-floorplan-card — the El Dashboardio night-house.
 * Renders the family's saved floorplan (rooms + furniture from the addon's
 * /floorplan store) as a dark isometric model. Rooms with lights on glow warm;
 * tapping a room toggles its lights. Thermostat chip lives in the Dining Room.
 */

const FP_API = "http://" + location.hostname.replace(/:.*/, "") + ":5000";
const S = 13, THICK = 16, GAP = 0.3;
const TITLES = { floor1: "1st Floor", floor2: "2nd Floor", basement: "Lower Level" };

const ROOM_LIGHTS = {
  "Office": ["switch.office_overhead", "light.office_lamp", "light.office_floor_lamp"],
  "Family Room": ["light.family_room_lamp_1", "light.family_room_lamp_2",
                  "light.familyroom_lamp_3", "switch.xmaslightsfamilyroom",
                  "light.charging_station"],
  "Kitchen": ["light.kitchen_cabinets"],
  "Foyer": ["light.foyer_lights"],
  "Porch": ["light.front_door_light"],
  "Ian's Room": ["light.devastator", "light.ianroom"],
  "Evan's Room": ["light.orange_dog"],
  "Master Bedroom": ["light.bedroom_lamp_1", "light.bedroom_lamp_2"],
};
const THERMO = { room: "Dining Room", floor: "floor1", entity: "climate.nest_thermostat" };

function iso(x, y, z) { return [(x - y) * 0.866 * S, (x + y) * 0.5 * S - (z || 0)]; }
function fmt(p) { return p[0].toFixed(1) + "," + p[1].toFixed(1); }
function pts(l) { return l.map(fmt).join(" "); }

function prism(x1, y1, x2, y2, z0, z1, top, side1, side2, stroke, sw, extra) {
  const pTL = iso(x1, y1, z1), pTR = iso(x2, y1, z1), pBR = iso(x2, y2, z1), pBL = iso(x1, y2, z1);
  const bBL = iso(x1, y2, z0), bBR = iso(x2, y2, z0), bTR = iso(x2, y1, z0);
  return '<polygon points="' + pts([pBL, pBR, bBR, bBL]) + '" fill="' + side1 + '" stroke="' + stroke + '" stroke-width="' + sw + '"/>'
    + '<polygon points="' + pts([pTR, pBR, bBR, bTR]) + '" fill="' + side2 + '" stroke="' + stroke + '" stroke-width="' + sw + '"/>'
    + '<polygon points="' + pts([pTL, pTR, pBR, pBL]) + '" fill="' + top + '" stroke="' + stroke + '" stroke-width="' + sw + '" ' + (extra || "") + "/>";
}

class NeonFloorplanCard extends HTMLElement {
  setConfig(config) {
    this._config = config || {};
    this._floor = this._config.floor || "floor1";
    this._layout = null;
    this._lastSig = "";
    this._fetchLayout();
  }
  getCardSize() { return 12; }

  async _fetchLayout() {
    try {
      const r = await fetch(FP_API + "/floorplan");
      this._layout = await r.json();
    } catch (e) { this._layout = null; }
    this._lastSig = "";
    if (this._hass) this._render();
    clearTimeout(this._t);
    this._t = setTimeout(() => this._fetchLayout(), 300000);
  }

  set hass(hass) {
    this._hass = hass;
    if (this._panelRoom) this._paintPanel();     // keep an open panel live
    const sig = Object.values(ROOM_LIGHTS).flat()
      .map(e => e + ":" + (hass.states[e] ? hass.states[e].state : "x")).join("|")
      + "|" + (hass.states[THERMO.entity] ? JSON.stringify(hass.states[THERMO.entity].attributes.current_temperature) + (hass.states[THERMO.entity].attributes.hvac_action || "") : "")
      + "|" + this._floor;
    if (sig === this._lastSig) return;
    this._lastSig = sig;
    this._render();
  }

  _roomLights(name) {
    return (ROOM_LIGHTS[name] || []).filter(e => this._hass.states[e]);
  }

  _render() {
    if (!this._hass) return;
    const lay = this._layout || {};
    const rooms = (lay.rooms && lay.rooms[this._floor]) || [];
    const furn = (lay.furniture && lay.furniture[this._floor]) || [];

    // bounds
    let px = [];
    for (const r of rooms)
      for (const c of [[r.x, r.y], [r.x + r.w, r.y], [r.x + r.w, r.y + r.d], [r.x, r.y + r.d]]) {
        const p = iso(c[0], c[1], 0); px.push(p, [p[0], p[1] + THICK]);
      }
    if (!px.length) px = [[0, 0], [500, 350]];
    const PAD = 26;
    const minx = Math.min(...px.map(p => p[0])) - PAD, maxx = Math.max(...px.map(p => p[0])) + PAD;
    const miny = Math.min(...px.map(p => p[1])) - PAD - 14, maxy = Math.max(...px.map(p => p[1])) + PAD;

    let defs = '<defs>'
      + '<filter id="nfglow" x="-40%" y="-40%" width="180%" height="180%">'
      + '<feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
      + '<radialGradient id="nfpool"><stop offset="0%" stop-color="rgba(255,190,90,0.55)"/>'
      + '<stop offset="55%" stop-color="rgba(255,170,60,0.22)"/><stop offset="100%" stop-color="rgba(255,170,60,0)"/></radialGradient>'
      + '</defs>';

    let body = "";
    const sorted = [...rooms].sort((a, b) => (a.x + a.y) - (b.x + b.y));
    const lit = {};
    for (const r of rooms) {
      const ents = this._roomLights(r.name);
      lit[r.name] = ents.filter(e => this._hass.states[e].state === "on");
    }

    // room slabs
    for (const r of sorted) {
      const hasL = this._roomLights(r.name).length > 0;
      const isLit = (lit[r.name] || []).length > 0;
      const edge = isLit ? "rgba(251,191,36,0.65)" : "rgba(34,211,238,0.4)";
      const topFill = isLit ? "#141428" : "#0b1226";
      body += '<g class="nfroom" data-room="' + r.name.replace(/"/g, "&quot;") + '" style="cursor:' + (hasL ? "pointer" : "default") + '">'
        + prism(r.x + GAP, r.y + GAP, r.x + r.w - GAP, r.y + r.d - GAP, -THICK, 0,
                topFill, "#060b18", "#091020", edge, 0.9)
        + "</g>";
      // warm pool for lit rooms, painted right after the slab so furniture sits above
      if (isLit) {
        const c = iso(r.x + r.w / 2, r.y + r.d / 2, 0);
        const rx = Math.max(r.w, 5) * 0.62 * S, ry = rx * 0.5;
        body += '<ellipse cx="' + c[0].toFixed(1) + '" cy="' + c[1].toFixed(1) + '" rx="' + rx.toFixed(0)
          + '" ry="' + ry.toFixed(0) + '" fill="url(#nfpool)" pointer-events="none"/>';
      }
    }

    // furniture silhouettes
    const sf = [...furn].sort((a, b) => (a.u + a.v) - (b.u + b.v));
    for (const it of sf) {
      const t = (this.constructor.TYPES || {})[it.type];
      const dims = t || [it.type, 3, 2, 12, "#131b36"];
      let w = dims[1] * (it.s || 1), d = dims[2] * (it.s || 1);
      if ((it.r || 0) % 2) { const tmp = w; w = d; d = tmp; }
      const h = dims[3] * Math.sqrt(it.s || 1);
      body += prism(it.u, it.v, it.u + w, it.v + d, 0, -h,
                    "#161f3d", "#0a1020", "#0e1630", "rgba(96,165,250,0.3)", 0.45, 'pointer-events="none"');
    }

    // labels + light dots
    for (const r of rooms) {
      const ents = this._roomLights(r.name);
      const on = (lit[r.name] || []).length;
      const lp = iso(r.x + r.w / 2, r.y + r.d * 0.17, 6);   // back edge, clear of the bulbs
      const col = on ? "#fde68a" : "rgba(126,231,247,0.5)";
      const glow = on ? "filter:drop-shadow(0 0 6px rgba(251,191,36,0.8));" : "";
      r.name.split(" & ").forEach((line, i) => {
        body += '<text x="' + lp[0].toFixed(1) + '" y="' + (lp[1] + i * 11).toFixed(1) + '" font-size="'
          + (r.w >= 9 ? 10.5 : 8.5) + '" font-weight="800" letter-spacing="1" text-anchor="middle" '
          + 'fill="' + col + '" style="text-transform:uppercase;' + glow + 'pointer-events:none;" '
          + 'font-family="Segoe UI, Roboto, sans-serif">' + line + "</text>";
      });
      // one hanging bulb per light, standing in the room and tappable on its own
      ents.forEach((e, i) => {
        const s = this._hass.states[e];
        const isOn = s.state === "on";
        const dead = s.state === "unavailable" || s.state === "unknown";
        const u = r.x + (r.w * (i + 1)) / (ents.length + 1);
        const v = r.y + r.d * 0.72;
        const foot = iso(u, v, 0);
        const b = iso(u, v, 26);
        const short = (s.attributes.friendly_name || e.split(".")[1].replace(/_/g, " "))
          .replace(new RegExp(r.name, "i"), "").replace(/lights?/i, "").trim() || "light";
        body += '<g class="nfbulb" data-e="' + e + '" style="cursor:pointer;">'
          + '<line x1="' + fmt(foot).replace(",", '" y1="') + '" x2="' + fmt(b).replace(",", '" y2="')
          + '" stroke="' + (isOn ? "rgba(251,191,36,0.35)" : "rgba(96,165,250,0.18)")
          + '" stroke-width="0.8" pointer-events="none"/>'
          + (isOn ? '<circle cx="' + b[0].toFixed(1) + '" cy="' + b[1].toFixed(1)
                    + '" r="15" fill="url(#nfpool)" pointer-events="none"/>' : "")
          + '<circle cx="' + b[0].toFixed(1) + '" cy="' + b[1].toFixed(1) + '" r="6.2" fill="'
          + (dead ? "#1e2740" : isOn ? "#fcd34d" : "#243049") + '" stroke="'
          + (dead ? "rgba(148,163,184,0.35)" : isOn ? "rgba(253,230,138,0.95)" : "rgba(126,231,247,0.5)")
          + '" stroke-width="1.1" ' + (isOn ? 'filter="url(#nfglow)"' : "") + ' pointer-events="none"/>'
          + '<circle cx="' + b[0].toFixed(1) + '" cy="' + b[1].toFixed(1)
          + '" r="16" fill="transparent"/>'
          + '<text x="' + b[0].toFixed(1) + '" y="' + (b[1] + 15).toFixed(1) + '" font-size="6.6" '
          + 'font-weight="800" text-anchor="middle" fill="'
          + (isOn ? "#fde68a" : "rgba(126,231,247,0.55)") + '" pointer-events="none" '
          + 'font-family="Segoe UI, Roboto, sans-serif" style="text-transform:uppercase;">'
          + short.slice(0, 12) + "</text>"
          + "</g>";
      });
    }

    // thermostat chip
    if (this._floor === THERMO.floor && this._hass.states[THERMO.entity]) {
      const tr = rooms.find(r => r.name === THERMO.room);
      if (tr) {
        const st = this._hass.states[THERMO.entity];
        const temp = st.attributes.current_temperature;
        const act = st.attributes.hvac_action || "";
        const tc = act === "cooling" ? "#22d3ee" : act === "heating" ? "#fb923c" : "#94a3b8";
        const cp = iso(tr.x + tr.w / 2, tr.y + 1.6, 28);
        body += '<g pointer-events="none"><rect x="' + (cp[0] - 24).toFixed(1) + '" y="' + (cp[1] - 10).toFixed(1)
          + '" width="48" height="19" rx="9.5" fill="rgba(8,12,26,0.92)" stroke="' + tc + '" stroke-width="0.9" filter="url(#nfglow)"/>'
          + '<text x="' + cp[0].toFixed(1) + '" y="' + (cp[1] + 3.5).toFixed(1) + '" font-size="10" font-weight="900" '
          + 'text-anchor="middle" fill="' + tc + '" font-family="Segoe UI, Roboto, sans-serif">'
          + (temp !== undefined ? Math.round(temp) + "°" : "--") + "</text></g>";
      }
    }

    const tabs = ["floor1", "floor2", "basement"].map(f =>
      '<button class="nftab' + (f === this._floor ? " on" : "") + '" data-floor="' + f + '">' + TITLES[f] + "</button>").join("");
    const onCount = Object.values(lit).reduce((a, l) => a + l.length, 0);

    this.innerHTML =
      '<ha-card style="background:transparent;border:none;box-shadow:none;">'
      + '<style>'
      + '.nfbar{display:flex;gap:8px;align-items:center;padding:8px 10px 2px;}'
      + '.nftab{border:1px solid rgba(34,211,238,.4);background:rgba(13,20,44,.7);color:#9fb2d0;'
      + 'border-radius:11px;padding:7px 14px;font-size:13px;font-weight:800;cursor:pointer;font-family:inherit;}'
      + '.nftab.on{background:rgba(34,211,238,.18);color:#7ee7f7;box-shadow:0 0 10px rgba(34,211,238,.3);}'
      + '.nfsum{margin-left:auto;font-size:12px;font-weight:800;color:' + (onCount ? "#fde68a" : "#64748b") + ';'
      + (onCount ? "text-shadow:0 0 8px rgba(251,191,36,.6);" : "") + '}'
      + '</style>'
      + '<div class="nfbar">' + tabs + '<span class="nfsum">' + (onCount ? "💡 " + onCount + " light" + (onCount === 1 ? "" : "s") + " on" : "all lights off") + "</span></div>"
      + '<svg viewBox="0 0 ' + (maxx - minx).toFixed(0) + " " + (maxy - miny).toFixed(0)
      + '" style="width:100%;height:calc(100vh - 118px);display:block;" xmlns="http://www.w3.org/2000/svg">'
      + defs + '<g transform="translate(' + (-minx).toFixed(1) + "," + (-miny).toFixed(1) + ')">' + body + "</g></svg>"
      + "</ha-card>";

    this.querySelectorAll(".nftab").forEach(b =>
      b.addEventListener("pointerup", () => { this._floor = b.dataset.floor; this._lastSig = ""; this._render(); }));
    this.querySelectorAll(".nfbulb").forEach(g =>
      g.addEventListener("pointerup", ev => {
        ev.stopPropagation();                    // this bulb, not the whole room
        this._hass.callService("homeassistant", "toggle", { entity_id: g.dataset.e });
      }));
    this.querySelectorAll(".nfroom").forEach(g =>
      g.addEventListener("pointerup", () => {
        const ents = this._roomLights(g.dataset.room);
        if (ents.length) this._openPanel(g.dataset.room);
      }));
  }

  /* ---------------------------------------------------------- light panel
   * Tapping a room used to flip every light in it at once. The panel keeps
   * that as one button and puts each light on its own row underneath, with a
   * brightness slider for the bulbs that have one. */
  _openPanel(room) {
    this._closePanel();
    this._panelRoom = room;
    const back = document.createElement("div");
    back.className = "nfpanel-back";
    back.innerHTML =
      '<style>' + NeonFloorplanCard.PANEL_CSS + '</style>' +
      '<div class="nfpanel">' +
        '<div class="nfphead"><span class="nfptitle"></span>' +
          '<button class="nfpx" title="Close">&times;</button></div>' +
        '<div class="nfpall">' +
          '<button class="nfpbtn on" data-all="on">All on</button>' +
          '<button class="nfpbtn" data-all="off">All off</button>' +
        '</div>' +
        '<div class="nfprows"></div>' +
      '</div>';
    back.addEventListener("pointerup", e => { if (e.target === back) this._closePanel(); });
    back.querySelector(".nfpx").addEventListener("pointerup", () => this._closePanel());
    back.querySelectorAll("[data-all]").forEach(b =>
      b.addEventListener("pointerup", () => {
        const ents = this._roomLights(this._panelRoom);
        this._hass.callService("homeassistant",
          b.dataset.all === "on" ? "turn_on" : "turn_off", { entity_id: ents });
      }));
    document.body.appendChild(back);
    this._panel = back;
    this._esc = e => { if (e.key === "Escape") this._closePanel(); };
    window.addEventListener("keydown", this._esc);
    this._paintPanel();
  }

  _closePanel() {
    window.removeEventListener("keydown", this._esc);
    if (this._panel) this._panel.remove();
    this._panel = null;
    this._panelRoom = null;
  }

  _paintPanel() {
    if (!this._panel || !this._hass) return;
    const room = this._panelRoom;
    const ents = this._roomLights(room);
    const on = ents.filter(e => this._hass.states[e].state === "on").length;
    this._panel.querySelector(".nfptitle").textContent =
      room.toUpperCase() + " · " + (on ? on + " of " + ents.length + " on" : "all off");
    const rows = this._panel.querySelector(".nfprows");
    const html = ents.map(e => {
      const s = this._hass.states[e];
      const lit = s.state === "on";
      const name = (s.attributes.friendly_name || e.split(".")[1].replace(/_/g, " "))
        .replace(new RegExp("^" + room + "\\s*", "i"), "");
      const dim = e.startsWith("light.") && s.attributes.brightness != null;
      const pct = dim ? Math.round(s.attributes.brightness / 2.55) : 0;
      return '<div class="nfprow' + (lit ? " lit" : "") + '" data-e="' + e + '">' +
        '<div class="nfptop">' +
          '<span class="nfpdot"></span>' +
          '<span class="nfpname">' + name + '</span>' +
          '<button class="nfptog' + (lit ? " lit" : "") + '" data-t="' + e + '">' +
            (lit ? "ON" : "OFF") + '</button>' +
        '</div>' +
        (dim ? '<div class="nfpdim"><input type="range" min="1" max="100" value="' + pct +
               '" data-b="' + e + '"><span class="nfppct">' + pct + '%</span></div>' : "") +
        '</div>';
    }).join("");
    // only rebuild when the shape changed, so a slider drag isn't yanked away
    if (rows.dataset.sig !== html.replace(/value="\d+"/g, "")) {
      rows.innerHTML = html;
      rows.dataset.sig = html.replace(/value="\d+"/g, "");
      rows.querySelectorAll("[data-t]").forEach(b =>
        b.addEventListener("pointerup", ev => {
          ev.stopPropagation();
          this._hass.callService("homeassistant", "toggle", { entity_id: b.dataset.t });
        }));
      rows.querySelectorAll("[data-b]").forEach(sl => {
        sl.addEventListener("input", () =>
          sl.parentElement.querySelector(".nfppct").textContent = sl.value + "%");
        sl.addEventListener("change", () =>
          this._hass.callService("light", "turn_on",
            { entity_id: sl.dataset.b, brightness_pct: Number(sl.value) }));
      });
    } else {
      rows.querySelectorAll("[data-b]").forEach(sl => {
        if (document.activeElement !== sl) {
          const s = this._hass.states[sl.dataset.b];
          const pct = s.attributes.brightness != null ? Math.round(s.attributes.brightness / 2.55) : 0;
          sl.value = pct;
          sl.parentElement.querySelector(".nfppct").textContent = pct + "%";
        }
      });
      rows.querySelectorAll(".nfprow").forEach(r => {
        const lit = this._hass.states[r.dataset.e].state === "on";
        r.classList.toggle("lit", lit);
        const b = r.querySelector(".nfptog");
        b.classList.toggle("lit", lit);
        b.textContent = lit ? "ON" : "OFF";
      });
    }
  }
}

NeonFloorplanCard.PANEL_CSS = [
  ".nfpanel-back{position:fixed;inset:0;z-index:99998;display:flex;align-items:center;",
  "justify-content:center;background:rgba(4,7,18,.78);backdrop-filter:blur(6px);",
  "-webkit-backdrop-filter:blur(6px);font-family:'Segoe UI',Roboto,sans-serif;}",
  ".nfpanel{width:min(94vw,430px);max-height:86vh;overflow-y:auto;padding:18px 18px 16px;",
  "border-radius:22px;background:rgba(10,16,38,.97);border:1px solid rgba(251,191,36,.45);",
  "box-shadow:0 0 40px rgba(251,191,36,.18),0 18px 50px rgba(0,0,0,.7);color:#eaf0fa;}",
  ".nfphead{display:flex;align-items:center;gap:10px;margin-bottom:12px;}",
  ".nfptitle{flex:1;font-size:14px;font-weight:900;letter-spacing:1px;color:#fde68a;",
  "text-shadow:0 0 10px rgba(251,191,36,.5);}",
  ".nfpx{background:none;border:none;color:#8195b5;font-size:26px;line-height:1;cursor:pointer;}",
  ".nfpall{display:flex;gap:9px;margin-bottom:12px;}",
  ".nfpbtn{flex:1;padding:10px 0;border-radius:12px;font-size:13px;font-weight:800;cursor:pointer;",
  "background:rgba(13,20,44,.9);border:1px solid rgba(34,211,238,.45);color:#7ee7f7;font-family:inherit;}",
  ".nfpbtn.on{border-color:rgba(251,191,36,.6);color:#fde68a;}",
  ".nfprow{padding:10px 12px;margin-bottom:8px;border-radius:14px;background:rgba(13,20,44,.8);",
  "border:1px solid rgba(96,165,250,.16);}",
  ".nfprow.lit{border-color:rgba(251,191,36,.5);box-shadow:0 0 14px rgba(251,191,36,.16);}",
  ".nfptop{display:flex;align-items:center;gap:10px;}",
  ".nfpdot{width:10px;height:10px;border-radius:50%;background:#334155;flex:none;}",
  ".nfprow.lit .nfpdot{background:#fbbf24;box-shadow:0 0 10px rgba(251,191,36,.9);}",
  ".nfpname{flex:1;font-size:15px;font-weight:700;text-transform:capitalize;",
  "white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}",
  ".nfptog{width:64px;padding:7px 0;border-radius:20px;font-size:12px;font-weight:900;",
  "cursor:pointer;background:rgba(2,6,23,.8);border:1px solid rgba(148,163,184,.4);",
  "color:#94a3b8;font-family:inherit;flex:none;}",
  ".nfptog.lit{background:rgba(251,191,36,.18);border-color:rgba(251,191,36,.75);color:#fde68a;",
  "box-shadow:0 0 12px rgba(251,191,36,.3);}",
  ".nfpdim{display:flex;align-items:center;gap:10px;margin:9px 2px 1px;}",
  ".nfpdim input{flex:1;accent-color:#fbbf24;height:22px;}",
  ".nfppct{width:42px;text-align:right;font-size:12px;font-weight:800;color:#fde68a;}",
].join("");

/* furniture dimensions — mirror of the editor's catalog */
NeonFloorplanCard.TYPES = {
  "Sofa": [0, 7, 3, 16], "Sectional L": [0, 9, 6.5, 16], "Loveseat": [0, 5, 3, 16],
  "Armchair": [0, 3, 3, 15], "Coffee table": [0, 4, 2, 9], "TV stand": [0, 6, 1.5, 11],
  "TV": [0, 5.5, 0.5, 26], "Bookshelf": [0, 3, 1, 34], "Rug": [0, 8, 5, 1.5],
  "Plant": [0, 1.5, 1.5, 22], "Piano": [0, 5, 2, 22], "Lamp": [0, 1.2, 1.2, 28],
  "Dining table": [0, 6, 3.5, 14], "Chair": [0, 1.5, 1.5, 14], "Island": [0, 6, 3, 17],
  "Counter": [0, 6, 2, 17], "Fridge": [0, 3, 2.5, 32], "Stove": [0, 2.5, 2.5, 17],
  "Bed (queen)": [0, 6.8, 5, 12], "Bed (twin)": [0, 6.5, 3.2, 12], "Dresser": [0, 5, 1.6, 16],
  "Nightstand": [0, 1.6, 1.6, 12], "Desk": [0, 5, 2.3, 14], "Office chair": [0, 2, 2, 16],
  "Toilet": [0, 1.6, 2.3, 14], "Tub": [0, 5, 2.5, 11], "Shower": [0, 3, 3, 30],
  "Vanity": [0, 4, 1.8, 16], "Washer": [0, 2.3, 2.3, 18], "Dryer": [0, 2.3, 2.3, 18],
  "Car": [0, 15, 6, 26], "Workbench": [0, 6, 2, 17], "Treadmill": [0, 6, 2.5, 24],
  "Weight rack": [0, 4, 2, 20], "Pool table": [0, 8, 4.5, 15], "Shelving": [0, 4, 1.5, 32],
};

customElements.define("neon-floorplan-card", NeonFloorplanCard);
window.customCards = window.customCards || [];
window.customCards.push({ type: "neon-floorplan-card", name: "Neon Floorplan", description: "Isometric night-house with live lights" });
