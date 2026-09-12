"""Make the two garages proportional, and label them for what they are.

The old rects had it backwards. Reading the rendered SVG label positions:

    Garage 3  screen x=197   (left)
    Garage    screen x=304
    Laundry   screen x=371

The user placed them by two independent landmarks - "the 2 car garage is on the
left of the current 1st floor diagram" and "the 1 car garage shares a wall with
the laundry" - and both point the same way:

    Garage 3 is the leftmost room      -> it is the 2 car
    Garage touches Laundry at y=8      -> it is the 1 car

Which means the sizes were inverted: the 1 car was 14x12 (168) and the 2 car was
10x11 (110). The bigger box was the smaller garage. That is the disproportion.

New rects keep both landmarks and fix the ratio:

    1 Car Garage  34,8  -> 41,19    7 wide x 11 deep   still under the Laundry
    2 Car Garage  34,19 -> 48,31   14 wide x 12 deep   still front-left

Exactly 2:1 on width - the axis the garage doors sit on - at near-equal depth,
which is how a real 1-bay and 2-bay compare. Depth is left slightly uneven
because the front bay is the one that projects toward the street.

Nothing else moves: no light or furniture coordinate falls inside either rect
(checked - the nearest are the laundry washer/dryer at y<2.6 and the front door
light at x=17).
"""
import io
import os
import re

EDITS = [
    # (file, old fragment, new fragment)
    ('gen_floorplans.py',
     '("Garage",      34,8,48,20,  "#d8d8d8"),',
     '("1 Car Garage",34,8,41,19,  "#d8d8d8"),'),
    ('gen_floorplans.py',
     '("Garage 3",    38,20,48,31, "#cfcfcf"),',
     '("2 Car Garage",34,19,48,31, "#cfcfcf"),'),
    ('gen_sh3d.py',
     '("Garage", 34,8,48,20), ("Garage 3", 38,20,48,31)',
     '("1 Car Garage", 34,8,41,19), ("2 Car Garage", 34,19,48,31)'),
]

HERE = os.path.dirname(os.path.abspath(__file__))

for fname, old, new in EDITS:
    path = os.path.join(HERE, fname)
    src = io.open(path, encoding='utf-8').read()
    if new in src:
        print('  %-20s already patched' % fname)
        continue
    if src.count(old) != 1:
        raise SystemExit('%s: expected exactly 1 match for %r, found %d'
                         % (fname, old[:40], src.count(old)))
    io.open(path, 'w', encoding='utf-8').write(src.replace(old, new, 1))
    print('  %-20s %s' % (fname, new.strip()))

print('patched', len(EDITS), 'rect definitions')
