#!/usr/bin/env python3
"""Build neon_store.json: the live storage file with the neon restyle applied.

- home view root replaced with the freshly built layout_patch.json (weather
  cards carried over from the live root)
- every flow "Back to Home" button-card becomes a pinned bottom-left pill
- every view gets the bg_neon.svg background
- chores/gameday iframe cache-busters bumped so tablets reload the new CSS
"""
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V = int(time.time() * 1000)

store = json.load(open(os.path.join(HERE, "new_store.json"), encoding="utf-8"))
cfg = store["data"]["config"]
root = json.load(open(os.path.join(HERE, "layout_patch.json"), encoding="utf-8"))["root"]

# ---------------------------------------------------- weather splice from live
home = cfg["views"][0]
cur = home["cards"][0]                       # current horizontal-stack root
wrow = cur["cards"][1]["cards"][0]           # RIGHT -> weather row
hourly = wrow["cards"][0]["cards"]           # [hdr, weather]
weekly = wrow["cards"][1]["cards"]
nrow = root["cards"][1]["cards"][0]
nrow["cards"][0]["cards"] = [hourly[0], hourly[1]]
nrow["cards"][1]["cards"] = [weekly[0], weekly[1]]
home["cards"] = [root]

# neon-tune the carried-over weather cards: cyan glowing header icons, a
# transparent bar card (the grey glass predates the restyle), cyan-gradient bars
for hdr in (hourly[0], weekly[0]):
    hdr["styles"]["icon"] = [{"--mdc-icon-size": "32px"}, {"width": "32px"},
                             {"color": "#22d3ee"},
                             {"filter": "drop-shadow(0 0 6px rgba(34,211,238,0.9))"}]
    hdr["styles"]["card"] = [
        {"background": "linear-gradient(180deg, rgba(34,211,238,0.34), rgba(34,211,238,0.10))"},
        {"box-shadow": "0 8px 14px -8px rgba(34,211,238,0.8)"},
        {"border": "none"},
        {"border-bottom": "3px solid #22d3ee"},
        {"border-radius": "0"},
        {"height": "48px"}, {"padding": "4px"}]
    hdr["styles"]["name"] = [
        {"font-size": "22px"}, {"font-weight": "900"}, {"white-space": "nowrap"},
        {"color": "#eafcff"}, {"letter-spacing": "2px"}, {"text-transform": "uppercase"},
        {"text-shadow": "0 0 14px rgba(34,211,238,0.9)"}]
for st in hourly[1]["styles"]["card"]:
    if "background-color" in st:
        st["background-color"] = "transparent"
    if "border" in st:
        st["border"] = "none"
bars = hourly[1]["custom_fields"]["bars"]
bars = bars.replace(
    "background:linear-gradient(90deg,'+light+','+rgb(c)+');",
    "background:linear-gradient(90deg,#075985,#0ea5e9 55%,#22d3ee);"
    "box-shadow:0 0 8px rgba(34,211,238,0.35);")
bars = bars.replace("background:rgba(143,176,232,0.12);",
                    "background:rgba(255,255,255,0.07);")
hourly[1]["custom_fields"]["bars"] = bars

# ---------------------------------------------------- chores view: full-width panel
# The stock "sections" view squeezes the chores iframe into one ~400px column
# ("one big bulky column"). Panel mode hands the iframe the whole screen.
for v in cfg["views"]:
    if v.get("path") != "chores-view":
        continue
    v.pop("sections", None)
    v["type"] = "panel"
    v["cards"] = [{"type": "vertical-stack", "cards": [
        {"type": "iframe", "url": "/local/chores.html?v=%d" % V,
         "card_mod": {"style":
             "ha-card{height:calc(100vh - 10px)!important;border:none!important;"
             "background:transparent!important;border-radius:0!important;box-shadow:none!important;}"
             "#root{height:100%!important;padding-top:0!important;}"
             "iframe{height:100%!important;width:100%!important;}"}},
        {"type": "custom:button-card", "name": "Back to Home", "icon": "mdi:home",
         "tap_action": {"action": "navigate", "navigation_path": "/el-dashboardio/0"}},
    ]}]

# ---------------------------------------------------- pinned back-home pill
PENDING_PILL = {
    "type": "custom:button-card", "entity": "sensor.chores_pending",
    "icon": "mdi:alert-decagram",
    "name": "[[[ var n = parseInt(entity.state); if (!n) return 'CHORES TO FIX'; "
            "return n + ' CHORE' + (n === 1 ? '' : 'S') + ' TO FIX'; ]]]",
    "tap_action": {"action": "navigate", "navigation_path": "/el-dashboardio/chores-view"},
    "card_mod": {"style":
        "ha-card{position:fixed!important;left:12px!important;bottom:66px!important;"
        "right:auto!important;width:170px!important;height:44px!important;z-index:999;"
        "background:rgba(24,8,14,0.94)!important;"
        "border:1px solid rgba(244,63,94,0.75)!important;"
        "border-radius:22px!important;"
        "box-shadow:0 0 16px rgba(244,63,94,0.4),0 6px 16px rgba(0,0,0,0.55)!important;}"},
    "styles": {
        "card": [{"height": "44px"}, {"padding": "0"}],
        "grid": [{"grid-template-areas": '"i n"'},
                 {"grid-template-columns": "26px auto"},
                 {"justify-content": "center"}, {"align-items": "center"},
                 {"column-gap": "5px"}],
        "name": [{"color": "#ffb4c2"}, {"font-size": "12px"}, {"font-weight": "900"},
                 {"letter-spacing": "0.5px"},
                 {"text-shadow": "0 0 8px rgba(244,63,94,0.6)"}],
        "icon": [{"color": "#ffb4c2"}, {"--mdc-icon-size": "20px"},
                 {"filter": "drop-shadow(0 0 6px rgba(244,63,94,0.9))"}]},
}


def pinned(old):
    card = {
        "type": "custom:button-card", "name": "Back to Home", "icon": "mdi:home",
        "tap_action": {"action": "navigate", "navigation_path": "/el-dashboardio/0"},
        "card_mod": {"style":
            "ha-card{position:fixed!important;left:12px!important;bottom:12px!important;"
            "right:auto!important;width:170px!important;height:46px!important;z-index:999;"
            "background:rgba(13,20,44,0.94)!important;"
            "border:1px solid rgba(34,211,238,0.65)!important;"
            "border-radius:23px!important;"
            "box-shadow:0 0 16px rgba(34,211,238,0.35),0 6px 16px rgba(0,0,0,0.55)!important;}"},
        "styles": {
            "card": [{"height": "46px"}, {"padding": "0"}],
            "grid": [{"grid-template-areas": '"i n"'},
                     {"grid-template-columns": "28px auto"},
                     {"justify-content": "center"}, {"align-items": "center"},
                     {"column-gap": "5px"}],
            "name": [{"color": "#7ee7f7"}, {"font-size": "14px"}, {"font-weight": "800"},
                     {"text-shadow": "0 0 8px rgba(34,211,238,0.5)"}],
            "icon": [{"color": "#7ee7f7"}, {"--mdc-icon-size": "21px"}]},
    }
    stack = {"type": "vertical-stack", "cards": [
        {"type": "conditional",
         "conditions": [
             {"condition": "state", "entity": "sensor.chores_pending", "state_not": "0"},
             {"condition": "state", "entity": "sensor.chores_pending", "state_not": "unavailable"},
             {"condition": "state", "entity": "sensor.chores_pending", "state_not": "unknown"}],
         "card": PENDING_PILL},
        card,
    ]}
    if "grid_options" in old:
        stack["grid_options"] = old["grid_options"]
    return stack


hits = 0


def walk(node):
    global hits
    if isinstance(node, dict):
        for key in ("cards", "sections"):
            kids = node.get(key)
            if isinstance(kids, list):
                for i, ch in enumerate(kids):
                    if (isinstance(ch, dict) and ch.get("type") == "custom:button-card"
                            and "Back to Home" in str(ch.get("name", ""))):
                        kids[i] = pinned(ch)
                        hits += 1
                    else:
                        walk(ch)
        if "card" in node and isinstance(node["card"], dict):
            walk(node["card"])


for v in cfg["views"]:
    for key in ("cards", "sections"):
        kids = v.get(key)
        if isinstance(kids, list):
            for i, ch in enumerate(kids):
                if (isinstance(ch, dict) and ch.get("type") == "custom:button-card"
                        and "Back to Home" in str(ch.get("name", ""))):
                    kids[i] = pinned(ch)
                    hits += 1
                else:
                    walk(ch)

# ---------------------------------------------------- electricity: top-5 circuits
# Replaces the stale "Circuits" section with day/week/month leaderboards
# rendered by /local/emporia_top5.js (registered as a lovelace resource).
def _top5(period):
    return {"type": "custom:emporia-top5-card", "period": period,
            "grid_options": {"columns": "full", "rows": "auto"}}


for v in cfg["views"]:
    if v.get("path") != "electricity":
        continue
    for sec in v.get("sections", []):
        cards = sec.get("cards", [])
        if cards and cards[0].get("type") == "heading" and cards[0].get("heading") == "Circuits":
            sec["cards"] = [
                {"type": "heading", "heading": "Top Circuits", "heading_style": "title",
                 "icon": "mdi:podium-gold"},
                _top5("day"), _top5("week"), _top5("month"),
            ]

# ---------------------------------------------------- cameras: ring feeds
NEON_CAM_MOD = {"style":
    "ha-card{border:1px solid rgba(34,211,238,0.45)!important;border-radius:16px!important;"
    "box-shadow:0 0 14px rgba(34,211,238,0.25),0 8px 20px rgba(0,0,0,0.5)!important;overflow:hidden;}"}


def _cam_section(title, icon, cam, extras=()):
    return {"type": "grid", "cards": [
        {"type": "heading", "heading": title, "heading_style": "title", "icon": icon},
        {"type": "picture-entity", "entity": cam, "camera_image": cam,
         "camera_view": "auto", "tap_action": {"action": "more-info"},
         "card_mod": dict(NEON_CAM_MOD),
         "grid_options": {"columns": "full", "rows": 5}},
    ] + list(extras)}


for v in cfg["views"]:
    if v.get("path") != "cameras":
        continue
    secs = v.get("sections", [])
    printer = next((s for s in secs if s.get("cards")
                    and s["cards"][0].get("heading") == "3D Printer"), None)
    backs = [s for s in secs if s.get("cards") and any(
        c.get("type") == "vertical-stack" or "Back to Home" in str(c.get("name", ""))
        for c in s["cards"])]
    front = _cam_section("Front Door", "mdi:doorbell-video", "camera.front_door_live_view", [
        {"type": "tile", "entity": "sensor.front_door_last_activity", "name": "Last Activity"},
        {"type": "tile", "entity": "sensor.front_door_battery", "name": "Battery"},
    ])
    rear = _cam_section("Back of House", "mdi:cctv", "camera.back_of_house_live_view")
    yard = _cam_section("Front Yard", "mdi:grass", "camera.front_yard_wyze", [
        {"type": "tile", "entity": "binary_sensor.wyze_cam_front_porch_cam_motion", "name": "Motion"},
        {"type": "tile", "entity": "sensor.wyze_cam_front_porch_cam_signal", "name": "WiFi"},
    ])
    if printer:
        printer["cards"][0]["heading"] = "3D Printers"
        printer["cards"].extend([
            {"type": "picture-entity", "entity": "camera.x2d_chamber",
             "camera_image": "camera.x2d_chamber", "camera_view": "auto",
             "tap_action": {"action": "more-info"},
             "card_mod": dict(NEON_CAM_MOD),
             "grid_options": {"columns": "full", "rows": 5}},
            {"type": "tile", "entity": "sensor.x2d_20p6aj631801302_print_progress",
             "name": "Progress"},
            {"type": "tile", "entity": "sensor.x2d_20p6aj631801302_remaining_time",
             "name": "Time Left"},
        ])
    v["sections"] = [front, rear, yard] + ([printer] if printer else []) + backs

# ---------------------------------------------------- 3D printing view (X2D)
X2D = "x2d_20p6aj631801302"

PRINT_HERO_JS = """[[[
  var S = 'sensor.%s_';
  var st = states[S+'print_status'], pr = states[S+'print_progress'];
  var lay = states[S+'current_layer'], rem = states[S+'remaining_time'];
  var s = st ? String(st.state) : 'unknown';
  var printing = s === 'printing' || s === 'running' || s === 'prepare';
  var pct = pr && !isNaN(parseFloat(pr.state)) ? Math.round(parseFloat(pr.state)) : 0;
  var col = printing ? '#22c55e' : (s==='paused'||s==='failed') ? '#ef4444'
          : (s==='finish') ? '#22d3ee' : '#94a3b8';
  var m = rem && !isNaN(parseInt(rem.state)) ? parseInt(rem.state) : null;
  var tleft = m === null ? '' : (Math.floor(m/60) ? Math.floor(m/60)+'h ' : '') + (m%%60) + 'm remaining';
  var layer = lay && lay.state !== 'unavailable' ? 'Layer ' + lay.state : '';
  return '<div style="width:100%%;box-sizing:border-box;padding:6px 10px;text-align:left;">'
    + '<div style="display:flex;align-items:center;gap:12px;">'
    +   '<img src="/local/logos/bambu.ico" style="width:38px;height:38px;border-radius:9px;'
    +     'filter:drop-shadow(0 0 10px rgba(34,197,94,0.8));">'
    +   '<div><div style="font-size:20px;font-weight:900;color:#f8fafc;letter-spacing:0.5px;">Bambu X2D</div>'
    +   '<div style="font-size:11px;font-weight:900;letter-spacing:1.5px;color:'+col+';'
    +     'text-shadow:0 0 10px '+col+';">'+s.toUpperCase()+'</div></div>'
    +   '<div style="margin-left:auto;font-size:34px;font-weight:900;color:'+col+';'
    +     'text-shadow:0 0 16px '+col+';">'+(printing?pct+'%%':'')+'</div>'
    + '</div>'
    + '<div style="height:12px;border-radius:6px;background:rgba(0,0,0,0.4);margin-top:10px;overflow:hidden;">'
    +   '<div style="width:'+pct+'%%;height:100%%;border-radius:6px;'
    +     'background:linear-gradient(90deg,#065f46,#22c55e,#86efac);box-shadow:0 0 12px #22c55e;"></div>'
    + '</div>'
    + '<div style="display:flex;margin-top:7px;font-size:11.5px;font-weight:700;color:#cbd5e1;">'
    +   '<span>'+layer+'</span><span style="margin-left:auto;">'+tleft+'</span>'
    + '</div>'
    + '</div>';
]]]""" % X2D

PRINT_HERO = {
    "type": "custom:button-card", "entity": "sensor.%s_print_status" % X2D,
    "show_icon": False, "show_name": False, "show_state": False,
    "tap_action": {"action": "none"},
    "triggers_update": ["sensor.%s_print_progress" % X2D,
                       "sensor.%s_current_layer" % X2D,
                       "sensor.%s_remaining_time" % X2D],
    "custom_fields": {"m": PRINT_HERO_JS},
    "card_mod": {"style":
        "ha-card{pointer-events:auto!important;background:rgba(8,14,26,0.88)!important;"
        "border:1px solid rgba(34,197,94,0.55)!important;border-radius:16px!important;"
        "box-shadow:0 0 18px rgba(34,197,94,0.25),0 8px 20px rgba(0,0,0,0.5)!important;}"},
    "styles": {"card": [{"padding": "6px"}],
               "grid": [{"grid-template-areas": '"m"'}],
               "custom_fields": {"m": [{"width": "100%"}]}},
    "grid_options": {"columns": "full", "rows": 3},
}


def _x2d_tile(entity, name):
    return {"type": "tile", "entity": entity, "name": name}


PRINT_VIEW = {
    "title": "3D Printing", "path": "printing", "subview": True,
    "icon": "mdi:printer-3d", "theme": "YOUR_THEME", "type": "sections",
    "show_icon_and_title": True, "max_columns": 3,
    "sections": [
        {"type": "grid", "cards": [
            {"type": "heading", "heading": "Print Status", "heading_style": "title",
             "icon": "mdi:printer-3d"},
            PRINT_HERO,
            _x2d_tile("sensor.%s_remaining_time" % X2D, "Time Left"),
            _x2d_tile("sensor.%s_current_layer" % X2D, "Layer"),
        ]},
        {"type": "grid", "cards": [
            {"type": "heading", "heading": "Temperatures", "heading_style": "title",
             "icon": "mdi:thermometer"},
            _x2d_tile("sensor.%s_left_nozzle_temperature" % X2D, "Left Nozzle"),
            _x2d_tile("sensor.%s_right_nozzle_temperature" % X2D, "Right Nozzle"),
            _x2d_tile("sensor.%s_bed_temperature" % X2D, "Bed"),
            _x2d_tile("sensor.%s_chamber_temperature" % X2D, "Chamber"),
        ]},
        {"type": "grid", "cards": [
            {"type": "heading", "heading": "Camera & Controls", "heading_style": "title",
             "icon": "mdi:video"},
            {"type": "picture-entity", "entity": "camera.x2d_chamber",
             "camera_image": "camera.x2d_chamber", "camera_view": "auto",
             "tap_action": {"action": "more-info"},
             "card_mod": {"style":
                 "ha-card{border:1px solid rgba(34,197,94,0.5)!important;border-radius:16px!important;"
                 "box-shadow:0 0 14px rgba(34,197,94,0.25),0 8px 20px rgba(0,0,0,0.5)!important;overflow:hidden;}"},
             "grid_options": {"columns": "full", "rows": 5}},
            _x2d_tile("switch.%s_camera" % X2D, "Chamber Camera"),
            _x2d_tile("light.%s_chamber_light" % X2D, "Chamber Light"),
        ]},
        {"type": "grid", "cards": [pinned({})]},
    ],
}

cfg["views"] = [v for v in cfg["views"] if v.get("path") != "printing"]
cfg["views"].append(PRINT_VIEW)

# ---------------------------------------------------- say-it view: voice intents
# Panel, not sections: same iframe-squeeze lesson as the chores page.
VOICE_VIEW = {
    "title": "Say It", "path": "voice", "subview": True,
    "icon": "mdi:microphone", "theme": "YOUR_THEME", "type": "panel",
    "cards": [{"type": "vertical-stack", "cards": [
        {"type": "iframe", "url": "/local/voice.html?v=%d" % V,
         "card_mod": {"style":
             "ha-card{height:calc(100vh - 10px)!important;border:none!important;"
             "background:transparent!important;border-radius:0!important;box-shadow:none!important;}"
             "#root{height:100%!important;padding-top:0!important;}"
             "iframe{height:100%!important;width:100%!important;}"}},
        {"type": "custom:button-card", "name": "Back to Home", "icon": "mdi:home",
         "tap_action": {"action": "navigate", "navigation_path": "/el-dashboardio/0"}},
    ]}],
}

cfg["views"] = [v for v in cfg["views"] if v.get("path") != "voice"]
cfg["views"].append(VOICE_VIEW)

# ---------------------------------------------------- family map: big + neon
# The stock map card sits in a ~280px box. Panel mode plus an explicit height
# hands it the screen; the tile pane is inverted into a dark map so it belongs
# on a neon board instead of glowing white in the middle of it.
FAMILY = [("device_tracker.life360_dad", "Dad", "#a855f7"),
          ("device_tracker.life360_mom", "Mom", "#f472b6"),
          ("device_tracker.life360_ian", "Ian", "#22d3ee"),
          ("device_tracker.life360_evan", "Evan", "#22c55e"),
          ("device_tracker.life360_colin", "Colin", "#facc15")]

MAP_INNER = (
    "#map{background:#070b1c!important;}"
    ".leaflet-tile-pane{filter:invert(1) hue-rotate(185deg) brightness(0.72) "
    "contrast(1.22) saturate(0.55);}"
    ".leaflet-marker-icon{filter:drop-shadow(0 0 7px rgba(34,211,238,0.85));}"
    ".leaflet-bar a{background:#0d142c!important;color:#7ee7f7!important;"
    "border-color:rgba(34,211,238,0.35)!important;}"
    ".leaflet-control-attribution{background:rgba(7,11,28,0.65)!important;"
    "color:#5b6b8c!important;font-size:9px!important;}"
    ".leaflet-control-attribution a{color:#7ee7f7!important;}")


def neon_map(height):
    return {
        "type": "map", "entities": [e for e, _, _ in FAMILY], "auto_fit": True,
        "hours_to_show": 2, "theme_mode": "dark",
        "card_mod": {"style": {
            ".": "ha-card{height:%s!important;border:1px solid rgba(34,211,238,0.55)!important;"
                 "border-radius:18px!important;overflow:hidden!important;"
                 "background:#070b1c!important;"
                 "box-shadow:0 0 24px rgba(34,211,238,0.30),0 10px 30px rgba(0,0,0,0.55)!important;}"
                 % height,
            "ha-map$": MAP_INNER,
            "ha-card ha-map$": MAP_INNER}}}


def who_chip(entity, name, color):
    js = ("""[[[
  var s = states['%s'];
  var raw = s ? s.state : 'unknown';
  var loc = raw === 'home' ? 'Home' : (raw === 'not_home' ? 'Away'
            : raw.charAt(0).toUpperCase() + raw.slice(1));
  var away = raw !== 'home';
  var mins = s ? Math.round((Date.now() - new Date(s.last_changed).getTime()) / 60000) : 0;
  var ago = mins < 1 ? 'just now' : (mins < 60 ? mins + 'm' : (mins < 1440
            ? Math.round(mins / 60) + 'h' : Math.round(mins / 1440) + 'd'));
  var b = s && s.attributes.battery_level != null ? s.attributes.battery_level
          : (s && s.attributes.battery != null ? s.attributes.battery : null);
  return '<div style="display:flex;flex-direction:column;align-items:center;gap:2px;">'
   + '<div style="font-size:13px;font-weight:900;letter-spacing:.6px;color:%s;'
   + 'text-shadow:0 0 10px %s;">' + '%s'.toUpperCase() + '</div>'
   + '<div style="font-size:15px;font-weight:800;color:' + (away ? '#eaf0fa' : '#8ef2dd')
   + ';white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%%;">'
   + loc + '</div>'
   + '<div style="font-size:10.5px;font-weight:700;color:#8195b5;">' + ago
   + (b != null ? ' \\u00b7 ' + Math.round(b) + '%%' : '') + '</div>'
   + '</div>';
]]]""" % (entity, color, color, name))
    return {"type": "custom:button-card", "entity": entity,
            "show_icon": False, "show_name": False, "show_state": False,
            "tap_action": {"action": "more-info"},
            "custom_fields": {"w": js},
            "styles": {"card": [{"background": "rgba(13,20,44,0.82)"},
                                {"border": "1px solid %s55" % color},
                                {"border-radius": "14px"},
                                {"box-shadow": "0 0 14px %s33" % color},
                                {"height": "74px"}, {"padding": "6px 4px"},
                                {"margin": "0 3px"}],
                       "grid": [{"grid-template-areas": '"w"'},
                                {"grid-template-columns": "1fr"},
                                {"align-items": "center"}],
                       "custom_fields": {"w": [{"width": "100%"},
                                               {"white-space": "normal"}]}}}


FAMILY_CARDS = [
    {"type": "horizontal-stack", "cards": [who_chip(*p) for p in FAMILY]},
    neon_map("calc(100vh - 190px)"),
    pinned({}),
]

for v in cfg["views"]:
    if v.get("path") == "family-view":
        v.pop("sections", None)
        v["type"] = "panel"
        v["cards"] = [{"type": "vertical-stack", "cards": FAMILY_CARDS}]
    elif v.get("path") == "family-map":
        v["type"] = "panel"
        v["cards"] = [{"type": "vertical-stack",
                       "cards": [neon_map("calc(100vh - 80px)"), pinned({})]}]

# ---------------------------------------------------- lighting view: night-house
# Replaces the old isometric lighting page with the live neon floorplan card
# (renders the family's saved layout from the addon's /floorplan store).
for v in cfg["views"]:
    if v.get("path") != "lighting":
        continue
    v.pop("sections", None)
    v["type"] = "panel"
    # this injection runs after the back-button walk, so pin directly
    v["cards"] = [{"type": "vertical-stack", "cards": [
        {"type": "custom:neon-floorplan-card", "mode": "lighting"},
        pinned({}),
    ]}]

# ------------------------------------------------ entertainment view: media house
# Same floorplan card, entertainment mode: TVs/speakers per room, tap to toggle,
# tap a room for a media panel (on/off, play-pause, volume).
for v in cfg["views"]:
    if v.get("path") != "entertainment":
        continue
    v.pop("sections", None)
    v["type"] = "panel"
    v["cards"] = [{"type": "vertical-stack", "cards": [
        {"type": "custom:neon-floorplan-card", "mode": "entertainment"},
        pinned({}),
    ]}]

# ---------------------------------------------------- Remotes: Firemote per TV
# "Remotes" menu tile -> a picker of the TVs; tap one -> a subview with that
# TV's graphical Firemote remote. (Firemote card is a HACS resource.)
REMOTES = [
    # slug, label, entity, device_family, device_type, icon, kind
    # kind "firemote" = graphical Firemote (needs ADB or Roku).
    # kind "atv"      = button D-pad driven by the Android TV Remote (no ADB).
    ("screenedporch", "Screened Porch", "remote.travel_google_tv", "", "", "mdi:television", "atv"),
    ("familyroom", "Family Room TV", "media_player.android_tv_192_168_1_58", "chromecast", "chromecast-4k", "mdi:television", "firemote"),
    ("basement", "Basement Google TV", "remote.basement_google_tv", "", "", "mdi:television", "atv"),
    ("evan", "Evan's Room TV", "remote.evan_s_room_tv", "", "", "mdi:television", "atv"),
    ("backporch", "Back Porch (Roku)", "media_player.insignia_7303x_ffff", "roku", "roku-generic-tcl", "mdi:television-classic", "firemote"),
    ("masterbed", "Master Bedroom FireTV", "media_player.fire_tv_192_168_1_140", "amazon-fire", "fire_tv_stick_4k_max", "mdi:fire", "firemote"),
    ("guestoffice", "Guest Room / Office FireTV", "media_player.fire_tv_192_168_1_130", "amazon-fire", "fire_tv_stick_4k_max", "mdi:fire", "firemote"),
]


def _rbtn(entity, cmd, icon, color="#c4b5fd", name=None):
    """One Android TV Remote button (fires remote.send_command)."""
    b = {"type": "custom:button-card", "show_icon": not name, "show_name": bool(name),
         "icon": icon,
         "tap_action": {"action": "call-service", "service": "remote.send_command",
                        "service_data": {"entity_id": entity, "command": cmd}},
         "styles": {"card": [{"height": "58px"}, {"border-radius": "16px"}, {"margin": "4px"},
                             {"background-color": "rgba(13,20,44,0.92)"},
                             {"border": "1px solid rgba(168,85,247,0.4)"},
                             {"box-shadow": "0 0 10px rgba(168,85,247,0.18)"}],
                    "icon": [{"--mdc-icon-size": "27px"}, {"color": color}],
                    "name": [{"font-size": "16px"}, {"font-weight": "900"}, {"color": color}]}}
    if name:
        b["name"] = name
    return b


_BLANK = {"type": "custom:button-card", "tap_action": {"action": "none"},
          "styles": {"card": [{"background": "transparent"}, {"box-shadow": "none"},
                              {"border": "none"}, {"height": "58px"}, {"margin": "4px"}]}}


def atv_remote(entity):
    """A neon D-pad remote for an Android TV Remote entity (no ADB needed)."""
    hs = lambda cards: {"type": "horizontal-stack", "cards": cards}
    stack = {"type": "vertical-stack", "cards": [
        hs([dict(_BLANK), _rbtn(entity, "POWER", "mdi:power", "#fb7185"), dict(_BLANK)]),
        hs([_rbtn(entity, "BACK", "mdi:keyboard-return"),
            _rbtn(entity, "HOME", "mdi:home"),
            _rbtn(entity, "VOLUME_MUTE", "mdi:volume-mute")]),
        hs([dict(_BLANK), _rbtn(entity, "DPAD_UP", "mdi:chevron-up"), dict(_BLANK)]),
        hs([_rbtn(entity, "DPAD_LEFT", "mdi:chevron-left"),
            _rbtn(entity, "DPAD_CENTER", "mdi:circle-outline", "#fde047", "OK"),
            _rbtn(entity, "DPAD_RIGHT", "mdi:chevron-right")]),
        hs([dict(_BLANK), _rbtn(entity, "DPAD_DOWN", "mdi:chevron-down"), dict(_BLANK)]),
        hs([_rbtn(entity, "VOLUME_DOWN", "mdi:volume-minus"),
            _rbtn(entity, "MEDIA_PLAY_PAUSE", "mdi:play-pause"),
            _rbtn(entity, "VOLUME_UP", "mdi:volume-plus")]),
    ]}
    return {"type": "custom:vertical-stack-in-card", "cards": [stack],
            "card_mod": {"style": "ha-card{max-width:330px;margin:0 auto!important;"
                                  "background:transparent!important;border:none!important;"
                                  "box-shadow:none!important;}"}}


def _remote_btn(slug, label, icon):
    return {"type": "custom:button-card", "name": label, "icon": icon,
            "show_icon": True, "show_name": True,
            "tap_action": {"action": "navigate",
                           "navigation_path": "/el-dashboardio/remote-" + slug},
            "styles": {"card": [{"background-color": "rgba(13,20,44,0.85)"},
                                {"border": "1px solid rgba(168,85,247,0.5)"},
                                {"border-radius": "16px"},
                                {"box-shadow": "0 0 16px rgba(168,85,247,0.25)"},
                                {"height": "112px"}, {"margin": "6px"}, {"padding": "8px"}],
                       "name": [{"font-size": "15px"}, {"font-weight": "800"},
                                {"color": "#eaf0fa"}, {"white-space": "normal"},
                                {"line-height": "1.1"}, {"margin-top": "6px"}],
                       "icon": [{"--mdc-icon-size": "40px"}, {"color": "#c4b5fd"},
                                {"filter": "drop-shadow(0 0 8px rgba(168,85,247,0.8))"}]}}


REMOTES_VIEW = {
    "title": "Remotes", "path": "remotes", "subview": True, "icon": "mdi:remote",
    "theme": "YOUR_THEME", "type": "panel",
    "cards": [{"type": "vertical-stack", "cards": [
        {"type": "custom:button-card", "show_icon": True, "icon": "mdi:remote",
         "name": "TV REMOTES", "tap_action": {"action": "none"},
         "styles": {"card": [{"background": "transparent"}, {"box-shadow": "none"},
                             {"border": "none"}, {"padding": "6px 0 2px"}],
                    "name": [{"font-size": "18px"}, {"font-weight": "900"},
                             {"letter-spacing": "1.5px"}, {"color": "#d8b4fe"},
                             {"text-shadow": "0 0 10px rgba(168,85,247,0.6)"}],
                    "icon": [{"--mdc-icon-size": "26px"}, {"color": "#d8b4fe"}]}},
        {"type": "grid", "columns": 3, "square": False,
         "cards": [_remote_btn(r[0], r[1], r[5]) for r in REMOTES]},
        pinned({}),
    ]}],
}
cfg["views"] = [v for v in cfg["views"] if v.get("path") != "remotes"]
cfg["views"].append(REMOTES_VIEW)

for slug, label, entity, fam, dtype, _icon, kind in REMOTES:
    path = "remote-" + slug
    if kind == "atv":
        remote_card = atv_remote(entity)
    else:
        fire = {"type": "custom:firemote-card", "entity": entity,
                "device_family": fam, "device_type": dtype, "compatibility_mode": "default",
                "card_mod": {"style": "ha-card{background:transparent!important;"
                                      "border:none!important;box-shadow:none!important;}"}}
        # link the Android TV Remote companion (speeds up Google TV key sends)
        ATR = {"familyroom": "remote.family_room_tv"}
        if slug in ATR:
            fire["android_tv_remote_entity"] = ATR[slug]
        elif entity.startswith("remote."):
            fire["android_tv_remote_entity"] = entity
        remote_card = fire
    cfg["views"] = [v for v in cfg["views"] if v.get("path") != path]
    cfg["views"].append({
        "title": label, "path": path, "subview": True, "icon": "mdi:remote",
        "theme": "YOUR_THEME", "type": "panel",
        "cards": [{"type": "vertical-stack", "cards": [
            {"type": "custom:button-card", "name": label, "tap_action": {"action": "none"},
             "styles": {"card": [{"background": "transparent"}, {"box-shadow": "none"},
                                 {"border": "none"}, {"padding": "8px 0 2px"}],
                        "name": [{"font-size": "17px"}, {"font-weight": "900"},
                                 {"color": "#d8b4fe"}, {"letter-spacing": "1px"}]}},
            remote_card,
            {"type": "custom:button-card", "name": "Back to Remotes", "icon": "mdi:arrow-left",
             "tap_action": {"action": "navigate", "navigation_path": "/el-dashboardio/remotes"},
             "styles": {"card": [{"background-color": "rgba(13,20,44,0.9)"},
                                 {"border": "1px solid rgba(168,85,247,0.55)"},
                                 {"border-radius": "14px"}, {"height": "46px"},
                                 {"margin": "10px auto 0"}, {"max-width": "260px"}],
                        "name": [{"color": "#d8b4fe"}, {"font-size": "14px"}, {"font-weight": "800"}],
                        "icon": [{"color": "#d8b4fe"}, {"--mdc-icon-size": "20px"}]}},
        ]}],
    })

# ---------------------------------------------------- cameras: alarm.com link
for v in cfg["views"]:
    if v.get("path") != "cameras":
        continue
    for sec in v.get("sections", []):
        cards = sec.get("cards", [])
        if cards and cards[0].get("heading") == "3D Printer":
            cards.append({
                "type": "custom:button-card", "name": "Alarm.com Camera",
                "icon": "mdi:shield-home",
                "label": "vendor-locked → opens Alarm.com video",
                "show_label": True,
                "tap_action": {"action": "url",
                               "url_path": "https://www.alarm.com/web/system/video"},
                "card_mod": {"style":
                    "ha-card{background:rgba(8,14,26,0.88)!important;"
                    "border:1px solid rgba(244,63,94,0.5)!important;border-radius:14px!important;"
                    "box-shadow:0 0 12px rgba(244,63,94,0.2)!important;}"},
                "styles": {"card": [{"height": "64px"}, {"padding": "4px"}],
                           "grid": [{"grid-template-areas": '"i n" "i l"'},
                                    {"grid-template-columns": "44px 1fr"},
                                    {"align-items": "center"}],
                           "name": [{"font-size": "13px"}, {"font-weight": "800"},
                                    {"color": "#ffb4c2"}, {"justify-self": "start"}],
                           "label": [{"font-size": "10px"}, {"color": "#94a3b8"},
                                     {"justify-self": "start"}],
                           "icon": [{"color": "#f43f5e"}, {"--mdc-icon-size": "26px"}]},
                "grid_options": {"columns": "full", "rows": 2},
            })

# ---------------------------------------------------- backgrounds + cache-bust
BG = {"image": "/local/bg_neon.svg?v=%d" % V, "size": "cover",
      "alignment": "center", "repeat": "no-repeat", "attachment": "fixed",
      "opacity": 100}
for v in cfg["views"]:
    v["background"] = dict(BG)

blob = json.dumps(store, ensure_ascii=False)
import re
blob = re.sub(r"(chores\.html\?v=)\d+", r"\g<1>%d" % V, blob)
blob = re.sub(r"(gameday\.html\?team=\w+&v=)\d+", r"\g<1>%d" % V, blob)
blob = re.sub(r"(grocery\.html\?v=)\d+", r"\g<1>%d" % V, blob)
blob = re.sub(r"(dinners\.html\?v=)\d+", r"\g<1>%d" % V, blob)
# old navy frame colours on iframe wrapper cards -> neon navy/cyan
blob = blob.replace("#0f1626", "#0a1226")
blob = blob.replace("rgba(74,120,214,0.28)", "rgba(34,211,238,0.30)")

out = os.path.join(HERE, "neon_store.json")
with open(out, "w", encoding="utf-8") as f:
    f.write(blob)
print("wrote", out, os.path.getsize(out), "bytes;", hits, "back buttons pinned")
