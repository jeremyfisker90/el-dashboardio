"""Bump the chores.html cache token in both lovelace configs.

The tablet and the phone dashboard load chores.html in an iframe with a ?v=
token. Without bumping it they keep serving the cached copy and a deploy is
invisible - the single most repeated failure in this project.
"""
import io
import json
import os
import re
import time

V = str(int(time.time() * 1000))
PAT = re.compile(r'(/local/chores\.html\?v=)\d+')

for src, out in (('dash_bump_in.json', 'dash_bump_out.json'),
                 ('phone_bump_in.json', 'phone_bump_out.json')):
    if not os.path.exists(src):
        continue
    raw = io.open(src, encoding='utf-8').read()
    hits = len(PAT.findall(raw))
    raw, n = PAT.subn(r'\g<1>' + V, raw)
    json.loads(raw)                      # never ship a file that won't parse
    tmp = out + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as fh:
        fh.write(raw)
    os.replace(tmp, out)
    print('%-22s %d token(s) -> %s' % (src, n, V))
