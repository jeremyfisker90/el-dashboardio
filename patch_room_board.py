"""Group the job board by room behind collapsible headers.

The board was three long flat grids. Standing at the tablet looking for "the
thing I have to do in the kitchen" meant reading every card. Rooms collapse it
to a short list you can scan, and the counts on each header mean you can tell
whether a room is worth opening without opening it.

Daily / Required / Optional still matter (6am reset, the optional credit gate),
so they survive as sub-labels inside an expanded room rather than as the top
level of the page.
"""
import io
import os

P = 'chores.html'
s = io.open(P, encoding='utf-8').read()

# ------------------------------------------------------------- board markup
OLD = """  if (daily.length){
    html += '<div class="sub dailysub" style="color:#7dd3fc">⏰ DAILY REQUIRED'
         + '<span class="pill daily2">RESETS 6AM · DO EVERY DAY</span></div>';
    html += '<div class="dailynote">These come back on their own — dailies every '
         + 'morning at 6am, 2-day jobs two days after they’re finished.</div>';
    html += grid(daily.map(c => choreHtml(c, false)));
  }
  html += '<div class="sub" style="color:#ff9a6b">REQUIRED'
       + '<span class="pill must">DO THESE FIRST</span></div>';
  html += req.length ? grid(req.map(c => choreHtml(c, false)))
                     : '<div class="empty">Every required chore is queued or done. 🎉</div>';
  const cr = D.optional_credits || {ian:0, evan:0};
  const ic = Math.max(0, cr.ian||0), ec = Math.max(0, cr.evan||0);
  html += '<div class="sub" style="color:#5fe0c6">OPTIONAL — EXTRA POINTS'
       + '<span class="pill open">🔓 1 REQUIRED = 1 OPTIONAL</span></div>';
  html += '<div style="font-size:12.5px;font-weight:700;margin:0 0 8px;color:#9fb3cf">'
       + 'Unlocked to spend now — '
       + '<span style="color:#2dd4bf;font-weight:800">Ian ' + ic + '</span> · '
       + '<span style="color:#fbbf24;font-weight:800">Evan ' + ec + '</span>'
       + ' <span style="color:#6b7a95">(each finishes a required to unlock one more)</span></div>';
  html += opt.length ? grid(opt.map(c => choreHtml(c, false)))
                     : '<div class="empty">No optional chores right now.</div>';
  html += '</div></div>';"""

NEW = """  {
    const cr = D.optional_credits || {ian:0, evan:0};
    const ic = Math.max(0, cr.ian||0), ec = Math.max(0, cr.evan||0);
    html += '<div class="dailynote">⏰ Dailies come back at 6am, 2-day jobs two days '
         + 'after they’re finished. 🔓 Optional unlocked now — '
         + '<span style="color:#2dd4bf;font-weight:800">Ian ' + ic + '</span> · '
         + '<span style="color:#fbbf24;font-weight:800">Evan ' + ec + '</span></div>';

    // room -> {daily, req, opt}, in the order rooms first appear on the board
    const rooms = new Map();
    const bucketOf = c => c.kind === 'optional' ? 'opt' : (isShort(c) ? 'daily' : 'req');
    const push = c => {
      const key = (c.room || '').trim() || NO_ROOM;
      if (!rooms.has(key)) rooms.set(key, {daily:[], req:[], opt:[]});
      rooms.get(key)[bucketOf(c)].push(c);
    };
    daily.forEach(push); req.forEach(push); opt.forEach(push);

    const names = [...rooms.keys()].sort((a,b) => {
      if ((a === NO_ROOM) !== (b === NO_ROOM)) return a === NO_ROOM ? 1 : -1;
      return a.localeCompare(b);
    });

    if (!names.length){
      html += '<div class="empty">Every chore is queued or done. 🎉</div>';
    } else {
      for (const name of names){
        const g = rooms.get(name);
        const n = g.daily.length + g.req.length + g.opt.length;
        const pts = [...g.daily, ...g.req, ...g.opt]
          .reduce((s,c) => s + (parseInt(c.points)||0), 0);
        const isOpen = OPEN_ROOMS.has(name);
        const bits = [];
        if (g.daily.length) bits.push(g.daily.length + ' daily');
        if (g.req.length)   bits.push(g.req.length + ' required');
        if (g.opt.length)   bits.push(g.opt.length + ' optional');
        html += '<div class="roomgrp' + (isOpen ? ' open' : '') + '">'
          + '<button class="roomhead" onclick="toggleRoom(' + JSON.stringify(name) + ')">'
          +   '<span class="rmchev">' + (isOpen ? '▾' : '▸') + '</span>'
          +   '<span class="rmname">' + esc(name) + '</span>'
          +   '<span class="rmmeta">' + bits.join(' · ') + '</span>'
          +   '<span class="rmpts">' + pts + ' pts</span>'
          + '</button>';
        if (isOpen){
          html += '<div class="roombody">';
          if (g.daily.length){
            html += '<div class="sub dailysub" style="color:#7dd3fc">⏰ DAILY REQUIRED'
                 + '<span class="pill daily2">RESETS 6AM</span></div>'
                 + grid(g.daily.map(c => choreHtml(c, false)));
          }
          if (g.req.length){
            html += '<div class="sub" style="color:#ff9a6b">REQUIRED'
                 + '<span class="pill must">DO THESE FIRST</span></div>'
                 + grid(g.req.map(c => choreHtml(c, false)));
          }
          if (g.opt.length){
            html += '<div class="sub" style="color:#5fe0c6">OPTIONAL — EXTRA POINTS'
                 + '<span class="pill open">🔓 1 REQUIRED = 1 OPTIONAL</span></div>'
                 + grid(g.opt.map(c => choreHtml(c, false)));
          }
          html += '</div>';
        }
        html += '</div>';
      }
    }
  }
  html += '</div></div>';"""

assert OLD in s, 'board section not found'
s = s.replace(OLD, NEW, 1)

# ------------------------------------------------------------- state + toggle
OLD2 = "  const grid = cards => '<div class=\"grid\">' + cards.join('') + '</div>';"
NEW2 = OLD2 + """

  // Which rooms are expanded. render() rebuilds the whole board on every poll,
  // so this has to live outside it or a room would snap shut under the kid's
  // finger mid-scroll.
"""
assert OLD2 in s, 'grid helper not found'
s = s.replace(OLD2, NEW2, 1)

# module-level state, next to the other globals
OLD3 = "function render(){"
NEW3 = """const NO_ROOM = 'Anywhere';
const OPEN_ROOMS = new Set();
function toggleRoom(name){
  if (OPEN_ROOMS.has(name)) OPEN_ROOMS.delete(name); else OPEN_ROOMS.add(name);
  render();
}

function render(){"""
assert OLD3 in s, 'render() not found'
s = s.replace(OLD3, NEW3, 1)

# ------------------------------------------------------------- styles
OLD4 = '  /* ---- filter-by-points bar + its popup ---- */'
NEW4 = """  /* ---- room accordion on the job board ---- */
  .roomgrp { margin:0 0 8px; border:1px solid rgba(120,150,190,0.22); border-radius:12px;
             background:rgba(12,18,34,0.55); overflow:hidden; }
  .roomgrp.open { border-color:rgba(34,211,238,0.45);
                  box-shadow:0 0 14px rgba(34,211,238,0.14); }
  .roomhead { display:flex; align-items:center; gap:9px; width:100%; padding:12px 13px;
              background:none; border:0; cursor:pointer; text-align:left;
              font-family:inherit; color:#e8f0ff; }
  .roomhead:active { filter:brightness(1.12); }
  .rmchev { color:#22d3ee; font-size:15px; width:13px; flex:none; }
  .rmname { font-size:16px; font-weight:900; letter-spacing:0.4px; flex:none; }
  .rmmeta { font-size:11.5px; font-weight:700; color:#8fa6c4; flex:1;
            white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .rmpts  { font-size:12.5px; font-weight:900; color:#7dd3fc; flex:none; }
  .roombody { padding:2px 10px 10px; }

  /* ---- filter-by-points bar + its popup ---- */"""
assert OLD4 in s, 'style anchor not found'
s = s.replace(OLD4, NEW4, 1)

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('chores.html: job board grouped into collapsible rooms')
