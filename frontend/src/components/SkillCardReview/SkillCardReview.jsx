import { useEffect, useState } from "react";
import { get, post } from "../../api";

export default function SkillCardReview() {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    get("/skills/pending")
      .then(setCards)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  async function decide(card, action) {
    setError("");
    setMessage("");
    setBusy(card.skill_id);
    try {
      await post(`/skills/${card.skill_id}/${action}`);
      setCards((list) => list.filter((c) => c.skill_id !== card.skill_id));
      setMessage(action === "approve" ? `Approved "${card.title}".` : `Removed "${card.title}".`);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  return (
    <>
      <h2>Review skill cards</h2>
      <p className="muted">
        The AI writes skill cards that teach a base skill, like reading a price. Nothing reaches a resident
        until you approve it here.
      </p>

      <div aria-live="polite">
        {message && <p className="card">{message}</p>}
        {error && <p className="error" role="alert">{error}</p>}
      </div>

      {loading && <p className="muted">Loading...</p>}
      {!loading && !error && cards.length === 0 && <p className="card">No skill cards are waiting.</p>}

      {cards.map((card) => (
        <section key={card.skill_id} className="card review">
          <h3>{card.title}</h3>
          {card.why && <p>{card.why}</p>}
          <ol>
            {(card.steps || []).map((step) => (
              <li key={step.id || step.text}>{step.text}</li>
            ))}
          </ol>
          {card.tips && card.tips.length > 0 && (
            <>
              <h4>Tips</h4>
              <ul>
                {card.tips.map((tip) => (
                  <li key={tip}>{tip}</li>
                ))}
              </ul>
            </>
          )}
          {card.exists && (
            <p className="error">A card with this id is already saved, so it can't be approved. Reject it, or give it a new id in the file.</p>
          )}
          <div className="actions">
            <button
              className="primary"
              onClick={() => decide(card, "approve")}
              disabled={busy === card.skill_id || card.exists}
            >
              Approve and save
            </button>
            <button onClick={() => decide(card, "reject")} disabled={busy === card.skill_id}>
              Reject
            </button>
          </div>
        </section>
      ))}
    </>
  );
}
