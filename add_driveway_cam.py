"""Add the Alarm.com Driveway camera to the live Cameras view.

Patched against the live storage rather than rebuilt through make_neon_store.py,
because new_store.json predates a lot of what is on the dashboard now and a full
rebuild would roll those changes back. make_neon_store.py carries the same
change for whenever a real rebuild happens next.

Alarm.com streams over Janus/WebRTC, which picture-entity cannot play - it would
show a frozen still. The integration's own card handles the negotiation.
"""
import io
import json
import os

NEON_CAM_MOD = {"style":
    "ha-card{border:1px solid rgba(34,211,238,0.45)!important;border-radius:16px!important;"
    "box-shadow:0 0 14px rgba(34,211,238,0.25),0 8px 20px rgba(0,0,0,0.5)!important;overflow:hidden;}"}

SECTION = {"type": "grid", "cards": [
    {"type": "heading", "heading": "Driveway", "heading_style": "title",
     "icon": "mdi:car"},
    {"type": "custom:alarm-webrtc-card", "entity": "camera.driveway_camera",
     "card_mod": dict(NEON_CAM_MOD),
     "grid_options": {"columns": "full", "rows": 5}},
]}

doc = json.load(io.open('dash.json', encoding='utf-8'))
cfg = doc['data']['config']

view = next((v for v in cfg['views'] if v.get('path') == 'cameras'), None)
if view is None:
    raise SystemExit('cameras view not found')

secs = view['sections']
if any(s.get('cards') and s['cards'][0].get('heading') == 'Driveway' for s in secs):
    raise SystemExit('Driveway section already present - nothing to do')

# Slot it after "Back of House" so the two Alarm.com feeds sit together, ahead
# of the Wyze yard cam and the printer.
idx = next((i for i, s in enumerate(secs)
            if s.get('cards') and s['cards'][0].get('heading') == 'Back of House'), None)
insert_at = (idx + 1) if idx is not None else 2
secs.insert(insert_at, SECTION)

tmp = 'dash_new.json.tmp'
with io.open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, separators=(',', ':'))
os.replace(tmp, 'dash_new.json')

print('inserted Driveway at section index', insert_at)
print('sections now:', [s['cards'][0].get('heading') for s in secs if s.get('cards')])
print('bytes:', os.path.getsize('dash_new.json'))
