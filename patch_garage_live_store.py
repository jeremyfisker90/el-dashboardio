"""Fix the garage proportions in the addon's floorplan store (the live one).

gen_floorplans.py is not what the wall tablet draws. neon-floorplan-card fetches
the addon's /floorplan store, which the user has since edited by hand (it has a
Screened in porch and Stairs the generator never had), so that store is the
authority and the generator is a stale sibling.

In the live store both garages are w=14 - a 1-bay and a 2-bay drawn exactly the
same width. That is the disproportion.

Which is which, from the user's two landmarks:

  "the 1 car garage shares a wall with the laundry"
      Laundry  x 26.5-44.5, y 8-13
      Garage   x 26.5-40.5, y 12.5-24.5   <- meets Laundry at y=12.5   = 1 car

  "the 2 car garage is on the left of the current 1st floor diagram"
      the card projects isometrically, so screen-left is the smaller (x - y):
      Garage    centre (33.5, 18.5)  x-y = 15.0
      Garage 3  centre (33.5, 29.5)  x-y =  4.0   <- leftmost            = 2 car

Both landmarks agree, and they say the labels were doing the opposite of what
the boxes showed.

New rects, 2:1 on width at near-equal depth, which is how a real 1-bay and
2-bay compare:

  1 Car Garage  x 33.5  y 12.5  w 10  d 12   still meets the Laundry
  2 Car Garage  x 26.5  y 24    w 20  d 11   still front-left, now twice as wide

The 1 car is right-aligned to x=43.5 so it finishes flush with the Kitchen's
outer wall (x=43) instead of leaving a notch at the house edge.

ROOM_LIGHTS in floorplan_card.js is keyed by exact room name and has no garage
entry, so the rename costs no light mapping.
"""
import io
import json
import os
import urllib.request

API = 'http://YOUR_HA_IP:5000'
HERE = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(HERE, 'floorplan_store.bak_garage.json')

NEW = {
    'Garage':   {'name': '1 Car Garage', 'x': 33.5, 'y': 12.5, 'w': 10, 'd': 12},
    'Garage 3': {'name': '2 Car Garage', 'x': 26.5, 'y': 24.0, 'w': 20, 'd': 11},
}

# ------------------------------------------------------------------ fetch
with urllib.request.urlopen(API + '/floorplan', timeout=20) as r:
    store = json.loads(r.read().decode('utf-8'))

if not os.path.exists(BACKUP):
    with io.open(BACKUP, 'w', encoding='utf-8') as fh:
        json.dump(store, fh, indent=1)
    print('backed up original store ->', os.path.basename(BACKUP))
else:
    print('backup already exists, left alone ->', os.path.basename(BACKUP))

rooms = store['rooms']['floor1']

# ------------------------------------------------------------------ edit
hits = 0
for room in rooms:
    spec = NEW.get(room.get('name'))
    if not spec:
        continue
    hits += 1
    before = '%-14s x=%-6s y=%-6s w=%-4s d=%s' % (
        room['name'], room['x'], room['y'], room['w'], room['d'])
    room.update(spec)          # id and color are deliberately preserved
    print('  %s\n    -> %-14s x=%-6s y=%-6s w=%-4s d=%s'
          % (before, room['name'], room['x'], room['y'], room['w'], room['d']))

if hits != len(NEW):
    raise SystemExit('expected %d garage rooms, matched %d' % (len(NEW), hits))

# ------------------------------------------------------------------ verify
by = {r['name']: r for r in rooms}
one, two = by['1 Car Garage'], by['2 Car Garage']
lau = by['Laundry']


def cx(r):
    return r['x'] + r['w'] / 2.0


def cy(r):
    return r['y'] + r['d'] / 2.0


# screen-left in this isometric projection is the smaller (x - y)
assert cx(two) - cy(two) < cx(one) - cy(one), '2 car must render left of 1 car'
# the 1 car must still touch the laundry: y edges meet and x ranges overlap
assert one['y'] <= lau['y'] + lau['d'], '1 car no longer meets the laundry in y'
assert one['x'] < lau['x'] + lau['w'] and lau['x'] < one['x'] + one['w'], \
    '1 car no longer overlaps the laundry in x'
assert abs(two['w'] / float(one['w']) - 2.0) < 0.01, 'width ratio must be 2:1'
print('checks passed: 2 car is left, 1 car meets the laundry, widths are 2:1')

# ------------------------------------------------------------------ write
body = json.dumps({'floors': store}).encode('utf-8')
req = urllib.request.Request(API + '/floorplan', data=body,
                             headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=20) as r:
    print('POST /floorplan ->', r.read().decode('utf-8'))
