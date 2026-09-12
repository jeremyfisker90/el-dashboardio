#!/usr/bin/env python3
"""Generate the family chores spreadsheet from whatever is live right now.

Upload to Google Drive -> it converts to a Sheet -> File > Share > Publish to web
-> pick the Chores tab -> CSV -> paste that link into the dashboard's
"Spreadsheet link..." button. Column headers are matched by keyword, so they can be
reworded freely.
"""
import json
import os
import subprocess
import sys

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Family Chores.xlsx")
API = "http://YOUR_HA_IP:5000/chores"

HEADERS = ["Chore Title", "Points", "Chore Steps/Details",
           "Type (Required / Optional)", "Frequency"]
NAVY, STEEL, INK = "1B2A4A", "4A78D6", "222222"
BAND, GREEN, AMBER, GREY = "EEF3FC", "1E7F4C", "B26B00", "6B7A95"
# The published-sheet URL is a secret (it exposes the whole workbook), so it is
# never hardcoded here. It is read from the add-on, which already stores it.
MEALS_CSV = ""
TRACKER_API = "http://YOUR_HA_IP:5000/meals/tracker"


def _band(ws, first_row, last_row, ncols):
    """Zebra striping + thin borders, so long lists stay readable."""
    from openpyxl.styles import Border, Side
    edge = Side(style="thin", color="D5DEEC")
    box = Border(left=edge, right=edge, top=edge, bottom=edge)
    for r in range(first_row, last_row + 1):
        for cidx in range(1, ncols + 1):
            cell = ws.cell(row=r, column=cidx)
            cell.border = box
            if r % 2 == 0:
                cell.fill = PatternFill("solid", fgColor=BAND)


def live_chores():
    """Pull the current catalog through the HA box (the API is LAN-only)."""
    try:
        raw = subprocess.check_output([
            "ssh", "-i", os.path.join(HERE, "keys", "id_ha"),
            "-o", "StrictHostKeyChecking=no", "root@YOUR_HA_IP",
            "curl -s -m 20 %s" % API], text=True, encoding="utf-8", timeout=60)
        return json.loads(raw).get("chores") or []
    except Exception as exc:
        print("could not reach the chores API (%s); writing headers only" % exc)
        return []


def _meals_url():
    """Ask the add-on for the published Meals CSV rather than storing it here."""
    try:
        raw = subprocess.check_output([
            "ssh", "-i", os.path.join(HERE, "keys", "id_ha"),
            "-o", "StrictHostKeyChecking=no", "root@YOUR_HA_IP",
            "curl -s -m 20 http://YOUR_HA_IP:5000/meals"], text=True,
            encoding="utf-8", timeout=60)
        return json.loads(raw).get("source_url") or ""
    except Exception:
        return ""


def live_meals():
    """The approved meal list, straight off the published Meals tab."""
    import csv as _csv
    import urllib.request
    url = MEALS_CSV or _meals_url()
    if not url:
        print("no meals URL available; skipping the Meals tab")
        return []
    try:
        raw = urllib.request.urlopen(url, timeout=25).read().decode("utf-8", "replace")
        rows = [r for r in _csv.reader(raw.splitlines()) if any(x.strip() for x in r)]
        out = []
        for r in rows[1:]:
            name = (r[0] if r else "").strip()
            if not name:
                continue
            out.append({"name": name,
                        "pre": (r[1] if len(r) > 1 else "").strip(),
                        "last": (r[2] if len(r) > 2 else "").strip()})
        return sorted(out, key=lambda m: m["name"].lower())
    except Exception as exc:
        print("could not read the Meals tab (%s)" % exc)
        return []


def live_tracker():
    try:
        raw = subprocess.check_output([
            "ssh", "-i", os.path.join(HERE, "keys", "id_ha"),
            "-o", "StrictHostKeyChecking=no", "root@YOUR_HA_IP",
            "curl -s -m 20 %s" % TRACKER_API], text=True, encoding="utf-8", timeout=60)
        return json.loads(raw).get("tracker") or []
    except Exception as exc:
        print("could not read the tracker (%s)" % exc)
        return []


def style_header(ws, headers):
    ws.append(headers)
    for i, _ in enumerate(headers, start=1):
        c = ws.cell(row=1, column=i)
        c.font = Font(bold=True, color="FFFFFF", size=12)
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"


# The SHEET is the source of truth for frequency — a sync pushes these values
# back into the add-on and overwrites anything set in the dashboard. So cadence
# changes have to be made here. Matched on a lowercase substring of the name.
FREQ_OVERRIDES = {
    "dry mop": "2-day",           # dry sweep 1st floor: reposts 2 days after it's done
    "walk the dog": "daily",      # reopens every morning at 6am
    "shared bathroom": "weekly",  # was bi-weekly
}


def _apply_freq_overrides(chores):
    for c in chores:
        nm = (c.get("name") or "").lower()
        for key, freq in FREQ_OVERRIDES.items():
            if key in nm:
                c["frequency"] = freq
    return chores


def _sheet_order(c):
    """Same order the dashboard shows: required first, short-cycle chores at the
    top (Walk the dog pinned), then weekly -> bi-weekly -> monthly."""
    freq = (c.get("frequency") or "").lower()
    short = 0 if freq in ("daily", "2-day") else 1
    dog = 0 if "walk the dog" in (c.get("name") or "").lower() else 1
    rank = {"daily": 0, "2-day": 1, "weekly": 2, "bi-weekly": 3, "monthly": 4}.get(freq, 9)
    return (c.get("kind") != "required", short, dog, rank, c.get("name", ""))


chores = sorted(_apply_freq_overrides(live_chores()), key=_sheet_order)

wb = openpyxl.Workbook()

# ---------------------------------------------------------------- Chores tab
ws = wb.active
ws.title = "Chores"
style_header(ws, HEADERS)
for c in chores:
    ws.append([c.get("name", ""), int(c.get("points", 0)), c.get("description", ""),
               c.get("kind", "required"), c.get("frequency", "weekly")])
for _ in range(15):
    ws.append(["", None, "", "", ""])

dv_kind = DataValidation(type="list", formula1='"required,optional"', allow_blank=True)
dv_kind.promptTitle = "Chore type"
dv_kind.prompt = ("required = has to be done before anyone can claim an optional one.\n"
                  "optional = extra points, unlocks once every required chore is claimed.")
ws.add_data_validation(dv_kind)
dv_kind.add("D2:D200")

dv_freq = DataValidation(type="list", formula1='"daily,2-day,weekly,bi-weekly,monthly"', allow_blank=True)
dv_freq.promptTitle = "How often"
dv_freq.prompt = ("How long before this chore comes back after it's been done.\n"
                  "daily = every day (reopens 6am), 2-day = 2 days after it's done, weekly = 7 days, bi-weekly = 14 days, monthly = 30 days.")
ws.add_data_validation(dv_freq)
dv_freq.add("E2:E200")

for col, w in {"A": 36, "B": 9, "C": 74, "D": 20, "E": 14}.items():
    ws.column_dimensions[col].width = w
for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=5):
    row[0].alignment = Alignment(vertical="center", wrap_text=True)
    row[1].alignment = Alignment(horizontal="center", vertical="center")
    row[2].alignment = Alignment(wrap_text=True, vertical="top")
    row[3].alignment = Alignment(horizontal="center", vertical="center")
    row[4].alignment = Alignment(horizontal="center", vertical="center")
    row[0].font = Font(bold=True, size=11)
    # colour-code the cadence so the short-cycle jobs stand out at a glance
    freq = str(row[4].value or "").lower()
    if freq in ("daily", "2-day"):
        row[4].font = Font(bold=True, color=GREEN, size=11)
    elif freq in ("bi-weekly", "monthly"):
        row[4].font = Font(color=AMBER, size=11)
    if str(row[3].value or "").lower().startswith("req"):
        row[3].font = Font(bold=True, color=NAVY, size=11)
    else:
        row[3].font = Font(color=GREY, size=11)
_band(ws, 2, ws.max_row, 5)
ws.auto_filter.ref = "A1:E%d" % ws.max_row

# ---------------------------------------------------------------- Rotation tab
rot = wb.create_sheet("Rotation")
style_header(rot, ["Chore Title", "Frequency", "Last Done", "Next Time It Posts"])
for c in chores:
    rot.append([c.get("name", ""), c.get("frequency", "weekly"),
                c.get("last_done") or "— never —", c.get("next_due") or "on the board now"])
for col, w in {"A": 36, "B": 14, "C": 16, "D": 20}.items():
    rot.column_dimensions[col].width = w
for row in rot.iter_rows(min_row=2, max_row=rot.max_row, max_col=4):
    for cell in row[1:]:
        cell.alignment = Alignment(horizontal="center", vertical="center")
_band(rot, 2, rot.max_row, 4)
rot.auto_filter.ref = "A1:D%d" % rot.max_row

note = rot.cell(row=rot.max_row + 2, column=1,
                value="Read-only snapshot. The dashboard tracks these dates live as the "
                      "boys claim chores — it can't write back into this sheet.")
note.font = Font(italic=True, color="777777", size=10)

# ---------------------------------------------------------------- Meals tab
meals = live_meals()
ml = wb.create_sheet("Meals")
style_header(ml, ["Meal", "Pre-Time", "Last cooked"])
for m in meals:
    ml.append([m["name"], m["pre"] or "Normal", m["last"]])
for col, w in {"A": 40, "B": 14, "C": 16}.items():
    ml.column_dimensions[col].width = w
for row in ml.iter_rows(min_row=2, max_row=ml.max_row, max_col=3):
    row[0].font = Font(bold=True, size=11)
    row[0].alignment = Alignment(vertical="center")
    row[1].alignment = Alignment(horizontal="center", vertical="center")
    row[2].alignment = Alignment(horizontal="center", vertical="center")
    # Fast meals are the whole point of the picker's filter, so make them pop
    if str(row[1].value or "").strip().lower().startswith("fast"):
        row[1].font = Font(bold=True, color=GREEN, size=11)
    else:
        row[1].font = Font(color=GREY, size=11)
if ml.max_row >= 2:
    _band(ml, 2, ml.max_row, 3)
    ml.auto_filter.ref = "A1:C%d" % ml.max_row
dv_pre = DataValidation(type="list", formula1='"Fast,Normal"', allow_blank=True)
dv_pre.promptTitle = "Prep time"
dv_pre.prompt = ("Fast = weeknight quick. The tablet's meal picker has a "
                 "'Fast only' filter that reads this column.")
ml.add_data_validation(dv_pre)
dv_pre.add("B2:B300")

# ---------------------------------------------------------------- Tracker tab
tracker = live_tracker()
tr = wb.create_sheet("Tracker")
style_header(tr, ["Meal", "Date Cooked", "Day", "Rating", "Notes"])
for t in tracker:
    tr.append([t.get("meal", ""), t.get("date", ""), t.get("day", ""),
               t.get("rating", ""), t.get("notes", "")])
for col, w in {"A": 40, "B": 14, "C": 12, "D": 10, "E": 46}.items():
    tr.column_dimensions[col].width = w
for row in tr.iter_rows(min_row=2, max_row=tr.max_row, max_col=5):
    row[0].font = Font(bold=True, size=11)
    for cell in row[1:4]:
        cell.alignment = Alignment(horizontal="center", vertical="center")
    row[4].alignment = Alignment(wrap_text=True, vertical="top")
if tr.max_row >= 2:
    _band(tr, 2, tr.max_row, 5)
    tr.auto_filter.ref = "A1:E%d" % tr.max_row
dv_rate = DataValidation(type="list", formula1='"up,down"', allow_blank=True)
dv_rate.promptTitle = "Did it land?"
dv_rate.prompt = "up = make it again, down = don't. Rate from the tablet or here."
tr.add_data_validation(dv_rate)
dv_rate.add("D2:D400")
tnote = tr.cell(row=tr.max_row + 2, column=1,
                value="What actually got cooked. The tablet logs this as meals are set; "
                      "use the planner's 'Copy for the Tracker tab' button to paste updates "
                      "in. Anything rated up is a candidate for the Meals tab.")
tnote.font = Font(italic=True, color="777777", size=10)

# ---------------------------------------------------------------- guide tab
gd = wb.create_sheet("How this works")
gd.column_dimensions["A"].width = 112
notes = [
    ("Family chores — how this sheet is used", True),
    ("", False),
    ("Anything you type on the 'Chores' tab shows up on the wall tablet within 5 minutes.", False),
    ("", False),
    ("Chore Title                  the name the boys will see", False),
    ("Points                       the points it's worth (a whole number)", False),
    ("Chore Steps/Details          how to do it — shows under the chore name on the tablet", False),
    ("Type (Required / Optional)   pick from the dropdown", False),
    ("Frequency                    weekly / bi-weekly / monthly — pick from the dropdown", False),
    ("", False),
    ("You can rename these headers. Columns are matched by keyword, so 'Task'/'Job'/", False),
    ("'Title' work for the name, 'Pts'/'Value' for points, 'Instructions'/'How to' for", False),
    ("the steps, 'Kind'/'Category' for the type, and 'How Often'/'Repeat' for frequency.", False),
    ("", False),
    ("Required vs optional", True),
    ("Every REQUIRED chore on the board has to be claimed before any OPTIONAL one can", False),
    ("be. Optional chores show with a lock until then, so the boys can't skip ahead to", False),
    ("the fun high-point jobs.", False),
    ("", False),
    ("How the frequency rotation works", True),
    ("The board is rebuilt every Monday. A chore only goes back up once its interval", False),
    ("has passed since it was last finished:", False),
    ("    weekly      back on the board 7 days after it was done", False),
    ("    bi-weekly   back after 14 days", False),
    ("    monthly     back after 30 days", False),
    ("So a monthly job finished on the 3rd won't reappear until the 2nd of next month.", False),
    ("A chore nobody finished just stays up — it doesn't get skipped.", False),
    ("The 'Rotation' tab shows where every chore currently sits.", False),
    ("", False),
    ("Three places to add chores — they all stay in sync", True),
    ("This sheet, the Cozi lists 'Chores Required' / 'Chores Optional', and the tablet", False),
    ("itself. A chore added in any one appears in the other two. Matching is by name,", False),
    ("so the same chore never shows up twice.", False),
    ("", False),
    ("This sheet is the source of truth for FREQUENCY — Cozi list items can't carry", False),
    ("one, so change frequency here (or on the tablet), not in Cozi.", False),
    ("", False),
    ("Deleting a row here removes the chore from the tablet too — unless one of the", False),
    ("boys already claimed it this week, which is protected.", False),
]
for i, (text, bold) in enumerate(notes, start=1):
    c = gd.cell(row=i, column=1, value=text)
    c.font = Font(bold=bold, size=12 if bold else 11, color=STEEL if bold else INK)

wb.save(OUT)
print("wrote %s (%d bytes) — %d chores across %d tabs"
      % (OUT, os.path.getsize(OUT), len(chores), len(wb.sheetnames)))
