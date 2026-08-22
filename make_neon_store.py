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
        {"type": "iframe", "url": "/local/chores.html?v=1",
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
        {"type": "custom:neon-floorplan-card"},
        pinned({}),
    ]}]

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
