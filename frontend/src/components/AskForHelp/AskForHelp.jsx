import { useEffect, useRef, useState } from "react";
import "./AskForHelp.css";

/**
 * "I'm stuck" (Role D). C puts this at the bottom of the resident screen:
 *
 *   <AskForHelp
 *     personId="jeremiah"
 *     taskId="heat_meal"
 *     stepId="s4"            // the step on screen now, or null
 *     week={3}
 *     sessionId="jeremiah-heat_meal-w03"
 *     autoRead={false}       // optional, from C's settings: read replies aloud
 *   />
 *
 * What it does:
 *   - big "I'm stuck" button opens a small panel (sends a stuck_pressed event)
 *   - the person types, or taps the mic to speak, or takes a photo
 *   - nothing is sent until they tap "Send"
 *   - the reply is shown large, with a read aloud button
 *   - "That helped" / "Still stuck". "Still stuck" suggests asking a person
 *
 * Photos: the panel tells the person the photo goes to an AI service, and not to photograph
 * people, cards, receipts, checkout pages or bank apps (docs/safety.md, section 2).
 *
 * Privacy: the text and the photo are never stored here. After sending, the
 * photo is cleared from state. The only thing logged is an ask_sent event that
 * holds the step guess (no text).
 */

const API = import.meta.env?.VITE_API_URL || "http://localhost:8000";
const MAX_PHOTO_SIDE = 800; // pixels. Photos are shrunk before they leave the device.

// Local time like "2026-11-16T18:02:10" (Format 2).
function nowStamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

// Shrink a photo in the browser and return a small JPEG data URL.
function shrinkPhoto(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, MAX_PHOTO_SIDE / Math.max(img.width, img.height));
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      resolve(canvas.toDataURL("image/jpeg", 0.7));
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("photo failed"));
    };
    img.src = url;
  });
}

const SpeechRecognition =
  typeof window !== "undefined" ? window.SpeechRecognition || window.webkitSpeechRecognition : null;

export default function AskForHelp({
  personId,
  taskId,
  stepId = null,
  week = 1,
  sessionId = "",
  autoRead = false,
  apiBase = API,
}) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [photo, setPhoto] = useState(null); // data URL, only until Send
  const [busy, setBusy] = useState(false);
  const [reply, setReply] = useState(null); // {reply, step_id_guess, needs_person}
  const [stillStuck, setStillStuck] = useState(false);
  const [listening, setListening] = useState(false);
  const [notice, setNotice] = useState("");
  const recognitionRef = useRef(null);
  const fileRef = useRef(null);

  // Stop talking and listening if the person leaves.
  useEffect(
    () => () => {
      window.speechSynthesis?.cancel();
      recognitionRef.current?.stop();
    },
    []
  );

  // One usage record (Format 2). Fire and forget: a failed log never blocks help.
  // The 12 columns match EVENT_COLUMNS in backend/logic/data_io.py.
  // This component only sends stuck_pressed and ask_sent. Neither uses help_shown
  // (the resident screen sets that), answer, or prompted (only step_done uses it),
  // so those stay empty here. The resident screen sends step_done, with prompted yes or no.
  function sendEvent(event, step) {
    const row = {
      person_id: personId,
      task_id: taskId,
      session_id: sessionId,
      week,
      timestamp: nowStamp(),
      event,
      step_id: step || "",
      seconds: "",
      days_since_last: "",
      help_shown: "",
      answer: "",
      prompted: "",
    };
    fetch(`${apiBase}/event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(row),
    }).catch(() => {});
  }

  function speak(message) {
    if (!("speechSynthesis" in window) || !message) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(message));
  }

  function openPanel() {
    setOpen(true);
    sendEvent("stuck_pressed", stepId);
  }

  function closePanel() {
    window.speechSynthesis?.cancel();
    recognitionRef.current?.stop();
    setOpen(false);
    setText("");
    setPhoto(null);
    setReply(null);
    setStillStuck(false);
    setNotice("");
  }

  function toggleMic() {
    if (listening) {
      recognitionRef.current?.stop();
      return;
    }
    const rec = new SpeechRecognition();
    rec.lang = "en-US";
    rec.continuous = true;      // keep listening through pauses
    rec.interimResults = true;  // show words while the person talks
    const startText = text ? text + " " : "";
    rec.onresult = (e) => {
      let spoken = "";
      for (let i = 0; i < e.results.length; i++) {
        spoken += e.results[i][0].transcript + " ";
      }
      // Fill the text box. The person checks it, then taps Send.
      setText((startText + spoken).trim());
    };
    rec.onerror = (e) => {
      if (e.error === "not-allowed" || e.error === "service-not-allowed") {
        setNotice("The microphone is blocked. Allow it in the browser, or type instead.");
      } else if (e.error !== "no-speech" && e.error !== "aborted") {
        setNotice("I couldn't hear that. You can type instead.");
      }
    };
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    setNotice("");
    setListening(true);
    rec.start();
  }

  async function onPhotoChosen(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      setPhoto(await shrinkPhoto(file));
      setNotice("");
    } catch {
      setNotice("I couldn't read that photo. Please try again.");
    }
  }

  async function send() {
    if (busy || (!text.trim() && !photo)) return;
    setBusy(true);
    setNotice("");
    window.speechSynthesis?.cancel();
    const body = { person_id: personId, task_id: taskId, step_id: stepId, text: text.trim(), image: photo };
    // The photo and text are cleared from the screen as soon as they are sent.
    setPhoto(null);
    setText("");
    try {
      const res = await fetch(`${apiBase}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error("bad response");
      const data = await res.json();
      setReply(data);
      sendEvent("ask_sent", data.step_id_guess); // the step guess only. No text, no photo.
      if (autoRead) speak(data.reply);
    } catch {
      setReply({
        reply: "I'm not sure. Please ask someone you trust.",
        step_id_guess: null,
        needs_person: false,
      });
    } finally {
      setBusy(false);
    }
  }

  if (!open) {
    return (
      <div className="ask">
        <button className="ask-big" onClick={openPanel}>
          I'm stuck
        </button>
      </div>
    );
  }

  return (
    <div className="ask">
      <section className="ask-panel" aria-label="Ask for help">
        {!reply && (
          <>
            <label className="ask-label" htmlFor="ask-text">
              What is hard right now?
            </label>
            <textarea
              id="ask-text"
              className="ask-text"
              rows={3}
              maxLength={500}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type here, or tap the microphone"
            />

            {photo && (
              <div className="ask-photo">
                <img src={photo} alt="Your photo, ready to send" />
                <button className="ask-small" onClick={() => setPhoto(null)}>
                  Remove photo
                </button>
              </div>
            )}

            <div className="ask-row">
              {SpeechRecognition && (
                <button className="ask-small" onClick={toggleMic} aria-pressed={listening}>
                  {listening ? "Stop listening" : "🎤 Speak"}
                </button>
              )}
              <button className="ask-small" onClick={() => fileRef.current?.click()}>
                📷 Take a photo
              </button>
              <input
                ref={fileRef}
                type="file"
                accept="image/*"
                capture="environment"
                hidden
                onChange={onPhotoChosen}
              />
            </div>
            <p className="ask-note">
              Take a photo of the thing you're stuck on. Please no people, cards, receipts, checkout
              pages or bank apps.
            </p>
            <p className="ask-note">
              A photo is sent to an AI service to get an answer. It is not saved.
            </p>
            {notice && <p className="ask-note" role="status">{notice}</p>}

            <div className="ask-row">
              <button className="ask-main" onClick={send} disabled={busy || (!text.trim() && !photo)}>
                {busy ? "Thinking…" : "Send"}
              </button>
              <button className="ask-small" onClick={closePanel}>
                Close
              </button>
            </div>
          </>
        )}

        {reply && (
          <>
            <p className="ask-reply" role="status" aria-live="polite">
              {reply.reply}
            </p>
            <div className="ask-row">
              <button className="ask-small" onClick={() => speak(reply.reply)}>
                🔊 Read aloud
              </button>
            </div>

            {reply.needs_person ? (
              <div className="ask-row">
                <button className="ask-main" onClick={closePanel}>
                  OK
                </button>
              </div>
            ) : stillStuck ? (
              <>
                <p className="ask-reply">Please ask someone you trust to help you.</p>
                <div className="ask-row">
                  <button className="ask-main" onClick={closePanel}>
                    Close
                  </button>
                </div>
              </>
            ) : (
              <div className="ask-row">
                <button className="ask-main" onClick={closePanel}>
                  That helped
                </button>
                <button className="ask-main ask-alt" onClick={() => setStillStuck(true)}>
                  Still stuck
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}
