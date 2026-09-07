"""Two-column categories, title+points rows, and a detail popup per chore.

An expanded room was rendering full chore cards - description, frequency pill,
assignee, action buttons - which meant one room filled the screen and you were
scrolling again, which was the original complaint. The expanded room now lists
nothing but title and points; everything else moves into a popup that opens when
you tap a row, reusing the overlay the point filter already uses.

Categories sit in two columns so the whole list is visible without scrolling.
"""
import io
import os

P = 'chores.html'
s = io.open(P, encoding='utf-8').read()


def sub(old, new, what):
    global s
    if old not in s:
        raise SystemExit('anchor missing: ' + what)
    s = s.replace(old, new, 1)


# ---------------------------------------------------- compact room contents
sub("""        if (isOpen){
          html += '<div class="roombody">'
               + '<button class="roomback" onclick="closeRoom()">← All rooms</button>';
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
        }""",
    """        if (isOpen){
          // Title and points only. Everything else lives in the popup, so an
          // open room stays short enough to read without scrolling.
          const rowsOf = (list, cls) => list.map(c =>
            '<button class="jobrow ' + cls + '" onclick="openChore(' + c.id + ')">'
            + '<span class="jr-name">' + esc(c.name) + '</span>'
            + '<span class="jr-pts">' + (parseInt(c.points)||0) + '</span>'
            + '</button>').join('');
          html += '<div class="roombody">'
               + '<button class="roomback" onclick="closeRoom()">← All rooms</button>'
               + '<div class="joblist">'
               +   rowsOf(g.daily, 'is-daily')
               +   rowsOf(g.req, 'is-req')
               +   rowsOf(g.opt, 'is-opt')
               + '</div></div>';
        }""",
    'room body')

# ---------------------------------------------------- two-column category list
sub("""    if (!names.length){
      html += '<div class="empty">Every chore is queued or done. 🎉</div>';
    } else {""",
    """    if (!names.length){
      html += '<div class="empty">Every chore is queued or done. 🎉</div>';
    } else {
      // Two columns while browsing categories; a drilled-in room takes the
      // full width so its job list has room to breathe.
      html += '<div class="roomcols' + (OPEN_ROOM ? ' solo' : '') + '">';""",
    'open roomcols')

sub("""        html += '</div>';
      }
    }
  }
  html += '</div></div>';""",
    """        html += '</div>';
      }
      html += '</div>';
    }
  }
  html += '</div></div>';""",
    'close roomcols')

# ---------------------------------------------------- the chore detail popup
sub("""<div id="ptfilter" class="casino-ov" onclick="if(event.target===this)closePts()">""",
    """<div id="chorepop" class="casino-ov" onclick="if(event.target===this)closeChore()">
  <div class="club jobbox">
    <button class="club-x" onclick="closeChore()">✕</button>
    <div class="club-sign small" id="jobTitle">CHORE</div>
    <div class="entry-msg" id="jobSub"></div>
    <div id="jobBody"></div>
  </div>
</div>

<div id="ptfilter" class="casino-ov" onclick="if(event.target===this)closePts()">""",
    'popup markup')

sub("""function closePts(){ document.getElementById('ptfilter').classList.remove('show'); }""",
    """function closePts(){ document.getElementById('ptfilter').classList.remove('show'); }

// ===== one chore, everything about it =====
function closeChore(){ document.getElementById('chorepop').classList.remove('show'); }

function openChore(id){
  const c = (D.chores || []).find(x => x.id === id);
  if (!c) return;
  const held = (D.claims || []).filter(x => x.chore_id === id
                 && (x.state === 'queued' || x.state === 'done'));
  const mine = k => held.some(x => x.kid === k);

  document.getElementById('jobTitle').innerHTML = esc(c.name);
  document.getElementById('jobSub').innerHTML =
    (parseInt(c.points)||0) + ' ' + LED
    + (c.room ? ' · ' + esc(canonRoom(c.room)) : '')
    + ' · ' + (c.kind === 'optional' ? 'Optional' : 'Required');

  const takeBtn = (k, label, cls) => mine(k)
    ? '<button class="' + cls + ' taken" disabled>' + label + ' already has it</button>'
    : '<button class="' + cls + '" onclick="takeChore(' + id + ',&#39;' + k + '&#39;)">'
      + label + ': take it</button>';

  document.getElementById('jobBody').innerHTML =
      (c.description ? '<div class="jobdesc">' + esc(c.description) + '</div>' : '')
    + (held.length
        ? '<div class="jobheld">Working on it now: '
          + held.map(x => (PICK_LABEL[x.kid] || x.kid)
              + (x.state === 'done' ? ' (waiting on a parent)' : '')).join(', ')
          + '</div>'
        : '')
    + '<div class="jobacts">'
    +   takeBtn('ian', 'Ian', 'ian')
    +   takeBtn('evan', 'Evan', 'evan')
    +   takeBtn('parent', 'Parent', 'parent')
    + '</div>'
    + '<div class="jobacts sm">'
    +   '<button class="btn ghost" onclick="closeChore(); editChore(' + id + ')">Edit</button>'
    +   '<button class="btn ghost" onclick="closeChore(); delChore(' + id + ')">Delete</button>'
    + '</div>';

  document.getElementById('chorepop').classList.add('show');
}

// Taking a job creates a claim; the chore stays on the board for everyone else.
async function takeChore(id, kid){
  try { await api('/chores/claim', {id, kid}); }
  catch(e){ alert(e.detail || ('Could not take it: ' + e.status)); }
  closeChore();
  await load();
}""",
    'popup logic')

# ---------------------------------------------------- styles
sub('</style>',
    """
  /* ---- job board: two columns of categories, compact rows inside ---- */
  .roomcols { display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:0 9px;
              align-items:start; }
  .roomcols.solo { grid-template-columns:1fr; }

  .joblist { display:grid; grid-template-columns:repeat(auto-fill, minmax(210px,1fr));
             gap:6px; }
  .jobrow { display:flex; align-items:center; gap:9px; width:100%; padding:9px 11px;
            font-family:inherit; text-align:left; cursor:pointer; color:#e8f0ff;
            background:rgba(255,255,255,0.028); border-radius:10px;
            border:1px solid rgba(140,170,215,0.16); border-left:3px solid #8fa6c4; }
  .jobrow:active { filter:brightness(1.12); transform:translateY(1px); }
  .jobrow.is-daily { border-left-color:#7dd3fc; }
  .jobrow.is-req   { border-left-color:#ff9a6b; }
  .jobrow.is-opt   { border-left-color:#5fe0c6; }
  .jr-name { flex:1; font-size:13.5px; font-weight:800; }
  .jr-pts  { flex:none; font-size:14px; font-weight:900; color:#ffd76e; }

  /* ---- the chore popup ---- */
  .jobbox { width:min(430px,94vw); text-align:left; }
  .jobbox .club-sign { font-size:20px; letter-spacing:1.2px; text-align:center; }
  .jobbox .entry-msg { text-align:center; }
  .jobdesc { margin:12px 0 0; padding:11px 12px; font-size:13px; line-height:1.45;
             color:#cbd5e1; background:rgba(255,255,255,0.03); border-radius:10px;
             border:1px solid rgba(140,170,215,0.16); }
  .jobheld { margin:10px 0 0; font-size:12px; font-weight:800; color:#fbbf24; }
  .jobacts { display:flex; gap:7px; margin-top:13px; flex-wrap:wrap; }
  .jobacts.sm { margin-top:9px; justify-content:flex-end; }
  .jobacts button { flex:1 1 110px; padding:10px 12px; font-family:inherit;
                    font-size:13px; font-weight:900; border-radius:10px;
                    cursor:pointer; border:1px solid; }
  .jobacts.sm button { flex:0 0 auto; font-size:12px; padding:7px 12px; }
  .jobacts .ian    { color:#2dd4bf; border-color:#2dd4bf66; background:rgba(45,212,191,.10); }
  .jobacts .evan   { color:#fbbf24; border-color:#fbbf2466; background:rgba(251,191,36,.10); }
  .jobacts .parent { color:#d8b4fe; border-color:#d8b4fe66; background:rgba(216,180,254,.10); }
  .jobacts .taken  { opacity:.45; cursor:default; }
</style>""",
    'popup styles')

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('board: 2-column categories, title+points rows, chore popup')
