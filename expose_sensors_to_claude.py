"""Expose sensors to the conversation agent only.

Home Assistant tracks exposure per assistant. Google Home keeps its curated 56 -
it chokes on sensors and that list was pruned this morning for a reason - while
the "conversation" key controls what Claude can see. Sensors are exactly where
an LLM earns its keep: it can already switch a light, but it could not tell you
the brisket temperature or whether a window was open.

Spook's 53 meta-counters are skipped. They count Home Assistant's own objects
("sensor.lights = 18", "sensor.areas = 17") and describe the software, not the
house, so they cost prompt space and invite confusion for no benefit.
"""
import io
import json
import os

SRC_EE = 'ee9.json'
SRC_ER = 'er8b.json'
OUT = 'ee_sensors.json'

SKIP_PLATFORMS = {'spook', 'spook_inverse'}

reg = json.load(io.open(SRC_ER, encoding='utf-8'))['data']['entities']
targets = [
    e['entity_id'] for e in reg
    if e['entity_id'].startswith(('sensor.', 'binary_sensor.'))
    and not e.get('disabled_by')
    and not e.get('hidden_by')
    and e.get('platform') not in SKIP_PLATFORMS
]

doc = json.load(io.open(SRC_EE, encoding='utf-8'))
ent = doc['data']['exposed_entities']

added = 0
for eid in targets:
    rec = ent.setdefault(eid, {}).setdefault('assistants', {})
    if not rec.get('conversation', {}).get('should_expose'):
        added += 1
    # only the conversation key is touched; Google and Alexa keep their settings
    rec['conversation'] = {'should_expose': True}

tmp = OUT + '.tmp'
with io.open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, separators=(',', ':'))
os.replace(tmp, OUT)

goog = sum(1 for v in ent.values()
           if v.get('assistants', {}).get('cloud.google_assistant', {}).get('should_expose'))
conv = sum(1 for v in ent.values()
           if v.get('assistants', {}).get('conversation', {}).get('should_expose'))
print('sensors newly exposed to conversation:', added)
print('total exposed to conversation        :', conv)
print('still exposed to Google Home         :', goog, '(unchanged)')
print('bytes:', os.path.getsize(OUT))
