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

export default function StepScreen({
  step, settings, paused, praiseLine, awayNote, log, onDone, onBreak, onHelp, onSpeak, splitToken, onSeeAll,
}) {
  const base = BASE[step.mode] ?? 1;
  const [reveal, setReveal] = useState(base);
  const [offerStage, setOfferStage] = useState(0);
  const [offerAnswered, setOfferAnswered] = useState(0); // stages already answered
  const [shownSmall, setShownSmall] = useState(1);       // small steps showing at Most help
  const [showVideo, setShowVideo] = useState(false);

  // prompted = "yes" only if help came to the person during this step (they said yes to
  // "Want help with this step?"). What the level shows at the start is not a prompt, and
  // neither is help they asked for themselves.
  const promptedRef = useRef(false);
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
      const elapsed = activeMsRef.current;
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
  }, [paused, step]);

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
  }

  // "Show the small steps" on the Help screen comes back here as a new splitToken.
  useEffect(() => {
    if (!splitToken || reveal >= 2) return;
    log(reveal === 0 ? "hint_requested" : "more_help_requested", { step_id: step.step_id, help_shown: "split" });
    setReveal(2);
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
  }

  // "Read again" is the Repeat button. It reads what is on the screen, in order: the step, the
  // CAUTION (most important for someone who listens instead of reads), the small steps that are
  // showing, then the tips if they are open. Nothing hidden is read.
  function repeat() {
    log("repeat_requested", { step_id: step.step_id });
    const parts = [step.text];
    if (step.safety) parts.push(`Caution: ${step.safety}`);
    if (reveal >= 2) substeps.slice(0, shownSmall).forEach((s) => parts.push(s.text));
    if (tipsOpen) step.tips.forEach((t) => parts.push(t));
    onSpeak(parts.map((t) => t.trim().replace(/[.:]?$/, ".")).join(" "));
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

      {reveal === 0 ? (
        <button className="card folded" onClick={openFolded}>
          <span className="next-line">Next: {step.text}</span>
          <span className="muted">Tap to open</span>
        </button>
      ) : (
        <div className="card">
          <div className="step-title">
            <h1 className="step-text">{step.text}</h1>
            <button className="navbtn read-again" onClick={repeat}>
              <Icon.speaker /> Read again
            </button>
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
          {reveal >= 2 && substeps.length > 0 && (
            <>
              <ol className="small-steps">
                {substeps.slice(0, shownSmall).map((s) => <li key={s.id}>{s.text}</li>)}
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
              <ul>{step.tips.map((t, i) => <li key={i}>{t}</li>)}</ul>
            </details>
          )}
        </div>
      )}

      {reveal === 0 && step.safety && <p className="caution"><strong>CAUTION:</strong> {step.safety}</p>}

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
