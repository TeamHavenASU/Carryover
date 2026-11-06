import { useEffect, useRef, useState } from "react";
import { Icon } from "../../lib/icons";
import { speak } from "../../lib/settings";
import { EXAMPLES, interpret, lev, words, yesNo } from "../../lib/voiceCommands";
import { findClickable } from "../../lib/voiceDom";
import "./VoiceAgent.css";

// The voice helper: a microphone and an "i" button on every page.
// Tap the microphone once. The browser asks for permission first (allow once, or while visiting).
// After that it listens from page to page until it is tapped again, or after 3 minutes with
// nothing said. It shows no transcript and no pop-ups: the page just does what was asked.
// It presses the same buttons a person would, so it works on every page: say a button's words
// ("continue", "next", "skip", "sky", "heat a meal") or an action ("read it again", "I need
// help"). It never presses "Done" by itself: it asks "Did you finish this step?" and waits for
// a yes. Carryover does not record or keep the audio. The browser's own speech service turns it
// into words (in Chrome, that service is Google's).
const SR = typeof window !== "undefined" ? window.SpeechRecognition || window.webkitSpeechRecognition : null;
const IDLE_MS = 3 * 60 * 1000;

// One listener for the whole app, so the microphone stays on when the page changes.
const engine = { on: false, rec: null, handler: null, subs: new Set(), idle: null, restart: null, quietUntil: 0 };
const emit = () => engine.subs.forEach((f) => f(engine.on));

function stopEngine() {
  engine.on = false;
  clearTimeout(engine.idle);
  clearTimeout(engine.restart);
  const r = engine.rec;
  engine.rec = null;
  try { r && r.abort && r.abort(); } catch { /* ignore */ }
  emit();
}
function armIdle() {
  clearTimeout(engine.idle);
  engine.idle = setTimeout(stopEngine, IDLE_MS);
}
function spawn() {
  if (!engine.on || !SR) return;
  const rec = new SR();
  rec.lang = "en-US";
  rec.continuous = true;
  rec.interimResults = false;
  rec.maxAlternatives = 4;
  rec.onresult = (e) => {
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const r = e.results[i];
      if (!r.isFinal) continue;
      const alts = [];
      for (let k = 0; k < r.length; k++) alts.push(r[k].transcript);
      if (engine.handler) engine.handler(alts);
    }
  };
  rec.onerror = (e) => {
    if (e.error === "not-allowed" || e.error === "service-not-allowed") { stopEngine(); if (engine.onBlocked) engine.onBlocked(); }
  };
  rec.onend = () => { if (engine.on && engine.rec === rec) engine.restart = setTimeout(spawn, 300); };
  engine.rec = rec;
  try { rec.start(); } catch { /* it starts again on the next end */ }
}
// Asks the browser for the microphone first, so the usual "Allow" question appears.
async function startEngine() {
  if (!SR) return "unsupported";
  try {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((t) => t.stop());
    }
  } catch { return "blocked"; }
  engine.on = true;
  armIdle();
  emit();
  spawn();
  return "ok";
}

const WHILE_READING = ["pause", "play", "replay", "help", "break", "stopListening"];

export default function VoiceAgent({ settings, view, tasks, onCommand }) {
  const [on, setOn] = useState(engine.on);
  const [info, setInfo] = useState(false);
  const [pending, setPending] = useState(false); // waiting for a yes or no to "Did you finish this step?"
  const [notice, setNotice] = useState("");
  const [live, setLive] = useState("");          // read by screen readers only
  const pendingRef = useRef(false);
  const noticeTimer = useRef(null);
  const latest = useRef({});
  latest.current = { view, tasks, onCommand, settings };
  const handleRef = useRef(null);

  const setPend = (v) => { pendingRef.current = v; setPending(v); };

  useEffect(() => {
    engine.subs.add(setOn);
    setOn(engine.on);
    const mine = (alts) => handleRef.current && handleRef.current(alts);
    engine.handler = mine;
    engine.onBlocked = () => showNotice("The microphone is blocked. Allow it in your browser, then tap the microphone again.");
    return () => {
      engine.subs.delete(setOn);
      if (engine.handler === mine) engine.handler = null;
      clearTimeout(noticeTimer.current);
    };
  }, []);

  // The question is only asked on a step.
  useEffect(() => { if (view !== "step" && pendingRef.current) setPend(false); }, [view]);

  function showNotice(text) {
    setNotice(text);
    clearTimeout(noticeTimer.current);
    noticeTimer.current = setTimeout(() => setNotice(""), 7000);
  }

  // Spoken only for questions and for things that need an answer. The microphone ignores the
  // app's own voice while it speaks.
  function say(text) {
    setLive(text);
    engine.quietUntil = Date.now() + 60000;
    speak(text, latest.current.settings, { onend: () => { engine.quietUntil = Date.now() + 900; }, onerror: () => { engine.quietUntil = 0; } });
  }

  function tell(name) { window.dispatchEvent(new CustomEvent("carryover:voice", { detail: { action: name } })); }

  function ask() {
    tell("dismissOffer");
    setPend(true);
    say("Did you finish this step? Say yes or no.");
  }

  // Press the button the person named. "Done" always goes through the question first.
  function press(item) {
    if (/^done$/i.test(item.label)) {
      const pre = latest.current.onCommand("prepareDone");
      if (pre.ok) ask(); else say(pre.say);
      return;
    }
    item.el.click();
    setLive(item.label);
  }

  function act(r) {
    const { view: v, onCommand: run } = latest.current;
    if (r.action === "stopListening") { stopEngine(); return; }
    if (r.action === "examples") { setInfo(true); return; }
    if (r.action === "clarify") { say(`Which one? ${r.arg.map((t) => t.title).join(", or ")}.`); return; }
    if (r.action === "done") {
      if (v === "splash") { run("play"); return; }
      const pre = run("prepareDone");
      if (pre.ok) ask(); else say(pre.say);
      return;
    }
    const res = run(r.action, r.arg);
    if (res.ok) setLive(res.say); else say(res.say);
  }

  // Everything heard comes here, with the browser's best few guesses at the words.
  function handleAlts(alts) {
    const { tasks: ts, onCommand: run } = latest.current;
    armIdle();
    tell("activity");
    // eslint-disable-next-line no-console
    console.log("[voice] heard", alts);
    const clean = alts.map((a) => a.trim()).filter(Boolean);
    if (!clean.length) return;

    const BACKISH = ["back", "bag", "pack", "bak", "beck", "bach", "black", "buck", "bec"];
    const isBack = (a) => { const w = words(a); return w.length > 0 && w.length <= 3 && w.some((x) => BACKISH.includes(x) || (x.length >= 3 && lev(x, "back") <= 1)); };
    if (clean.some(isBack)) {
      setPend(false);
      try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch { /* ignore */ }
      const rb = latest.current.onCommand("back");
      // eslint-disable-next-line no-console
      console.log("[voice] heard", clean, "-> back", rb);
      if (rb.ok) setLive(rb.say); else say(rb.say);
      return;
    }

    const said = (a) => a.toLowerCase().replace(/[^a-z ]/g, " ").replace(/ +/g, " ").trim();
    if (info && clean.some((a) => /\b(close|closed|clothes|got it|okay|ok|dismiss|exit)\b/.test(said(a)))) { setInfo(false); setLive("Closed."); return; }
    if (!info && clean.some((a) => /\b(info|information|i button|the i|eye button|how does it work|how the microphone works|instructions)\b/.test(said(a)))) { setInfo(true); return; }

    if (pendingRef.current) {
      for (const a of clean) {
        const yn = yesNo(a);
        if (yn === "yes") { setPend(false); const r = run("doneConfirmed"); if (r.ok) setLive(r.say); else say(r.say); return; }
        if (yn === "no") { setPend(false); setLive("Okay. Take your time."); return; }
      }
      return;
    }

    if (latest.current.view === "done") {
      for (const a of clean) { const f = findClickable(a); if (f.exact) { press(f.exact); return; } }
      for (const a of clean) { const r = interpret(a, ts); if (["tasks", "start", "play", "done", "home"].includes(r.action)) { act(r); return; } }
    }
    const busy = (window.speechSynthesis && window.speechSynthesis.speaking) || Date.now() < engine.quietUntil;
    if (busy) {
      // While something is being read aloud, only short control words count.
      for (const a of clean) {
        const r = interpret(a, ts);
        if (words(a).length <= 3 && WHILE_READING.includes(r.action)) { act(r); return; }
      }
      return;
    }

    for (const a of clean) { const f = findClickable(a); if (f.exact) { press(f.exact); return; } }
    for (const a of clean) { const r = interpret(a, ts); if (r.action !== "unknown") { act(r); return; } }
    for (const a of clean) {
      const f = findClickable(a);
      if (f.fuzzy) { press(f.fuzzy); return; }
      if (f.options) { say(`Which one? ${f.options.join(", or ")}.`); return; }
    }
  }
  handleRef.current = handleAlts;

  async function toggle() {
    if (engine.on) { stopEngine(); return; }
    setInfo(false);
    const r = await startEngine();
    if (r === "blocked") showNotice("The microphone is blocked. Allow it in your browser, then tap the microphone again.");
    if (r === "unsupported") showNotice("This browser does not have listening. Try Chrome or Safari, or tap the buttons.");
  }

  function answer(yes) {
    setPend(false);
    if (yes) { const r = latest.current.onCommand("doneConfirmed"); if (!r.ok) say(r.say); } else setLive("Okay. Take your time.");
  }

  return (
    <span className="mic-bar">
      <button className="icon-btn info-btn" onClick={() => setInfo((v) => !v)}
        aria-expanded={info} aria-label="How the microphone works" data-tip="How the microphone works">
        <span aria-hidden="true">i</span>
      </button>
      <button className={`icon-btn mic ${on ? "on" : ""}`} onClick={toggle}
        aria-pressed={on} aria-label="Microphone" data-tip={on ? "Microphone is on. Tap to turn off" : "Turn the microphone on"}>
        <Icon.mic />
      </button>
      <span className="visually-hidden" role="status" aria-live="polite">{live}</span>

      {info && (
        <div className="card voice-panel" role="dialog" aria-label="How the microphone works">
          <h2>How the microphone works</h2>
          <div className="voice-scroll">
          <ul className="voice-examples">
            <li>Tap the microphone once. Your browser asks your permission first. After that it stays on from page to page.</li>
            <li>Tap it again to turn it off. It also turns off after 3 minutes with nothing said.</li>
            <li>Say the words on any button or choice: continue, next, skip, sky, slow, soft, heat a meal.</li>
            {EXAMPLES.map((x) => <li key={x}>{x}</li>)}
          </ul>
          <p className="muted note">While it is on, your browser listens and turns your voice into words. In Chrome, that is done by Google. Carryover does not record or keep your voice.</p>
          </div>
          <button className="btn" onClick={() => setInfo(false)}>Close</button>
        </div>
      )}

      {pending && !info && (
        <div className="card voice-confirm" role="alertdialog" aria-label="Did you finish this step?">
          <p><strong>Did you finish this step?</strong></p>
          <div className="row">
            <button className="btn primary" onClick={() => answer(true)}>Yes, I finished</button>
            <button className="btn" onClick={() => answer(false)}>Not yet</button>
          </div>
        </div>
      )}

      {notice && <div className="card voice-confirm" role="alert"><p>{notice}</p></div>}
    </span>
  );
}
