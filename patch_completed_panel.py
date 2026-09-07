"""Move completed work out of the queue columns and behind one top button.

The right-hand column was carrying two jobs at once - what's still to do, and
everything already finished - so the queues kept getting pushed off screen by a
week's worth of banked work. The queues now show only open work; completed jobs
and the three weekly totals live behind a "Completed Jobs" button at the top.
"""
import io
import os

P = 'chores.html'
s = io.open(P, encoding='utf-8').read()

# ------------------------------------------------- strip from the kid panels
OLD = """      + (doneK.length
          ? '<div class="ksub donesub ' + k + '">✅ COMPLETED TODAY'
            + '<span class="kcount">' + doneK.length + ' done · ' + donePts + ' pts</span></div>'
            + doneK.map(doneCard).join('')
          : '')
      + (bank.length
          ? '<div class="ksub donesub ' + k + '">🏦 EARNED THIS WEEK'
            + '<span class="kcount">' + bank.length + ' job' + (bank.length === 1 ? '' : 's')
            + ' · ' + bankPts + ' pts</span></div>'
            + bank.map(e => bankRow(e, kcol)).join('')
          : '')
      + '</div></div>';"""
NEW = """      + '</div></div>';"""
assert OLD in s, 'kid completed block not found'
s = s.replace(OLD, NEW, 1)

# the locals it used are now dead weight in kidPanel
OLD = """    const doneK = done.filter(c => c.done_by === k)
        .slice().sort((a,b) => String(doneTime(b)||'').localeCompare(String(doneTime(a)||'')));
    const donePts = doneK.reduce((s, c) => s + (parseInt(c.points) || 0), 0);
    // Everything banked since Monday, newest first. Chore-day stamps only exist
    // on entries claimed after this shipped; older ones just sort last.
    const bank = ((D.log || {})[k] || []).slice()
        .sort((a,b) => String(b.at || b.on || '').localeCompare(String(a.at || a.on || '')));
    const bankPts = bank.reduce((s, e) => s + (parseInt(e.points) || 0), 0);
    const kcol = k === 'ian' ? '#2dd4bf' : '#fbbf24';
"""
NEW = """    const doneK = done.filter(c => c.done_by === k);
"""
assert OLD in s, 'kid panel locals not found'
s = s.replace(OLD, NEW, 1)

# ------------------------------------------------- strip from the parent panel
OLD = """      + (doneP.length
          ? '<div class="ksub donesub parentq">✅ CLOSED TODAY'
            + '<span class="kcount">' + doneP.length + ' done · '
            + doneP.reduce((a,c)=>a+(parseInt(c.points)||0),0) + ' pts</span></div>'
            + doneP.map(doneCard).join('')
          : '')
      + (pBank.length
          ? '<div class="ksub donesub parentq">🗄️ CLOSED THIS WEEK'
            + '<span class="kcount">' + pBank.length + ' job'
            + (pBank.length === 1 ? '' : 's') + ' · ' + pBankPts + ' pts</span></div>'
            + pBank.map(e => bankRow(e, '#d8b4fe')).join('')
          : '')
      + '</div></div>';"""
NEW = """      + '</div></div>';"""
assert OLD in s, 'parent completed block not found'
s = s.replace(OLD, NEW, 1)

OLD = """    // Closed work comes off the weekly log, so it survives the 6am roll
    // instead of clearing every morning like the live chore list does.
    const pBank = ((D.log || {}).parent || []).slice()
        .sort((a,b) => String(b.at || b.on || '').localeCompare(String(a.at || a.on || '')));
    const pBankPts = pBank.reduce((s,e) => s + (parseInt(e.points)||0), 0);
"""
assert OLD in s, 'parent bank locals not found'
s = s.replace(OLD, '', 1)

# ------------------------------------------------- the new panel + its button
OLD = """  html += '<button class="adhoc-btn" onclick="adhocChore()">🎯 Ad-Hoc Chore Addition</button>';"""
NEW = """  // Completed work, all three people, behind one button. Off by default so the
  // board opens on what still needs doing.
  {
    const totalDone = ((D.log||{}).ian||[]).length + ((D.log||{}).evan||[]).length
                    + ((D.log||{}).parent||[]).length;
    html += '<button class="done-btn' + (SHOW_DONE ? ' on' : '') + '" onclick="toggleCompleted()">'
         +   '<span>' + (SHOW_DONE ? '▾' : '▸') + ' ✅ Completed Jobs</span>'
         +   '<span class="db-tot">'
         +     '<span style="color:#2dd4bf">Ian ' + (tot.ian||0) + '</span>'
         +     '<span style="color:#fbbf24">Evan ' + (tot.evan||0) + '</span>'
         +     '<span style="color:#d8b4fe">Parents ' + (tot.parent||0) + '</span>'
         +   '</span>'
         + '</button>';

    if (SHOW_DONE){
      // A parent still needs undo/reject on today's work, so live chore cards
      // render above the week's banked rows rather than instead of them.
      const section = (key, label, colour) => {
        const liveCards = done.filter(c => c.done_by === key)
          .slice().sort((a,b) => String(doneTime(b)||'').localeCompare(String(doneTime(a)||'')));
        const bank = ((D.log||{})[key]||[]).slice()
          .sort((a,b) => String(b.at||b.on||'').localeCompare(String(a.at||a.on||'')));
        const pts = tot[key] || 0;
        return '<div class="donecol">'
          + '<div class="donecol-head" style="border-color:' + colour + '77">'
          +   '<span class="dc-name" style="color:' + colour + '">' + label + '</span>'
          +   '<span class="dc-pts" style="color:' + colour + '">' + pts + ' pts</span>'
          +   '<span class="dc-sub">' + bank.length + ' job' + (bank.length===1?'':'s')
          +     ' this week</span>'
          + '</div>'
          + (liveCards.length
              ? '<div class="ksub donesub">✅ TODAY</div>' + liveCards.map(doneCard).join('')
              : '')
          + (bank.length
              ? '<div class="ksub donesub">🏦 THIS WEEK</div>'
                + bank.map(e => bankRow(e, colour)).join('')
              : '<div class="empty">Nothing banked yet this week.</div>')
          + '</div>';
      };
      html += '<div class="panel donep"><div class="phead">✅ Completed Jobs'
           +   '<span class="note">' + totalDone + ' banked this week · resets Monday</span>'
           + '</div><div class="pbody"><div class="donecols">'
           +   section('ian', 'Ian', '#2dd4bf')
           +   section('evan', 'Evan', '#fbbf24')
           +   section('parent', 'Parents', '#d8b4fe')
           + '</div></div></div>';
    }
  }

  html += '<button class="adhoc-btn" onclick="adhocChore()">🎯 Ad-Hoc Chore Addition</button>';"""
assert OLD in s, 'adhoc button anchor not found'
s = s.replace(OLD, NEW, 1)

# ------------------------------------------------- state
OLD = "const NO_ROOM = 'Anywhere';"
NEW = """let SHOW_DONE = false;
function toggleCompleted(){ SHOW_DONE = !SHOW_DONE; render(); }

const NO_ROOM = 'Anywhere';"""
assert OLD in s, 'state anchor not found'
s = s.replace(OLD, NEW, 1)

# ------------------------------------------------- styles
OLD = '  /* ---- room accordion on the job board ---- */'
NEW = """  /* ---- completed-jobs button + its three columns ---- */
  .done-btn { display:flex; align-items:center; justify-content:space-between; gap:10px;
              width:calc(100% - 4px); margin:0 2px 10px; padding:13px 16px;
              font-family:inherit; font-size:15px; font-weight:900; letter-spacing:0.4px;
              color:#dbeafe; background:rgba(12,18,34,0.78); cursor:pointer;
              border:1px solid rgba(120,150,190,0.3); border-radius:13px; }
  .done-btn.on { border-color:rgba(34,211,238,0.5);
                 box-shadow:0 0 14px rgba(34,211,238,0.16); }
  .done-btn:active { transform:translateY(1px); filter:brightness(1.1); }
  .db-tot { display:flex; gap:12px; font-size:13px; font-weight:900; }
  .donecols { display:grid; grid-template-columns:repeat(auto-fit, minmax(230px, 1fr));
              gap:12px; }
  .donecol-head { display:flex; align-items:baseline; gap:8px; padding:8px 10px;
                  margin:0 0 8px; border:1px solid; border-radius:10px;
                  background:rgba(255,255,255,0.03); }
  .dc-name { font-size:15px; font-weight:900; }
  .dc-pts  { font-size:14px; font-weight:900; margin-left:auto; }
  .dc-sub  { font-size:11px; font-weight:700; color:#8fa6c4; width:100%; }

  /* ---- room accordion on the job board ---- */"""
assert OLD in s, 'style anchor not found'
s = s.replace(OLD, NEW, 1)

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('chores.html: completed jobs moved behind a top button')
