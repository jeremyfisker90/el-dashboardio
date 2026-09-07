"""Give every top-level menu the casino treatment.

The page already had one genuinely fun element - the casino marquee - and then
five flat grey bars above and below it. This puts the whole stack on one visual
system: a dark lacquered panel, a neon rule along the top edge, chrome-gold
numerals for points, and a soft glow that intensifies on the active item. The
structure stays rigid on purpose; the fun comes from the light, not from
wobbling the layout around.
"""
import io
import os

P = 'chores.html'
s = io.open(P, encoding='utf-8').read()


def sub(old, new, what):
    global s
    if old not in s:
        raise SystemExit('anchor missing: ' + what)
    s = s.replace(old, new, 1)


sub('  /* ---- whose-queue bar ---- */',
    """  /* ================= the neon menu system =================
     Every full-width control at the top of the page shares this shell so the
     stack reads as one machine: black lacquer, a lit rule across the top, and
     a bloom that comes up when the thing is active. */
  .neon { position:relative; width:calc(100% - 4px); margin:0 2px 11px;
          border-radius:14px; overflow:hidden;
          background:
            linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0) 42%),
            linear-gradient(180deg, #0b1020 0%, #070b16 100%);
          border:1px solid rgba(140,170,215,0.22);
          box-shadow:0 1px 0 rgba(255,255,255,0.05) inset,
                     0 10px 22px rgba(0,0,0,0.55); }
  /* the lit rule - each menu sets --neon to its own colour */
  .neon::before { content:''; position:absolute; inset:0 0 auto 0; height:2px;
                  background:linear-gradient(90deg, transparent,
                             var(--neon,#22d3ee) 18%, var(--neon,#22d3ee) 82%, transparent);
                  box-shadow:0 0 12px var(--neon,#22d3ee),
                             0 0 26px color-mix(in srgb, var(--neon,#22d3ee) 55%, transparent);
                  opacity:.85; }
  .neon.on { border-color:color-mix(in srgb, var(--neon,#22d3ee) 55%, transparent);
             box-shadow:0 0 20px color-mix(in srgb, var(--neon,#22d3ee) 26%, transparent),
                        0 10px 24px rgba(0,0,0,0.6); }
  .neon:active { transform:translateY(1px); }
  /* marquee dots down both sides, like the cabinet trim */
  .neon.lit::after { content:''; position:absolute; inset:auto 0 0 0; height:2px;
                     background:repeating-linear-gradient(90deg,
                       color-mix(in srgb, var(--neon,#22d3ee) 75%, transparent) 0 3px,
                       transparent 3px 11px);
                     opacity:.5; }
  .neon-title { font-size:15px; font-weight:900; letter-spacing:1.1px;
                text-transform:uppercase; color:#eaf4ff;
                text-shadow:0 0 10px color-mix(in srgb, var(--neon,#22d3ee) 70%, transparent); }
  /* points read like a scoreboard, not body copy */
  .chrome { font-weight:900; letter-spacing:0.5px;
            background:linear-gradient(180deg,#fff9d6 0%,#ffd76e 45%,#c98f13 100%);
            -webkit-background-clip:text; background-clip:text; color:transparent;
            text-shadow:0 0 14px rgba(255,196,60,0.35); }

  /* ---- whose-queue bar ---- */""",
    'neon system')

# ---- apply the shell to each menu -------------------------------------
sub('''  .qbar { display:flex; align-items:center; gap:8px; flex-wrap:wrap;
          width:calc(100% - 4px); margin:0 2px 10px; padding:9px 12px;
          background:rgba(12,18,34,0.78); border:1px solid rgba(120,150,190,0.3);
          border-radius:13px; }
  .qbar-lbl { font-size:14px; font-weight:900; color:#dbeafe; letter-spacing:0.4px;
              margin-right:4px; }''',
    '''  .qbar { --neon:#a855f7; display:flex; align-items:center; gap:9px; flex-wrap:wrap;
          padding:11px 13px; }
  .qbar-lbl { font-size:14px; font-weight:900; color:#eaf4ff; letter-spacing:1.1px;
              text-transform:uppercase; margin-right:2px;
              text-shadow:0 0 10px rgba(168,85,247,0.7); }''',
    'qbar shell')

sub('''  .qlink { flex:1 1 130px; display:flex; flex-direction:column; align-items:flex-start;
           gap:1px; padding:8px 12px; font-family:inherit; cursor:pointer;
           background:rgba(255,255,255,0.03); border:1px solid var(--qc);
           border-radius:11px; color:#e8f0ff; }''',
    '''  .qlink { flex:1 1 132px; display:flex; flex-direction:column; align-items:flex-start;
           gap:1px; padding:9px 13px; font-family:inherit; cursor:pointer;
           color:#e8f0ff; border-radius:11px;
           background:linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0));
           border:1px solid color-mix(in srgb, var(--qc) 55%, transparent);
           box-shadow:0 0 0 rgba(0,0,0,0); transition:box-shadow .15s, background .15s; }''',
    'qlink shell')

sub('''  .done-btn { display:flex; align-items:center; justify-content:space-between; gap:10px;
              width:calc(100% - 4px); margin:0 2px 10px; padding:13px 16px;
              font-family:inherit; font-size:15px; font-weight:900; letter-spacing:0.4px;
              color:#dbeafe; background:rgba(12,18,34,0.78); cursor:pointer;
              border:1px solid rgba(120,150,190,0.3); border-radius:13px; }
  .done-btn.on { border-color:rgba(34,211,238,0.5);
                 box-shadow:0 0 14px rgba(34,211,238,0.16); }
  .done-btn:active { transform:translateY(1px); filter:brightness(1.1); }
  .db-tot { display:flex; gap:12px; font-size:13px; font-weight:900; }''',
    '''  .done-btn { --neon:#22c55e; display:flex; align-items:center;
              justify-content:space-between; gap:10px; padding:14px 17px;
              font-family:inherit; font-size:15px; font-weight:900; letter-spacing:1.1px;
              text-transform:uppercase; color:#eaf4ff; cursor:pointer;
              text-shadow:0 0 10px rgba(34,197,94,0.6); }
  .db-tot { display:flex; gap:14px; font-size:13.5px; font-weight:900;
            letter-spacing:0.3px; text-transform:none; }''',
    'done-btn shell')

sub('''  .adhoc-btn { display:block; width:calc(100% - 4px); margin:0 2px 12px; padding:13px 16px;''',
    '''  .adhoc-btn { --neon:#f97316; display:block; padding:14px 17px;''',
    'adhoc shell')

sub('''  .rothead { cursor:pointer; user-select:none; }''',
    '''  .rothead { cursor:pointer; user-select:none; letter-spacing:1px;
             text-transform:uppercase; }''',
    'rothead')

sub('''  .roomgrp { margin:0 0 8px; border:1px solid rgba(120,150,190,0.22); border-radius:12px;
             background:rgba(12,18,34,0.55); overflow:hidden; }
  .roomgrp.open { border-color:rgba(34,211,238,0.45);
                  box-shadow:0 0 14px rgba(34,211,238,0.14); }''',
    '''  .roomgrp { --neon:#22d3ee; position:relative; margin:0 0 9px; border-radius:12px;
             overflow:hidden;
             background:linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0) 40%),
                        linear-gradient(180deg,#0b1020,#080d18);
             border:1px solid rgba(140,170,215,0.2);
             box-shadow:0 1px 0 rgba(255,255,255,0.04) inset; }
  .roomgrp::before { content:''; position:absolute; inset:0 0 auto 0; height:2px;
                     background:linear-gradient(90deg, transparent, #22d3ee 20%,
                                #22d3ee 80%, transparent);
                     box-shadow:0 0 10px #22d3ee; opacity:.55; }
  .roomgrp.open { border-color:rgba(34,211,238,0.5);
                  box-shadow:0 0 22px rgba(34,211,238,0.2); }
  .roomgrp.open::before { opacity:1; }''',
    'roomgrp shell')

sub('''  .rmname { font-size:16px; font-weight:900; letter-spacing:0.4px; flex:none; }''',
    '''  .rmname { font-size:16px; font-weight:900; letter-spacing:1px; flex:none;
             text-transform:uppercase; text-shadow:0 0 9px rgba(34,211,238,0.45); }''',
    'rmname')

tmp = P + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(s)
os.replace(tmp, P)
print('styles: one neon menu system across the stack')
