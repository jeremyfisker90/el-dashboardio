#!/usr/bin/env python3
"""Build garage_section.json — a Lovelace 'grid' section with an animated
house-front garage view (left bay = 2-car cover.2_car_garage, right bay = 1-car
cover.1_car_garage). Doors roll up when open; tap a door to open/close it.
Injected into the el-dashboardio 'alarm' view (renamed "Alarm/Garage").
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# custom:button-card JS template. onclick args use the HTML entity &#39; for the
# single quote so nothing needs backslash-escaping inside the JS string.
GARAGE_JS = r"""[[[
  if(!window.garageTap){ window.garageTap=function(ent){ var h=document.querySelector('home-assistant').hass; var s=h.states[ent]; var op=s&&(s.state==='open'||s.state==='opening'); h.callService('cover', op?'close_cover':'open_cover', {entity_id:ent}); }; }
  var L=states['cover.2_car_garage'], R=states['cover.1_car_garage'];
  var lo=L&&(L.state==='open'||L.state==='opening'), ro=R&&(R.state==='open'||R.state==='opening');
  var anyOpen=lo||ro;
  function bay(x,w,isOpen,label,ent){
    var col=isOpen?'#f43f5e':'#22d3ee';
    var ty=isOpen?-172:0, cid='c'+x, i, yy;
    var panels='';
    for(i=1;i<=4;i++){ yy=80+i*30; panels+='<line x1="'+(x+8)+'" y1="'+yy+'" x2="'+(x+w-8)+'" y2="'+yy+'" stroke="rgba(0,0,0,0.30)" stroke-width="2.5"/>'; }
    var cols=Math.max(2,Math.round(w/50)), gw=(w-16)/cols, wins='';
    for(i=0;i<cols;i++){ wins+='<rect x="'+(x+8+i*gw+4)+'" y="92" width="'+(gw-8)+'" height="17" rx="2" fill="rgba(125,205,255,0.35)" stroke="rgba(0,0,0,0.3)"/>'; }
    return '<clipPath id="'+cid+'"><rect x="'+x+'" y="80" width="'+w+'" height="172" rx="5"/></clipPath>'
      +'<rect x="'+x+'" y="80" width="'+w+'" height="172" rx="5" fill="#05070f"/>'
      +(isOpen?'<rect x="'+x+'" y="80" width="'+w+'" height="172" rx="5" fill="rgba(244,63,94,0.16)"/><text x="'+(x+w/2)+'" y="180" text-anchor="middle" font-size="34" fill="rgba(244,63,94,0.75)" font-weight="900" letter-spacing="3">OPEN</text>':'')
      +'<g clip-path="url(#'+cid+')"><g style="transition:transform 1.1s cubic-bezier(.4,.05,.2,1)" transform="translate(0,'+ty+')">'
      +'<rect x="'+x+'" y="80" width="'+w+'" height="172" rx="5" fill="url(#dg)" stroke="'+col+'" stroke-width="3"/>'+wins+panels
      +'<rect x="'+(x+w/2-9)+'" y="222" width="18" height="7" rx="2" fill="#6b7280"/>'
      +'</g></g>'
      +'<rect x="'+x+'" y="80" width="'+w+'" height="172" rx="5" fill="none" stroke="'+col+'" stroke-width="3" filter="url(#'+(isOpen?'gr':'gc')+')"/>'
      +'<rect x="'+x+'" y="80" width="'+w+'" height="172" fill="transparent" style="cursor:pointer" onclick="garageTap(&#39;'+ent+'&#39;)"/>'
      +'<text x="'+(x+w/2)+'" y="277" text-anchor="middle" font-size="15" font-weight="900" fill="#e8eeff" letter-spacing="1">'+label+'</text>'
      +'<text x="'+(x+w/2)+'" y="294" text-anchor="middle" font-size="12" font-weight="800" fill="'+col+'">'+(isOpen?'● OPEN':'● CLOSED')+'</text>';
  }
  var svg='<svg viewBox="0 0 500 300" width="100%" style="max-width:560px;display:block;margin:0 auto;">'
    +'<defs>'
    +'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#101c38"/><stop offset="1" stop-color="#0a0f1e"/></linearGradient>'
    +'<linearGradient id="dg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cdd6e8"/><stop offset="1" stop-color="#98a6c0"/></linearGradient>'
    +'<linearGradient id="rf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b2b4d"/><stop offset="1" stop-color="#231932"/></linearGradient>'
    +'<filter id="gr" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#f43f5e"/></filter>'
    +'<filter id="gc" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#22d3ee"/></filter>'
    +'</defs>'
    +'<rect x="0" y="58" width="500" height="242" fill="url(#sky)"/>'
    +'<rect x="0" y="252" width="500" height="48" fill="#12182b"/>'
    +'<polygon points="18,62 482,62 448,16 52,16" fill="url(#rf)" stroke="#4c3b62" stroke-width="2"/>'
    +'<rect x="18" y="56" width="464" height="9" rx="2" fill="#2c2142"/>'
    +'<rect x="256" y="80" width="34" height="172" fill="#0c1222"/>'
    +bay(40,210,lo,'2 CAR GARAGE','cover.2_car_garage')
    +bay(296,150,ro,'1 CAR GARAGE','cover.1_car_garage')
    +'</svg>';
  var banner=anyOpen
    ?'<div style="text-align:center;font-size:14px;font-weight:900;letter-spacing:1px;color:#fecaca;background:rgba(244,63,94,0.18);border:1px solid rgba(244,63,94,0.55);border-radius:11px;padding:7px;margin:2px 8px 8px;box-shadow:0 0 14px rgba(244,63,94,0.3);">⚠ GARAGE DOOR OPEN — tap a door to close</div>'
    :'<div style="text-align:center;font-size:13px;font-weight:800;letter-spacing:1px;color:#86efac;background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.4);border-radius:11px;padding:7px;margin:2px 8px 8px;">✓ Both garage doors closed</div>';
  return '<div style="width:100%;text-align:left;">'+banner+svg+'</div>';
]]]"""

card = {
    "type": "custom:button-card",
    "entity": "cover.1_car_garage",
    "show_icon": False, "show_name": False, "show_state": False,
    "tap_action": {"action": "none"},
    "triggers_update": ["cover.1_car_garage", "cover.2_car_garage"],
    "custom_fields": {"g": GARAGE_JS},
    "styles": {
        "card": [{"padding": "8px"}, {"background": "rgba(8,12,26,0.92)"},
                 {"border": "1px solid rgba(34,211,238,0.4)"}, {"border-radius": "16px"},
                 {"box-shadow": "0 0 18px rgba(34,211,238,0.22)"}],
        "grid": [{"grid-template-areas": '"g"'}],
        "custom_fields": {"g": [{"width": "100%"}]},
    },
    "grid_options": {"columns": "full", "rows": "auto"},
}

section = {"type": "grid", "cards": [
    {"type": "heading", "heading": "Garage", "heading_style": "title", "icon": "mdi:garage-variant"},
    card,
    {"type": "tile", "entity": "cover.2_car_garage", "name": "2 Car Garage"},
    {"type": "tile", "entity": "cover.1_car_garage", "name": "1 Car Garage"},
]}

out = os.path.join(HERE, "garage_section.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(section, f, ensure_ascii=False)
print("wrote", out, os.path.getsize(out), "bytes")
