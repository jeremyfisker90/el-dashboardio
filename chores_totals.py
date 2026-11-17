#!/usr/bin/env python3
"""Weekly points totals -> HA command_line sensor (for the Chores dashboard tile).

Reads the chores add-on's own API, so it reflects chores added from the dashboard,
from Cozi, or from the shared spreadsheet alike.
"""
import json
import sys
import urllib.request

URL = "http://YOUR_HA_IP:5000/chores"
HIST_URL = "http://YOUR_HA_IP:5000/chores/history"
TIMEOUT = 15

PLACEHOLDER = {
    "state": "—", "ok": False, "ian": 0, "evan": 0, "target": 100,
    "required_left": 0, "required_total": 0, "optional_unlocked": True,
    "open_required": 0, "open_optional": 0,
    "done_ian": 0, "done_evan": 0, "pts_open": 0,
    "parent": 0,
    "leader": "", "streak_kid": "", "streak_weeks": 0,
    "last_kid": "", "last_ian": 0, "last_evan": 0, "last_week_start": "",
    "total_ian": 0, "total_evan": 0, "total_weeks": 1,
    "pending": 0, "queued_ian": 0, "queued_evan": 0,
    "awaiting": 0, "awaiting_pts": 0, "awaiting_list": [], "unfinished": 0,
    "min_ian": 0, "min_evan": 0, "pay_ian": 0, "pay_evan": 0,
    "capped_ian": False, "capped_evan": False, "pay_per_hour": 25,
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
        # The queue/approval cycle lives on claims now, not on the chore rows.
        # A chore never leaves the board, so its own done_by/queued_for/rejected
        # fields no longer describe who owes what - these three attributes read
        # the claims instead.
        claims = d.get("claims") or []
        queued = [c for c in claims if c.get("state") == "queued"]
        out.update({
            "ok": True,
            "ian": int(tot.get("ian", 0)),
            "evan": int(tot.get("evan", 0)),
            # weekly parent total. Deliberately NOT fed into leader/streak/champion.
            "parent": int(tot.get("parent", 0)),
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
            # A parent sent it back with a note and it is waiting to be redone.
            # /chores/reject is the only thing that sets `rejected`, and it puts
            # the claim back to queued; done, approve, reassign, clear_rejection
            # and the Monday roll all drop the key. So this is exactly the set of
            # FIX cards, which is what the red "N CHORES TO FIX" pill counts.
            "pending": len([c for c in queued if c.get("rejected")]),
            # jobs sitting in each kid's queue (rejected redos count too)
            "queued_ian": len([c for c in queued if c.get("kid") == "ian"]),
            "queued_evan": len([c for c in queued if c.get("kid") == "evan"]),
        })
        # Claims a kid marked done that no parent has signed off. The add-on drops
        # these at the Monday roll with no points, which is what the Sunday 10pm
        # reminder to the parents is for.
        labels = {"ian": "Ian", "evan": "Evan", "parent": "Parent"}
        wait = [c for c in claims if c.get("state") == "done"]
        out["awaiting"] = len(wait)
        out["awaiting_pts"] = sum(int(c.get("points", 0)) for c in wait)
        out["awaiting_list"] = ["%s: %s (%d)" % (labels.get(c.get("kid"), c.get("kid", "?")),
                                                 c.get("name", "?"), int(c.get("points", 0)))
                                for c in wait]
        out["unfinished"] = len(queued)
        # Past 100 points a job pays its minutes at pay_per_hour (add-on 2.5.0).
        earn = d.get("earnings") or {}
        for k in ("ian", "evan"):
            e = earn.get(k) or {}
            out["min_" + k] = int(e.get("minutes", 0))
            out["pay_" + k] = float(e.get("pay", 0))
            out["capped_" + k] = bool(e.get("capped", False))
        out["pay_per_hour"] = d.get("pay_per_hour", 25)
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
