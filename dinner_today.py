#!/usr/bin/env python3
"""Today's planned dinner -> HA command_line sensor (for the meal-plan tile).

Reads the Cozi "Dinners" list through the chores add-on. Items look like
"Friday: Salmon"; the day name is matched case-insensitively.

The add-on's Cozi session lapses every few hours (sensor.cozi_live dips to 0
for a minute each time). A read that lands in that window used to print
"none" and blank the tile, so a 503 gets one /relogin + retry, and if the
add-on still can't answer, the last good copy of the list is used instead.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

ADDON = "http://YOUR_HA_IP:5000"
TIMEOUT = 15
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".dinners_cache.json")
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_lists():
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(ADDON + "/lists", timeout=TIMEOUT) as r:
                data = json.loads(r.read().decode("utf-8"))
            return data if isinstance(data, list) else data.get("lists", [])
        except urllib.error.HTTPError as exc:
            if exc.code != 503 or attempt == 2:
                raise
            req = urllib.request.Request(ADDON + "/relogin", data=b"", method="POST")
            urllib.request.urlopen(req, timeout=TIMEOUT).read()


def dinners_items():
    """Items of the shopping-type "Dinners" list, live or from the last good read."""
    try:
        lists = fetch_lists()
        dinners = [l for l in lists if (l.get("title") or "").lower() == "dinners"]
        lst = next((l for l in dinners if l.get("listType") == "shopping"),
                   dinners[0] if dinners else None)
        items = [it.get("text") or "" for it in (lst or {}).get("items") or []]
        try:
            with open(CACHE, "w", encoding="utf-8") as fh:
                json.dump(items, fh)
        except OSError:
            pass
        return items, None
    except Exception as exc:
        try:
            with open(CACHE, encoding="utf-8") as fh:
                return json.load(fh), "cached: " + str(exc)[:80]
        except (OSError, ValueError):
            raise exc


def main():
    out = {"state": "none", "meal": ""}
    try:
        items, note = dinners_items()
        if note:
            out["error"] = note
        day = DAYS[datetime.date.today().weekday()].lower()
        for text in items:
            text = text.strip()
            if text.lower().startswith(day):
                meal = text.split(":", 1)[1].strip() if ":" in text else ""
                if meal:
                    out.update({"state": meal[:80], "meal": meal})
                break
    except Exception as exc:
        out["error"] = str(exc)[:100]
    sys.stdout.write(json.dumps(out))


if __name__ == "__main__":
    main()
