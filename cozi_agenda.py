#!/usr/bin/env python3
"""Live Cozi appointments -> sensor.cozi_live, in the exact schema the tablet's
schedule rail (sensor.today_schedule + its SCHEDULE_JS) already expects:

    events = [{summary: 'Name: desc', start: ISO, end: ISO, cal: 'cozi'}, ...]

`Name` is a household first name so the rail's who() colours it per person. This
reads Cozi DIRECTLY from the add-on (no Google in the path), so the rail can show
Cozi appointments within a minute instead of waiting hours for Cozi->Google.
"""
import datetime
import json
import sys
import urllib.request

ADDON = "http://YOUR_HA_IP:5000"
DAYS = 14

# Cozi household member id -> the first-name key the rail's who() understands
# (Tom/Mom/Ian/Evan map to colours; Loki the dog is left off -> Family grey).
MEMBERS = {
    "26d73760-41ef-496f-b426-adfac51b9f5e": "Dad",
    "7cd5c3ac-3ae4-4228-94b8-44138996c8f4": "Mom",
    "4c16b999-cbf5-4bad-8161-068882eabc54": "Evan",
    "1a4d1dae-6eae-452d-84d0-509078eca5f8": "Ian",
}


def _get(url):
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=DAYS)
    events, seen = [], set()
    d = today.replace(day=1)
    for _ in range(3):                       # this month + the next two
        try:
            data = _get("%s/cozi/calendar/%d/%d" % (ADDON, d.year, d.month))
        except Exception:
            data = {}
        for k, it in (data.get("items") or {}).items():
            if it.get("itemType", "appointment") != "appointment":
                continue
            day = it.get("day")
            if not day:
                continue
            key = (it.get("id") or k) + "|" + day
            if key in seen:
                continue
            seen.add(key)
            try:
                dd = datetime.date.fromisoformat(day)
            except Exception:
                continue
            if dd < today or dd > horizon:
                continue
            desc = it.get("description") or it.get("descriptionShort") or "(appointment)"
            mems = [MEMBERS[m] for m in (it.get("householdMembers") or []) if m in MEMBERS]
            summary = "%s: %s" % (mems[0], desc) if len(mems) == 1 else desc
            st = it.get("startTime")
            if st:
                start = day + "T" + st
                end = day + "T" + it["endTime"] if it.get("endTime") else start
            else:
                start = end = day            # all-day (length 10 -> rail shows "All day")
            events.append({"summary": summary, "start": start, "end": end, "cal": "cozi"})
        d = (d.replace(day=28) + datetime.timedelta(days=7)).replace(day=1)
    events.sort(key=lambda e: e["start"])
    sys.stdout.write(json.dumps({"state": str(len(events)), "events": events}))


if __name__ == "__main__":
    main()
