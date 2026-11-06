import { useEffect, useRef, useState } from "react";
import { Icon } from "../lib/icons";

// How much of the step is showing, from the help level in today's view:
//   0 = folded: "Next: <step>"                       -> mode "hide"
//   1 = the full step sentence only                  -> mode "hint"
//   2 = the step plus small steps, one at a time     -> mode "split"
// The level comes from the backend. The screen only reveals more when asked.
const BASE = { hide: 0, hint: 1, split: 2 };
const LEVEL_OF = ["hide", "hint", "split"];

const IMG_BASE = import.meta.env.BASE_URL + "img/";
const VIDEO_BASE = import.meta.env.BASE_URL + "video/";

// A step's video is null today. Accepts a file name, a web address, or {file, credit}.
const videoSource = (v) => {
  const file = typeof v === "string" ? v : v.file || v.url;
  return /^(https?:)?\//.test(file) ? file : VIDEO_BASE + file;
};

// Under pictures of a device: a picture marked device: true in the task file, or one whose
// description names a microwave.
const isDevicePicture = (p) => p.device === true || /microwave/i.test(p.alt || "");

// The words of a line, each one tappable: tap a word and reading starts from it. The word being
// read is highlighted.
function Spoken({ id, text, hl, onPick }) {
  const out = [];
  const re = /\S+/g;
  let last = 0;
  let m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const s = m.index;
    const e = s + m[0].length;
    const on = hl && hl.key === id && hl.start >= s && hl.start < e;
    out.push(
      <span key={s} role="button" tabIndex={0} className={`word${on ? " hl" : ""}`}
        onClick={() => onPick(id, s)}
        onKeyDown={(ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); onPick(id, s); } }}>
        {m[0]}
      </span>
    );
    last = e;
  }
  if (last < text.length) out.push(text.slice(last));
  return <>{out}</>;
}

export default function StepScreen({
  step, settings, paused, praiseLine, awayNote, log, onDone, onBreak, onHelp, onSpeak, splitToken, onSeeAll,
}) {
  const base = BASE[step.mode] ?? 1;
  // The step is always shown. A step that starts folded (help level 0) now shows its sentence.
  const [reveal, setReveal] = useState(Math.max(base, 1));
  const [offerStage, setOfferStage] = useState(0);
  const [offerAnswered, setOfferAnswered] = useState(0); // stages already answered
  const [shownSmall, setShownSmall] = useState(1);       // small steps showing at Most help
  const [showVideo, setShowVideo] = useState(false);
  const [reading, setReading] = useState("idle"); // idle | playing | paused
  const readingRef = useRef("idle");
  const segs = useRef([]);      // pieces to read, in order
  const pos = useRef(0);        // the piece to read next
  const off = useRef(0);        // the letter in that piece where reading stopped
  const token = useRef(0);      // changes whenever reading is stopped or restarted
  const started = useRef(false); // audio was started on this step
  const [hl, setHl] = useState(null); // the word being read: { key, start }
  const setR = (v) => { readingRef.current = v; setReading(v); if (v === "idle") setHl(null); };
  useEffect(() => {
    token.current += 1;
    window.speechSynthesis?.cancel();
    segs.current = []; pos.current = 0; off.current = 0; started.current = false;
    setR("idle");
    return () => { token.current += 1; window.speechSynthesis?.cancel(); };
  }, [step.step_id]); // eslint-disable-line react-hooks/exhaustive-deps

  // prompted = "yes" only if help came to the person during this step (they said yes to
  // "Want help with this step?"). What the level shows at the start is not a prompt, and
  // neither is help they asked for themselves.
  const promptedRef = useRef(false);
  const resetAtRef = useRef(0);           // activity (speech, taps) restarts the help timers from here
  const [activityTick, setActivityTick] = useState(0);
  const activeMsRef = useRef(0);          // time on this step, break time excluded
  const runningSinceRef = useRef(null);
  const loggedStart = useRef(false);
  const tipsLogged = useRef(false);
  const [tipsOpen, setTipsOpen] = useState(false);

  // Log that the step was shown once.
  useEffect(() => {
    if (loggedStart.current) return;
    loggedStart.current = true;
    log("step_started", { step_id: step.step_id, help_shown: step.mode });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Timing. Stops while paused (break time never counts) and never runs on waiting steps.
  useEffect(() => {
    if (paused) return undefined;
    runningSinceRef.current = Date.now();
    const timers = [];
    if (!step.wait) {
      const elapsed = activeMsRef.current - resetAtRef.current;
      step.hint_waits.forEach((sec, i) => {
        const wait = sec * 1000 - elapsed;
        if (wait <= 0) {
          setOfferStage((n) => Math.max(n, i + 1));
        } else {
          timers.push(setTimeout(() => {
            setOfferStage((n) => Math.max(n, i + 1));
          }, wait));
        }
      });
    }
    return () => {
      timers.forEach(clearTimeout);
      activeMsRef.current += Date.now() - runningSinceRef.current;
      runningSinceRef.current = null;
    };
  }, [paused, step, activityTick]);

  const offerShown = offerStage > offerAnswered && reveal < 2 && !step.wait;

  const substeps =
    step.substeps_by_phone && step.substeps_by_phone[settings.phoneType]
      ? step.substeps_by_phone[settings.phoneType]
      : step.substeps;

  function openMore(eventName) {
    const next = Math.min(reveal + 1, 2);
    if (next === reveal) return;
    log(eventName, { step_id: step.step_id, help_shown: LEVEL_OF[next] });
    setReveal(next);
    if (next >= 2 && substeps[0]) queueRead({ key: "small-" + substeps[0].id, text: substeps[0].text });
  }

  // "Show the small steps" on the Help screen comes back here as a new splitToken.
  useEffect(() => {
    if (!splitToken || reveal >= 2) return;
    log(reveal === 0 ? "hint_requested" : "more_help_requested", { step_id: step.step_id, help_shown: "split" });
    setReveal(2);
    if (substeps[0]) queueRead({ key: "small-" + substeps[0].id, text: substeps[0].text });
  }, [splitToken]); // eslint-disable-line react-hooks/exhaustive-deps

  // "Help with this step" counts as used help the moment it is tapped (hint_requested is in
  // definitions.json used_help_events), so opening Help and leaving never looks like "done alone".
  function helpTap() {
    log("hint_requested", { step_id: step.step_id, help_shown: LEVEL_OF[Math.min(reveal, 2)] });
    onHelp();
  }

  // Folded step ("Next: ..."): one tap opens it.
  function openFolded() {
    openMore("hint_requested");
  }

  function answerOffer(yes) {
    log("help_offer_answer", { step_id: step.step_id, answer: yes ? "yes" : "no" });
    setOfferAnswered(offerStage);
    if (yes) promptedRef.current = true;
    if (yes) openMore(reveal === 0 ? "hint_requested" : "more_help_requested");
  }

  function showNextSmall() {
    const next = substeps[shownSmall];
    if (!next) return;
    log("small_step_opened", { step_id: step.step_id, answer: next.id });
    setShownSmall(shownSmall + 1);
    queueRead({ key: "small-" + next.id, text: next.text });
  }

  // The button on the step itself, there from the first moment.
  function showSmallSteps() {
    openMore(reveal === 0 ? "hint_requested" : "more_help_requested");
  }

  // Reading aloud works through a list of pieces: the step, the CAUTION, the small steps showing,
  // then the tips if they are open. Replay starts from the first piece. Pause stops at the word
  // it is on and Play carries on from there. Tapping any word starts reading from that word. A
  // small step that opens later is added to the end, so it is read next.
  const clean = (x) => x.trim().replace(/[.:]?$/, ".");
  function buildParts() {
    const parts = [{ key: "step", text: step.text }];
    if (step.safety) parts.push({ key: "caution", text: `Caution: ${step.safety}` });
    if (reveal >= 2) substeps.slice(0, shownSmall).forEach((s) => parts.push({ key: "small-" + s.id, text: s.text }));
    if (tipsOpen) step.tips.forEach((tip, i) => parts.push({ key: "tip-" + i, text: tip }));
    return parts;
  }

  function playFrom() {
    const my = ++token.current;
    started.current = true;
    setR("playing");
    const next = () => {
      if (token.current !== my) return;
      if (pos.current >= segs.current.length) { setR("idle"); return; }
      const i = pos.current;
      const part = segs.current[i];
      const full = clean(part.text);
      const from = Math.min(off.current, full.length);
      onSpeak(full.slice(from), {
        onboundary: (e) => {
          if (token.current !== my || e.name === "sentence") return;
          off.current = from + e.charIndex;
          setHl({ key: part.key, start: from + e.charIndex });
        },
        onend: () => { if (token.current !== my) return; pos.current = i + 1; off.current = 0; next(); },
        onerror: (e) => {
          if (token.current !== my) return;
          if (e && (e.error === "canceled" || e.error === "interrupted")) return;
          setR("idle");
        },
      });
    };
    next();
  }

  function repeat() {
    log("repeat_requested", { step_id: step.step_id });
    segs.current = buildParts();
    pos.current = 0;
    off.current = 0;
    window.speechSynthesis?.cancel();
    playFrom();
  }

  // Tap a word: read from that word on.
  function readFrom(key, charStart) {
    const parts = buildParts();
    const i = parts.findIndex((x) => x.key === key);
    if (i < 0) return;
    log("repeat_requested", { step_id: step.step_id });
    segs.current = parts;
    pos.current = i;
    off.current = charStart;
    window.speechSynthesis?.cancel();
    playFrom();
  }

  function pauseReading() {
    token.current += 1;
    window.speechSynthesis?.cancel();
    setR("paused");
  }

  function togglePlay() {
    if (readingRef.current === "playing") pauseReading();
    else if (readingRef.current === "paused") playFrom();
    else if (started.current && pos.current < segs.current.length) playFrom();
    else repeat();
  }

  // A small step just opened: add it to the reading. If audio was never started, nothing is read.
  function queueRead(part) {
    if (!started.current) return;
    segs.current.push(part);
    if (readingRef.current === "idle") playFrom(); // it had finished: read the new piece now
  }

  function done() {
    const seconds = Math.round(
      (activeMsRef.current + (runningSinceRef.current ? Date.now() - runningSinceRef.current : 0)) / 100
    ) / 10;
    log("step_done", {
      step_id: step.step_id,
      seconds,
      help_shown: step.mode, // the level today's view said to show, not what was opened later
      prompted: promptedRef.current ? "yes" : "no",
    });
    onDone();
  }


  // The voice helper sends actions here. They run the same functions as the buttons, so the
  // events logged are the same. Nothing runs while this step is not on screen.
  function markActive(hideOffer) {
    resetAtRef.current = activeMsRef.current + (runningSinceRef.current ? Date.now() - runningSinceRef.current : 0);
    if (hideOffer) setOfferAnswered((n) => Math.max(n, offerStage));
    setActivityTick((n) => n + 1);
  }
  const markRef = useRef(null);
  markRef.current = markActive;
  useEffect(() => {
    const tap = () => { if (!paused && markRef.current) markRef.current(false); };
    window.addEventListener("pointerdown", tap);
    window.addEventListener("keydown", tap);
    return () => { window.removeEventListener("pointerdown", tap); window.removeEventListener("keydown", tap); };
  }, [paused]);
  const voiceRef = useRef(null);
  voiceRef.current = (action) => {
    switch (action) {
      case "replay": repeat(); break;
      case "pause": if (readingRef.current === "playing") pauseReading(); break;
      case "play": if (readingRef.current !== "playing") togglePlay(); break;
      case "smallSteps":
        if (reveal < 2 && substeps.length > 0) showSmallSteps();
        else if (reveal >= 2 && shownSmall < substeps.length) showNextSmall();
        break;
      case "done": done(); break;
      case "help": helpTap(); break;
      case "activity": markActive(false); break;
      case "dismissOffer": markActive(true); break;
      default: break;
    }
  };
  useEffect(() => {
    const onVoice = (e) => { if (!paused && voiceRef.current) voiceRef.current(e.detail && e.detail.action); };
    window.addEventListener("carryover:voice", onVoice);
    return () => window.removeEventListener("carryover:voice", onVoice);
  }, [paused]);

  const fade = settings.animations === "off" ? "" : "fade-in";

  return (
    <section className="has-bottom-actions">
      {awayNote && <div className="card status" role="status"><p>{awayNote}</p></div>}
      {/* One line: what was just done (with a check), where they are now, and All steps */}
      <div className="step-status">
        <p className="step-status-text" aria-live="polite">
          {praiseLine && (
            <span className="done-chip"><span className="done-check"><Icon.check /></span>{praiseLine.replace(/\.$/, "")}</span>
          )}
          <span className="step-count">Step {step.number} of {step.total}</span>
        </p>
        <button className="navbtn" onClick={onSeeAll}>All steps</button>
      </div>

      {(
        <div className="card">
          <div className="step-title">
            <h1 className="step-text"><Spoken id="step" text={step.text} hl={hl} onPick={readFrom} /></h1>
            <div className="read-controls" role="group" aria-label="Read aloud">
              <button className="icon-btn" onClick={repeat} aria-label="Replay" data-tip="Replay"><Icon.replay /></button>
              <button className="icon-btn" onClick={togglePlay}
                aria-label={reading === "playing" ? "Pause" : "Play"} data-tip={reading === "playing" ? "Pause" : "Play"}>
                {reading === "playing" ? <Icon.pause /> : <Icon.play />}
              </button>
            </div>
          </div>
          {/* CAUTION always shows, at every help level, right under the step sentence */}
          {step.safety && <p className="caution"><strong>CAUTION:</strong> {step.safety}</p>}
          {settings.pictures && step.picture && (
            <>
              <img className="step-picture" src={IMG_BASE + step.picture.file} alt={step.picture.alt} />
              {isDevicePicture(step.picture) && <p className="muted">Your microwave may look different.</p>}
            </>
          )}
          {settings.pictures && step.video && (
            showVideo ? (
              <>
                <video className="step-picture" controls src={videoSource(step.video)} />
                {step.video.credit && <p className="muted">{step.video.credit}</p>}
              </>
            ) : (
              <button className="btn" onClick={() => setShowVideo(true)}>Watch a short video</button>
            )
          )}
          {reveal < 2 && substeps.length > 0 && (
            <button className="btn primary" onClick={showSmallSteps}>Show the small steps</button>
          )}
          {reveal >= 2 && substeps.length > 0 && (
            <>
              <ol className="small-steps">
                {substeps.slice(0, shownSmall).map((s) => <li key={s.id}><Spoken id={"small-" + s.id} text={s.text} hl={hl} onPick={readFrom} /></li>)}
              </ol>
              {shownSmall < substeps.length && (
                <button className="btn" onClick={showNextSmall}>
                  Show next small step ({shownSmall + 1} of {substeps.length})
                </button>
              )}
            </>
          )}
          {step.tips.length > 0 && (
            <details onToggle={(e) => {
              setTipsOpen(e.currentTarget.open);
              // Opening the tips counts as used help (definitions.json), logged once per step.
              if (e.currentTarget.open && !tipsLogged.current) {
                tipsLogged.current = true;
                log("hint_requested", { step_id: step.step_id, help_shown: LEVEL_OF[Math.min(reveal, 2)] });
              }
            }}>
              <summary><Icon.open /> Tips</summary>
              <ul>{step.tips.map((tip, i) => <li key={i}><Spoken id={"tip-" + i} text={tip} hl={hl} onPick={readFrom} /></li>)}</ul>
            </details>
          )}
        </div>
      )}

      {/* Fixed to the bottom, same place on every step. The help offer sits just above. */}
      <div className="bottom-actions">
        {offerShown && (
          <div className={`card offer ${fade}`} role="status">
            <p>Want help with this step?</p>
            <div className="row">
              <button className="btn primary" onClick={() => answerOffer(true)}>Yes</button>
              <button className="btn" onClick={() => answerOffer(false)}>No, I'm OK</button>
            </div>
          </div>
        )}
        <button className="btn primary" onClick={done}>Done</button>
        <div className="row">
          <button className="btn" onClick={helpTap}>Help with this step</button>
          <button className="btn" onClick={onBreak}>Take a break</button>
        </div>
      </div>
    </section>
  );
}
