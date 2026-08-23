#!/usr/bin/env python3
"""Build phone_cfg.json: a tight, finger-friendly phone dashboard (url_path 'phone').

Home = a full-bleed 2x2 grid of big tiles (Remotes / Chores / Say It / Schedule).
Each tile deep-links to a panel subview:
  - remotes  : the TV picker + per-TV Firemote / D-pad remotes (same as the tablet)
  - chores   : /local/chores.html full screen
  - say it   : /local/voice.html full screen (mic works in the app WebView)
  - schedule : native calendar card (Cozi family + others), agenda list view

Everything navigates within /phone so it stays self-contained. Firemote /
button-card / card-mod / vertical-stack-in-card are global lovelace resources,
so they resolve on this dashboard too.

Output is just the lovelace config ({"views":[...]}) for lovelace/config/save.
"""
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V = int(time.time() * 1000)
DASH = "el-phone"       # url_path (HA requires a hyphen)
NP = "/%s/" % DASH      # navigation prefix

BG = {"image": "/local/bg_neon.svg?v=%d" % V, "size": "cover",
      "alignment": "center", "repeat": "no-repeat", "attachment": "fixed",
      "opacity": 100}

# ------------------------------------------------------------------ remotes data
REMOTES = [
    # slug, label, entity, device_family, device_type, icon, kind
    ("screenedporch", "Screened Porch", "remote.travel_google_tv", "", "", "mdi:television", "atv"),
    ("familyroom", "Family Room TV", "media_player.android_tv_192_168_1_58", "chromecast", "chromecast-4k", "mdi:television", "firemote"),
    ("workout", "Workout Room TV", "media_player.android_tv_192_168_1_178", "chromecast", "chromecast-4k", "mdi:dumbbell", "firemote"),
    ("basement", "Basement Google TV", "media_player.android_tv_192_168_1_91", "chromecast", "chromecast-4k", "mdi:television", "firemote"),
    ("evan", "Evan's Room TV", "media_player.android_tv_192_168_1_84", "chromecast", "chromecast-4k", "mdi:television", "firemote"),
    ("backporch", "Back Porch (Roku)", "media_player.insignia_7303x_ffff", "roku", "roku-generic-tcl", "mdi:television-classic", "firemote"),
    ("masterbed", "Master Bedroom FireTV", "media_player.fire_tv_192_168_1_140", "amazon-fire", "fire_tv_stick_4k_max", "mdi:fire", "firemote"),
    ("guestoffice", "Guest Room / Office FireTV", "media_player.fire_tv_192_168_1_130", "amazon-fire", "fire_tv_stick_4k_max", "mdi:fire", "firemote"),
]

# schedule calendars (Cozi family first, then household + the kids' football)
CALENDARS = [
    "calendar.the_family_cozi",
    "calendar.family",
    "calendar.dad",
    "calendar.kids_football_games",
]

# ------------------------------------------------------------------ home tiles
def big_tile(label, icon, path, color, glow):
    """One large finger-target that fills half the screen width and height."""
    return {
        "type": "custom:button-card", "name": label, "icon": icon,
        "show_icon": True, "show_name": True,
        "tap_action": {"action": "navigate", "navigation_path": NP + path},
        "styles": {
            "card": [{"height": "calc((100vh - 96px) / 2)"}, {"margin": "5px"},
                     {"border-radius": "26px"},
                     {"background": "linear-gradient(160deg, rgba(13,20,44,0.96), rgba(8,12,28,0.96))"},
                     {"border": "1.5px solid %s" % glow},
                     {"box-shadow": "0 0 22px %s, inset 0 0 30px rgba(0,0,0,0.5)" % color}],
            "grid": [{"grid-template-areas": '"i" "n"'},
                     {"grid-template-rows": "1fr auto"},
                     {"align-items": "center"}, {"justify-items": "center"},
                     {"row-gap": "6px"}, {"padding-bottom": "16px"}],
            "icon": [{"--mdc-icon-size": "84px"}, {"color": color},
                     {"filter": "drop-shadow(0 0 16px %s)" % glow}],
            "name": [{"font-size": "23px"}, {"font-weight": "900"},
                     {"letter-spacing": "1.5px"}, {"text-transform": "uppercase"},
                     {"color": "#eaf0fa"}, {"text-shadow": "0 0 12px %s" % color}],
        },
    }


HOME_VIEW = {
    "title": "Home", "path": "home", "icon": "mdi:cellphone",
    "theme": "YOUR_THEME", "type": "panel", "background": dict(BG),
    "cards": [{"type": "vertical-stack", "cards": [
        {"type": "horizontal-stack", "cards": [
            big_tile("Remotes", "mdi:remote", "remotes", "#c4b5fd", "rgba(168,85,247,0.55)"),
            big_tile("Chores", "mdi:broom", "chores", "#fb7185", "rgba(244,63,94,0.55)"),
        ]},
        {"type": "horizontal-stack", "cards": [
            big_tile("Say It", "mdi:microphone", "say-it", "#22d3ee", "rgba(34,211,238,0.55)"),
            big_tile("Schedule", "mdi:calendar-month", "schedule", "#22c55e", "rgba(34,197,94,0.55)"),
        ]},
    ]}],
}

# ------------------------------------------------------------------ back button
def back_home(color="#7ee7f7", glow="rgba(34,211,238,0.55)"):
    return {
        "type": "custom:button-card", "name": "Home", "icon": "mdi:home",
        "tap_action": {"action": "navigate", "navigation_path": NP + "home"},
        "card_mod": {"style":
            "ha-card{position:fixed!important;left:50%%!important;"
            "transform:translateX(-50%%)!important;bottom:14px!important;"
            "width:150px!important;height:48px!important;z-index:999;"
            "background:rgba(13,20,44,0.95)!important;"
            "border:1px solid %s!important;border-radius:24px!important;"
            "box-shadow:0 0 16px %s,0 6px 16px rgba(0,0,0,0.55)!important;}" % (glow, glow)},
        "styles": {
            "card": [{"height": "48px"}, {"padding": "0"}],
            "grid": [{"grid-template-areas": '"i n"'},
                     {"grid-template-columns": "28px auto"},
                     {"justify-content": "center"}, {"align-items": "center"},
                     {"column-gap": "6px"}],
            "name": [{"color": color}, {"font-size": "15px"}, {"font-weight": "800"},
                     {"text-shadow": "0 0 8px %s" % glow}],
            "icon": [{"color": color}, {"--mdc-icon-size": "22px"}]},
    }


def iframe_view(title, path, url, icon):
    return {
        "title": title, "path": path, "subview": True, "icon": icon,
        "theme": "YOUR_THEME", "type": "panel", "background": dict(BG),
        "cards": [{"type": "vertical-stack", "cards": [
            {"type": "iframe", "url": url,
             "card_mod": {"style":
                 "ha-card{height:calc(100vh - 8px)!important;border:none!important;"
                 "background:transparent!important;border-radius:0!important;box-shadow:none!important;}"
                 "#root{height:100%!important;padding-top:0!important;}"
                 "iframe{height:100%!important;width:100%!important;}"}},
            back_home(),
        ]}],
    }


# ------------------------------------------------------------------ schedule view
SCHEDULE_VIEW = {
    "title": "Schedule", "path": "schedule", "subview": True,
    "icon": "mdi:calendar-month", "theme": "YOUR_THEME", "type": "panel",
    "background": dict(BG),
    "cards": [{"type": "vertical-stack", "cards": [
        {"type": "calendar", "initial_view": "listWeek", "entities": CALENDARS,
         "card_mod": {"style":
             "ha-card{height:calc(100vh - 78px)!important;overflow:auto!important;"
             "background:rgba(8,12,28,0.9)!important;"
             "border:1px solid rgba(34,197,94,0.5)!important;border-radius:18px!important;"
             "box-shadow:0 0 20px rgba(34,197,94,0.25)!important;margin:6px!important;}"}},
        back_home("#86efac", "rgba(34,197,94,0.55)"),
    ]}],
}

# ------------------------------------------------------------------ remotes views
def _rbtn(entity, cmd, icon, color="#c4b5fd", name=None):
    b = {"type": "custom:button-card", "show_icon": not name, "show_name": bool(name),
         "icon": icon,
         "tap_action": {"action": "call-service", "service": "remote.send_command",
                        "service_data": {"entity_id": entity, "command": cmd}},
         "styles": {"card": [{"height": "62px"}, {"border-radius": "16px"}, {"margin": "4px"},
                             {"background-color": "rgba(13,20,44,0.92)"},
                             {"border": "1px solid rgba(168,85,247,0.4)"},
                             {"box-shadow": "0 0 10px rgba(168,85,247,0.18)"}],
                    "icon": [{"--mdc-icon-size": "29px"}, {"color": color}],
                    "name": [{"font-size": "17px"}, {"font-weight": "900"}, {"color": color}]}}
    if name:
        b["name"] = name
    return b


_BLANK = {"type": "custom:button-card", "tap_action": {"action": "none"},
          "styles": {"card": [{"background": "transparent"}, {"box-shadow": "none"},
                              {"border": "none"}, {"height": "62px"}, {"margin": "4px"}]}}


def atv_remote(entity):
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
            "card_mod": {"style": "ha-card{max-width:360px;margin:0 auto!important;"
                                  "background:transparent!important;border:none!important;"
                                  "box-shadow:none!important;}"}}


def _remote_btn(slug, label, icon):
    return {"type": "custom:button-card", "name": label, "icon": icon,
            "show_icon": True, "show_name": True,
            "tap_action": {"action": "navigate", "navigation_path": NP + "remote-" + slug},
            "styles": {"card": [{"background-color": "rgba(13,20,44,0.85)"},
                                {"border": "1px solid rgba(168,85,247,0.5)"},
                                {"border-radius": "18px"},
                                {"box-shadow": "0 0 16px rgba(168,85,247,0.25)"},
                                {"height": "120px"}, {"margin": "5px"}, {"padding": "8px"}],
                       "name": [{"font-size": "14px"}, {"font-weight": "800"},
                                {"color": "#eaf0fa"}, {"white-space": "normal"},
                                {"line-height": "1.1"}, {"margin-top": "6px"}],
                       "icon": [{"--mdc-icon-size": "42px"}, {"color": "#c4b5fd"},
                                {"filter": "drop-shadow(0 0 8px rgba(168,85,247,0.8))"}]}}


REMOTES_VIEW = {
    "title": "Remotes", "path": "remotes", "subview": True, "icon": "mdi:remote",
    "theme": "YOUR_THEME", "type": "panel", "background": dict(BG),
    "cards": [{"type": "vertical-stack", "cards": [
        {"type": "custom:button-card", "show_icon": True, "icon": "mdi:remote",
         "name": "TV REMOTES", "tap_action": {"action": "none"},
         "styles": {"card": [{"background": "transparent"}, {"box-shadow": "none"},
                             {"border": "none"}, {"padding": "8px 0 4px"}],
                    "name": [{"font-size": "19px"}, {"font-weight": "900"},
                             {"letter-spacing": "1.5px"}, {"color": "#d8b4fe"},
                             {"text-shadow": "0 0 10px rgba(168,85,247,0.6)"}],
                    "icon": [{"--mdc-icon-size": "26px"}, {"color": "#d8b4fe"}]}},
        {"type": "grid", "columns": 2, "square": False,
         "cards": [_remote_btn(r[0], r[1], r[5]) for r in REMOTES]},
        back_home("#d8b4fe", "rgba(168,85,247,0.55)"),
    ]}],
}


def remote_subview(slug, label, entity, fam, dtype, kind):
    if kind == "atv":
        remote_card = atv_remote(entity)
    else:
        remote_card = {"type": "custom:firemote-card", "entity": entity,
                       "device_family": fam, "device_type": dtype,
                       "compatibility_mode": "default",
                       "card_mod": {"style": "ha-card{background:transparent!important;"
                                             "border:none!important;box-shadow:none!important;}"}}
        ATR = {"familyroom": "remote.family_room_tv"}
        if slug in ATR:
            remote_card["android_tv_remote_entity"] = ATR[slug]
        elif entity.startswith("remote."):
            remote_card["android_tv_remote_entity"] = entity
    return {
        "title": label, "path": "remote-" + slug, "subview": True, "icon": "mdi:remote",
        "theme": "YOUR_THEME", "type": "panel", "background": dict(BG),
        "cards": [{"type": "vertical-stack", "cards": [
            {"type": "custom:button-card", "name": label, "tap_action": {"action": "none"},
             "styles": {"card": [{"background": "transparent"}, {"box-shadow": "none"},
                                 {"border": "none"}, {"padding": "10px 0 2px"}],
                        "name": [{"font-size": "18px"}, {"font-weight": "900"},
                                 {"color": "#d8b4fe"}, {"letter-spacing": "1px"}]}},
            remote_card,
            {"type": "custom:button-card", "name": "Back to Remotes", "icon": "mdi:arrow-left",
             "tap_action": {"action": "navigate", "navigation_path": NP + "remotes"},
             "styles": {"card": [{"background-color": "rgba(13,20,44,0.9)"},
                                 {"border": "1px solid rgba(168,85,247,0.55)"},
                                 {"border-radius": "14px"}, {"height": "48px"},
                                 {"margin": "12px auto 0"}, {"max-width": "280px"}],
                        "name": [{"color": "#d8b4fe"}, {"font-size": "15px"}, {"font-weight": "800"}],
                        "icon": [{"color": "#d8b4fe"}, {"--mdc-icon-size": "20px"}]}},
        ]}],
    }


# ------------------------------------------------------------------ assemble
views = [
    HOME_VIEW,
    REMOTES_VIEW,
    iframe_view("Chores", "chores", "/local/chores.html?v=%d" % V, "mdi:broom"),
    iframe_view("Say It", "say-it", "/local/voice.html?v=%d" % V, "mdi:microphone"),
    SCHEDULE_VIEW,
]
for slug, label, entity, fam, dtype, _icon, kind in REMOTES:
    views.append(remote_subview(slug, label, entity, fam, dtype, kind))

config = {"views": views}

out = os.path.join(HERE, "phone_cfg.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False)
print("wrote", out, os.path.getsize(out), "bytes;", len(views), "views")
