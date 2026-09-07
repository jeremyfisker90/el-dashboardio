"""Point the click handlers at claim ids.

approve / reject / done / unclaim all take a claim id now. The cards already
pass the right number - they render claims - but the handlers were still looking
the id up in D.chores to build their confirmation text, which found nothing.
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


# a claim lookup, next to the chore one
sub("""async function reject(id){
  const c = (D.chores||[]).find(x=>x.id===id) || {};
  const who = c.done_by === 'ian' ? 'Ian' : 'Evan';""",
    """const findClaim = id => (D.claims||[]).find(x=>x.id===id) || {};

async function reject(id){
  const c = findClaim(id);
  const who = PICK_LABEL[c.kid] || 'They';""",
    'reject lookup')

sub("""    accent:'#f43f5e', validate:pin=>pin===PARENT_CODE});
  if(!ok) return;
  const comment = prompt('What needs fixing? (this note shows on the chore)');""",
    """    accent:'#f43f5e', validate:pin=>pin===PARENT_CODE});
  if(!ok) return;
  const comment = prompt('What needs fixing? (this note shows on the chore)');""",
    'reject comment')

sub("""  const ok = await askCode({title:'🚫 Parent Code', sub:'Send <b>'+esc(c.name||'this chore')+'</b> back? '+who+' loses '+(c.points||0)+' '+LED+'.',""",
    """  const ok = await askCode({title:'🚫 Parent Code', sub:'Send <b>'+esc(c.name||'this chore')+'</b> back to '+who+'? Nothing was banked yet, so no points change.',""",
    'reject copy')

sub("""async function approveChore(id){
  const c = (D.chores||[]).find(x=>x.id===id) || {};
  const who = c.done_by === 'ian' ? 'Ian' : 'Evan';
  const ok = await askCode({title:'✅ Parent Code',
    sub:'Accept <b>'+esc(c.name||'this chore')+'</b> by '+who+'? It moves to '+who+'’s completed jobs.',""",
    """async function approveChore(id){
  const c = findClaim(id);
  const who = PICK_LABEL[c.kid] || 'them';
  const ok = await askCode({title:'✅ Parent Code',
    sub:'Accept <b>'+esc(c.name||'this chore')+'</b> by '+who+'? '+(c.points||0)+' '+LED+' move to '+who+' now.',""",
    'approve lookup')

# the kid's "Done ✓" button in their queue finishes a claim, it doesn't re-claim
sub("""            : '<button class="' + w + '" onclick="claim(' + c.id + ',&#39;' + w + '&#39;)">'
              + (w === 'ian' ? 'Ian' : 'Evan') + ': Done ✓</button>')
        + '<button class="release" onclick="queueChore(' + c.id + ',\\'na\\')">↩ Board</button></div>';""",
    """            : '<button class="' + w + '" onclick="markDone(' + c.id + ')">'
              + (w === 'ian' ? 'Ian' : 'Evan') + ': Done ✓</button>')
        + '<button class="release" onclick="unclaim(' + c.id + ')">↩ Drop it</button></div>';""",
    'queue done button')

# parents finish their own queued claim in one move
sub("""            ? '<button class="parent" onclick="parentDone(' + c.id + ')">Parent: Done ✓</button>'""",
    """            ? '<button class="parent" onclick="markDone(' + c.id + ', true)">Parent: Done ✓</button>'""",
    'parent done button')

# edit/delete on a queue card act on the chore behind the claim
sub("""      + '<button class="btn ghost" style="padding:5px 10px;font-size:12px" onclick="editChore(' + c.id + ')">Edit</button> '
      + '<button class="btn ghost" style="padding:5px 10px;font-size:12px" onclick="delChore(' + c.id + ')">Delete</button></div>'""",
    """      + '<button class="btn ghost" style="padding:5px 10px;font-size:12px" onclick="editChore(' + (c.chore_id || c.id) + ')">Edit</button> '
      + '<button class="btn ghost" style="padding:5px 10px;font-size:12px" onclick="delChore(' + (c.chore_id || c.id) + ')">Delete</button></div>'""",
    'queue edit/delete')

# markDone: kid finishes; a parent's own claim is approved in the same breath
sub("""async function unclaim(id){""",
    """// A kid finishing sends the claim to the parent queue. A parent finishing
// their own job needs no sign-off, so it approves straight through.
async function markDone(id, isParent){
  try {
    await api('/chores/done', {id});
    if (isParent) await api('/chores/approve', {id});
  } catch(e){ alert('Could not complete: ' + (e.detail||e.status)); }
  await load();
}

async function unclaim(id){""",
    'markDone')

# board filter popup: every chore is always available now
sub("""  const all = (D.chores || []).filter(c => c.posted !== false && !c.done_by);""",
    """  const all = D.chores || [];""",
    'showPts source')

sub("""    const q = c.queued_for || 'na';
    const where = q === 'ian' ? 'In Ian’s queue'
                : q === 'evan' ? 'In Evan’s queue' : 'On the board';""",
    """    const held = (D.claims||[]).filter(x => x.chore_id === c.id
                   && (x.state === 'queued' || x.state === 'done'));
    const q = held.length ? held[0].kid : 'na';
    const where = held.length
      ? held.map(x => PICK_LABEL[x.kid] || x.kid).join(' + ') + ' working on it'
      : 'On the board';""",
    'showPts where')

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('handlers repointed at claim ids')
