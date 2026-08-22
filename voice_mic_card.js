// Neon "Say It" tile with an in-place listening popup.
//
// Tapping the tile opens an overlay on top of the dashboard — pulsing mic,
// live transcript, and it closes itself when you stop talking. The sentence
// goes through Home Assistant's conversation engine, which is where the Cozi
// list/appointment intents live, so the popup gets the real spoken answer back
// ("Added butter to the Kroger list") instead of a canned OK.
//
// Browsers only hand out the microphone on a secure origin (https or
// localhost). Over plain http the popup falls back to a text box in the same
// frame, so the tile is still useful on the wall tablet.

const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const SILENCE_MS = 2600;      // stop listening this long after the last word
const CLOSE_MS = 2200;        // how long the answer stays up before it closes

const CSS = `
.nvm-tile{display:flex;flex-direction:column;align-items:center;justify-content:center;
  height:88px;margin:0 3px;padding:7px 2px;box-sizing:border-box;cursor:pointer;
  background:rgba(13,20,44,.82);border:1px solid rgba(250,204,21,.35);border-radius:14px;
  box-shadow:0 0 14px rgba(250,204,21,.24),0 6px 16px rgba(0,0,0,.45);
  -webkit-tap-highlight-color:transparent;}
.nvm-tile:active{background:rgba(250,204,21,.10);}
.nvm-tile svg{width:32px;height:32px;fill:#facc15;filter:drop-shadow(0 0 8px rgba(250,204,21,.85));}
.nvm-tile .nvm-lbl{margin-top:3px;font-size:12px;font-weight:700;color:#eaf0fa;line-height:1.05;}

.nvm-back{position:fixed;inset:0;z-index:99999;display:flex;align-items:center;
  justify-content:center;background:rgba(4,7,18,.82);backdrop-filter:blur(7px);
  -webkit-backdrop-filter:blur(7px);animation:nvm-fade .16s ease;}
@keyframes nvm-fade{from{opacity:0}to{opacity:1}}
.nvm-box{width:min(92vw,460px);padding:30px 26px 24px;border-radius:26px;text-align:center;
  font-family:'Segoe UI',Roboto,sans-serif;color:#eaf0fa;background:rgba(10,16,38,.96);
  border:1px solid rgba(34,211,238,.45);
  box-shadow:0 0 44px rgba(34,211,238,.22),0 20px 60px rgba(0,0,0,.7);}
.nvm-ring{position:relative;width:140px;height:140px;margin:4px auto 16px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  background:radial-gradient(circle at 50% 35%,rgba(34,211,238,.28),rgba(13,20,44,.9));
  border:2px solid rgba(34,211,238,.6);}
.nvm-ring svg{width:62px;height:62px;fill:#7ee7f7;filter:drop-shadow(0 0 12px rgba(34,211,238,.9));}
.nvm-ring.on{border-color:rgba(244,114,182,.9);
  background:radial-gradient(circle at 50% 35%,rgba(244,114,182,.32),rgba(13,20,44,.9));
  animation:nvm-pulse 1.15s ease-in-out infinite;}
.nvm-ring.on svg{fill:#fbcfe8;filter:drop-shadow(0 0 14px rgba(244,114,182,.95));}
.nvm-ring.ok{border-color:rgba(45,212,191,.85);
  background:radial-gradient(circle at 50% 35%,rgba(45,212,191,.30),rgba(13,20,44,.9));}
.nvm-ring.ok svg{fill:#8ef2dd;}
.nvm-ring.bad{border-color:rgba(244,63,94,.8);}
@keyframes nvm-pulse{
  0%,100%{box-shadow:0 0 20px rgba(244,114,182,.35),inset 0 0 26px rgba(244,114,182,.10);transform:scale(1);}
  50%{box-shadow:0 0 52px rgba(244,114,182,.8),inset 0 0 40px rgba(244,114,182,.26);transform:scale(1.045);}}
.nvm-said{min-height:26px;font-size:19px;font-weight:700;line-height:1.35;margin:2px 6px 8px;}
.nvm-said.dim{color:#8195b5;font-weight:600;font-size:15px;}
.nvm-ans{font-size:16px;font-weight:700;line-height:1.4;margin:10px 4px 0;color:#8ef2dd;}
.nvm-ans.bad{color:#ffc7e2;}
.nvm-row{display:flex;gap:9px;margin-top:14px;}
.nvm-row input{flex:1;min-width:0;background:#0a1226;border:2px solid rgba(34,211,238,.4);
  color:#eaf0fa;border-radius:12px;padding:13px 13px;font-size:16px;outline:none;}
.nvm-row button{background:rgba(34,211,238,.2);color:#7ee7f7;border:1px solid rgba(34,211,238,.6);
  border-radius:12px;padding:0 18px;font-size:16px;font-weight:800;cursor:pointer;}
.nvm-foot{margin-top:14px;font-size:11.5px;letter-spacing:.4px;color:#8195b5;}
.nvm-foot span{color:#7ee7f7;cursor:pointer;}
`;

const MIC_SVG = '<svg viewBox="0 0 24 24"><path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z"/></svg>';
const OK_SVG = '<svg viewBox="0 0 24 24"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>';

class VoiceMicCard extends HTMLElement {
  setConfig(config) {
    this._config = config || {};
    if (!this._built) this._build();
  }

  set hass(hass) { this._hass = hass; }

  getCardSize() { return 1; }

  _build() {
    this._built = true;
    const root = this.attachShadow({mode: 'open'});
    const style = document.createElement('style');
    style.textContent = CSS;
    const tile = document.createElement('div');
    tile.className = 'nvm-tile';
    tile.innerHTML = MIC_SVG + '<div class="nvm-lbl">' +
      ((this._config && this._config.name) || 'Say It') + '</div>';
    // pointerup, not click: touchscreens swallow synthetic clicks on these cards
    tile.addEventListener('pointerup', () => this._open());
    root.append(style, tile);
  }

  // ---------------------------------------------------------------- popup
  _open() {
    if (this._back) return;
    const back = document.createElement('div');
    back.className = 'nvm-back';
    const shadow = back.attachShadow ? null : null;   // overlay lives in the page
    const style = document.createElement('style');
    style.textContent = CSS;
    back.appendChild(style);
    const box = document.createElement('div');
    box.className = 'nvm-box';
    box.innerHTML =
      '<div class="nvm-ring"><span class="nvm-ico">' + MIC_SVG + '</span></div>' +
      '<div class="nvm-said dim">Listening…</div>' +
      '<div class="nvm-ans"></div>' +
      '<div class="nvm-foot">Say “add butter to the Kroger list” · <span>recent</span></div>';
    back.appendChild(box);
    back.addEventListener('pointerup', e => { if (e.target === back) this._close(); });
    box.querySelector('.nvm-foot span').addEventListener('pointerup', e => {
      e.stopPropagation();
      this._close();
      history.pushState(null, '', '/el-dashboardio/voice');
      window.dispatchEvent(new CustomEvent('location-changed', {detail: {replace: false}}));
    });
    document.body.appendChild(back);
    this._back = back;
    this._esc = e => { if (e.key === 'Escape') this._close(); };
    window.addEventListener('keydown', this._esc);

    this._ring = box.querySelector('.nvm-ring');
    this._said = box.querySelector('.nvm-said');
    this._ans = box.querySelector('.nvm-ans');
    this._foot = box.querySelector('.nvm-foot');

    if (SR && window.isSecureContext) this._listen();
    else this._noMic();
  }

  _close() {
    clearTimeout(this._silence);
    clearTimeout(this._autoclose);
    try { if (this._rec) { this._rec.onend = null; this._rec.abort(); } } catch (e) {}
    this._rec = null;
    window.removeEventListener('keydown', this._esc);
    if (this._back) this._back.remove();
    this._back = null;
  }

  // No usable microphone (almost always: the dashboard is served over plain
  // http, and browsers only hand out the mic on a secure origin). Say so and
  // get out of the way — the Say It page still takes typing.
  _noMic() {
    this._ring.classList.add('bad');
    this._said.textContent = window.isSecureContext
      ? 'This browser has no microphone support'
      : 'Microphone needs an https address';
    this._said.classList.add('dim');
    this._ans.textContent = 'Tap “recent” to type it instead';
    this._autoclose = setTimeout(() => this._close(), 4200);
  }

  _typeInstead(box) {
    this._said.textContent = 'Type it';
    this._said.classList.add('dim');
    this._foot.innerHTML = window.isSecureContext
      ? 'This browser has no speech recognition · <span>recent</span>'
      : 'Microphone needs https — typing works everywhere · <span>recent</span>';
    this._foot.querySelector('span').addEventListener('pointerup', e => {
      e.stopPropagation();
      this._close();
      history.pushState(null, '', '/el-dashboardio/voice');
      window.dispatchEvent(new CustomEvent('location-changed', {detail: {replace: false}}));
    });
    const row = document.createElement('div');
    row.className = 'nvm-row';
    row.innerHTML = '<input placeholder="add butter to the kroger list"><button>Send</button>';
    box.insertBefore(row, this._ans);
    const input = row.querySelector('input');
    const go = () => { const v = input.value.trim(); if (v) { row.remove(); this._send(v); } };
    row.querySelector('button').addEventListener('pointerup', e => { e.stopPropagation(); go(); });
    input.addEventListener('keydown', e => { if (e.key === 'Enter') go(); });
    setTimeout(() => input.focus(), 60);
  }

  _listen() {
    const rec = new SR();
    this._rec = rec;
    rec.lang = 'en-US';
    rec.interimResults = true;
    rec.continuous = false;
    rec.maxAlternatives = 1;
    this._ring.classList.add('on');

    const quiet = () => {                       // no words for a while -> stop
      clearTimeout(this._silence);
      this._silence = setTimeout(() => { try { rec.stop(); } catch (e) {} }, SILENCE_MS);
    };
    quiet();

    rec.onresult = e => {
      let text = '', done = false;
      for (const r of e.results) { text += r[0].transcript; if (r.isFinal) done = true; }
      this._said.textContent = text;
      this._said.classList.remove('dim');
      quiet();
      if (done) { clearTimeout(this._silence); this._send(text); }
    };
    rec.onerror = e => {
      clearTimeout(this._silence);
      this._ring.classList.remove('on');
      this._ring.classList.add('bad');
      this._said.textContent = e.error === 'not-allowed'
        ? 'Microphone is blocked' : 'Didn’t catch that';
      this._said.classList.add('dim');
      this._autoclose = setTimeout(() => this._close(), CLOSE_MS);
    };
    rec.onend = () => {
      this._ring.classList.remove('on');
      if (!this._sent && !this._back) return;
      if (!this._sent) {                        // stopped without hearing anything
        this._said.textContent = 'Nothing heard';
        this._said.classList.add('dim');
        this._autoclose = setTimeout(() => this._close(), 1300);
      }
    };
    try { rec.start(); } catch (e) { this._typeInstead(this._back.querySelector('.nvm-box')); }
  }

  async _send(text) {
    this._sent = true;
    clearTimeout(this._silence);
    try { if (this._rec) { this._rec.onend = null; this._rec.abort(); } } catch (e) {}
    this._ring.classList.remove('on');
    this._said.textContent = text;
    this._said.classList.remove('dim');
    this._ans.textContent = 'Working…';
    let speech = '', ok = false;
    try {
      const r = await this._hass.callWS({type: 'conversation/process', text});
      speech = r?.response?.speech?.plain?.speech || '';
      ok = r?.response?.response_type !== 'error';
    } catch (e) {
      speech = 'Home Assistant did not answer.';
    }
    this._ans.textContent = speech || (ok ? 'Done.' : 'Sorry, that did not work.');
    this._ans.classList.toggle('bad', !ok);
    this._ring.classList.add(ok ? 'ok' : 'bad');
    if (ok) this._ring.querySelector('.nvm-ico').innerHTML = OK_SVG;
    this._speak(speech);
    this._autoclose = setTimeout(() => this._close(), CLOSE_MS + (speech.length > 60 ? 1400 : 0));
  }

  _speak(text) {
    try {
      if (!text || !window.speechSynthesis) return;
      const u = new SpeechSynthesisUtterance(text);
      u.rate = 1.03;
      speechSynthesis.cancel();
      speechSynthesis.speak(u);
    } catch (e) {}
  }
}

customElements.define('voice-mic-card', VoiceMicCard);
window.customCards = window.customCards || [];
window.customCards.push({type: 'voice-mic-card', name: 'Say It (voice popup)',
                         description: 'Neon mic tile that opens a listening popup'});
