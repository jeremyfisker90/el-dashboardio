"""Room list, refreshed device map, and a colour picker for RGB bulbs.

Three changes to the isometric card:

1. A room list down the left. The only way in was tapping a small slab on the
   diagram, which is fine on a desk and awkward on the wall tablet. The list is
   a second door to the same panel - the slabs still work.

2. The device map rebuilt from Home Assistant's areas, and the Office's Sonoff
   relay added. Several ids in the old map had died in the SmartThings rename.

3. RGB bulbs get a colour button in their row. Detected from
   supported_color_modes rather than a hardcoded list, so a swapped bulb
   declares itself instead of needing this file edited.
"""
import io
import os

P = 'floorplan_card.js'
s = io.open(P, encoding='utf-8').read()


def sub(old, new, what):
    global s
    if old not in s:
        raise SystemExit('anchor missing: ' + what)
    s = s.replace(old, new, 1)


# ------------------------------------------------------------ 1. device map
sub('''const ROOM_LIGHTS = {
  "Office": ["light.smart_rgbtw_bulb", "switch.office_overhead"],''',
    '''const ROOM_LIGHTS = {
  "Office": ["light.smart_rgbtw_bulb", "switch.office_overhead", "switch.sonoff"],''',
    'office sonoff')

# ------------------------------------------------------------ 2. colour支持
sub('''  _paintPanel() {''',
    '''  /* A bulb is colour-capable if it says so. hs/xy/rgb all mean "has a hue";
   * color_temp alone is just warm-to-cool and gets no colour button. */
  _canColour(e) {
    const s = this._hass.states[e];
    if (!s || !e.startsWith("light.")) return false;
    const modes = s.attributes.supported_color_modes || [];
    return modes.some(m => ["hs", "xy", "rgb", "rgbw", "rgbww"].includes(m));
  }

  _openColour(entity) {
    const s = this._hass.states[entity];
    const cur = s && s.attributes.rgb_color;
    const wrap = document.createElement("div");
    wrap.className = "nfpanel-back nfcolour";
    wrap.innerHTML =
      '<style>' + NeonFloorplanCard.PANEL_CSS + '</style>' +
      '<div class="nfpanel"><div class="nfphead">' +
        '<span class="nfptitle">COLOUR</span>' +
        '<button class="nfpx" title="Close">&times;</button></div>' +
        '<div class="nfswatches">' +
          NeonFloorplanCard.SWATCHES.map(c =>
            '<button class="nfsw" data-rgb="' + c.rgb.join(",") + '"' +
            ' style="background:rgb(' + c.rgb.join(",") + ')" title="' + c.name + '"></button>'
          ).join("") +
        '</div>' +
        '<div class="nfpdim"><span class="nfpicn">🎨</span>' +
          '<input type="color" class="nfpick" value="' +
            (cur ? "#" + cur.map(v => v.toString(16).padStart(2, "0")).join("") : "#ffffff") +
          '"><span class="nfppct">custom</span></div>' +
      '</div>';
    const close = () => wrap.remove();
    wrap.addEventListener("pointerup", e => { if (e.target === wrap) close(); });
    wrap.querySelector(".nfpx").addEventListener("pointerup", close);
    wrap.querySelectorAll(".nfsw").forEach(b =>
      b.addEventListener("pointerup", ev => {
        ev.stopPropagation();
        this._hass.callService("light", "turn_on", {
          entity_id: entity, rgb_color: b.dataset.rgb.split(",").map(Number) });
        close();
      }));
    wrap.querySelector(".nfpick").addEventListener("change", ev => {
      const h = ev.target.value;
      this._hass.callService("light", "turn_on", { entity_id: entity, rgb_color: [
        parseInt(h.substr(1, 2), 16), parseInt(h.substr(3, 2), 16),
        parseInt(h.substr(5, 2), 16)] });
      close();
    });
    document.body.appendChild(wrap);
  }

  _paintPanel() {''',
    'colour helpers')

# the colour button itself, next to the on/off toggle
sub('''          (ENT ? '<button class="nfppp" data-pp="' + e + '">' + (playing ? "⏸" : "▶") + '</button>' : "") +
          '<button class="nfptog' + (lit ? " lit" : "") + '" data-t="' + e + '">' +
            (lit ? "ON" : "OFF") + '</button>' +''',
    '''          (ENT ? '<button class="nfppp" data-pp="' + e + '">' + (playing ? "⏸" : "▶") + '</button>' : "") +
          (!ENT && this._canColour(e)
            ? '<button class="nfpcol" data-c="' + e + '" title="Change colour">🎨</button>' : "") +
          '<button class="nfptog' + (lit ? " lit" : "") + '" data-t="' + e + '">' +
            (lit ? "ON" : "OFF") + '</button>' +''',
    'colour button')

sub('''      rows.querySelectorAll("[data-pp]").forEach(b =>''',
    '''      rows.querySelectorAll("[data-c]").forEach(b =>
        b.addEventListener("pointerup", ev => {
          ev.stopPropagation();
          this._openColour(b.dataset.c);
        }));
      rows.querySelectorAll("[data-pp]").forEach(b =>''',
    'colour handler')

# ------------------------------------------------------------ 3. swatches
sub('''const THERMO = {''',
    '''// A small fixed palette beats a colour wheel on a wall tablet: eight taps that
// always land on something usable, with the picker there for anything else.
NeonFloorplanCardSwatches = [
  { name: "Warm white", rgb: [255, 214, 170] },
  { name: "Daylight",   rgb: [255, 255, 255] },
  { name: "Amber",      rgb: [255, 170, 60] },
  { name: "Red",        rgb: [255, 60, 60] },
  { name: "Green",      rgb: [80, 230, 120] },
  { name: "Cyan",       rgb: [60, 220, 240] },
  { name: "Blue",       rgb: [80, 120, 255] },
  { name: "Purple",     rgb: [190, 110, 255] },
];

const THERMO = {''',
    'swatch palette')

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('floorplan_card.js: sonoff, colour button, swatch palette')
