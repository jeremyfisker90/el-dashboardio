"""Add the FireBoard cook tile to the home rail and a Cook view with the graph.

The tile reports the hottest live probe so the state is readable from across the
room, and it only lights up when meat is actually on - an idle smoker shouldn't
pull the eye. Tapping it opens the Cook view.

The graph is the point of the view, so it is conditional: ApexCharts renders
only while at least one probe is reading, and a quiet placeholder stands in the
rest of the time. A chart of six flat "unknown" lines is worse than no chart.

Patched against live storage; make_neon_store.py is behind the live dashboard.
"""
import io
import json
import os

CH = ['sensor.fireboard_channel_%d' % i for i in range(1, 7)]
CONN = 'binary_sensor.fireboard_connectivity'
NAV = '/el-dashboardio/cook-view'

# ---------------------------------------------------------------- home tile
# Mirrors the 3D-printer tile next to it: 88px card, logo column on the left,
# big state text on the right, colour carrying the status.
TILE_JS = """[[[
  var chans = ['1','2','3','4','5','6'];
  var temps = [];
  for (var i = 0; i < chans.length; i++){
    var s = states['sensor.fireboard_channel_' + chans[i]];
    if (s && !isNaN(parseFloat(s.state))) temps.push(parseFloat(s.state));
  }
  var conn = states['%s'];
  var online = conn && conn.state === 'on';
  var cooking = temps.length > 0;
  var col = cooking ? '#f97316' : (online ? '#94a3b8' : '#64748b');
  var line1, line2 = '';
  if (cooking){
    var hot = Math.round(Math.max.apply(null, temps));
    line1 = hot + '\\u00B0';
    line2 = temps.length + ' probe' + (temps.length === 1 ? '' : 's');
  } else {
    line1 = online ? 'IDLE' : 'OFFLINE';
  }
  return '<div style="display:flex;align-items:center;gap:3px;width:100%%;box-sizing:border-box;padding:0 3px;">'
    + '<div style="display:flex;flex-direction:column;align-items:center;flex:none;width:62px;">'
    +   '<ha-icon icon="mdi:grill" style="--mdc-icon-size:27px;color:' + col + ';'
    +     'filter:drop-shadow(0 0 6px ' + col + ');"></ha-icon>'
    +   '<div style="font-size:10px;font-weight:700;color:#f8fafc;margin-top:2px;">FireBoard</div>'
    + '</div>'
    + '<div style="flex:1;text-align:center;">'
    +   '<div style="font-size:14px;font-weight:900;color:' + col + ';line-height:1.1;'
    +     'text-shadow:0 0 10px ' + col + ';">' + line1 + '</div>'
    +   (line2 ? '<div style="font-size:10px;font-weight:700;color:#cbd5e1;margin-top:1px;">'
    +     line2 + '</div>' : '')
    + '</div>'
    + '</div>';
]]]""" % CONN

TILE = {
    "type": "custom:button-card",
    "entity": CONN,
    "show_icon": False,
    "show_name": False,
    "show_state": False,
    "tap_action": {"action": "navigate", "navigation_path": NAV},
    "custom_fields": {"m": TILE_JS},
    "styles": {
        "card": [
            {"background-color": "rgba(8,12,24,0.86)"},
            {"border": "1px solid rgba(249,115,22,0.35)"},
            {"border-radius": "14px"},
            {"box-shadow": "0 0 16px rgba(249,115,22,0.24), 0 4px 14px rgba(0,0,0,0.6),"
                           " inset 0 0 20px rgba(255,255,255,0.025)"},
            {"height": "88px"},
            {"padding": "4px 2px"},
            {"margin": "0 3px"},
        ],
        "grid": [
            {"grid-template-areas": '"m"'},
            {"grid-template-columns": "1fr"},
            {"align-items": "center"},
        ],
        "custom_fields": {"m": [{"width": "100%"}]},
    },
}

# ---------------------------------------------------------------- cook view
SERIES_COLORS = ['#f97316', '#ef4444', '#22d3ee', '#a3e635', '#e879f9', '#fbbf24']

GRAPH = {
    "type": "custom:apexcharts-card",
    "header": {"show": True, "title": "Probe Temperatures", "show_states": True,
               "colorize_states": True},
    "graph_span": "6h",
    "update_interval": "30s",
    "apex_config": {
        "chart": {"height": 340, "foreColor": "#cbd5e1",
                  "background": "transparent", "toolbar": {"show": False}},
        "stroke": {"curve": "smooth", "width": 3},
        "grid": {"borderColor": "rgba(148,163,184,0.18)"},
        "legend": {"show": True, "position": "bottom"},
        "tooltip": {"theme": "dark", "shared": True},
        "yaxis": {"decimalsInFloat": 0, "forceNiceScale": True},
    },
    "series": [
        {"entity": CH[i], "name": "Probe %d" % (i + 1), "color": SERIES_COLORS[i],
         "stroke_width": 3, "curve": "smooth", "group_by": {"func": "avg", "duration": "1min"}}
        for i in range(6)
    ],
    "card_mod": {"style":
        "ha-card{background:rgba(8,12,24,0.86)!important;"
        "border:1px solid rgba(249,115,22,0.40)!important;border-radius:16px!important;"
        "box-shadow:0 0 18px rgba(249,115,22,0.22),0 8px 20px rgba(0,0,0,0.55)!important;}"},
    "grid_options": {"columns": "full", "rows": 8},
}

IDLE_CARD = {
    "type": "markdown",
    "content": ("## No cook running\n\nPlug a probe into the FireBoard and the graph "
                "appears here automatically.\n\nConnectivity: "
                "{{ 'online' if is_state('" + CONN + "','on') else 'offline' }}"),
    "card_mod": {"style":
        "ha-card{background:rgba(8,12,24,0.70)!important;"
        "border:1px dashed rgba(148,163,184,0.35)!important;border-radius:16px!important;"
        "box-shadow:none!important;color:#94a3b8!important;}"},
    "grid_options": {"columns": "full", "rows": 4},
}

# The graph is worth nothing with every series unknown, so gate it on a probe
# actually reading. Both cards are conditional on the same template, inverted.
LIVE_TMPL = ("{{ expand('" + "','".join(CH) + "') "
             "| map(attribute='state') | select('is_number') | list | count > 0 }}")


LIVE_EXPR = LIVE_TMPL.strip('{} ')
IDLE_TMPL = "{{ not (" + LIVE_EXPR + ") }}"


def cond(card, want_live):
    """Wrap a card so it shows only while probes are (or aren't) reading."""
    return {
        "type": "conditional",
        "conditions": [{"condition": "template",
                        "value_template": LIVE_TMPL if want_live else IDLE_TMPL}],
        "card": card,
    }


def build_view(back_section):
    probes = {"type": "grid", "cards": [
        {"type": "heading", "heading": "Probes", "heading_style": "title",
         "icon": "mdi:thermometer"},
    ] + [{"type": "tile", "entity": CH[i], "name": "Probe %d" % (i + 1)} for i in range(6)]
        + [{"type": "tile", "entity": CONN, "name": "FireBoard"}]}

    chart = {"type": "grid", "cards": [
        {"type": "heading", "heading": "Cook", "heading_style": "title", "icon": "mdi:grill"},
        cond(GRAPH, True),
        cond(IDLE_CARD, False),
    ]}

    return {
        "type": "sections",
        "title": "Cook",
        "path": "cook-view",
        "icon": "mdi:grill",
        "show_icon_and_title": True,
        "max_columns": 3,
        "sections": [chart, probes, back_section],
    }


doc = json.load(io.open('dash2.json', encoding='utf-8'))
cfg = doc['data']['config']

if any(v.get('path') == 'cook-view' for v in cfg['views']):
    raise SystemExit('cook-view already exists - nothing to do')

back = json.load(io.open('back_section.json', encoding='utf-8'))
cfg['views'].append(build_view(back))

rail = cfg['views'][0]['cards'][0]['cards'][1]['cards'][4]
navs = [(c.get('tap_action') or {}).get('navigation_path', '') for c in rail['cards']]
if NAV in navs:
    raise SystemExit('cook tile already on the rail')
# Slot it after the printer, before the voice mic card which must stay last.
rail['cards'].insert(8, TILE)

tmp = 'dash_cook.json.tmp'
with io.open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, separators=(',', ':'))
os.replace(tmp, 'dash_cook.json')

print('views now:', len(cfg['views']), '| new view:', cfg['views'][-1]['path'])
print('rail tiles:', len(rail['cards']))
for c in rail['cards']:
    print('   ', (c.get('tap_action') or {}).get('navigation_path', c.get('type')))
print('bytes:', os.path.getsize('dash_cook.json'))
