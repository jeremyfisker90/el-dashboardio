"""Execute the real render() against live data in every UI state.

node --check only proves the file parses. This actually runs the page against
the add-on's current payload, which is how the JSON.stringify onclick bug and
the dead title-case regex were both caught - neither was a syntax error.
"""
import io
import json
import os
import re
import subprocess
import urllib.request

HARNESS = """
globalThis.location = {protocol:'http:', hostname:'YOUR_HA_IP',
                       origin:'http://YOUR_HA_IP'};
const _el = {
  set innerHTML(v){ globalThis.__OUT = v; },
  get innerHTML(){ return globalThis.__OUT || ''; },
  addEventListener(){}, querySelectorAll: () => [], appendChild(){},
  style:{}, classList:{add(){}, remove(){}, toggle(){}} };
globalThis.window = globalThis;
globalThis.document = { getElementById: () => _el, querySelector: () => _el,
  querySelectorAll: () => [], createElement: () => _el, addEventListener(){},
  body:_el, documentElement:_el };
globalThis.localStorage = { getItem: () => null, setItem(){} };
globalThis.fetch = async () => ({ ok:true, json: async () => ({}) });
globalThis.alert = () => {}; globalThis.confirm = () => true;
globalThis.prompt = () => null;
globalThis.setInterval = () => 0; globalThis.setTimeout = () => 0;
globalThis.requestAnimationFrame = () => 0;
"""

CHECKS = """
D = __PAYLOAD__;
function run(tag){
  try { render(); return globalThis.__OUT || ''; }
  catch(e){ console.log(tag + ' FAILED: ' + e.message); return ''; }
}
function ok(label, cond){ console.log((cond ? '  PASS  ' : '  FAIL  ') + label); }

let o = run('default');
console.log('default render: ' + o.length + ' chars');
ok('queue bar present', o.indexOf('qbar') >= 0);
ok('neon shell applied', o.indexOf('neon lit') >= 0);
ok('right column gone', o.indexOf('colR') < 0);
ok('two-column wrapper gone', o.indexOf('class="cols"') < 0);
ok('casino line updated', o.indexOf('house wins') >= 0);
ok('room headers rendered', (o.match(/roomhead/g) || []).length > 1);
ok('no stale schedule copy', o.indexOf('Dailies come back') < 0);

SHOW_DONE = true;  o = run('completed');
ok('completed panel opens', o.indexOf('donecols') >= 0);
SHOW_DONE = false;

QUEUE_WHO = 'ian';    o = run('ian');
ok('ian queue opens', o.indexOf('Ian’S QUEUE') >= 0);
QUEUE_WHO = 'parent'; o = run('parent');
ok('parent queue opens', o.indexOf('PARENT QUEUE') >= 0);
QUEUE_WHO = null;

toggleRoomIdx(0); o = globalThis.__OUT;
ok('drill-down shows one room', (o.match(/roomhead/g) || []).length === 1);
ok('back button present', o.indexOf('roomback') >= 0);
closeRoom(); o = globalThis.__OUT;
ok('back returns to full list', (o.match(/roomhead/g) || []).length > 1);

const handlers = [...o.matchAll(/onclick="([a-zA-Z]+)\\(/g)].map(m => m[1]);
const missing = [...new Set(handlers)].filter(h => {
  try { return typeof eval(h) !== 'function'; } catch(e){ return true; }
});
ok('every onclick handler exists' + (missing.length ? ' -> ' + missing.join(', ') : ''),
   missing.length === 0);
"""


def main():
    src = io.open('chores.html', encoding='utf-8').read()
    js = re.search(r'<script[^>]*>(.*)</script>', src, re.S).group(1)
    payload = json.load(urllib.request.urlopen(
        'http://YOUR_HA_IP:5000/chores', timeout=30))
    checks = CHECKS.replace('__PAYLOAD__', json.dumps(payload))
    io.open('_smoke.js', 'w', encoding='utf-8').write(HARNESS + js + checks)
    r = subprocess.run(['node', '_smoke.js'], capture_output=True, text=True)
    print((r.stdout or '').strip())
    if r.stderr.strip():
        print('STDERR:', r.stderr.strip()[:600])
    os.remove('_smoke.js')


main()
