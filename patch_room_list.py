"""A clickable room list beside the diagram.

Tapping a room slab works on a desk and is fiddly on the wall tablet - the
smaller rooms are a few dozen pixels of angled polygon. The list is a second
way into the same panel: same rooms, same order as the diagram reads, showing
how many devices are on. The slabs keep working.

Rooms with nothing mapped are listed greyed rather than hidden, so it stays
obvious which rooms still need devices assigned.
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


# ---------------------------------------------------------------- markup
sub('''      + '<div class="nfbar">' + tabs + '<span class="nfsum">'
      + (onCount ? (ENT ? "🔊 " + onCount + " playing" : "💡 " + onCount + " light" + (onCount === 1 ? "" : "s") + " on")
                 : (ENT ? "nothing playing" : "all lights off")) + "</span></div>"
      + '<svg viewBox="0 0 ' + (maxx - minx).toFixed(0) + " " + (maxy - miny).toFixed(0)
      + '" style="width:100%;height:calc(100vh - 118px);display:block;" xmlns="http://www.w3.org/2000/svg">'
      + defs + '<g transform="translate(' + (-minx).toFixed(1) + "," + (-miny).toFixed(1) + ')">' + body + "</g></svg>"
      + "</ha-card>";''',
    '''      + '<div class="nfbar">' + tabs + '<span class="nfsum">'
      + (onCount ? (ENT ? "🔊 " + onCount + " playing" : "💡 " + onCount + " light" + (onCount === 1 ? "" : "s") + " on")
                 : (ENT ? "nothing playing" : "all lights off")) + "</span></div>"
      + '<div class="nfsplit">'
      +   '<div class="nflist">' + roomList + '</div>'
      +   '<svg viewBox="0 0 ' + (maxx - minx).toFixed(0) + " " + (maxy - miny).toFixed(0)
      +   '" style="width:100%;height:calc(100vh - 126px);display:block;" xmlns="http://www.w3.org/2000/svg">'
      +   defs + '<g transform="translate(' + (-minx).toFixed(1) + "," + (-miny).toFixed(1) + ')">' + body + "</g></svg>"
      + '</div>'
      + "</ha-card>";''',
    'split layout')

# ---------------------------------------------------------------- the list
sub('''    const tabs = ["floor1", "floor2", "basement"].map(f =>''',
    '''    // Read top-left to bottom-right, the same way the eye crosses the diagram,
    // so a room's place in the list roughly matches where it sits on the floor.
    const roomList = [...rooms]
      .sort((a, b) => (a.y + a.x) - (b.y + b.x))
      .map(r => {
        const ents = this._roomLights(r.name);
        const onN = ents.filter(e => this._isOn(e)).length;
        return '<button class="nfli' + (ents.length ? "" : " none") + (onN ? " lit" : "") + '"'
          + ' data-lroom="' + r.name.replace(/"/g, "&quot;") + '">'
          + '<span class="nflidot"></span>'
          + '<span class="nfliname">' + r.name + '</span>'
          + '<span class="nflin">' + (ents.length ? (onN ? onN + "/" + ents.length : ents.length) : "") + '</span>'
          + '</button>';
      }).join("");

    const tabs = ["floor1", "floor2", "basement"].map(f =>''',
    'room list build')

# ---------------------------------------------------------------- styles
sub("""      + '.nfsum{margin-left:auto;""",
    """      + '.nfsplit{display:flex;align-items:stretch;gap:10px;padding:0 10px 6px;}'
      + '.nflist{flex:0 0 172px;display:flex;flex-direction:column;gap:4px;overflow-y:auto;'
      + 'max-height:calc(100vh - 126px);padding-right:2px;}'
      + '.nfli{display:flex;align-items:center;gap:8px;width:100%;padding:7px 10px;cursor:pointer;'
      + 'font-family:inherit;font-size:12.5px;font-weight:800;color:#c7d6ee;text-align:left;'
      + 'background:rgba(13,20,44,.55);border:1px solid rgba(120,150,190,.22);border-radius:10px;}'
      + '.nfli:active{filter:brightness(1.15);}'
      + '.nfli.none{opacity:.38;cursor:default;}'
      + '.nfli.lit{border-color:' + ACC_SOFT + ';color:#fff3d4;'
      + 'box-shadow:0 0 10px ' + (ENT ? "rgba(56,189,248,.22)" : "rgba(251,191,36,.22)") + ';}'
      + '.nflidot{flex:none;width:7px;height:7px;border-radius:50%;background:#41506b;}'
      + '.nfli.lit .nflidot{background:' + ACC + ';box-shadow:0 0 7px ' + ACC + ';}'
      + '.nfliname{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}'
      + '.nflin{flex:none;font-size:11px;font-weight:900;color:#8fa6c4;}'
      + '.nfsplit svg{flex:1;min-width:0;}'
      + '.nfsum{margin-left:auto;""",
    'list styles')

# ---------------------------------------------------------------- handler
sub('''    this.querySelectorAll(".nfroom").forEach(g =>''',
    '''    this.querySelectorAll("[data-lroom]").forEach(b =>
      b.addEventListener("pointerup", () => {
        const ents = this._roomLights(b.dataset.lroom);
        if (ents.length) this._openPanel(b.dataset.lroom);
      }));
    this.querySelectorAll(".nfroom").forEach(g =>''',
    'list handler')

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('floorplan_card.js: clickable room list added beside the diagram')
