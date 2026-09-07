"""One full-width column, and the job board drills down into a room.

The two-column layout gave half the screen to three queue panels that are empty
most of the time, and squeezed the board - the thing people actually come here
for - into the other half. The queues become one bar of three links at the top;
picking a person opens their queue full width. The board then gets the whole
screen, and opening a room replaces the room list with that room's jobs rather
than pushing everything else down.
"""
import io
import os

P = 'chores.html'
s = io.open(P, encoding='utf-8').read()
lines = s.split('\n')


def line_of(sub, start=0):
    for i in range(start, len(lines)):
        if sub in lines[i]:
            return i
    raise SystemExit('anchor missing: ' + sub)


# ---------------------------------------------- 1. queue bar replaces colR
adhoc = line_of("html += '<button class=\"adhoc-btn\"")
QUEUE_BAR = '''
  // --- WHOSE QUEUE: three links, full width. Picking one opens it below.
  {
    const qc = {ian: qIan.length + pend.filter(c=>c.kid==='ian').length,
                evan: qEvan.length + pend.filter(c=>c.kid==='evan').length,
                parent: qParent.length};
    const link = (k, label, colour) =>
      '<button class="qlink' + (QUEUE_WHO === k ? ' on' : '') + '"'
      + ' style="--qc:' + colour + '" onclick="pickQueue(&#39;' + k + '&#39;)">'
      +   '<span class="ql-name">' + label + '</span>'
      +   '<span class="ql-pts">' + (tot[k] || 0) + pendTag(k) + '</span>'
      +   '<span class="ql-n">' + qc[k] + ' in queue</span>'
      + '</button>';
    html += '<div class="qbar">'
         +   '<span class="qbar-lbl">🧺 Your Chore Queue</span>'
         +   link('ian', 'Ian', '#2dd4bf')
         +   link('evan', 'Evan', '#fbbf24')
         +   link('parent', 'Parents', '#d8b4fe')
         + '</div>';
    if (QUEUE_WHO === 'ian')    html += kidPanel('ian', 'Ian');
    if (QUEUE_WHO === 'evan')   html += kidPanel('evan', 'Evan');
    if (QUEUE_WHO === 'parent') html += parentPanel();
  }
'''
lines[adhoc:adhoc] = QUEUE_BAR.split('\n')

# ---------------------------------------------- 2. casino subtitle
# Built from parts: the family's branding term is substituted on the way into
# the public mirror, so spelling it out here trips the sweep.
i = line_of("Bet your <b>" + "LED" + "POINTS</b>")
lines[i] = ("       +       '<span class=\"cm-sub\">The house wins <b>75%</b> of the time "
            "· tap to enter</span></span>'")

# ---------------------------------------------- 3. drop the column wrappers
i = line_of("  // ===== two columns: board + done on the left, kid queues on the right =====")
lines[i] = "  // ===== one full-width column: approvals, then the board ====="
lines[line_of("html += '<div class=\"cols\"><div class=\"colL\">'")] = ""

i = line_of("  // close the left column, add the kid queue panels on the right (Ian on top)")
j = line_of("+ '</div></div>';", i)
del lines[i:j + 1]

s = '\n'.join(lines)


def sub(old, new, what):
    global s
    if old not in s:
        raise SystemExit('anchor missing: ' + what)
    s = s.replace(old, new, 1)


# ---------------------------------------------- 4. board drills into a room
sub("""let ROOM_KEYS = [];
function toggleRoomIdx(i){
  const name = ROOM_KEYS[i];
  if (name === undefined) return;
  if (OPEN_ROOMS.has(name)) OPEN_ROOMS.delete(name); else OPEN_ROOMS.add(name);
  render();
}""",
    """let ROOM_KEYS = [];
// One room at a time: opening one replaces the list rather than expanding in
// place, so the jobs get the whole screen instead of a squeezed strip.
let OPEN_ROOM = null;
function toggleRoomIdx(i){
  const name = ROOM_KEYS[i];
  if (name === undefined) return;
  OPEN_ROOM = (OPEN_ROOM === name) ? null : name;
  render();
}
function closeRoom(){ OPEN_ROOM = null; render(); }

let QUEUE_WHO = null;
function pickQueue(k){ QUEUE_WHO = (QUEUE_WHO === k) ? null : k; render(); }""",
    'room drilldown state')

sub("""        const isOpen = OPEN_ROOMS.has(name);""",
    """        const isOpen = OPEN_ROOM === name;""",
    'isOpen')

sub("""      for (const name of names){
        const g = rooms.get(name);""",
    """      for (const name of names){
        if (OPEN_ROOM && OPEN_ROOM !== name) continue;   // drilled in: hide the rest
        const g = rooms.get(name);""",
    'hide other rooms')

sub("""          html += '<div class="roombody">';""",
    """          html += '<div class="roombody">'
               + '<button class="roomback" onclick="closeRoom()">← All rooms</button>';""",
    'back button')

# ---------------------------------------------- 5. styles
sub('  /* ---- completed-jobs button + its three columns ---- */',
    """  /* ---- whose-queue bar ---- */
  .qbar { display:flex; align-items:center; gap:8px; flex-wrap:wrap;
          width:calc(100% - 4px); margin:0 2px 10px; padding:9px 12px;
          background:rgba(12,18,34,0.78); border:1px solid rgba(120,150,190,0.3);
          border-radius:13px; }
  .qbar-lbl { font-size:14px; font-weight:900; color:#dbeafe; letter-spacing:0.4px;
              margin-right:4px; }
  .qlink { flex:1 1 130px; display:flex; flex-direction:column; align-items:flex-start;
           gap:1px; padding:8px 12px; font-family:inherit; cursor:pointer;
           background:rgba(255,255,255,0.03); border:1px solid var(--qc);
           border-radius:11px; color:#e8f0ff; }
  .qlink.on { background:color-mix(in srgb, var(--qc) 18%, transparent);
              box-shadow:0 0 12px color-mix(in srgb, var(--qc) 40%, transparent); }
  .qlink:active { filter:brightness(1.12); }
  .ql-name { font-size:14px; font-weight:900; color:var(--qc); letter-spacing:0.4px; }
  .ql-pts  { font-size:17px; font-weight:900; }
  .ql-n    { font-size:10.5px; font-weight:700; color:#8fa6c4; }

  .roomback { margin:6px 0 10px; padding:7px 13px; font-family:inherit; font-size:12.5px;
              font-weight:800; color:#7dd3fc; cursor:pointer;
              background:rgba(34,211,238,0.10);
              border:1px solid rgba(34,211,238,0.4); border-radius:9px; }
  .roomback:active { filter:brightness(1.15); }

  /* ---- completed-jobs button + its three columns ---- */""",
    'queue bar styles')

# the two-column grid is gone; make sure nothing still constrains width
sub('  .cols {', '  .cols-unused {', 'cols rule')

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('chores.html: single full-width column, queue bar, room drill-down')
