import { useState } from "react";
import { WORLD_CHOICES } from "../lib/worlds";

// "Choose your game world": Sky, Space or Animals. Animals asks one more
// question (which animal). The background and the rewards follow the choice, and
// it can be changed any time in Settings.
export default function ChooseWorld({ settings, update, onDone }) {
  const [family, setFamily] = useState(null);
  const chosen = WORLD_CHOICES.find((w) => w.id === family);

  function pickFamily(w) {
    if (w.options) { setFamily(w.id); return; }
    update({ gameWorld: w.id });
    onDone();
  }
  function pickOption(w, value) {
    update({ gameWorld: w.id, [w.sub]: value });
    onDone();
  }

  if (chosen) {
    return (
      <section>
        <h1>Which animal do you like?</h1>
        {chosen.options.map(([value, label]) => (
          <button key={value} className="btn answer-btn" onClick={() => pickOption(chosen, value)}>{label}</button>
        ))}
        <button className="btn link" onClick={() => setFamily(null)}>Back to the worlds</button>
      </section>
    );
  }
  return (
    <section>
      <h1>Choose your game world</h1>
      <p className="card-text">The background and what you unlock follow your choice. You can change it in Settings.</p>
      {WORLD_CHOICES.map((w) => (
        <button key={w.id} className={`btn world-choice ${settings.gameWorld === w.id ? "on" : ""}`} onClick={() => pickFamily(w)}>
          <span className={`world-swatch ${w.id}`} aria-hidden="true" />
          <span><strong>{w.name}</strong><br /><span className="muted">{w.blurb}</span></span>
        </button>
      ))}
    </section>
  );
}
