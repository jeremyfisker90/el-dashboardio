# Setting up El Dashboardio

This is a working reference, not a one-click install — expect an evening of
adapting entity ids and taste. The path below is the order that works.

## 0. What you need

- Home Assistant OS (the add-on requires Supervisor) on your LAN.
- A wall tablet running [Fully Kiosk Browser](https://www.fully-kiosk.com/)
  (built for 1280x800 landscape; other sizes need the sizing pass in step 7).
- A Cozi account (free) if you want the chores/meal/shopping integrations.
- Python 3 on your desktop for the build scripts.

## 1. HACS custom cards

Install via HACS → Frontend, then add as Lovelace resources:

- [button-card](https://github.com/custom-cards/button-card)
- [card-mod](https://github.com/thomasloven/lovelace-card-mod)
- [vertical-stack-in-card](https://github.com/ofekashery/vertical-stack-in-card)

## 2. Files onto the HA box

```
/config/www/     <- chores.html, gameday.html, grocery.html, bg_neon.svg, goat.svg, goat.jpg, font_loader.js
/config/bin/     <- gameday.py, chores_totals.py, dinner_today.py   (chmod +x)
```

## 3. The chores add-on

Settings → Add-ons → Add-on Store → ⋮ → Repositories → add
`https://github.com/jeremyfisker90/cozi-proxy-addon` → install
**Cozi Proxy API** → enter your Cozi credentials → start.
No Cozi? Set `cozi_enabled: false` — chores then sync with the Google Sheet
only, and `configuration-snippets.yaml` has a calendar-based dinner sensor
(GOOGLE MODE section). Full API docs live in that repo's README.

## 4. Configuration

- Merge `configuration-snippets.yaml` into your `configuration.yaml`
  (the two game sensors, the chores sensor, and the `frontend:
  extra_module_url` font loader).
- Merge `templates.yaml` into your template config: the agenda sensor
  (`sensor.today_schedule`), the dinners sensor, and the hourly forecast
  sensor. **Swap the calendar and weather entity ids for your own.**
- Restart HA once (the font loader needs it; everything later hot-reloads).

Game sensors: find your team's ESPN id at
`site.api.espn.com/apis/site/v2/sports/football/nfl/teams` (or your league)
and edit the `gameday.py` arguments in the snippet.

## 5. Personalization checklist (don't skip)

| Where | What |
| --- | --- |
| `build_layout.py` | Bus-tracker URL (`YOUR_STUDENT_ID`), kid names/colors, room menu paths |
| `chores.html` | `CLAIM_CODES` — the kids' claim PINs |
| `templates.yaml` | Your calendar entity ids; the `cal: 'dad'` tag maps a whole calendar to one person |
| `configuration-snippets.yaml` | ESPN team ids, accents |
| `chore_catalog.py` | Seed chores (run once against the add-on, optional) |
| `make_chores_sheet.py` | Generates the Google Sheet workbook to share |

## 6. Build and deploy the view

The home view is generated, not hand-edited:

1. Grab a dump of your dashboard's storage config
   (`/config/.storage/lovelace.<your_dashboard>`) and save it as
   `new_store.json` next to the scripts. The builder splices its generated
   home view into your existing dashboard (sub-views untouched).
2. `python build_layout.py && python make_neon_store.py`
3. Upload the result where HA can serve it
   (`scp neon_store.json root@HA:/config/www/neon_cfg.json`), then from any
   logged-in browser tab run in the console:

```js
const store = await fetch('/local/neon_cfg.json?nc='+Date.now()).then(r=>r.json());
await document.querySelector('home-assistant').hass.callWS(
  {type:'lovelace/config/save', url_path:'YOUR-DASHBOARD', config: store.data.config});
```

No restart — connected tablets refresh themselves. Iterate by re-running
steps 2–3.

> `make_neon_store.py` expects the home view's weather cards to exist in your
> current dashboard (it carries them over). Easiest start: put any two
> weather cards on your home view first, or strip the `__HOURLY__`/`__WEEKLY__`
> placeholders from `build_layout.py`.

## 7. Google Sheet (optional but the best part for co-parents)

Run `make_chores_sheet.py` to generate the workbook, upload to Google Drive
(convert to Sheets), share with your co-parent, then File → Share →
Publish to web → the chores tab as **CSV**, and paste that link into the
dashboard's "Spreadsheet link…" button (or `POST /chores/sheeturl`).
Column headers are keyword-matched, so wording is flexible.

## 8. The goat

The Grand Champion tile expects a photo at `/config/www/goat.jpg` — a goat
staring into the camera works best (the G.O.A.T., obviously). Supply your own;
any majestic farm animal at `object-fit: cover` proportions will do. The drawn
`goat.svg` is included if you prefer a watermark instead — swap the `<img>` in
`CHAMP_JS` for the old background-image layer.

## 9. Store logos (optional)

The shopping-lists page shows real store logos on the list cards. Drop SVGs
into `/config/www/logos/` named `kroger.svg`, `aldi.svg`, `costco.svg`,
`homedepot.svg`, `lowes.svg` (Wikimedia Commons has all of them — search the
store name + "logo svg"). The 3D-print tile also expects `bambu.ico` there
(grab your printer brand's favicon). A list whose title matches a brand gets its chip(s);
combined lists like "Home Depot/Lowe's" or a Kroger list that also covers Aldi
show both logos. If a logo file is missing the card just falls back to an
emoji, so this step is safe to skip. Edit the `BRANDS` and `EMOJI` tables at
the top of `grocery.html` to match your own store names.

## 10. Tablet notes

- Fully Kiosk: set the start URL to your dashboard path, enable screen-always-on.
- Android WebView renders ~10–15% taller than desktop Chrome — if the column
  overflows your screen, trim the fixed row heights/margins in
  `build_layout.py` (see the gotchas list in the README).
