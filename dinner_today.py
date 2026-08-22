#!/usr/bin/env python3
"""Today's planned dinner -> HA command_line sensor (for the meal-plan tile).

Reads the Cozi "Dinners" list through the chores add-on. Items look like
"Friday: Salmon"; the day name is matched case-insensitively.
"""
import datetime
import json
import sys
import urllib.request

URL = "http://192.168.1.226:5000/lists"
TIMEOUT = 15
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def main():
    out = {"state": "none", "meal": ""}
    try:
        with urllib.request.urlopen(URL, timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8"))
        lists = data if isinstance(data, list) else data.get("lists", [])
        dinners = [l for l in lists if (l.get("title") or "").lower() == "dinners"]
        lst = next((l for l in dinners if l.get("listType") == "shopping"),
                   dinners[0] if dinners else None)
        if lst:
            day = DAYS[datetime.date.today().weekday()].lower()
            for it in lst.get("items") or []:
                text = (it.get("text") or "").strip()
                if text.lower().startswith(day):
                    meal = text.split(":", 1)[1].strip() if ":" in text else ""
                    if meal:
                        out = {"state": meal[:80], "meal": meal}
                    break
    except Exception as exc:
        out["error"] = str(exc)[:100]
    sys.stdout.write(json.dumps(out))


if __name__ == "__main__":
    main()
