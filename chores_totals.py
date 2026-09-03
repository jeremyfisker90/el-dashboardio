#!/usr/bin/env python3
"""Weekly points totals -> HA command_line sensor (for the Chores dashboard tile).

Reads the chores add-on's own API, so it reflects chores added from the dashboard,
from Cozi, or from the shared spreadsheet alike.
"""
import json
import sys
import urllib.request

URL = "http://192.168.1.226:5000/chores"
HIST_URL = "http://192.168.1.226:5000/chores/history"
TIMEOUT = 15

PLACEHOLDER = {
    "state": "—", "ok": False, "ian": 0, "evan": 0, "target": 100,
    "required_left": 0, "required_total": 0, "optional_unlocked": True,
    "open_required": 0, "open_optional": 0,
    "done_ian": 0, "done_evan": 0, "pts_open": 0,
    "leader": "", "streak_kid": "", "streak_weeks": 0,
    "last_kid": "", "last_ian": 0, "last_evan": 0, "last_week_start": "",
    "total_ian": 0, "total_evan": 0, "total_weeks": 1,
    "pending": 0, "queued_ian": 0, "queued_evan": 0,
}


def hist_stats():
    """Stats from CLOSED weeks only.

    Returns (streak_kid, streak_weeks, hist_ian, hist_evan, hist_weeks, last).
    `last` describes the most recently closed week, which is what the Grand
    Champion badge shows: {kid, ian, evan, week_start}. The badge deliberately
    reports the previous week rather than the week in progress, so the title is
    settled rather than changing every time somebody finishes a chore.
    """
    try:
        with urllib.request.urlopen(HIST_URL, timeout=TIMEOUT) as r:
            hist = json.loads(r.read().decode("utf-8")).get("history") or []
    except Exception:
        return "", 0, 0, 0, 0, {}
    hi = sum(int((h.get("totals") or {}).get("ian", 0)) for h in hist)
    he = sum(int((h.get("totals") or {}).get("evan", 0)) for h in hist)
    kid, weeks = "", 0
    for h in reversed(hist):
        t = h.get("totals") or {}
        i, e = int(t.get("ian", 0)), int(t.get("evan", 0))
        if i == e:
            break
        w = "ian" if i > e else "evan"
        if not kid:
            kid = w
        if w != kid:
            break
        weeks += 1
    last = {}
    if hist:
        lt = hist[-1].get("totals") or {}
        li, le = int(lt.get("ian", 0)), int(lt.get("evan", 0))
        last = {"kid": "" if li == le else ("ian" if li > le else "evan"),
                "ian": li, "evan": le,
                "week_start": hist[-1].get("week_start") or ""}
    return kid, weeks, hi, he, len(hist), last


def main():
    out = dict(PLACEHOLDER)
    try:
        with urllib.request.urlopen(URL, timeout=TIMEOUT) as r:
            d = json.loads(r.read().decode("utf-8"))
        tot = d.get("totals") or {}
        chores = d.get("chores") or []
        out.update({
            "ok": True,
            "ian": int(tot.get("ian", 0)),
            "evan": int(tot.get("evan", 0)),
            "target": int(d.get("target", 100)),
            "required_left": int(d.get("required_left", 0)),
            "required_total": int(d.get("required_total", 0)),
            "optional_unlocked": bool(d.get("optional_unlocked", True)),
            "open_required": len([c for c in chores
                                  if c.get("kind", "required") != "optional" and not c.get("done_by")]),
            "open_optional": len([c for c in chores
                                  if c.get("kind") == "optional" and not c.get("done_by")]),
            "done_ian": len([c for c in chores if c.get("done_by") == "ian"]),
            "done_evan": len([c for c in chores if c.get("done_by") == "evan"]),
            "pts_open": sum(int(c.get("points", 0)) for c in chores
                            if not c.get("done_by") and c.get("posted") is not False),
            "pending": len([c for c in chores
                            if c.get("rejected") and not c.get("done_by")]),
            # jobs sitting in each kid's queue (rejected redos count too)
            "queued_ian": len([c for c in chores if not c.get("done_by")
                               and (c.get("queued_for") == "ian"
                                    or (c.get("rejected") or {}).get("kid") == "ian")]),
            "queued_evan": len([c for c in chores if not c.get("done_by")
                                and (c.get("queued_for") == "evan"
                                     or (c.get("rejected") or {}).get("kid") == "evan")]),
        })
        out["leader"] = ("ian" if out["ian"] > out["evan"]
                         else "evan" if out["evan"] > out["ian"] else "")
        sk, sw, hi, he, hw, last = hist_stats()
        out["streak_kid"], out["streak_weeks"] = sk, sw
        out["last_kid"] = last.get("kid", "")
        out["last_ian"] = int(last.get("ian", 0))
        out["last_evan"] = int(last.get("evan", 0))
        out["last_week_start"] = last.get("week_start", "")
        out["total_ian"] = hi + out["ian"]
        out["total_evan"] = he + out["evan"]
        out["total_weeks"] = hw + 1
        out["state"] = "Ian %d / Evan %d" % (out["ian"], out["evan"])
    except Exception as exc:
        out["state"] = "unavailable"
        out["error"] = str(exc)[:100]
    sys.stdout.write(json.dumps(out))


if __name__ == "__main__":
    main()
