"""One design system for the whole page.

The page had accumulated four corner radii (18 / 14 / 12 / 12), three different
panel backgrounds, a lime ad-hoc button, a 3px-bordered casino marquee and a
neon rule stapled onto three of the five menus. Each piece was fine alone; put
together they read as noise.

This appends a normalising layer at the end of the stylesheet, so it wins on
cascade without unpicking 610 lines by hand. Every container gets the same
lacquer, the same border, the same radius and the same header type. The only
thing that varies between sections is one accent colour, and it is used in one
place: a thin rule along the top edge, brighter when the section is active.

Restraint is the point - it should look like one machine, not five.
"""
import io
import os

P = 'chores.html'
s = io.open(P, encoding='utf-8').read()

SYSTEM = """
  /* ==================================================================
     DESIGN SYSTEM - normalising layer, deliberately last in the sheet.
     Everything above sets its own look; this makes them agree.
     ================================================================== */
  :root {
    --r: 14px;                       /* one radius, everywhere */
    --bd: rgba(140,170,215,0.20);    /* one border */
    --bd-on: color-mix(in srgb, var(--neon,#22d3ee) 50%, transparent);
    --lacquer: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0) 46%),
               linear-gradient(180deg, #0b1020 0%, #070b16 100%);
    --lift: 0 1px 0 rgba(255,255,255,0.045) inset, 0 8px 20px rgba(0,0,0,0.5);
    --glow: 0 0 18px color-mix(in srgb, var(--neon,#22d3ee) 20%, transparent);
  }

  /* ---- every container: same shell, different accent ---- */
  .panel, .kpanel, .neon, .roomgrp, .ptbar, .casino-marquee, .donecol-head {
    position:relative;
    border-radius:var(--r) !important;
    background:var(--lacquer) !important;
    border:1px solid var(--bd) !important;
    box-shadow:var(--lift) !important;
    overflow:hidden;
  }
  .panel        { --neon:#22d3ee; margin:0 2px 11px; width:calc(100% - 4px); }
  .kpanel       { --neon:#22d3ee; margin:0 2px 11px; width:calc(100% - 4px); }
  .kpanel.ian   { --neon:#2dd4bf; }
  .kpanel.evan  { --neon:#fbbf24; }
  .kpanel.parentq { --neon:#d8b4fe; }
  .roomgrp      { --neon:#22d3ee; margin:0 0 9px; }
  .ptbar        { --neon:#38bdf8; margin:0 0 12px; padding:10px 12px; }
  .done-btn     { --neon:#22c55e; }
  .qbar         { --neon:#a855f7; }
  .adhoc-btn    { --neon:#f97316; }
  .casino-marquee { --neon:#e879f9; margin:0 2px 11px !important;
                    width:calc(100% - 4px) !important; padding:16px 18px !important;
                    border-width:1px !important; }

  /* ---- the one accent gesture: a rule along the top edge ---- */
  .panel::before, .kpanel::before, .neon::before, .roomgrp::before,
  .ptbar::before, .casino-marquee::before {
    content:''; position:absolute; inset:0 0 auto 0; height:2px; z-index:2;
    background:linear-gradient(90deg, transparent, var(--neon) 20%,
                               var(--neon) 80%, transparent);
    box-shadow:0 0 10px var(--neon);
    opacity:.45; pointer-events:none;
  }
  .neon.on::before, .roomgrp.open::before, .done-btn.on::before { opacity:1; }
  .neon.on, .roomgrp.open { border-color:var(--bd-on) !important;
                            box-shadow:var(--lift), var(--glow) !important; }
  /* the marquee's cabinet bulbs and the dotted trim were the loudest things
     on the page; the accent rule already says "casino" */
  .neon.lit::after, .cm-bulbs { display:none !important; }

  /* ---- one header type treatment ---- */
  .phead, .khead, .done-btn, .qbar-lbl, .rmname, .cm-title {
    font-size:14px !important; font-weight:900 !important;
    letter-spacing:1.1px !important; text-transform:uppercase !important;
    color:#eaf4ff !important;
    text-shadow:0 0 9px color-mix(in srgb, var(--neon,#22d3ee) 55%, transparent) !important;
  }
  .phead, .khead { padding:11px 14px !important;
                   border-bottom:1px solid rgba(140,170,215,0.13) !important;
                   background:rgba(255,255,255,0.018) !important; }
  .pbody, .kbody { padding:12px !important; }
  /* secondary text on a header - counts, hints - stays quiet */
  .note, .qcount, .rmmeta, .cm-sub, .ql-n, .dc-sub {
    font-size:11px !important; font-weight:700 !important; letter-spacing:0.2px !important;
    text-transform:none !important; color:#8fa6c4 !important; text-shadow:none !important; }
  .note, .qcount { margin-left:auto; }

  /* ---- numbers read as one scoreboard ---- */
  .kpts, .ql-pts, .rmpts, .dc-pts, .db-tot, .badge {
    font-weight:900 !important; letter-spacing:0.3px !important; }

  /* ---- the ad-hoc button was the only lime thing on the page ---- */
  .adhoc-btn { color:#eaf4ff !important; background:var(--lacquer) !important;
               border:1px solid var(--bd) !important; padding:14px 17px !important;
               font-size:14px !important; letter-spacing:1.1px !important;
               text-transform:uppercase !important; }
  .adhoc-btn:active, .casino-marquee:active, .done-btn:active, .qlink:active,
  .roomhead:active { transform:translateY(1px); filter:brightness(1.08); }

  /* ---- casino marquee: same shell, keeps its character in the type ---- */
  .cm-inner { gap:14px !important; }
  .cm-title { font-size:19px !important; letter-spacing:3px !important;
              color:#fdf4ff !important;
              text-shadow:0 0 14px rgba(232,121,249,0.75) !important; }
  .cm-ico { filter:drop-shadow(0 0 8px rgba(232,121,249,0.55)); }

  /* ---- section labels inside a panel ---- */
  .sub, .ksub, .donesub {
    font-size:11px !important; font-weight:900 !important; letter-spacing:1.1px !important;
    text-transform:uppercase !important; color:#9fb3cf !important;
    border-top:1px solid rgba(140,170,215,0.12); padding-top:9px !important;
    margin:12px 0 8px !important; }
  .dailynote { font-size:11.5px !important; font-weight:700 !important;
               color:#9fb3cf !important; background:rgba(255,255,255,0.025) !important;
               border:1px solid rgba(140,170,215,0.14) !important;
               border-radius:10px !important; padding:9px 11px !important; }
"""

anchor = '</style>'
if anchor not in s:
    raise SystemExit('no </style> found')
s = s.replace(anchor, SYSTEM + anchor, 1)

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('appended the normalising design-system layer')
