import { useEffect } from "react";

const IMG_BASE = import.meta.env.BASE_URL + "img/";

// A skill card shows before the step that needs it (today's view says which).
// Same calm layout as a step. Logs skill_card_shown once when it appears.
export default function SkillCardScreen({ entry, settings, log, onContinue }) {
  const card = entry.card;

  useEffect(() => {
    log("skill_card_shown", { step_id: entry.step_id, answer: entry.skill_id });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <section>
      <h1>{card.title}</h1>
      <div className="card">
        {card.why && <p className="muted">{card.why}</p>}
        {settings.pictures && card.picture && (
          <img className="step-picture" src={IMG_BASE + card.picture.file} alt={card.picture.alt} />
        )}
        <ol className="small-steps">
          {card.steps.map((s) => <li key={s.id}>{s.text}</li>)}
        </ol>
        {card.tips && card.tips.length > 0 && (
          <details>
            <summary>Tips</summary>
            <ul>{card.tips.map((t, i) => <li key={i}>{t}</li>)}</ul>
          </details>
        )}
      </div>
      <button className="btn primary" onClick={onContinue}>Continue to the step</button>
    </section>
  );
}
