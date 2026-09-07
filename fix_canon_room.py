"""Repair canonRoom, which lowercased room names and never re-capitalised them.

The title-casing used a regex whose backslashes were doubled on the way into the
file, so it matched nothing and every room rendered lower case. Rewritten without
a regex - there is no escaping to get wrong.
"""
import io
import os

P = 'chores.html'
lines = io.open(P, encoding='utf-8').read().split('\n')

start = next(i for i, l in enumerate(lines) if 'function canonRoom(v){' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == '}')

lines[start:end + 1] = [
    'function canonRoom(v){',
    "  const t = String(v || '').trim();",
    '  if (!t) return NO_ROOM;',
    '  // Title Case without a regex: "OUtdoors" and "outdoors" both land on',
    '  // "Outdoors" so a typo in the sheet cannot split a room in two.',
    "  return t.toLowerCase().split(' ').filter(Boolean)",
    '    .map(w => w.charAt(0).toUpperCase() + w.slice(1))',
    "    .join(' ');",
    '}',
]

out = '\n'.join(lines)
tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(out)
os.replace(tmp, P)
print('canonRoom rewritten without a regex')
