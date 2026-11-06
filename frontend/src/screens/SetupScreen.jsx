import { useEffect, useState } from "react";
import { getSetup } from "../lib/api";
import { AnswerIcon } from "../lib/icons";
import { describeWorld, resolveWorld } from "../lib/worlds";

// First-time setup: one question per screen, Skip uses the defaults.
// Questions, answers and defaults come from definitions.json (via GET /setup).
const label = (v) => String(v).replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

// Pictures for the answers: one icon set (Lucide), always next to the words.
const Pic = ({ id }) => <AnswerIcon id={id} />;

// The worlds the first question offers (prototype). The first one picked becomes their game world.
const WORLD_ANSWERS = ["sky", "animals", "space"];
const ANIMALS = [["cat", "Cat"], ["dog", "Dog"], ["fox", "Fox"]];

export default function SetupScreen({ update, setBack }) {
  const [questions, setQuestions] = useState(null);
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState({}); // question id -> answer
  const [typed, setTyped] = useState("");
  const [error, setError] = useState("");
  const [animal, setAnimal] = useState("cat");
  const [allSet, setAllSet] = useState(null); // the answers, once every question is done

  useEffect(() => {
    // Prototype: the first question offers only the three worlds we have drawn (Sky, Animals,
    // Space), instead of the full interest list in definitions.json.
    getSetup()
      .then((qs) => setQuestions(qs.map((q) => (q.id === "interests" ? { ...q, text: "What do you love? Pick one", answers: ["sky", "animals", "space"], single: true, pick_up_to: 0 } : q))))
      .catch((e) => setError(e.message));
  }, []);

  // Back goes to the previous question (the top bar's Back). Each new question starts at the top.
  useEffect(() => {
    // setBack is a state setter, so a function must be wrapped or React would call it right away
    setBack(allSet ? () => () => setAllSet(null) : i > 0 ? () => () => setI((n) => n - 1) : null);
    return () => setBack(null);
  }, [i, allSet]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    const root = document.querySelector(".resident");
    if (root) root.scrollTop = 0;
    window.scrollTo(0, 0);
  }, [i, allSet]);

  if (error) return <div className="card status" role="alert">{error}</div>;
  if (!questions) return <p className="muted">Loading…</p>;

  const defaults = Object.fromEntries(questions.map((q) => [q.id, q.default]));
  // The first world they picked is their game world. Animals also keeps which animal.
  // Every answer is saved together on the last page ("All set").
  const save = (answers) => {
    const loves = answers.interests || [];
    const world = WORLD_ANSWERS.find((w) => loves.includes(w));
    update({ ...defaults, ...answers, setupDone: true, ...(world ? { gameWorld: world, animalChoice: animal } : {}) });
  };
  const finish = (answers) => setAllSet(answers);
  const q = questions[i];

  // The last page: one calm note about Settings, instead of pop-ups later in the app.
  if (allSet) {
    return (
      <section className="all-set center-page">
        <div className="card status">
          <h1>You are all set</h1>
          <p>You can change any of these choices later. Open <strong>Settings</strong> at the bottom of the screen for more changes, like text size, colors, reading aloud and sounds.</p>
        </div>
        <button className="btn primary" onClick={() => save(allSet)}>Go to my tasks</button>
        <div className="card status settings-note">
          <h1>What you can change in Settings</h1>
          <ul>
            <li>Text size, font and colors</li>
            <li>Pictures on or off</li>
            <li>Reading aloud: the voice and the speed</li>
            <li>Sounds and animations</li>
            <li>Game or Normal style</li>
            <li>Your support person and how to reach them</li>
            <li>Sharing with staff, which stays off until you turn it on</li>
          </ul>
        </div>
      </section>
    );
  }

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
    <section className="center-page">
      <p className="muted" aria-live="polite">Question {i + 1} of {questions.length}</p>
      <h1>{q.text}</h1>

      {q.single ? (
        <>
          <fieldset className="choices">
            <legend className="visually-hidden">{q.text}</legend>
            {q.answers.map((a) => (
              <label key={a} className={`check choice ${chosen[0] === a ? "on" : ""}`}>
                <input type="radio" name="world" value={a} checked={chosen[0] === a} onChange={() => { setPicked({ ...picked, [q.id]: [a] }); update({ gameWorld: a }); }} />
                <Pic id={a} />{label(a)}
              </label>
            ))}
          </fieldset>
          {chosen[0] === "animals" && (
            <fieldset>
              <legend>Which animal?</legend>
              <div className="segmented">
                {ANIMALS.map(([v, t]) => (
                  <label key={v} className={`segment ${animal === v ? "on" : ""}`}>
                    <input type="radio" name="animal" value={v} checked={animal === v} onChange={() => { setAnimal(v); update({ animalChoice: v }); }} />{t}
                  </label>
                ))}
              </div>
            </fieldset>
          )}
          <button className="btn primary" onClick={() => next(chosen)}>Next</button>
        </>
      ) : (
        <>
          {q.id === "style" && (
            // Try both before picking. Both previews are samples only.
            <div className="preview-row">
              <div className="card">
                <h2>Game style</h2>
                <p>{describeWorld(resolveWorld({ gameWorld: WORLD_ANSWERS.find((w) => (picked.interests || []).includes(w)) || "sky", animalChoice: animal }))}</p>
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
