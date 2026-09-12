"""Turn on yolo mode for the Claude conversation agent.

The entry's options were {} - the integration's defaults leave every privileged
tool off, so the agent could hear a request, understand it, and then have no
tool with which to act. That is exactly the "listened and did nothing" symptom.

Writing the tool list explicitly rather than relying on the yolo_mode flag
alone, so the enabled set is visible in the entry instead of implied by a
default that a future version could change.
"""
import io
import json
import os

# every tool the integration defines; the seven privileged ones are the reason
# for this change
ALL_TOOLS = [
    "add_automation", "call_service", "get_calendar_events", "get_error_log",
    "get_history", "get_logbook", "get_statistics", "internet_lookup",
    "list_automations", "manage_list", "modify_dashboard", "render_template",
    "send_notification", "set_model", "toggle_automation", "who_is_home",
]

P = 'ce_live.json'
doc = json.load(io.open(P, encoding='utf-8'))

found = 0
for e in doc['data']['entries']:
    if e.get('domain') != 'ai_subscription_assist':
        continue
    found += 1
    opts = dict(e.get('options') or {})
    opts['yolo_mode'] = True
    opts['enabled_tools'] = ALL_TOOLS
    e['options'] = opts
    print('entry:', e.get('title'), e.get('entry_id'))
    print('  yolo_mode    :', opts['yolo_mode'])
    print('  enabled_tools:', len(opts['enabled_tools']), 'tools')

if not found:
    raise SystemExit('no ai_subscription_assist entry found')

tmp = 'ce_new.json.tmp'
with io.open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, separators=(',', ':'))
os.replace(tmp, 'ce_new.json')
print('bytes:', os.path.getsize('ce_new.json'))
