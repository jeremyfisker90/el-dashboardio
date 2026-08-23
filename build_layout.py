#!/usr/bin/env python3
"""Rebuild the home view — neon glass v10 (mockup-matched).

Near-black glass tiles, per-button accent colors, glowing icons, gradient
washes. Layout unchanged: agenda rail left, compact column right. Weather
cards are spliced in by the store builder.
"""
import json
import os
import time

V = int(time.time() * 1000)

# design system (matched to the user's reference mockup)
TILE = "rgba(8,12,24,0.86)"            # tile body — near-opaque dark
INK = "#f8fafc"                         # primary text
CYAN = "#22d3ee"                        # weather / schedule accent
RED = "#ef4444"                         # dinners
BLUE = "#3b82f6"                        # family / electricity
YELLOW = "#facc15"                      # bus
PURPLE = "#a855f7"                      # grocery / entertainment
GREEN = "#22c55e"                       # cameras
PINKRED = "#f43f5e"                     # alarm
LBLUE = "#60a5fa"                       # lighting
TEAL = "#2dd4bf"                        # Ian
ORANGE = "#fb923c"                      # Evan
AMBER = "#fbbf24"                       # chores star

RAIL_PCT = 20
CHROME = 22


def bd(hexc, a):
    r, g, b = int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)
    return "rgba(%d,%d,%d,%s)" % (r, g, b, a)


def glow(hexc, spread="0.30"):
    return ("0 0 16px %s, 0 4px 14px rgba(0,0,0,0.6), "
            "inset 0 0 20px rgba(255,255,255,0.025)" % bd(hexc, spread))


def igl(hexc):
    return "drop-shadow(0 0 6px %s)" % bd(hexc, "0.9")


# ---------------------------------------------------------------- agenda rail
SCHEDULE_JS = """[[[
  const S = states['sensor.today_schedule'];
  const evs = (S && S.attributes.events) ? S.attributes.events : [];
  const NC = {Dad:'#a855f7', Mom:'#f472b6', Ian:'#2dd4bf', Evan:'#fbbf24',
              Colin:'#60a5fa', Family:'#94a3b8'};
  const LB = {Dad:'Dad', Mom:'Mom ❤️', Ian:'Ian', Evan:'Evan', Colin:'Colin', Family:'Family'};
  const who = function(e){ const m=((e.summary)||'').match(/^\\s*([A-Za-z]+)\\s*:/);
      if (m && NC[m[1]]) return m[1];
      if (e.cal === 'dad') return 'Dad';
      if (e.cal === 'ian') return 'Ian';
      return 'Family'; };
  const rga = function(h,a){ return 'rgba(' + parseInt(h.slice(1,3),16) + ','
      + parseInt(h.slice(3,5),16) + ',' + parseInt(h.slice(5,7),16) + ',' + a + ')'; };
  const esc = function(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/"/g,'&quot;'); };
  if (!evs.length) return '<div style="padding:14px;color:#9fb2d0;font-size:12px;">Nothing on the calendar.</div>';

  const sorted = evs.slice().sort(function(a,b){ return String(a.start).localeCompare(String(b.start)); });
  const today = new Date(); today.setHours(0,0,0,0);
  const groups = {};
  sorted.forEach(function(e){ const k = String(e.start).slice(0,10);
      (groups[k] = groups[k] || []).push(e); });

  let agenda = '';
  Object.keys(groups).sort().forEach(function(k){
    const d = new Date(k + 'T00:00:00');
    const diff = Math.round((d - today) / 86400000);
    if (diff < 0) return;
    const isToday = diff === 0;
    const label = isToday ? 'Today' : diff === 1 ? 'Tomorrow'
                : d.toLocaleDateString([], {weekday:'long'});
    const sub = d.toLocaleDateString([], {month:'short', day:'numeric'});
    const frame = isToday
      ? 'background:rgba(34,211,238,0.06);border:1px solid rgba(34,211,238,0.5);box-shadow:0 0 14px rgba(34,211,238,0.22);'
      : 'background:rgba(255,255,255,0.03);border:1px solid rgba(34,211,238,0.15);';
    agenda += '<div style="' + frame + 'border-radius:12px;padding:6px 7px 3px;margin-bottom:8px;">'
          +   '<div style="display:flex;align-items:baseline;gap:6px;">'
          +     '<span style="font-size:13px;font-weight:800;letter-spacing:0.4px;color:'
          +       (isToday ? '#7ee7f7' : '#a5c6f0')
          +       ';text-shadow:0 0 10px rgba(34,211,238,0.55);">' + label + '</span>'
          +     '<span style="font-size:10px;color:#8195b5;">' + sub + '</span>'
          +   '</div>'
          +   '<div style="height:2px;border-radius:2px;margin:3px 0 6px;'
          +     'background:linear-gradient(90deg,#22d3ee,rgba(34,211,238,0.04));"></div>';
    groups[k].forEach(function(e){
      const p = who(e);
      const c = NC[p] || '#94a3b8';
      const allday = (e.start && e.start.length <= 10);
      let tt = 'All day';
      if (!allday) { const s = new Date(e.start);
        tt = s.toLocaleTimeString([], {hour:'numeric', minute:'2-digit'}).replace(' ',''); }
      const title = (e.summary || '').replace(/^\\s*[A-Za-z]+:\\s*/, '');
      const end = (e.end && !allday) ? new Date(e.end) : null;
      const rng = tt + (end ? ' \\u2013 '
        + end.toLocaleTimeString([], {hour:'numeric', minute:'2-digit'}).replace(' ','') : '');
      const det = '<div class="evd" style="display:none;margin-top:4px;padding-top:4px;'
        + 'border-top:1px solid ' + rga(c,0.35) + ';">'
        + '<div style="font-size:11px;font-weight:700;color:#f2f6ff;line-height:1.3;">' + esc(title) + '</div>'
        + '<div style="font-size:10px;color:#cfe0ff;font-weight:700;">\\u23F0 ' + rng + '</div>'
        + (e.location ? '<div style="font-size:10px;color:#aebdd6;line-height:1.3;">\\uD83D\\uDCCD '
            + esc(String(e.location).slice(0,120)) + '</div>' : '')
        + (e.description ? '<div style="font-size:10px;color:#aebdd6;line-height:1.3;">'
            + esc(String(e.description).slice(0,220)) + '</div>' : '')
        + '</div>';
      // pointerup, NOT click: on touch screens button-card's action handler
      // swallows the synthetic click, and a pan gesture fires pointercancel
      // instead — so this toggles on taps only, mouse and finger alike.
      agenda += '<div onpointerup="var d=this.querySelector(\\'.evd\\');'
            +   'd.style.display=d.style.display===\\'block\\'?\\'none\\':\\'block\\';" '
            +   'style="cursor:pointer;margin-bottom:5px;'
            +   'background:linear-gradient(90deg,' + rga(c,0.20) + ',' + rga(c,0.03) + ');'
            +   'border-left:3px solid ' + c + ';border-radius:8px;padding:4px 5px 4px 6px;">'
            +   '<div style="display:flex;gap:7px;align-items:flex-start;">'
            +   '<span style="flex:none;width:48px;">'
            +     '<span style="display:block;font-size:10.5px;font-weight:800;color:' + c + ';'
            +       'text-shadow:0 0 8px ' + rga(c,0.6) + ';line-height:1.2;">' + tt + '</span>'
            +     '<span style="display:block;font-size:9px;font-weight:700;color:' + c + ';'
            +       'opacity:.85;line-height:1.2;">' + (LB[p] || p) + '</span>'
            +   '</span>'
            +   '<span style="flex:1;min-width:0;font-size:12px;font-weight:700;color:#f2f6ff;'
            +     'line-height:1.25;white-space:normal;overflow-wrap:anywhere;'
            +     'display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;'
            +     'max-height:30px;overflow:hidden;">' + title + '</span>'
            +   '</div>'
            +   det
            + '</div>';
    });
    agenda += '</div>';
  });
  return '<div id="agsc" style="text-align:left;height:calc(100vh - 96px);overflow-y:auto;'
    + 'touch-action:pan-y;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;'
    + 'padding-right:2px;">' + agenda + '</div>';
]]]"""

SCHEDULE_RAIL = {
    "type": "custom:vertical-stack-in-card",
    "card_mod": {"style":
        ":host{flex:0 0 %d%% !important;max-width:%d%% !important;margin-right:2px;}"
        "ha-card{background:%s!important;border:1px solid %s!important;"
        "border-radius:16px!important;box-shadow:%s!important;"
        "height:calc(100vh - %dpx)!important;overflow:hidden;position:relative;}"
        "ha-card::after{content:'';position:absolute;left:1px;right:1px;bottom:1px;"
        "height:26px;background:linear-gradient(180deg,rgba(8,12,24,0),rgba(8,12,24,0.92));"
        "pointer-events:none;border-radius:0 0 15px 15px;}"
        % (RAIL_PCT, RAIL_PCT, TILE, bd(CYAN, "0.45"), glow(CYAN), CHROME)},
    "cards": [
        {"type": "custom:button-card", "name": "Schedule", "icon": "mdi:calendar-month",
         "show_icon": True, "show_name": True, "tap_action": {"action": "none"},
         "styles": {
             "card": [{"background": "linear-gradient(180deg, rgba(34,211,238,0.34), rgba(34,211,238,0.10))"},
                      {"box-shadow": "0 8px 14px -8px rgba(34,211,238,0.8)"},
                      {"border": "none"},
                      {"border-bottom": "3px solid #22d3ee"},
                      {"border-radius": "0"},
                      {"height": "38px"}, {"padding": "4px 4px 0"}],
             "grid": [{"grid-template-areas": '"i n"'}, {"grid-template-columns": "26px auto"},
                      {"justify-content": "center"}, {"align-items": "center"},
                      {"column-gap": "7px"}],
             "name": [{"color": "#eafcff"}, {"font-size": "16px"}, {"font-weight": "900"},
                      {"letter-spacing": "2px"}, {"text-transform": "uppercase"},
                      {"text-shadow": "0 0 14px rgba(34,211,238,0.9)"}],
             "icon": [{"color": CYAN}, {"--mdc-icon-size": "20px"},
                      {"filter": igl(CYAN)}]}},
        {"type": "custom:button-card", "entity": "sensor.today_schedule",
         "show_icon": False, "show_name": False, "show_state": False,
         "tap_action": {"action": "none"},
         "custom_fields": {"agenda": SCHEDULE_JS},
         "card_mod": {"style":
             # tap_action "none" makes button-card set pointer-events:none on
             # ha-card, which kills the tappable rows AND touch scrolling —
             # force it back on (the card itself still does nothing on tap).
             "ha-card{touch-action:pan-y!important;pointer-events:auto!important;}"
             "#agsc::-webkit-scrollbar{width:4px;}"
             "#agsc::-webkit-scrollbar-thumb{background:rgba(34,211,238,0.35);border-radius:2px;}"
             "#agsc::-webkit-scrollbar-track{background:transparent;}"},
         "styles": {
             "card": [{"background": "none"}, {"box-shadow": "none"}, {"border": "none"},
                      {"padding": "0 6px 0 8px"},
                      {"height": "calc(100vh - %dpx)" % (CHROME + 48)},
                      {"overflow": "hidden"}, {"justify-content": "flex-start"}],
             "grid": [{"grid-template-areas": '"agenda"'}, {"align-content": "start"}],
             "custom_fields": {"agenda": [{"width": "100%"}, {"align-self": "start"}]}}},
    ],
}


# ---------------------------------------------------------------- right side
def nav(p):
    return {"action": "navigate", "navigation_path": "/el-dashboardio/" + p}


def quick(name, icon, tap, accent, icon_px=32, font=17, h=60):
    return {"type": "custom:button-card", "name": name, "icon": icon,
            "show_icon": True, "show_name": True, "tap_action": tap,
            "styles": {
                "card": [{"background": "linear-gradient(135deg, %s 0%%, %s 45%%, %s 100%%)"
                          % (bd(accent, "0.38"), bd(accent, "0.10"), TILE)},
                         {"border": "1px solid %s" % bd(accent, "0.70")},
                         {"border-radius": "14px"}, {"box-shadow": glow(accent, "0.32")},
                         {"height": "%dpx" % h}, {"margin": "0 3px 12px"}, {"padding": "0 4px"}],
                "grid": [{"grid-template-areas": '"i n"'},
                         {"grid-template-columns": "%dpx auto" % (icon_px + 4)},
                         {"justify-content": "center"}, {"align-items": "center"},
                         {"column-gap": "8px"}],
                "img_cell": [{"width": "%dpx" % icon_px}, {"height": "%dpx" % icon_px},
                             {"justify-content": "center"}],
                "icon": [{"color": accent}, {"--mdc-icon-size": "%dpx" % icon_px},
                         {"width": "%dpx" % icon_px}, {"filter": igl(accent)}],
                "name": [{"color": INK}, {"font-size": "%dpx" % font},
                         {"font-weight": "700"}, {"justify-self": "center"},
                         {"white-space": "normal"}, {"line-height": "1.05"}]}}


CHORES_JS = """[[[
  var a = states['sensor.chores_points'] ? states['sensor.chores_points'].attributes : null;
  var ian = a && a.ok ? a.ian : null, evan = a && a.ok ? a.evan : null;
  var tgt = a && a.target ? a.target : 100;
  var left = a ? (a.required_left || 0) : 0;
  var oreq = a ? (a.open_required || 0) : 0, oopt = a ? (a.open_optional || 0) : 0;
  var dIan = a ? (a.done_ian || 0) : 0, dEvan = a ? (a.done_evan || 0) : 0;
  var qIan = a ? (a.queued_ian || 0) : 0, qEvan = a ? (a.queued_evan || 0) : 0;
  var pts = a ? (a.pts_open || 0) : 0;
  var lead = (ian !== null && evan !== null && ian !== evan) ? (ian > evan ? 'ian' : 'evan') : null;
  function rg(h,a){ return 'rgba(' + parseInt(h.slice(1,3),16) + ',' + parseInt(h.slice(3,5),16)
    + ',' + parseInt(h.slice(5,7),16) + ',' + a + ')'; }
  function kid(id, nm, val, done, queued, col, grad){
    var pct = val === null ? 0 : Math.min(100, Math.round(val / tgt * 100));
    var isLead = lead === id;
    var crown = isLead ? '<span style="font-size:26px;line-height:1;'
      + 'filter:drop-shadow(0 0 8px rgba(250,204,21,0.9));">\\uD83D\\uDC51</span>' : '';
    var sk = a ? a.streak_kid : '', sw = a ? (a.streak_weeks || 0) : 0;
    var isLoser = lead !== null && !isLead;
    var parts = [];
    if (isLead) parts.push('<div style="font-size:10px;font-weight:900;letter-spacing:0.5px;color:#fde047;'
      + 'text-shadow:0 0 8px rgba(250,204,21,0.8);">\\uD83D\\uDC51 CURRENT LEADER</div>');
    if (isLoser) parts.push('<div style="font-size:9.5px;font-weight:900;letter-spacing:0.4px;color:#f9a8d4;'
      + 'text-shadow:0 0 8px rgba(244,114,182,0.8);">\\uD83C\\uDF38 A LITTLE LIGHT IN THE LOAFERS</div>');
    if (sk === id && sw > 0) parts.push('<div style="font-size:10px;font-weight:900;letter-spacing:0.5px;color:#ffb27a;'
      + 'text-shadow:0 0 8px rgba(251,146,60,0.8);">\\uD83D\\uDD25 ' + sw + '-WEEK WIN STREAK</div>');
    var ribbon = parts.length
      ? '<div style="position:absolute;top:5px;right:9px;text-align:right;line-height:1.3;">' + parts.join('') + '</div>'
      : '';
    return '<div style="flex:1;min-width:0;position:relative;'
      + 'background:linear-gradient(135deg,' + rg(col,0.62) + ',' + rg(col,0.38) + ' 70%,' + rg(col,0.15) + ') , #0a0f1e;'
      + 'border:2px solid ' + rg(col,0.9) + ';border-radius:12px;padding:19px 13px 9px;'
      + 'box-shadow:0 0 16px ' + rg(col,0.45) + ', inset 0 0 22px ' + rg(col,0.15) + ';">'
      + ribbon
      + '<div style="display:flex;align-items:baseline;gap:9px;">'
      +   '<span style="font-size:16px;font-weight:800;letter-spacing:0.6px;color:' + col + ';">' + nm + '</span>'
      +   crown
      +   '<span style="font-size:38px;font-weight:800;color:#fff;line-height:1;'
      +     'text-shadow:0 0 18px ' + col + ', 0 1px 3px rgba(0,0,0,0.9);">' + (val === null ? '--' : val) + '</span>'
      +   '<span style="font-size:14px;color:#e2e8f0;">/ ' + tgt + '</span>'
      + '</div>'
      + '<div style="height:12px;background:rgba(0,0,0,0.35);border-radius:6px;margin-top:7px;overflow:hidden;">'
      +   '<div style="width:' + pct + '%;height:100%;background:' + grad + ';border-radius:7px;'
      +     'box-shadow:0 0 12px ' + col + ';"></div>'
      + '</div>'
      + '<div style="margin-top:5px;display:flex;align-items:center;gap:6px;font-size:10.5px;font-weight:700;color:#e2e8f0;min-width:0;">'
      +   '<span style="flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
      +     done + ' done this week</span>'
      +   '<span style="flex:none;white-space:nowrap;font-size:10px;font-weight:900;'
      +     'color:' + (queued > 0 ? '#fff' : '#94a3b8') + ';'
      +     'background:' + rg(col, queued > 0 ? 0.45 : 0.18) + ';border:1px solid ' + rg(col,0.8) + ';'
      +     'border-radius:11px;padding:1px 7px;'
      +     (queued > 0 ? 'box-shadow:0 0 8px ' + rg(col,0.6) + ';' : '')
      +     '">\\uD83E\\uDDFA ' + queued + '</span>'
      + '</div>'
      + '</div>';
  }
  var badge = left > 0
    ? '<span style="display:inline-block;font-size:12px;font-weight:800;color:#ffb27a;'
      + 'background:rgba(251,146,60,0.16);border:1px solid rgba(251,146,60,0.55);'
      + 'border-radius:20px;padding:3px 11px;box-shadow:0 0 10px rgba(251,146,60,0.25);">'
      + left + ' REQUIRED LEFT</span>'
    : '<span style="display:inline-block;font-size:12px;font-weight:800;color:#5eead4;'
      + 'background:rgba(45,212,191,0.14);border:1px solid rgba(45,212,191,0.55);'
      + 'border-radius:20px;padding:3px 11px;box-shadow:0 0 10px rgba(45,212,191,0.25);">'
      + 'OPTIONAL UNLOCKED</span>';
  return '<div style="display:flex;align-items:center;gap:14px;width:100%;box-sizing:border-box;">'
    + '<div style="flex:none;max-width:225px;text-align:left;">'
    +   '<div style="display:flex;align-items:center;gap:11px;">'
    +     '<ha-icon icon="mdi:star" style="--mdc-icon-size:40px;color:#fde047;'
    +       'filter:drop-shadow(0 0 10px rgba(250,204,21,0.95));"></ha-icon>'
    +     '<span style="font-size:24px;font-weight:800;letter-spacing:1px;color:#f8fafc;'
    +       'text-shadow:0 0 14px rgba(251,191,36,0.5);">CHORES</span>'
    +   '</div>'
    +   '<div style="margin-top:7px;">' + badge + '</div>'
    +   '<div style="margin-top:6px;font-size:11px;color:#f1f5f9;font-weight:600;">'
    +     oreq + ' required \\u00b7 ' + oopt + ' optional on the board</div>'
    +   '<div style="margin-top:2px;font-size:11px;font-weight:800;color:#fde047;'
    +     'text-shadow:0 0 8px rgba(250,204,21,0.5);">' + pts + ' pts up for grabs</div>'
    + '</div>'
    + '<div style="flex:none;width:2px;align-self:stretch;margin:8px 0;'
    +   'background:linear-gradient(180deg,rgba(251,191,36,0),rgba(251,191,36,0.5),rgba(251,191,36,0));"></div>'
    + kid('ian', 'IAN', ian, dIan, qIan, '#2dd4bf', 'linear-gradient(90deg,#0d9488,#2dd4bf,#5eead4)')
    + kid('evan', 'EVAN', evan, dEvan, qEvan, '#fb923c', 'linear-gradient(90deg,#ea580c,#fb923c,#fdba74)')
    + '</div>';
]]]"""

MEAL_JS = """[[[
  var a = states['sensor.todays_dinner'] ? states['sensor.todays_dinner'].attributes : null;
  var meal = (a && a.meal) ? String(a.meal).trim() : null;
  if (meal === '') meal = null;
  var line = meal
    ? '<span style="display:block;font-size:12px;font-weight:800;color:#fecaca;text-align:center;'
      + 'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:210px;">Today\\'s dinner: ' + meal + '</span>'
    : '<span style="display:block;font-size:12px;font-weight:700;font-style:italic;color:#cbd5e1;text-align:center;">Open for ideas!</span>';
  return '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;width:100%;">'
    + '<div style="display:flex;align-items:center;justify-content:center;gap:8px;">'
    +   '<ha-icon icon="mdi:silverware-fork-knife" style="--mdc-icon-size:26px;color:#ef4444;'
    +     'filter:drop-shadow(0 0 6px rgba(239,68,68,0.9));"></ha-icon>'
    +   '<span style="font-size:15px;font-weight:700;color:#f8fafc;line-height:1.2;">Weekly Meal Plan</span>'
    + '</div>'
    + line
    + '</div>';
]]]"""

MEAL_TILE = {
    "type": "custom:button-card", "entity": "sensor.todays_dinner",
    "show_icon": False, "show_name": False, "show_state": False,
    "tap_action": nav("dinners-view"), "custom_fields": {"m": MEAL_JS},
    "styles": {"card": [{"background": "linear-gradient(135deg, %s 0%%, %s 45%%, %s 100%%)"
                         % (bd(RED, "0.38"), bd(RED, "0.10"), TILE)},
                        {"border": "1px solid %s" % bd(RED, "0.70")},
                        {"border-radius": "14px"}, {"box-shadow": glow(RED, "0.32")},
                        {"height": "60px"}, {"margin": "0 3px 12px"}, {"padding": "0 4px"}],
               "grid": [{"grid-template-areas": '"m"'}, {"grid-template-columns": "1fr"},
                        {"align-items": "center"}],
               "custom_fields": {"m": [{"width": "100%"}]}}}

LIFE_JS = """[[[
  var P = [
    ['device_tracker.life360_mom', 'Mom', '#f472b6'],
    ['device_tracker.life360_dad', 'Dad', '#a855f7'],
    ['device_tracker.life360_ian', 'Ian', '#2dd4bf'],
    ['device_tracker.life360_evan', 'Evan', '#fbbf24'],
    ['device_tracker.life360_colin', 'Colin', '#60a5fa']
  ];
  var chips = [];
  for (var i = 0; i < P.length; i++) {
    var st = states[P[i][0]];
    if (!st || !st.state || st.state === 'unavailable' || st.state === 'unknown') continue;
    var loc = st.state === 'home' ? 'Home' : st.state === 'not_home' ? 'Away'
            : st.state.charAt(0).toUpperCase() + st.state.slice(1);
    chips.push('<span style="white-space:nowrap;"><span style="color:' + P[i][2]
      + ';font-weight:800;">' + P[i][1] + ':</span> <span style="color:#e2e8f0;">'
      + loc + '</span></span>');
  }
  var line = chips.length
    ? chips.join('<span style="color:#64748b;"> \\u00b7 </span>')
    : '<span style="color:#94a3b8;font-style:italic;">no location data</span>';
  return '<div style="display:flex;align-items:center;gap:9px;width:100%;box-sizing:border-box;padding:0 7px;">'
    + '<ha-icon icon="mdi:account-group" style="--mdc-icon-size:24px;color:#3b82f6;flex:none;'
    +   'filter:drop-shadow(0 0 6px rgba(59,130,246,0.9));"></ha-icon>'
    + '<div style="flex:1;min-width:0;text-align:left;">'
    +   '<div style="font-size:14px;font-weight:700;color:#f8fafc;line-height:1.2;">Life 360</div>'
    +   '<div style="font-size:10px;font-weight:700;line-height:1.3;white-space:normal;'
    +     'overflow:hidden;max-height:27px;">' + line + '</div>'
    + '</div></div>';
]]]"""

LIFE_TILE = {
    "type": "custom:button-card", "entity": "device_tracker.life360_mom",
    "triggers_update": ["device_tracker.life360_mom", "device_tracker.life360_dad",
                        "device_tracker.life360_ian", "device_tracker.life360_evan",
                        "device_tracker.life360_colin"],
    "show_icon": False, "show_name": False, "show_state": False,
    "tap_action": nav("family-view"), "custom_fields": {"m": LIFE_JS},
    "styles": {"card": [{"background": "linear-gradient(135deg, %s 0%%, %s 45%%, %s 100%%)"
                         % (bd(BLUE, "0.38"), bd(BLUE, "0.10"), TILE)},
                        {"border": "1px solid %s" % bd(BLUE, "0.70")},
                        {"border-radius": "14px"}, {"box-shadow": glow(BLUE, "0.32")},
                        {"height": "60px"}, {"margin": "0 3px 12px"}, {"padding": "0 4px"}],
               "grid": [{"grid-template-areas": '"m"'}, {"grid-template-columns": "1fr"},
                        {"align-items": "center"}],
               "custom_fields": {"m": [{"width": "100%"}]}}}

CHAMP_JS = """[[[
  var a = states['sensor.chores_points'] ? states['sensor.chores_points'].attributes : null;
  var ti = a ? (a.total_ian || 0) : 0, te = a ? (a.total_evan || 0) : 0;
  var tw = a ? (a.total_weeks || 1) : 1;
  var champ = ti === te ? null : (ti > te ? 'ian' : 'evan');
  var champName = champ === 'ian' ? 'IAN' : champ === 'evan' ? 'EVAN' : 'TIED';
  var champCol = champ === 'ian' ? '#2dd4bf' : champ === 'evan' ? '#fb923c' : '#d8b4fe';
  var champPts = champ === 'evan' ? te : ti;
  var champNice = champ === 'ian' ? 'Ian' : champ === 'evan' ? 'Evan' : 'Tied';
  var otherName = champ === 'ian' ? 'EVAN' : 'IAN';
  var otherPts = champ === 'ian' ? te : ti;
  var streak = a ? (a.streak_weeks || 0) : 0;
  var streakKid = a ? a.streak_kid : null;
  var flame = (streak > 1 && streakKid === champ)
    ? '<span style="font-size:12px;filter:drop-shadow(0 0 6px rgba(251,146,60,.9));">\\uD83D\\uDD25 ' + streak + 'w</span>' : '';
  return '<style>'
    + '@keyframes champSheen{0%{background-position:200% center}100%{background-position:-200% center}}'
    + '@keyframes champCrown{0%,100%{transform:translateY(0) scale(1);filter:drop-shadow(0 0 9px rgba(250,204,21,.85))}'
    +   '50%{transform:translateY(-2px) scale(1.08);filter:drop-shadow(0 0 18px rgba(250,204,21,1))}}'
    + '.champGold{background:linear-gradient(100deg,#eab308 0%,#fde68a 22%,#fffbe6 38%,#fde047 50%,#fde68a 64%,#eab308 92%);'
    +   'background-size:220% auto;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;'
    +   'color:transparent;animation:champSheen 4.5s linear infinite;}'
    + '</style>'
    + '<div style="position:relative;width:100%;height:138px;overflow:hidden;border-radius:12px;">'
    + '<img src="/local/goat.jpg?v=1" style="position:absolute;left:0;top:0;width:100%;height:100%;'
    +   'object-fit:cover;object-position:center 30%;opacity:0.26;border-radius:12px;z-index:0;">'
    // warm gold vignette so the crest glows from the center
    + '<div style="position:absolute;inset:0;z-index:0;border-radius:12px;'
    +   'background:radial-gradient(120% 90% at 50% 40%, rgba(250,204,21,0.16), transparent 60%);'
    +   'box-shadow:inset 0 0 22px rgba(250,204,21,0.22);"></div>'
    + '<div style="position:relative;z-index:1;display:flex;flex-direction:column;justify-content:space-between;'
    + 'align-items:center;width:100%;height:100%;box-sizing:border-box;padding:6px 0 3px;">'
    + '<div class="champGold" style="font-family:UnifrakturMaguntia,Georgia,serif;font-size:24px;'
    +   'white-space:nowrap;line-height:1;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.95));">Grand Champion</div>'
    // gilded flourish divider
    + '<div style="display:flex;align-items:center;gap:5px;width:74%;margin:-1px 0;">'
    +   '<span style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(250,204,21,.85));"></span>'
    +   '<span style="color:#fde047;font-size:8px;line-height:1;filter:drop-shadow(0 0 4px rgba(250,204,21,.9));">\\u25C6</span>'
    +   '<span style="flex:1;height:1px;background:linear-gradient(90deg,rgba(250,204,21,.85),transparent);"></span>'
    + '</div>'
    // crown sits BEHIND the name as a backdrop, laurels flank it, name on top
    + '<div style="position:relative;display:flex;align-items:center;justify-content:center;'
    +   'width:100%;height:52px;">'
    +   '<span style="position:absolute;left:8px;top:50%;transform:translateY(-50%) scaleX(-1);'
    +     'font-size:24px;opacity:.75;z-index:0;filter:drop-shadow(0 0 6px rgba(250,204,21,.7));">\\uD83C\\uDF3F</span>'
    +   '<span style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);'
    +     'font-size:58px;line-height:1;opacity:.6;z-index:0;'
    +     'animation:champCrown 2.4s ease-in-out infinite;">\\uD83D\\uDC51</span>'
    +   '<span style="position:absolute;right:8px;top:50%;transform:translateY(-50%);'
    +     'font-size:26px;opacity:.8;z-index:0;filter:drop-shadow(0 0 6px rgba(250,204,21,.7));">\\uD83C\\uDF3F</span>'
    // solid bright gold — the animated gradient renders too dark on the tablet WebView
    +   '<span style="position:relative;z-index:1;font-family:Cinzel,Georgia,serif;'
    +     'font-weight:900;font-size:42px;line-height:1;letter-spacing:1px;color:#ffe14a;'
    +     'text-shadow:0 2px 8px rgba(0,0,0,1),0 0 10px rgba(250,204,21,.55),0 0 3px rgba(0,0,0,1);">'
    +     champNice + ' ' + champPts + '</span>'
    + '</div>'
    + '<div style="display:flex;justify-content:space-between;align-items:center;width:100%;padding:0 4px;">'
    +   '<span style="font-size:11px;font-weight:800;color:#f2d98c;white-space:nowrap;letter-spacing:.4px;">WEEK ' + tw + '</span>'
    +   flame
    +   '<span style="font-size:12.5px;font-weight:900;color:#fbbad6;white-space:nowrap;'
    +     'text-shadow:0 0 8px rgba(244,114,182,0.7);">\\uD83C\\uDF38 ' + otherName + ' ' + otherPts + '</span>'
    + '</div>'
    + '</div>'
    + '</div>';
]]]"""

CHAMP_TILE = {
    "type": "custom:button-card", "entity": "sensor.chores_points",
    "show_icon": False, "show_name": False, "show_state": False,
    "tap_action": nav("chores-view"), "custom_fields": {"m": CHAMP_JS},
    "card_mod": {"style":
        "@import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Cinzel:wght@700;800;900&display=swap');"
        ":host{flex:0 0 218px !important;max-width:218px !important;}"},
    "styles": {"card": [{"background-color": "rgba(8,12,24,0.9)"},
                        {"background-image": "linear-gradient(135deg, rgba(168,85,247,0.50) 0%, rgba(168,85,247,0.26) 75%, rgba(8,12,24,0.05) 100%)"},
                        {"border": "1px solid rgba(168,85,247,0.9)"},
                        {"border-radius": "16px"},
                        {"box-shadow": glow(PURPLE, "0.50")},
                        {"height": "150px"}, {"margin": "0 3px 12px"}, {"padding": "0 10px"}],
               "grid": [{"grid-template-areas": '"m"'}, {"grid-template-columns": "1fr"},
                        {"align-items": "center"}],
               "custom_fields": {"m": [{"width": "100%"}]}}}

CHORES_TILE = {
    "type": "custom:button-card", "entity": "sensor.chores_points",
    "show_icon": False, "show_name": False, "show_state": False,
    "tap_action": nav("chores-view"), "custom_fields": {"m": CHORES_JS},
    "card_mod": {"style": ":host{flex:1 1 auto !important;min-width:0 !important;}"},
    "styles": {"card": [{"background-color": "rgba(8,12,24,0.9)"},
                        {"background-image": "linear-gradient(135deg, rgba(250,204,21,0.46) 0%, rgba(253,224,71,0.28) 75%, rgba(8,12,24,0.05) 100%)"},
                        {"border": "1px solid rgba(250,204,21,0.85)"},
                        {"border-radius": "16px"},
                        {"box-shadow": glow(YELLOW, "0.45")},
                        {"height": "150px"}, {"margin": "0 3px 12px"}, {"padding": "0 18px"}],
               "grid": [{"grid-template-areas": '"m"'}, {"grid-template-columns": "1fr"},
                        {"align-items": "center"}],
               "custom_fields": {"m": [{"width": "100%"}]}}}

TEAMS = [
    ("bengals", "sensor.bengals_next_game", "BENGALS", "#fb4f14", "#ffd9c7",
     "linear-gradient(135deg, rgba(251,79,20,0.62) 0%, rgba(251,79,20,0.48) 75%, rgba(8,10,20,0.05) 100%)"),
    ("buckeyes", "sensor.buckeyes_next_game", "BUCKEYES", "#e11d2e", "#ffd2d2",
     "linear-gradient(135deg, rgba(190,0,30,0.80) 0%, rgba(150,0,25,0.62) 75%, rgba(10,8,24,0.05) 100%)"),
]


def tile_js(label, txt):
    return """[[[
  var a = entity ? entity.attributes : null;
  var TXT = '%s';
  var SH = '0 1px 3px rgba(0,0,0,0.95), 0 0 2px rgba(0,0,0,0.9)';
  if (!a || !a.has_game) return '<div style="display:flex;align-items:center;justify-content:center;height:100%%;color:#fff;font-size:11px;text-shadow:' + SH + ';">%s</div>';
  var d = a.kickoff_iso ? new Date(a.kickoff_iso) : null;
  var day = d ? d.toLocaleDateString([], {weekday:'short', month:'short', day:'numeric'}) : '';
  var tm = (d && a.time_valid !== false) ? d.toLocaleTimeString([], {hour:'numeric', minute:'2-digit'}) : 'TBD';
  var when = a.game_state === 'in' ? ('LIVE  ' + (a.score_us||0) + '-' + (a.score_them||0))
           : a.game_state === 'post' ? ('Final ' + (a.result||'') + ' ' + a.score_us + '-' + a.score_them)
           : (day + ' \\u00b7 ' + tm);
  var cd = '';
  if (a.game_state === 'in') { cd = 'LIVE NOW'; }
  else if (d && a.game_state === 'pre') {
    var t0 = new Date(); t0.setHours(0,0,0,0);
    var g0 = new Date(d); g0.setHours(0,0,0,0);
    var dd = Math.round((g0 - t0) / 86400000);
    cd = dd <= 0 ? 'TODAY' : dd === 1 ? 'TOMORROW' : 'IN ' + dd + ' DAYS';
  }
  var AT = '<span style="font-size:30px;font-weight:900;color:#fff;line-height:1;flex:none;'
    + 'text-shadow:0 0 14px ' + TXT + ', ' + SH + ';">@</span>';
  var hosting = a.home_away === 'home';
  var live = a.game_state === 'in';
  var whenLine = live
    ? '<div style="margin-top:1px;font-size:19px;font-weight:900;color:#fff;'
      + 'text-shadow:0 0 12px ' + TXT + ', ' + SH + ';white-space:nowrap;">'
      + '<span style="font-size:10px;font-weight:900;color:#fff;background:#dc2626;'
      +   'border-radius:12px;padding:2px 8px;margin-right:7px;vertical-align:middle;'
      +   'box-shadow:0 0 10px rgba(220,38,38,0.8);">LIVE</span>'
      + (a.us_abbr || '') + ' ' + (a.score_us || 0) + ' \\u2014 ' + (a.score_them || 0) + ' '
      + (a.opp_abbr || '') + '</div>'
    : '<div style="margin-top:1px;font-size:15px;font-weight:800;color:#fff;text-shadow:' + SH + ';white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + when + '</div>';
  return '<div style="display:flex;align-items:center;gap:8px;width:100%%;height:100%%;">'
    + (hosting ? AT : '')
    + '<img src="' + a.us_logo + '" style="width:64px;height:64px;flex:none;object-fit:contain;'
    +   'filter:drop-shadow(0 0 12px rgba(255,255,255,0.5));">'
    + '<span style="font-size:11px;font-weight:900;color:#fff;opacity:.65;flex:none;text-shadow:' + SH + ';">VS</span>'
    + (hosting ? '' : AT)
    + '<img src="' + a.opp_logo + '" style="width:54px;height:54px;flex:none;object-fit:contain;'
    +   'filter:drop-shadow(0 0 10px rgba(255,255,255,0.45));">'
    + '<div style="flex:1;min-width:0;text-align:left;margin-left:6px;">'
    +   '<div style="font-size:15px;font-weight:900;letter-spacing:0.6px;color:#fff;text-shadow:' + SH + ';'
    +     'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">%s '
    +     '<span style="font-size:11px;font-weight:800;opacity:.75;">' + a.vs_at + '</span> '
    +     (a.opponent_short || a.opp_abbr || '').toUpperCase() + '</div>'
    +   whenLine
    +   '<div style="font-size:10.5px;color:#fff;opacity:.8;text-shadow:' + SH + ';white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + (a.week_text || '') + (a.venue ? ' \\u00b7 ' + a.venue : '') + '</div>'
    +   '<div style="font-size:10.5px;color:' + TXT + ';text-shadow:' + SH + ';white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">\\uD83D\\uDCFA ' + (a.network || 'TBD') + '</div>'
    + '</div>'
    + '<div style="flex:none;display:flex;flex-direction:column;align-items:flex-end;gap:6px;">'
    +   '<span style="font-size:10px;font-weight:900;border-radius:20px;padding:3px 10px;color:#fff;background:rgba(0,0,0,0.45);border:1px solid rgba(255,255,255,0.6);text-shadow:' + SH + ';">'
    +     (a.home_away === 'home' ? 'HOME' : 'AWAY') + '</span>'
    +   (cd ? '<span style="font-size:12px;font-weight:900;letter-spacing:0.5px;color:#fff;text-shadow:0 0 10px ' + TXT + ', ' + SH + ';">' + cd + '</span>' : '')
    + '</div>'
    + '</div>';
]]]""" % (txt, label.title(), label)


def game_tile(slug, ent, label, accent, txt, grad):
    return {"type": "custom:button-card", "entity": ent, "show_icon": False,
            "show_name": False, "show_state": False, "tap_action": nav(slug + "-view"),
            "custom_fields": {"m": tile_js(label, txt)},
            "styles": {"card": [{"background-color": "rgba(8,12,24,0.9)"},
                                {"background-image": grad},
                                {"border": "1px solid %s" % bd(accent, "0.80")},
                                {"border-radius": "16px"},
                                {"box-shadow": glow(accent, "0.40")},
                                {"height": "104px"}, {"margin": "0 3px 12px"}, {"padding": "0 11px"}],
                       "grid": [{"grid-template-areas": '"m"'},
                                {"grid-template-columns": "1fr"}, {"align-items": "center"}],
                       "custom_fields": {"m": [{"width": "100%"}, {"height": "100%"}]}}}


LIGHT_MENU_JS = """[[[
  var on = 0, ks = Object.keys(states);
  for (var i = 0; i < ks.length; i++) {
    if (ks[i].indexOf('light.') === 0 && states[ks[i]].state === 'on') on++;
  }
  var line = on > 0
    ? '<span style="font-size:17px;font-weight:900;color:#fde047;text-shadow:0 0 10px rgba(250,204,21,0.7);">' + on + ' ON</span>'
    : '<span style="font-size:13px;font-weight:800;color:#94a3b8;">All off</span>';
  return '<div style="display:flex;align-items:center;gap:3px;width:100%;box-sizing:border-box;padding:0 3px;">'
    + '<div style="display:flex;flex-direction:column;align-items:center;flex:none;width:62px;">'
    +   '<ha-icon icon="mdi:lightbulb-group" style="--mdc-icon-size:27px;color:#60a5fa;'
    +     'filter:drop-shadow(0 0 6px rgba(96,165,250,0.9));"></ha-icon>'
    +   '<div style="font-size:10px;font-weight:700;color:#f8fafc;margin-top:2px;">Lighting</div>'
    + '</div>'
    + '<div style="flex:1;text-align:center;">' + line + '</div>'
    + '</div>';
]]]"""

THERMO_JS = """[[[
  var c = states['climate.nest_thermostat'];
  var w = states['weather.forecast_home_2'];
  var tin = c && c.attributes.current_temperature != null ? Math.round(c.attributes.current_temperature) : '--';
  var tout = w && w.attributes.temperature != null ? Math.round(w.attributes.temperature) : '--';
  var act = c ? (c.attributes.hvac_action || c.state || '') : '';
  var A = act === 'cooling' ? ['\\u2744\\uFE0F', 'COOLING', '#22d3ee']
        : act === 'heating' ? ['\\uD83D\\uDD25', 'HEATING', '#fb923c']
        : act === 'fan' ? ['\\uD83C\\uDF00', 'FAN', '#60a5fa']
        : ['', 'IDLE', '#94a3b8'];
  return '<div style="display:flex;align-items:center;gap:3px;width:100%;box-sizing:border-box;padding:0 3px;">'
    + '<div style="display:flex;flex-direction:column;align-items:center;flex:none;width:62px;">'
    +   '<ha-icon icon="mdi:thermostat" style="--mdc-icon-size:27px;color:#22d3ee;'
    +     'filter:drop-shadow(0 0 6px rgba(34,211,238,0.9));"></ha-icon>'
    +   '<div style="font-size:10px;font-weight:700;color:#f8fafc;margin-top:2px;">Thermostat</div>'
    + '</div>'
    + '<div style="flex:1;text-align:center;">'
    +   '<div style="font-size:12.5px;font-weight:800;color:#f8fafc;white-space:nowrap;">' + tin + '\\u00b0'
    +     '<span style="font-size:8.5px;color:#94a3b8;font-weight:700;"> IN</span>'
    +     ' <span style="color:#64748b;">\\u00b7</span> ' + tout + '\\u00b0'
    +     '<span style="font-size:8.5px;color:#94a3b8;font-weight:700;"> OUT</span></div>'
    +   '<div style="margin-top:2px;font-size:9.5px;font-weight:900;letter-spacing:0.8px;color:' + A[2] + ';'
    +     'text-shadow:0 0 8px ' + A[2] + ';">' + (A[0] ? A[0] + ' ' : '') + A[1] + '</div>'
    + '</div>'
    + '</div>';
]]]"""

ELEC_JS = """[[[
  var wv = parseFloat(entity && entity.state) || 0;
  var kw = (wv / 1000).toFixed(1) + ' kW';
  var col = wv < 5000 ? '#22c55e' : wv < 9000 ? '#facc15' : '#ef4444';
  var pct = Math.max(1, Math.min(99, wv / 12000 * 100));
  return '<div style="display:flex;align-items:center;gap:3px;width:100%;box-sizing:border-box;padding:0 3px;">'
    + '<div style="display:flex;flex-direction:column;align-items:center;flex:none;width:62px;">'
    +   '<ha-icon icon="mdi:flash" style="--mdc-icon-size:27px;color:#3b82f6;'
    +     'filter:drop-shadow(0 0 6px rgba(59,130,246,0.9));"></ha-icon>'
    +   '<div style="font-size:10px;font-weight:700;color:#f8fafc;margin-top:2px;">Electricity</div>'
    + '</div>'
    + '<div style="flex:1;">'
    +   '<div style="font-size:14px;font-weight:900;color:' + col + ';line-height:1;'
    +     'text-shadow:0 0 10px ' + col + ';text-align:center;">' + kw + '</div>'
    +   '<div style="position:relative;height:7px;width:100%;display:flex;margin-top:5px;">'
    +     '<div style="flex:41.7;background:rgba(34,197,94,0.75);border-radius:4px 0 0 4px;"></div>'
    +     '<div style="flex:33.3;background:rgba(250,204,21,0.75);"></div>'
    +     '<div style="flex:25;background:rgba(239,68,68,0.75);border-radius:0 4px 4px 0;"></div>'
    +     '<div style="position:absolute;left:' + pct + '%;top:-3px;width:3px;height:13px;'
    +       'background:#fff;border-radius:2px;box-shadow:0 0 6px #fff;transform:translateX(-50%);"></div>'
    +   '</div>'
    + '</div>'
    + '</div>';
]]]"""


PRINT3D_JS = """[[[
  var st = states['sensor.x2d_20p6aj631801302_print_status'];
  var pr = states['sensor.x2d_20p6aj631801302_print_progress'];
  var rem = states['sensor.x2d_20p6aj631801302_remaining_time'];
  var s = st ? String(st.state) : 'unknown';
  var printing = s === 'printing' || s === 'running' || s === 'prepare';
  var col = printing ? '#22c55e' : (s === 'paused' || s === 'failed') ? '#ef4444'
          : (s === 'finish') ? '#22d3ee' : '#94a3b8';
  var line1, line2 = '';
  if (printing){
    line1 = pr && !isNaN(parseFloat(pr.state)) ? Math.round(parseFloat(pr.state)) + '%' : 'PRINTING';
    var m = rem && !isNaN(parseInt(rem.state)) ? parseInt(rem.state) : null;
    if (m !== null) line2 = (Math.floor(m/60) ? Math.floor(m/60) + 'h ' : '') + (m % 60) + 'm left';
  } else {
    line1 = (s === 'unknown' || s === 'unavailable') ? 'OFFLINE' : s.toUpperCase();
  }
  return '<div style="display:flex;align-items:center;gap:3px;width:100%;box-sizing:border-box;padding:0 3px;">'
    + '<div style="display:flex;flex-direction:column;align-items:center;flex:none;width:62px;">'
    +   '<img src="/local/logos/bambu.ico" style="width:27px;height:27px;border-radius:7px;'
    +     'filter:drop-shadow(0 0 6px rgba(34,197,94,0.9));">'
    +   '<div style="font-size:10px;font-weight:700;color:#f8fafc;margin-top:2px;">3D Print</div>'
    + '</div>'
    + '<div style="flex:1;text-align:center;">'
    +   '<div style="font-size:14px;font-weight:900;color:' + col + ';line-height:1.1;'
    +     'text-shadow:0 0 10px ' + col + ';">' + line1 + '</div>'
    +   (line2 ? '<div style="margin-top:2px;font-size:9.5px;font-weight:800;color:#a7f3d0;">' + line2 + '</div>' : '')
    + '</div>'
    + '</div>';
]]]"""


def menu_live(js, path, accent, entity=None, triggers=None):
    card = {"type": "custom:button-card", "show_icon": False, "show_name": False,
            "show_state": False, "tap_action": nav(path), "custom_fields": {"m": js},
            "styles": {"card": [{"background-color": TILE},
                                {"border": "1px solid %s" % bd(accent, "0.35")},
                                {"border-radius": "14px"},
                                {"box-shadow": glow(accent, "0.24")},
                                {"height": "88px"}, {"padding": "4px 2px"}, {"margin": "0 3px"}],
                       "grid": [{"grid-template-areas": '"m"'},
                                {"grid-template-columns": "1fr"}, {"align-items": "center"}],
                       "custom_fields": {"m": [{"width": "100%"}]}}}
    if entity:
        card["entity"] = entity
    if triggers:
        card["triggers_update"] = triggers
    return card


def menu(name, icon, path, accent):
    return {"type": "custom:button-card", "name": name, "icon": icon,
            "show_icon": True, "show_name": True, "tap_action": nav(path),
            "styles": {"card": [{"background-color": TILE},
                                {"border": "1px solid %s" % bd(accent, "0.35")},
                                {"border-radius": "14px"},
                                {"box-shadow": glow(accent, "0.24")},
                                {"height": "88px"}, {"padding": "7px 2px"}, {"margin": "0 3px"}],
                       "name": [{"font-size": "12px"}, {"font-weight": "700"},
                                {"white-space": "normal"}, {"line-height": "1.05"},
                                {"color": INK}],
                       "icon": [{"--mdc-icon-size": "32px"}, {"color": accent},
                                {"filter": igl(accent)}]}}


def tile_wrap(cards):
    return {"type": "custom:vertical-stack-in-card",
            "card_mod": {"style":
                "ha-card{background:%s!important;border:1px solid %s!important;"
                "border-radius:16px!important;box-shadow:%s!important;"
                "overflow:hidden;margin:0 3px 12px!important;}"
                % (TILE, bd(CYAN, "0.45"), glow(CYAN, "0.24"))},
            "cards": cards}


ROWS = [
    {"type": "horizontal-stack", "cards": [
        tile_wrap(["__HOURLY_HDR__", "__HOURLY__"]),
        tile_wrap(["__WEEKLY_HDR__", "__WEEKLY__"]),
    ]},
    {"type": "horizontal-stack", "cards": [
        MEAL_TILE,
        LIFE_TILE,
        quick("Ian's Bus", "mdi:bus-school",
              {"action": "url",
               "url_path": "https://myridek12.tylerapp.com/buslocationmap/student/YOUR_STUDENT_ID"},
              YELLOW),
        quick("Cozi Shopping Lists", "mdi:cart", nav("grocery-view"), PURPLE),
    ]},
    {"type": "horizontal-stack", "cards": [CHORES_TILE, CHAMP_TILE]},
    {"type": "horizontal-stack", "cards": [game_tile(*t) for t in TEAMS]},
    {"type": "horizontal-stack", "cards": [
        menu_live(LIGHT_MENU_JS, "lighting", LBLUE, triggers="all"),
        menu("Remotes", "mdi:remote", "remotes", PURPLE),
        menu_live(THERMO_JS, "environment", CYAN,
                  entity="climate.nest_thermostat",
                  triggers=["climate.nest_thermostat", "weather.forecast_home_2"]),
        menu("Alarm", "mdi:shield-home", "alarm", PINKRED),
        menu_live(ELEC_JS, "electricity", BLUE,
                  entity="sensor.home_vue_power_minute_average"),
        menu("Cameras", "mdi:cctv", "cameras", GREEN),
        menu_live(PRINT3D_JS, "printing", GREEN,
                  entity="sensor.x2d_20p6aj631801302_print_status",
                  triggers=["sensor.x2d_20p6aj631801302_print_progress",
                            "sensor.x2d_20p6aj631801302_remaining_time"]),
        # opens its own listening popup rather than navigating away
        {"type": "custom:voice-mic-card", "name": "Say It"},
    ]},
]

RIGHT = {"type": "custom:vertical-stack-in-card",
         "card_mod": {"style": ":host{flex:1 1 auto !important;min-width:0 !important;}"
                               "ha-card{background:transparent!important;"
                               "box-shadow:none!important;border:none!important;"
                               "overflow:hidden!important;padding-right:8px!important;"
                               "box-sizing:border-box!important;}"},
         "cards": ROWS}

# horizontal-stack splits its children evenly, so flex-basis is how the rail gets
# its own share of the width instead of a straight 50/50.
ROOT = {"type": "horizontal-stack", "cards": [SCHEDULE_RAIL, RIGHT]}

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "layout_patch.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump({"root": ROOT}, f)
print("wrote", out, os.path.getsize(out), "bytes")
