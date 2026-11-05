import { useEffect, useRef, useState } from "react";

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

// Under pictures of a device: the task file does not mark them yet, so a picture whose
// description names a microwave counts, or one marked device: true.
const isDevicePicture = (p) => p.device === true || /microwave/i.test(p.alt || "");

export default function StepScreen({
  step, today, settings, index, paused, praiseLine, awayNote, log, onDone, onBackStep, onBreak, onSeeAll, onSpeak,
}) {
  const base = BASE[step.mode] ?? 1;
  const [reveal, setReveal] = useState(base);
  const [offerStage, setOfferStage] = useState(0);
  const [offerAnswered, setOfferAnswered] = useState(0); // stages already answered
  const [shownSmall, setShownSmall] = useState(1);       // small steps showing at Most help
  const [askMessage, setAskMessage] = useState(false);
  const [showVideo, setShowVideo] = useState(false);

  // prompted = "yes" only if help came to the person during this step (they said yes to
  // "Want help with this step?"). What the level shows at the start is not a prompt, and
  // neither is help they asked for themselves.
  const promptedRef = useRef(false);
  const activeMsRef = useRef(0);          // time on this step, break time excluded
  const runningSinceRef = useRef(null);
  const loggedStart = useRef(false);

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

  function helpTap() {
    openMore(reveal === 0 ? "hint_requested" : "more_help_requested");
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

  function repeat() {
    log("repeat_requested", { step_id: step.step_id });
    if (settings.readAloud) onSpeak(step.text);
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

  return (
    <section hidden={paused}>
      {praiseLine && <p className="muted">{praiseLine}</p>}
      {awayNote && <div className="card status" role="status"><p>{awayNote}</p></div>}
      <p className="muted" aria-live="polite">Step {step.number} of {step.total}</p>

      {reveal === 0 ? (
        <div className="card"><p className="next-line">Next: {step.text}</p></div>
      ) : (
        <div className="card">
          <h1>{step.text}</h1>
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
          {reveal >= 2 && step.tips.length > 0 && (
            <details>
              <summary>Tips</summary>
              <ul>{step.tips.map((t, i) => <li key={i}>{t}</li>)}</ul>
            </details>
          )}
        </div>
      )}

      {step.safety && (
        <p className="caution"><strong>CAUTION:</strong> {step.safety}</p>
      )}

      {offerShown && (
        <div className="card offer">
          <p>Want help with this step?</p>
          <div className="row">
            <button className="btn primary" onClick={() => answerOffer(true)}>Yes</button>
            <button className="btn" onClick={() => answerOffer(false)}>No, I'm OK</button>
          </div>
        </div>
      )}

      {settings.readAloud && (
        <button className="btn link" onClick={() => onSpeak(step.text)}>Read aloud</button>
      )}

      {/* These four buttons are always in this order and this place (rule 1). */}
      <button className="btn primary" onClick={done}>Done</button>
      <button className="btn" onClick={helpTap} disabled={reveal >= 2}>Help with this step</button>
      <button className="btn" onClick={repeat}>Repeat</button>
      <button className="btn" onClick={onBreak}>Take a break</button>

      <button className="btn link" onClick={onBackStep} disabled={index === 0}>
        Tapped Done by mistake? Go back
      </button>
      <button className="btn link" onClick={onSeeAll}>See all steps</button>
      <button className="btn link" onClick={() => setAskMessage(true)}>
        Ask {settings.supportPerson}
      </button>
      {askMessage && (
        <div className="card" role="status">
          <p>Please ask {settings.supportPerson}.</p>
        </div>
      )}
    </section>
  );
}
