import { useState } from "react";
import GameDone from "./GameDone";

// Short and factual (praise setting). No points, streaks, badges or confetti.
// The check questions to ask come from today's view (check_questions), which
// already says which steps and whether this session is one to ask.
// A step with offer_less_help: true gets "Want to try with less help next time?"
// (UI rule 15, the person decides). The answer is logged as end_question, yes or keep.
export default function DoneScreen({ today, settings, update, personId, donePromise, onFinish, log }) {
  const total = today.steps.length;
  const message =
    settings.praise === "off" ? null
    : settings.praise === "cheerful" ? `All ${total} steps done. Well done.`
    : `All ${total} steps done.`;

  const questions = [
    ...today.check_questions.map((c) => ({ kind: "check", step_id: c.step_id, text: c.question })),
    ...today.steps
      .filter((s) => s.offer_less_help)
      .map((s) => ({ kind: "less", step_id: s.step_id, text: s.text })),
  ];
  const [qi, setQi] = useState(0);
  const q = questions[qi];

  function answer(a) {
    log(q.kind === "less" ? "end_question" : "check_answer", { step_id: q.step_id, answer: a });
    setQi(qi + 1);
  }

  return (
    <section>
      <h1>{today.title}</h1>
      {message && <div className="card status"><p>{message}</p></div>}
      {settings.style === "game" && (
        <GameDone personId={personId} title={today.title} settings={settings} update={update} donePromise={donePromise} />
      )}
      {q && (
        <div className="card">
          {q.kind === "less" ? (
            <>
              <p className="muted">{q.text}</p>
              <p>Want to try with less help next time?</p>
              <div className="row">
                <button className="btn" onClick={() => answer("yes")}>Yes, try less help</button>
                <button className="btn" onClick={() => answer("keep")}>No, keep the help</button>
              </div>
            </>
          ) : (
            <>
              <p>{q.text}</p>
              <div className="row">
                <button className="btn" onClick={() => answer("yes")}>Yes</button>
                <button className="btn" onClick={() => answer("no")}>No</button>
              </div>
            </>
          )}
        </div>
      )}
      <button className="btn primary" onClick={onFinish}>Back to the task list</button>
    </section>
  );
}
