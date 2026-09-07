"""Make 'parent' a first-class destination for ad-hoc and assigned chores.

Both pickers offered only Ian and Evan, so the parent queue could only ever be
reached by rejecting a kid's work. Some jobs simply aren't a kid's to do.

Also gives the parent panel the same open/closed shape the kids have, and reads
the closed list off the weekly log so it survives the 6am roll instead of
emptying every morning.

Line-oriented on purpose: the prompt strings contain backslash escapes that get
mangled through a shell heredoc.
"""
import io
import os

P = 'chores.html'
lines = io.open(P, encoding='utf-8').read().split('\n')


def find(sub, start=0, needed=True):
    for i in range(start, len(lines)):
        if sub in lines[i]:
            return i
    if needed:
        raise SystemExit('anchor not found: ' + sub)
    return -1


# ---------------------------------------------------------------- pickers
# Both blocks are identical except for the line that follows them.
PICK_NEW = [
    "  const kid = pickAssignee();",
    "  if (!kid) return;",
]

first = find("const pick = prompt('Assign to who?")
assert 'try {' in lines[first + 4], lines[first + 4]
lines[first:first + 4] = PICK_NEW
# the second picker shifted up by two lines
second = find("const pick = prompt('Assign to who?", first + 1)
assert 'const who =' in lines[second + 4], lines[second + 4]
lines[second:second + 5] = PICK_NEW + ["  const who = PICK_LABEL[kid];"]

# assignNotify's own label line, just after its api() call
lbl = find("const who = kid === 'ian' ? 'Ian' : 'Evan';")
lines[lbl] = "    const who = PICK_LABEL[kid];"

# ---------------------------------------------------------------- helper
helper = """// Ian / Evan / Parent. Some jobs are not a kid's to do, so the parent queue is a
// real destination rather than somewhere chores only land after a rejection.
function pickAssignee(){
  const pick = prompt('Assign to who?' + String.fromCharCode(10, 10)
    + '  1 = Ian' + String.fromCharCode(10)
    + '  2 = Evan' + String.fromCharCode(10)
    + '  3 = Parent');
  if (pick === null) return null;
  const k = {'1':'ian', '2':'evan', '3':'parent'}[pick.trim()];
  if (!k){ alert('Enter 1, 2 or 3'); return null; }
  return k;
}
const PICK_LABEL = {ian: 'Ian', evan: 'Evan', parent: 'Parent'};
""".split('\n')

anchor = find('async function assignNotify(id){')
lines[anchor:anchor] = helper

# ------------------------------------------------- parent open/closed queue
# It returned '' when empty, so the parents' queue simply vanished. Give it the
# same always-present open/closed shape the kids' panels have.
i = find("if (!q.length && !doneP.length) return '';")
lines[i] = "    // Always render: an empty parent queue is information too."

i = find("const doneP = done.filter(c => c.done_by === 'parent')")
lines[i + 1] = (lines[i + 1] + "\n"
                "    // Closed work comes off the weekly log, so it survives the 6am roll\n"
                "    // instead of clearing every morning like the live chore list does.\n"
                "    const pBank = ((D.log || {}).parent || []).slice()\n"
                "        .sort((a,b) => String(b.at || b.on || '')"
                ".localeCompare(String(a.at || a.on || '')));\n"
                "    const pBankPts = pBank.reduce((s,e) => s + (parseInt(e.points)||0), 0);")

i = find("Nothing queued for the parents")
lines[i] = ("      + (!q.length ? '<div class=\"empty\">Nothing queued for the parents — "
            "assign one with 3 = Parent.</div>' : '')")

i = find("COMPLETED BY PARENTS")
lines[i] = "          ? '<div class=\"ksub donesub parentq\">✅ CLOSED TODAY'"

i = find("+ doneP.map(doneCard).join('')")
lines[i] = (lines[i] + "\n          : '')\n"
            "      + (pBank.length\n"
            "          ? '<div class=\"ksub donesub parentq\">🗄️ CLOSED THIS WEEK'\n"
            "            + '<span class=\"kcount\">' + pBank.length + ' job'\n"
            "            + (pBank.length === 1 ? '' : 's') + ' · ' + pBankPts + ' pts</span></div>'\n"
            "            + pBank.map(e => bankRow(e, '#d8b4fe')).join('')")

out = '\n'.join(lines)
tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(out)
os.replace(tmp, P)
print('chores.html patched: parent destination + open/closed parent queue')
