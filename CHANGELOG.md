# Changelog

## 2026-08 — second wave

**TL;DR for the "I don't want Cozi" crowd: you don't need it.** Set
`cozi_enabled: false` and the whole system runs on Google products — chores
sync against a shared **Google Sheet** (co-parent edits it from anywhere), the
schedule pulls from **Google Calendar**, and the "tonight's dinner" tile reads
a calendar instead of a Cozi list. Cozi is now one optional input among
several. Setup for both modes is in [INSTALL.md](INSTALL.md).

### Chores got a real workflow (add-on v1.11 → v1.15)

- **Per-kid job queues**: kids grab jobs off the board into their own queue,
  then complete them (PIN-gated) from there. Queues survive the sheet sync,
  reset weekly, and show as count badges on the home screen.
- **Parent "Assign & notify"**: assign a chore and the kid gets a **text
  message** — free, via carrier email-to-SMS gateways (Gmail app password, no
  Twilio). Completions auto-text the other parent with the details. Rejected
  chores land back at the top of the offender's queue with the parent's note.
- **Two-column layout**: job board + done pile on the left, each kid's queue
  panel (score, progress, compact tap-to-expand job cards) on the right.
  Every section is a contained panel with a header band.
- **Self-tidying board**: fuzzy name matching merges wording-drift duplicates
  across sources ("Mop the 1st floor" vs "Mop first floor"), dailies re-open
  every morning, weekly/bi-weekly/monthly items only repost when actually due.

### New pages

- **Neon shopping lists**: store-logo cards (logo-only, live item counts),
  section headers preserved, picker filtered to the lists you actually shop
  from.
- **3D printing**: menu tile with live print status (%, time left), a printer
  page (progress hero, dual-nozzle/bed/chamber temps), and the chamber camera
  — the printer's RTSPS stream takes minutes to serve a first keyframe, solved
  by having go2rtc hold the stream open 24/7 (`preload:`).
- **Cameras**: doorbell + rear cam (Ring), front yard (Wyze via
  docker-wyze-bridge — mind the port collisions), printer cams.
- **Energy leaderboards**: top-5 circuits for today / this week / this month,
  pulled from HA's long-term statistics via a small custom card
  (`emporia_top5.js`) — week and month backfill instantly.

### The floorplan

- **Drag-and-drop floorplan editor** (`floorplan_editor.html`): rooms AND
  furniture are editable objects — drag rooms with half-foot snapping, resize
  per foot, rename, add halls/closets/stairs, then furnish from a ~30-piece
  isometric palette. Layout saves to the add-on (`/floorplan`).
- **Live "night-house" card** (`floorplan_card.js`): renders the saved layout
  as a dark isometric model — rooms with lights on glow warm amber (real
  light state), tap a room to toggle its lights, per-light dots, thermostat
  chip, floor switcher.

### Fixes worth stealing

- Tap targets inside `button-card` custom fields: `tap_action: none` sets
  `pointer-events: none` on the card (kills touch), and touchscreens swallow
  synthetic clicks — use `onpointerup`, never `onclick`.
- Iframe pages inside `sections` views get squeezed into one ~400px column —
  mount them in `panel` views.
- HA 2026.8: energy dashboard grid sources are flat now (no `flow_from`), and
  the built-in go2rtc no longer accepts custom streams (use the add-on).

## 2026-08 — initial release

Neon wall-tablet dashboard: schedule rail, weather, chores with points and a
Grand Champion, game-day tiles with live scores, live menu tiles, meal plan,
family locations, shopping lists.
