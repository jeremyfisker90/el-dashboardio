"""Give the useful area-less sensors an Area so Claude can see them.

Home Assistant builds the conversation agent's picture of the house from areas -
"an overview of the areas and the devices in this smart home". An entity with no
area is left out of that overview even when it is exposed, which is why asking
about the dryer got "you don't appear to have this device" while the door
sensors answered fine.

Only the ones worth asking about by voice. The other ~60 orphans are backup
timers, phone internals and integration counters that nobody will ever ask for
out loud, and each one costs prompt space on every single request.
"""
import io
import json
import os

ASSIGN = {
    # laundry: the pair that exposed this whole problem
    'binary_sensor.washer_running': 'laundry_room',
    'binary_sensor.dryer_running': 'laundry_room',
    # kitchen is where the tablet lives and where these get asked about
    'sensor.todays_dinner': 'kitchen',
    'sensor.dinners_this_week': 'kitchen',
    'sensor.chores_pending': 'kitchen',
    'sensor.chores_points': 'kitchen',
    'sensor.today_schedule': 'kitchen',
    'sensor.google_keep_notes': 'kitchen',
    'sensor.cozi_live': 'kitchen',
    'sensor.hourly_forecast_home': 'kitchen',
    # the FireBoard sits by the grill
    'sensor.fireboard_channel_1': 'backporch',
    'sensor.fireboard_channel_2': 'backporch',
    'sensor.fireboard_channel_3': 'backporch',
    'sensor.fireboard_channel_4': 'backporch',
    'sensor.fireboard_channel_5': 'backporch',
    'sensor.fireboard_channel_6': 'backporch',
    'binary_sensor.fireboard_connectivity': 'backporch',
    # game day
    'sensor.bengals_next_game': 'family_room',
    'sensor.buckeyes_next_game': 'family_room',
}

SRC = 'er8b.json'
OUT = 'er_areas2.json'

doc = json.load(io.open(SRC, encoding='utf-8'))
ents = doc['data']['entities']

done, missing = [], []
seen = set()
for e in ents:
    eid = e['entity_id']
    if eid in ASSIGN:
        seen.add(eid)
        e['area_id'] = ASSIGN[eid]
        done.append((eid, ASSIGN[eid]))

missing = [k for k in ASSIGN if k not in seen]

tmp = OUT + '.tmp'
with io.open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, separators=(',', ':'))
os.replace(tmp, OUT)

for eid, area in done:
    print('  %-42s -> %s' % (eid, area))
if missing:
    print('NOT FOUND in registry:', missing)
print('assigned:', len(done), '| entities:', len(ents))
