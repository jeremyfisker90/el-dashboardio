#!/usr/bin/env python3
"""Next/current game for one team -> HA command_line sensor + a local JSON file.

Usage:  gameday.py <league-path> <team-id> <slug> <display-name> <accent-hex>
  e.g.  gameday.py nfl 4 bengals "Bengals" "#fb4f14"
        gameday.py college-football 194 buckeyes "Buckeyes" "#bb0000"

Pulls the ESPN public team-schedule API across preseason (1), regular season (2)
and postseason (3). No API key and no season year -- ESPN resolves the current
season itself, so this keeps working year over year.

Two outputs per run:
  * stdout -- compact JSON for the current/next game (command_line json_attributes)
  * /config/www/<slug>_schedule.json -- full season for /local/gameday.html

NOTE: ESPN 403s requests that spoof a browser User-Agent, so we deliberately send
urllib's default UA. Do not "helpfully" add a Mozilla UA here -- it breaks.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

URL = ("https://site.api.espn.com/apis/site/v2/sports/football/{league}"
       "/teams/{team}/schedule?seasontype={st}")
WWW_DIR = "/config/www"
TIMEOUT = 20


def fetch(league, team, seasontype):
    u = URL.format(league=league, team=team, st=seasontype)
    with urllib.request.urlopen(u, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def all_events(league, team):
    events = []
    for st in (1, 2, 3):
        try:
            data = fetch(league, team, st)
        except Exception:
            continue
        for e in data.get("events") or []:
            if e.get("date"):
                events.append(e)
    seen, out = set(), []
    for e in events:
        eid = e.get("id")
        if eid in seen:
            continue
        seen.add(eid)
        out.append(e)
    out.sort(key=lambda e: e["date"])
    return out


def when(ev):
    """ESPN dates look like 2026-08-22T23:00Z -> aware UTC datetime."""
    return datetime.strptime(ev["date"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)


def state_of(ev):
    comp = (ev.get("competitions") or [{}])[0]
    return ((comp.get("status") or {}).get("type") or {}).get("state") or "pre"


def pick(events):
    """Live game wins; then a game that finished in the last 18h (so the tile keeps
    showing today's final); then the next scheduled game; else the last one played."""
    now = datetime.now(timezone.utc)
    for e in events:
        if state_of(e) == "in":
            return e
    recent = [e for e in events
              if state_of(e) == "post" and timedelta(0) <= now - when(e) <= timedelta(hours=18)]
    if recent:
        return recent[-1]
    upcoming = [e for e in events if when(e) >= now]
    if upcoming:
        return upcoming[0]
    return events[-1] if events else None


def network_for(comp, us_home_away):
    """Prefer a national feed; otherwise the market feed our side receives (which
    flips with home/away). College games usually carry one national entry."""
    casts = comp.get("broadcasts") or []

    def name(b):
        m = b.get("media") or {}
        return (m.get("shortName") or m.get("callLetters") or "").strip()

    def market(b):
        return ((b.get("market") or {}).get("type") or "").lower()

    for b in casts:
        if market(b) == "national" and name(b):
            return name(b)
    want = "home" if us_home_away == "home" else "away"
    for b in casts:
        if market(b) == want and name(b):
            return name(b)
    for b in casts:
        if name(b):
            return name(b)
    return ""


def logo_of(team, league):
    """Prefer ESPN's `dark` variant -- it carries the white outline that keeps a
    dark crest (Ohio State's scarlet O especially) from vanishing on a black tile.
    Skip the `scoreboard` crops; we want the full mark."""
    logos = team.get("logos") or []
    for l in logos:
        rel = l.get("rel") or []
        if "dark" in rel and "scoreboard" not in rel:
            return l.get("href")
    for l in logos:
        if "default" in (l.get("rel") or []):
            return l.get("href")
    sport = "nfl" if league == "nfl" else "ncaa"
    tid = team.get("id") or ""
    return "https://a.espncdn.com/i/teamlogos/%s/500-dark/%s.png" % (sport, tid)


def score_of(c):
    v = c.get("score")
    if isinstance(v, dict):
        v = v.get("value") or v.get("displayValue")
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def summarize(ev, team_id, league):
    """Flatten one ESPN event into the fields the dashboard actually uses."""
    comp = (ev.get("competitions") or [{}])[0]
    us = them = None
    for c in comp.get("competitors") or []:
        if str((c.get("team") or {}).get("id")) == str(team_id):
            us = c
        else:
            them = c
    if not us or not them:
        raise ValueError("could not identify both teams")

    home_away = (us.get("homeAway") or "home").lower()
    us_team, opp_team = us.get("team") or {}, them.get("team") or {}
    opp_abbr = (opp_team.get("abbreviation") or "").upper()
    status = (comp.get("status") or {}).get("type") or {}
    state = status.get("state") or "pre"
    kick = when(ev)
    s_us, s_them = score_of(us), score_of(them)

    week = ev.get("week") or {}
    stype = ev.get("seasonType") or {}
    week_text = week.get("text") or ""
    if not week_text and week.get("number"):
        week_text = "%s Week %s" % (stype.get("name") or "Week", week["number"])

    result = ""
    if state == "post" and s_us is not None and s_them is not None:
        result = "W" if s_us > s_them else ("L" if s_us < s_them else "T")

    return {
        "id": ev.get("id") or "",
        "opponent": opp_team.get("displayName") or "",
        "opponent_short": opp_team.get("shortDisplayName") or opp_team.get("nickname") or "",
        "opp_abbr": opp_abbr,
        "opp_logo": logo_of(opp_team, league),
        "us_abbr": (us_team.get("abbreviation") or "").upper(),
        "us_logo": logo_of(us_team, league),
        "home_away": home_away,
        "home_away_label": "HOME" if home_away == "home" else "AWAY",
        "vs_at": "vs" if home_away == "home" else "@",
        "kickoff_iso": kick.isoformat().replace("+00:00", "Z"),
        # ESPN sets timeValid=false for flex/TBD kickoffs (it parks them at local midnight)
        "time_valid": bool(ev.get("timeValid", comp.get("timeValid", True))),
        "network": network_for(comp, home_away) or "TBD",
        "venue": (comp.get("venue") or {}).get("fullName") or "",
        "week_text": week_text,
        "season_type": stype.get("name") or "",
        "game_state": state,
        "status_detail": status.get("shortDetail") or status.get("detail") or "",
        "score_us": s_us,
        "score_them": s_them,
        "result": result,
    }


def headline(g):
    """Short state string for the sensor (HA caps state at 255 chars)."""
    if g["game_state"] == "in":
        return "LIVE  %s %s - %s %s" % (g["us_abbr"], g["score_us"] or 0,
                                        g["score_them"] or 0, g["opp_abbr"])
    if g["game_state"] == "post":
        if g["score_us"] is None or g["score_them"] is None:
            return "Final %s %s" % (g["vs_at"], g["opp_abbr"])
        return "Final %s %s-%s %s" % (g["result"], g["score_us"], g["score_them"], g["opp_abbr"])
    kick = datetime.strptime(g["kickoff_iso"], "%Y-%m-%dT%H:%M:%SZ")
    return "%s %s %s" % (kick.strftime("%a %b %d").replace(" 0", " "), g["vs_at"], g["opp_abbr"])


def write_www(slug, payload):
    """Full schedule for /local/gameday.html. Best effort -- never fail the sensor."""
    try:
        path = os.path.join(WWW_DIR, "%s_schedule.json" % slug)
        tmp = path + ".tmp"
        if not os.path.isdir(WWW_DIR):
            os.makedirs(WWW_DIR, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        os.replace(tmp, path)
    except Exception:
        pass


def main():
    if len(sys.argv) < 6:
        sys.stdout.write(json.dumps({"state": "bad args", "has_game": False}))
        return
    league, team_id, slug, title, accent = sys.argv[1:6]

    out = {"state": "No game data", "has_game": False, "title": title, "accent": accent}
    try:
        events = all_events(league, team_id)
        if not events:
            raise ValueError("no events returned")
        games = []
        for e in events:
            try:
                games.append(summarize(e, team_id, league))
            except Exception:
                continue
        chosen = pick(events)
        current = summarize(chosen, team_id, league) if chosen else None
        if not current:
            raise ValueError("no current game")
        write_www(slug, {
            "updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "current_id": current["id"], "title": title, "accent": accent,
            "us_logo": current["us_logo"], "games": games,
        })
        out.update(current)
        out["state"] = headline(current)
        out["has_game"] = True
    except Exception as exc:
        out["status_detail"] = str(exc)[:120]
    sys.stdout.write(json.dumps(out))


if __name__ == "__main__":
    main()
