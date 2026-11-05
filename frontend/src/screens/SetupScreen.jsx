import { useEffect, useState } from "react";
import { getSetup } from "../lib/api";
import { AnswerIcon } from "../lib/icons";

// First-time setup: one question per screen, Skip uses the defaults.
// Questions, answers and defaults come from definitions.json (via GET /setup).
const label = (v) => String(v).replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

// Pictures for the answers: one icon set (Lucide), always next to the words.
const Pic = ({ id }) => <AnswerIcon id={id} />;

export default function SetupScreen({ update }) {
  const [questions, setQuestions] = useState(null);
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState({}); // question id -> answer
  const [typed, setTyped] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getSetup().then(setQuestions).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="card status" role="alert">{error}</div>;
  if (!questions) return <p className="muted">Loading…</p>;

  const defaults = Object.fromEntries(questions.map((q) => [q.id, q.default]));
  const finish = (answers) => update({ ...defaults, ...answers, setupDone: true });
  const q = questions[i];

  function next(answer) {
    const answers = { ...picked, [q.id]: answer };
    setPicked(answers);
    setTyped("");
    if (i + 1 >= questions.length) finish(answers);
    else setI(i + 1);
  }

  const chosen = picked[q.id] || [];
  const multi = Boolean(q.pick_up_to);

  return (
    <section>
      <p className="muted" aria-live="polite">Question {i + 1} of {questions.length}</p>
      <h1>{q.text}</h1>

      {multi ? (
        <>
          <p className="muted">Pick up to {q.pick_up_to}</p>
          {q.answers.map((a) => {
            const typedOne = a.startsWith("other");
            const on = chosen.includes(a);
            return typedOne ? (
              <div key={a}>
                <label htmlFor="other">{label(a)}</label>
                <input id="other" type="text" value={typed} onChange={(e) => setTyped(e.target.value)} />
              </div>
            ) : (
              <label key={a} className="check">
                <input
                  type="checkbox"
                  checked={on}
                  disabled={!on && chosen.length >= q.pick_up_to}
                  onChange={() => setPicked({ ...picked, [q.id]: on ? chosen.filter((x) => x !== a) : [...chosen, a] })}
                />
                <Pic id={a} />{label(a)}
              </label>
            );
          })}
          <button className="btn primary" onClick={() => next(typed.trim() ? [...chosen, typed.trim()].slice(0, q.pick_up_to) : chosen)}>
            Next
          </button>
        </>
      ) : (
        <>
          {q.id === "style" && (
            // Try both before picking. Both previews are samples only.
            <div className="preview-row">
              <div className="card">
                <h2>Game style</h2>
                <p>The whole app sits in a sky. Finish a task and pick something for your sky: a bird, a balloon, a kite or a rainbow. Every 2 tasks a new cloud island arrives.</p>
                <p className="muted">Asking for help never changes it. Nothing is taken away.</p>
              </div>
              <div className="card">
                <h2>Normal</h2>
                <p>Heat a meal: done</p>
                <p className="muted">Short and plain. No game.</p>
              </div>
            </div>
          )}
          {q.answers.map((a) => (
            <button key={a} className="btn answer-btn" onClick={() => next(a)}>
              <Pic id={q.id === "sound" && a === "normal" ? "normal_sound" : a} />{label(a)}
            </button>
          ))}
        </>
      )}

      {/* Skip keeps the answers already given and uses the defaults for the rest. */}
      <button className="btn link" onClick={() => finish(picked)}>Skip</button>
    </section>
  );
}
