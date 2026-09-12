"""Generate a Sweet Home 3D starter model (.sh3d) of the mirrored Berkley Hall.
Walls + named rooms on 3 levels; scale 1 plan-unit = 30 cm. Furnish/render in SH3D."""
import zipfile, os, sys

OUT = os.path.dirname(os.path.abspath(__file__))
SC = 30.0  # cm per plan unit

FLOORS = {
    "lvl-b":  ("Lower Level", -292, [
        ("Steam Room", 0,0,8,10), ("Rec Room", 8,0,28,12), ("Gym", 0,10,14,18),
        ("Workout", 0,18,14,24), ("Bath", 14,16,24,24), ("Workshop", 28,0,44,24)]),
    "lvl-1":  ("1st Floor", 0, [
        ("Office", 0,0,10,12), ("Family Room", 10,0,24,12), ("Kitchen", 24,0,34,12),
        ("Laundry", 34,0,40,8), ("Bath", 0,12,6,17), ("Dining Room", 18,14,27,24),
        ("Living Room", 0,19,12,30), ("Foyer", 14,24,20,30), ("Porch", 10,30,26,34),
        ("1 Car Garage", 34,8,41,19), ("2 Car Garage", 34,19,48,31)]),
    "lvl-2":  ("2nd Floor", 292, [
        ("Ian's Room", 0,0,12,10), ("Bath", 0,10,8,15), ("Evan's Room", 0,15,12,24),
        ("Master Bedroom", 14,0,30,12), ("Master Bath", 30,0,42,7), ("Closet", 30,7,42,12),
        ("Hall", 12,10,30,15), ("Guest Office", 30,15,44,24)]),
}

xml = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<home version="7000" name="BerkleyHallMirrored" wallHeight="250">']
order = ["lvl-b", "lvl-1", "lvl-2"]
for i, lid in enumerate(order):
    name, elev, _ = FLOORS[lid]
    xml.append(f'<level id="{lid}" name="{name}" elevation="{elev}" floorThickness="12" height="250" elevationIndex="{i}"/>')

wid = 0
for lid in order:
    _, _, rooms = FLOORS[lid]
    # dedupe shared edges so adjacent rooms share one wall
    edges = {}
    for name, x1, y1, x2, y2 in rooms:
        for e in (((x1,y1),(x2,y1)), ((x2,y1),(x2,y2)), ((x1,y2),(x2,y2)), ((x1,y1),(x1,y2))):
            key = tuple(sorted(e))
            edges[key] = edges.get(key, 0) + 1
    for (p1, p2) in edges:
        wid += 1
        xml.append(f'<wall id="w{wid}" levelId="{lid}" xStart="{p1[0]*SC:.0f}" yStart="{p1[1]*SC:.0f}" '
                   f'xEnd="{p2[0]*SC:.0f}" yEnd="{p2[1]*SC:.0f}" height="250" thickness="10"/>')
    for name, x1, y1, x2, y2 in rooms:
        pts = "".join(f'<point x="{px*SC:.0f}" y="{py*SC:.0f}"/>'
                      for px, py in ((x1,y1),(x2,y1),(x2,y2),(x1,y2)))
        xml.append(f'<room levelId="{lid}" name="{name}" nameXOffset="0" nameYOffset="0">{pts}</room>')

xml.append('</home>')
path = os.path.join(OUT, "berkley-mirrored.sh3d")
with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("Home.xml", "\n".join(xml))
print(path, os.path.getsize(path), "bytes,", wid, "walls")
