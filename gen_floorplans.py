"""Isometric (2.5D) floorplan SVGs — v2.
Layout = Zicka "Berkley Hall" mirrored left-right (user's house), 3rd garage bay at front,
basement from user's sketch. Adds simple isometric furniture.
Outputs floor SVGs + floorplans.json (data URIs + light icon percent coords)."""
import json, base64, os

OUT = os.path.dirname(os.path.abspath(__file__))
S = 13.0
THICK = 16
GAP = 0.4
PAD = 26

def iso(x, y, z=0.0):
    return ((x - y) * 0.866 * S, (x + y) * 0.5 * S - z)

def shade(hexcol, f):
    h = hexcol.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))

def fmt(p):
    return f"{p[0]:.1f},{p[1]:.1f}"

# rooms: (name, x1,y1,x2,y2, fill)   |   furn: (x1,y1,x2,y2, height_px, fill)
FLOORS = {
    "floor1": {
        "title": "1st Floor",
        "rooms": [
            ("Office",       0,0,10,12,  "#cdd9e6"),
            ("Family Room", 10,0,24,12,  "#f3ddc0"),
            ("Kitchen",     24,0,34,12,  "#cfe0c3"),
            ("Laundry",     34,0,40,8,   "#d9e5d6"),
            ("Bath",         0,12,6,17,  "#d5dce3"),
            ("Hall",        12,12,18,24, "#eae3d2"),
            ("Dining Room", 18,14,27,24, "#e5d0d8"),
            ("Living Room",  0,19,12,30, "#e8d5c8"),
            ("Foyer",       14,24,20,30, "#e9e2d0"),
            ("Porch",       10,30,26,34, "#d5dce3"),
            ("1 Car Garage",34,8,41,19,  "#d8d8d8"),
            ("2 Car Garage",34,19,48,31, "#cfcfcf"),
        ],
        "furn": [
            # family room: L sectional + TV + coffee table
            (11,4.5,12.8,10, 12, "#8a6f52"), (11,4.5,17,6.2, 12, "#8a6f52"),
            (15,0.6,21,1.4, 20, "#3a3a3a"),
            (14.2,7.4,16.8,9.2, 8, "#a3865f"),
            # kitchen island + back counter
            (26,5,32,7.2, 14, "#b0a18b"), (24.3,0.5,33.7,2.1, 14, "#9c8f7b"),
            # dining table
            (20,16.5,25,21.5, 12, "#8a6f52"),
            # living: two sofas
            (1.5,21,3.3,28, 12, "#7d8a9c"), (9,21,10.8,28, 12, "#7d8a9c"),
            # office desk
            (1,1,7,3, 12, "#8a6f52"),
            # laundry washer+dryer
            (35,0.6,37.2,2.6, 14, "#e8e8ee"), (37.6,0.6,39.6,2.6, 14, "#e8e8ee"),
        ],
        "lights": [
            ("switch.office_overhead",      5,4.5,  "mdi:ceiling-light-multiple"),
            ("light.office_lamp",           2.2,9.5,"mdi:lamp"),
            ("light.office_floor_lamp",     8,9.5,  "mdi:floor-lamp"),
            ("switch.office_fan",           5,7.5,  "mdi:fan"),
            ("light.family_room_lamp_1",    13.5,2.8,"mdi:lamp"),
            ("light.family_room_lamp_2",    21.5,3.5,"mdi:lamp"),
            ("light.familyroom_lamp_3",     13,11,  "mdi:floor-lamp"),
            ("switch.xmaslightsfamilyroom", 21.5,10,"mdi:string-lights"),
            ("light.charging_station",      18.5,8.5,"mdi:led-strip-variant"),
            ("light.kitchen_cabinets",      29,3.5, "mdi:wall-sconce-flat"),
            ("light.foyer_lights",          17,26.5,"mdi:ceiling-light"),
            ("light.front_door_light",      17,30.5,"mdi:outdoor-lamp"),
        ],
        "media": [
            ("media_player.family_room_tv",   17,2.5, "mdi:television"),
            ("media_player.denon_avr_x2700h_2", 21,5, "mdi:audio-video"),
            ("media_player.family_room_speaker", 13,9, "mdi:speaker"),
            ("media_player.kitchen_display",  26,9.5, "mdi:monitor-speaker"),
            ("media_player.kitchen_max",      31,9.5, "mdi:speaker"),
            ("media_player.office_google_home", 3,6, "mdi:speaker"),
            ("media_player.travel_google_tv", 7.5,6, "mdi:television"),
            ("media_player.travel_google_tv_2", 18,32, "mdi:television-classic"),
            ("media_player.spotify",          22,17, "mdi:spotify"),
        ],
    },
    "floor2": {
        "title": "2nd Floor",
        "rooms": [
            ("Ian's Room",     0,0,12,10,  "#e3d3c8"),
            ("Bath",           0,10,8,15,  "#d5dce3"),
            ("Evan's Room",    0,15,12,24, "#cde3df"),
            ("Master Bedroom",14,0,30,12,  "#cfd8ea"),
            ("Master Bath",   30,0,42,7,   "#d5dce3"),
            ("Closet",        30,7,42,12,  "#e9e2d0"),
            ("Hall",          12,10,30,15, "#e9e2d0"),
            ("Open Below",    14,15,26,24, "#efece4"),
            ("Guest & Office",30,15,44,24, "#ddd5e6"),
        ],
        "furn": [
            (3,0.6,9,4.6, 14, "#a56f6f"),          # ian bed
            (3,19.4,9,23.4, 14, "#5f8a80"),        # evan bed
            (18.5,0.6,25.5,6, 14, "#6f7fa5"),      # master bed
            (31,0.8,35,3.6, 12, "#e8e8ee"),        # tub
            (31.5,16,37.5,18, 12, "#8a6f52"),      # guest desk
            (39,19,43.4,23.4, 14, "#9c8aa5"),      # guest bed
        ],
        "lights": [
            ("light.devastator",     2.5,7,  "mdi:lamp"),
            ("light.ianroom",        9.5,7,  "mdi:led-strip-variant"),
            ("switch.vortex",        6,7,    "mdi:fan"),
            ("light.orange_dog",     6,17.5, "mdi:lamp"),
            ("light.bedroom_lamp_1", 16.5,2, "mdi:lamp"),
            ("light.bedroom_lamp_2", 27.5,2, "mdi:lamp"),
        ],
        "media": [
            ("media_player.ian_s_google_home",  6,3,    "mdi:speaker"),
            ("media_player.evan_s_google_home", 4,17.5, "mdi:speaker"),
            ("media_player.evan_s_room_tv_3",   8.5,22, "mdi:television"),
            ("media_player.bedroom_google_home",22,9,   "mdi:speaker"),
        ],
    },
    "basement": {
        "title": "Lower Level",
        "rooms": [
            ("Steam Room", 0,0,8,10,   "#cfe0dd"),
            ("Rec Room",   8,0,28,12,  "#f3ddc0"),
            ("Gym",        0,10,14,24, "#cde3df"),
            ("Hall",      14,12,28,16, "#eae3d2"),
            ("Bath",      14,16,24,24, "#d5dce3"),
            ("Workshop",  28,0,44,24,  "#d8d8d8"),
        ],
        "furn": [
            (10,1,18,3, 14, "#7a5c3e"),            # bar
            (10,8.5,16,10.5, 12, "#7d8a9c"),       # rec sofa
            (20,11.3,26,12, 20, "#3a3a3a"),        # rec TV wall
            (2,11,5,16.5, 10, "#888f96"),          # treadmill
            (8,11,12,13.5, 8, "#888f96"),          # weight bench
            (2,19.5,7,22.5, 8, "#888f96"),         # workout bench
            (29,0.8,43,2.8, 16, "#8a6f52"),        # workbench
        ],
        "lights": [],
        "media": [
            ("media_player.basement_speaker",     22,4,  "mdi:speaker"),
            ("media_player.basement_google_tv_2", 20,9,  "mdi:television"),
            ("media_player.denon_avr_x2300w",     25,7,  "mdi:audio-video"),
            ("media_player.fitness_room_speaker", 11,15.5,"mdi:speaker"),
            ("media_player.workout_room_tv_google_tv", 10.5,20.5, "mdi:television"),
        ],
    },
}

def prism(body, x1, y1, x2, y2, z0, z1, fill, stroke_f=0.62, sw=0.6):
    pTL, pTR, pBR, pBL = iso(x1,y1,z1), iso(x2,y1,z1), iso(x2,y2,z1), iso(x1,y2,z1)
    bBL, bBR, bTR = iso(x1,y2,z0), iso(x2,y2,z0), iso(x2,y1,z0)
    st = shade(fill, stroke_f)
    body.append((x1+y1, f'<polygon points="{fmt(pBL)} {fmt(pBR)} {fmt(bBR)} {fmt(bBL)}" fill="{shade(fill,0.72)}" stroke="{st}" stroke-width="{sw}"/>'
                        f'<polygon points="{fmt(pTR)} {fmt(pBR)} {fmt(bBR)} {fmt(bTR)}" fill="{shade(fill,0.84)}" stroke="{st}" stroke-width="{sw}"/>'
                        f'<polygon points="{fmt(pTL)} {fmt(pTR)} {fmt(pBR)} {fmt(pBL)}" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>'))

def gen(key, floor):
    # furniture is user-placed in floorplan_editor.html now, never baked in
    rooms, furn = floor["rooms"], []
    pts = []
    for _, x1, y1, x2, y2, _ in rooms:
        for cx, cy in ((x1,y1),(x2,y1),(x2,y2),(x1,y2)):
            p = iso(cx, cy, 0); pts.append(p); pts.append((p[0], p[1]+THICK))
    minx = min(p[0] for p in pts)-PAD; maxx = max(p[0] for p in pts)+PAD
    miny = min(p[1] for p in pts)-PAD-30; maxy = max(p[1] for p in pts)+PAD
    W, H = maxx-minx, maxy-miny

    raw = []   # (sortkey, svg) — rooms drawn as slabs below z=0
    ax1=min(r[1] for r in rooms); ay1=min(r[2] for r in rooms)
    ax2=max(r[3] for r in rooms); ay2=max(r[4] for r in rooms)
    sh=[iso(ax1-1,ay1-1,-(THICK+6)), iso(ax2+1,ay1-1,-(THICK+6)), iso(ax2+1,ay2+1,-(THICK+6)), iso(ax1-1,ay2+1,-(THICK+6))]
    shadow = f'<polygon points="{" ".join(fmt(p) for p in sh)}" fill="#000" opacity="0.08"/>'

    labels = []
    for name, x1, y1, x2, y2, fill in rooms:
        a,b,c,d = x1+GAP, y1+GAP, x2-GAP, y2-GAP
        prism(raw, a, b, c, d, -THICK, 0, fill, sw=0.8)
        cx, cy = (x1+x2)/2, (y1+y2)/2
        lp = iso(cx, cy, -3)
        fs = 12 if (x2-x1) >= 9 else 10
        for i, line in enumerate(name.split(" & ")):
            labels.append((x1+y1+100, f'<text transform="translate({lp[0]:.1f},{lp[1]+i*12:.1f})" font-family="Segoe UI, Roboto, sans-serif" font-size="{fs}" font-weight="600" fill="#5a5245" text-anchor="middle" opacity="0.9">{line}</text>'))
    for x1, y1, x2, y2, h, fill in furn:
        prism(raw, x1, y1, x2, y2, 0, h, fill, sw=0.5)

    raw.sort(key=lambda t: t[0])
    # rooms are all below furniture (z), but draw order: sort by depth handles overlap
    body = [shadow] + [s for _, s in raw] + [s for _, s in labels]
    body.append(f'<text x="{PAD/2}" y="26" font-family="Segoe UI, Roboto, sans-serif" font-size="20" font-weight="700" fill="#8a8272" opacity="0.85">{floor["title"]}</text>')

    # translate everything via group transform instead of per-point
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}">'
           f'<g transform="translate({-minx:.1f},{-miny:.1f})">' + "".join(body) + '</g>'
           f'</svg>')
    # title text was placed pre-transform; fix: draw it outside group
    svg = svg.replace(f'<text x="{PAD/2}" y="26"', '</g><text x="13" y="26"').replace('</g></svg>', '</svg>')
    with open(os.path.join(OUT, f"{key}.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    def markers(key2):
        out = []
        for ent, lx, ly, icon in floor.get(key2, []):
            p = iso(lx, ly, 8)
            out.append({"entity": ent, "icon": icon,
                        "left": round((p[0]-minx)/W*100, 1), "top": round((p[1]-miny)/H*100, 1)})
        return out
    return svg, markers("lights"), markers("media")

result = {}
for key, floor in FLOORS.items():
    svg, lights, media = gen(key, floor)
    result[key] = {"datauri": "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode(),
                   "lights": lights, "media": media, "svg_bytes": len(svg)}
with open(os.path.join(OUT, "floorplans.json"), "w") as f:
    json.dump(result, f)
print({k: (v["svg_bytes"], len(v["lights"]), len(v["media"])) for k, v in result.items()})
