"""Point the board at claims instead of chore state.

The chore rows no longer carry done_by / queued_for / posted, so every list the
page derived from them has to come off D.claims. The board itself becomes the
full catalogue - it never shrinks, because taking a job no longer removes it.
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


# ------------------------------------------------------------- derived lists
sub('''  const all = D.chores || [];
  const posted = all.filter(c=>c.posted !== false);
  const later  = all.filter(c=>c.posted === false && !c.done_by);
  const pend = posted.filter(c=>!c.done_by && c.rejected);
  const open = posted.filter(c=>!c.done_by && !c.rejected);
  const qFor = c => c.queued_for || 'na';
  const qIan  = open.filter(c=>qFor(c)==='ian');
  const qEvan = open.filter(c=>qFor(c)==='evan');
  const qParent = open.filter(c=>qFor(c)==='parent');
  const board = open.filter(c=>['ian','evan','parent'].indexOf(qFor(c)) < 0);
  const reqAll = board.filter(c=>c.kind !== 'optional');
  const opt  = board.filter(c=>c.kind === 'optional');
  // short-cycle required chores get their own block at the very top of the board.
  // Walk the dog is pinned first, then the rest of the dailies, then the 2-day jobs.
  const isShort = c => ['daily','2-day'].indexOf(String(c.frequency||'').toLowerCase()) >= 0;
  const dogFirst = (a,b) => {
    const dog = c => /walk the dog/i.test(c.name||'') ? 0 : 1;
    if (dog(a) !== dog(b)) return dog(a) - dog(b);
    const rank = c => String(c.frequency||'').toLowerCase() === 'daily' ? 0 : 1;
    if (rank(a) !== rank(b)) return rank(a) - rank(b);
    return String(a.name||'').localeCompare(String(b.name||''));
  };
  const daily = reqAll.filter(isShort).slice().sort(dogFirst);
  const req   = reqAll.filter(c=>!isShort(c));
  // finished by a kid but not yet signed off by a parent
  const awaiting = all.filter(c=>c.done_by && !c.approved);
  // parent-approved -> these are the ones that show in COMPLETED JOBS
  const done = all.filter(c=>c.done_by && c.approved);
  const unlocked = !!D.optional_unlocked;''',
    '''  const all = D.chores || [];
  const claims = D.claims || [];
  // The board is the whole catalogue now. Taking a job creates a claim; it never
  // removes the chore, which is what lets both kids hold the same one at once.
  const board = all;
  const req = board.filter(c => c.kind !== 'optional');
  const opt = board.filter(c => c.kind === 'optional');
  const daily = [];                       // no schedule, so no daily block
  const later = [];                       // and nothing is ever "not due yet"
  const isShort = () => false;

  const openClaims = claims.filter(c => c.state === 'queued');
  const pend    = openClaims.filter(c => c.rejected);       // sent back to redo
  const qIan    = openClaims.filter(c => c.kid === 'ian'    && !c.rejected);
  const qEvan   = openClaims.filter(c => c.kid === 'evan'   && !c.rejected);
  const qParent = openClaims.filter(c => c.kid === 'parent' && !c.rejected);
  const awaiting = claims.filter(c => c.state === 'done');   // waiting on a parent
  const done     = claims.filter(c => c.state === 'approved');
  const unlocked = true;
  // How many open claims each kid holds on a given chore - drives the "in your
  // queue" marker on a board card that is still sitting there.
  const heldBy = (chore, kid) =>
    openClaims.filter(c => c.chore_id === chore.id && c.kid === kid).length;''',
    'derived lists')

# ------------------------------------------------------- claims carry the kid
sub('''    const w = isFix ? (c.rejected && c.rejected.kid) || 'na' : (c.queued_for || 'na');''',
    '''    const w = isFix ? (c.rejected && c.rejected.kid) || 'na' : (c.kid || 'na');''',
    'queueCard owner')

for old, new, what in (
    ("""    const col = c.done_by === 'ian' ? '#2dd4bf' : c.done_by === 'parent' ? '#a855f7' : '#fbbf24';
    const nm  = c.done_by === 'ian' ? 'Ian' : c.done_by === 'parent' ? 'Parent' : 'Evan';
    return '<div class="chore qmini awaitmini who-' + c.done_by + '" style="border-color:' + col + '99">'""",
     """    const col = c.kid === 'ian' ? '#2dd4bf' : c.kid === 'parent' ? '#a855f7' : '#fbbf24';
    const nm  = c.kid === 'ian' ? 'Ian' : c.kid === 'parent' ? 'Parent' : 'Evan';
    return '<div class="chore qmini awaitmini who-' + c.kid + '" style="border-color:' + col + '99">'""",
     'awaitCard'),
    ("""    const col = c.done_by === 'ian' ? '#2dd4bf'
              : c.done_by === 'parent' ? '#a855f7' : '#fbbf24';
    const nm  = c.done_by === 'ian' ? 'Ian'
              : c.done_by === 'parent' ? 'Parent' : 'Evan';
    return '<div class="chore qmini donemini who-' + c.done_by + '" style="border-color:' + col + '77">'""",
     """    const col = c.kid === 'ian' ? '#2dd4bf'
              : c.kid === 'parent' ? '#a855f7' : '#fbbf24';
    const nm  = c.kid === 'ian' ? 'Ian'
              : c.kid === 'parent' ? 'Parent' : 'Evan';
    return '<div class="chore qmini donemini who-' + c.kid + '" style="border-color:' + col + '77">'""",
     'doneCard'),
):
    sub(old, new, what)

sub("""        const liveCards = done.filter(c => c.done_by === key)""",
    """        const liveCards = done.filter(c => c.kid === key)""",
    'completed panel filter')

# ------------------------------------------------------------- banked+pending
sub("""    const val = tot[k] || 0;""",
    """    const val = tot[k] || 0;
    const pendPts = (D.pending || {})[k] || 0;""",
    'kid pending')

sub("""      + '<span class="kpts">' + val + ' <small>/ ' + t + '</small></span>'""",
    """      + '<span class="kpts">' + val + ' <small>/ ' + t + '</small>'
      +   (pendPts ? '<em class="pendpts">+' + pendPts + ' pending</em>' : '') + '</span>'""",
    'kid points header')

sub("""      + '<span class="kpts" style="color:#d8b4fe">' + pPts + ' <small>pts</small></span>'""",
    """      + '<span class="kpts" style="color:#d8b4fe">' + pPts + ' <small>pts</small>'
      +   (((D.pending||{}).parent) ? '<em class="pendpts">+' + D.pending.parent
            + ' pending</em>' : '') + '</span>'""",
    'parent points header')

sub("""         +     '<span style="color:#2dd4bf">Ian ' + (tot.ian||0) + '</span>'
         +     '<span style="color:#fbbf24">Evan ' + (tot.evan||0) + '</span>'
         +     '<span style="color:#d8b4fe">Parents ' + (tot.parent||0) + '</span>'""",
    """         +     '<span style="color:#2dd4bf">Ian ' + (tot.ian||0) + pendTag('ian') + '</span>'
         +     '<span style="color:#fbbf24">Evan ' + (tot.evan||0) + pendTag('evan') + '</span>'
         +     '<span style="color:#d8b4fe">Parents ' + (tot.parent||0) + pendTag('parent') + '</span>'""",
    'completed button totals')

sub("""  const grid = cards => '<div class="grid">' + cards.join('') + '</div>';""",
    """  const grid = cards => '<div class="grid">' + cards.join('') + '</div>';
  // "35 pts · 30 waiting on a parent" - shortened to a +N tag so it fits.
  const pendTag = k => { const p = (D.pending || {})[k] || 0;
                         return p ? ' <em class="pendpts">+' + p + '</em>' : ''; };""",
    'pendTag helper')

# ------------------------------------------------------------------- styles
sub('  /* ---- completed-jobs button + its three columns ---- */',
    """  .pendpts { font-style:normal; font-size:11px; font-weight:800; color:#fbbf24;
              margin-left:5px; opacity:.9; }

  /* ---- completed-jobs button + its three columns ---- */""",
    'pending style')

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('chores.html: lists, cards and headers moved onto claims')
