"""Rename the Lighting tile to "Smart" and drop the cat-gap state.

The isometric view stopped being about lights a while ago - it carries media,
the thermostat and now switches - so "Lighting" undersells it.

The cat gap was a workaround for having no position sensor on the 1-car door:
a boolean a human had to remember to flip, which made the tile lie whenever they
forgot. Both doors now read the same way, straight off the Alarm.com cover.
"""
import io
import json
import os
import re

doc = json.load(io.open('dash5.json', encoding='utf-8'))
cfg = doc['data']['config']
rail = cfg['views'][0]['cards'][0]['cards'][1]['cards'][4]

# ---------------------------------------------------------------- 1. rename
tile = rail['cards'][0]
assert (tile.get('tap_action') or {}).get('navigation_path', '').endswith('/lighting')
before = tile['custom_fields']['m']
after = before.replace('>Lighting<', '>Smart<')
if after == before:
    raise SystemExit('Lighting label not found in the tile')
tile['custom_fields']['m'] = after
print('rail tile: Lighting -> Smart')

# ---------------------------------------------------------- 2. cat gap gone
blob = json.dumps(doc)
print('cat_gap references before:', blob.count('cat_gap'))


def strip_cat(node):
    """Rewrite the 1-car garage button so it reads like the 2-car one."""
    n = 0
    if isinstance(node, dict):
        cf = node.get('custom_fields')
        if isinstance(cf, dict) and isinstance(cf.get('b'), str) and 'cat_gap' in cf['b']:
            js = cf['b']
            # the cat branch is a single statement; neutralise it and let the
            # existing open/closed logic stand
            js = re.sub(r"var cg=states\['input_boolean\.cat_gap'\];"
                        r"var isCat=open&&cg&&cg\.state==='on';",
                        "var isCat=false;", js)
            cf['b'] = js
            n += 1
        tu = node.get('triggers_update')
        if isinstance(tu, list) and 'input_boolean.cat_gap' in tu:
            node['triggers_update'] = [x for x in tu if x != 'input_boolean.cat_gap']
        for v in list(node.values()):
            n += strip_cat(v)
    elif isinstance(node, list):
        # drop the standalone CAT GAP toggle card entirely
        keep = []
        for item in node:
            s = json.dumps(item) if isinstance(item, (dict, list)) else ''
            if isinstance(item, dict) and item.get('entity') == 'input_boolean.cat_gap' \
                    and 'custom_fields' in item and 'c' in item.get('custom_fields', {}):
                n += 1
                continue
            keep.append(item)
        node[:] = keep
        for item in node:
            n += strip_cat(item)
    return n


hits = strip_cat(cfg)
blob = json.dumps(doc)
print('cat button edits:', hits, '| cat_gap references after:', blob.count('cat_gap'))

tmp = 'dash_smart.json.tmp'
with io.open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, separators=(',', ':'))
os.replace(tmp, 'dash_smart.json')
print('bytes:', os.path.getsize('dash_smart.json'))
