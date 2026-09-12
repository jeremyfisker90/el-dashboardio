"""Remove ai_subscription_assist so the official Anthropic integration can load.

Its manifest pins anthropic==0.78.0. HA's own anthropic integration needs a
newer SDK and dies importing it:

    ImportError: cannot import name 'BashCodeExecutionToolResultBlock'

Both cannot coexist, and the official one is the keeper. This also frees the
conversation.claude_conversation entity_id, which the third-party integration
is currently squatting on.
"""
import io
import json
import os

DOMAIN = 'ai_subscription_assist'

# ---------------------------------------------------------------- entries
doc = json.load(io.open('ce4.json', encoding='utf-8'))
entries = doc['data']['entries']
gone = [e['entry_id'] for e in entries if e.get('domain') == DOMAIN]
doc['data']['entries'] = [e for e in entries if e.get('domain') != DOMAIN]
print('config entries removed:', len(gone), gone)

with io.open('ce_rm.json.tmp', 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, separators=(',', ':'))
os.replace('ce_rm.json.tmp', 'ce_rm.json')

# ---------------------------------------------------------------- entities
er = json.load(io.open('er7.json', encoding='utf-8'))
ents = er['data']['entities']
before = len(ents)
er['data']['entities'] = [
    e for e in ents
    if e.get('platform') != DOMAIN and e.get('config_entry_id') not in gone
]
print('entities removed:', before - len(er['data']['entities']))

with io.open('er_rm.json.tmp', 'w', encoding='utf-8') as fh:
    json.dump(er, fh, separators=(',', ':'))
os.replace('er_rm.json.tmp', 'er_rm.json')
print('wrote ce_rm.json and er_rm.json')
