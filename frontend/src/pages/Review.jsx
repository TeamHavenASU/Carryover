import { useEffect, useState } from "react";
import { get, post } from "../api";
import SkillCardReview from "../components/SkillCardReview/SkillCardReview";
import "./Review.css";

const MIN_STEPS = 3;
const MAX_STEPS = 6;

export default function Review() {
  const [items, setItems] = useState([]);
  const [drafts, setDrafts] = useState({}); // split_id -> list of small steps being edited
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    get("/review/pending")
      .then((list) => {
        setItems(list);
        setDrafts(Object.fromEntries(list.map((i) => [i.split_id, [...i.substeps]])));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function setDraft(id, next) {
    setDrafts((d) => ({ ...d, [id]: next }));
  }

  function removeItem(id) {
    setItems((list) => list.filter((i) => i.split_id !== id));
  }

  async function approve(item) {
    setError("");
    setMessage("");
    try {
      await post(`/review/${item.split_id}/approve`, { substeps: drafts[item.split_id] });
      removeItem(item.split_id);
      setMessage(`Saved the small steps for "${item.step_text}".`);
    } catch (e) {
      setError(e.message);
    }
  }

  async function reject(item) {
    setError("");
    setMessage("");
    try {
      await post(`/review/${item.split_id}/reject`);
      removeItem(item.split_id);
      setMessage("Suggestion removed.");
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <>
      <h1>Review AI steps</h1>
      <p className="muted">
        The AI suggests small steps for a hard step. Nothing reaches a resident until you approve it here.
        You can edit the words first.
      </p>

      <div aria-live="polite">
        {message && <p className="card">{message}</p>}
        {error && <p className="error" role="alert">{error}</p>}
      </div>

      {loading && <p className="muted">Loading...</p>}
      {!loading && items.length === 0 && <p className="card">Nothing is waiting for review.</p>}

      {items.map((item) => (
        <Suggestion
          key={item.split_id}
          item={item}
          draft={drafts[item.split_id] || []}
          onChange={(next) => setDraft(item.split_id, next)}
          onApprove={() => approve(item)}
          onReject={() => reject(item)}
        />
      ))}

      <SkillCardReview />
    </>
  );
}

function Suggestion({ item, draft, onChange, onApprove, onReject }) {
  const outOfDate = item.step_text === "";
  const valid = draft.length >= MIN_STEPS && draft.length <= MAX_STEPS && draft.every((s) => s.trim());

  function edit(i, text) {
    onChange(draft.map((s, n) => (n === i ? text : s)));
  }

  function remove(i) {
    onChange(draft.filter((_, n) => n !== i));
  }

  function move(i, by) {
    const next = [...draft];
    [next[i], next[i + by]] = [next[i + by], next[i]];
    onChange(next);
  }

  if (outOfDate) {
    return (
      <section className="card review">
        <h2>{item.task_id}: {item.step_id}</h2>
        <p>This task or step no longer exists, so the suggestion can't be used.</p>
        <button onClick={onReject}>Remove suggestion</button>
      </section>
    );
  }

  return (
    <section className="card review">
      <h2>{item.task_title}</h2>
      <p>
        <strong>Step:</strong> {item.step_text}
      </p>

      <h3>Small steps now</h3>
      {item.current_substeps.length > 0 ? (
        <ol>
          {item.current_substeps.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      ) : (
        <p className="muted">None yet.</p>
      )}

      <h3>Suggested small steps</h3>
      <ol className="edit-list">
        {draft.map((text, i) => (
          <li key={i}>
            <input
              type="text"
              value={text}
              onChange={(e) => edit(i, e.target.value)}
              aria-label={`Small step ${i + 1}`}
            />
            <button onClick={() => move(i, -1)} disabled={i === 0} aria-label={`Move small step ${i + 1} up`}>
              Up
            </button>
            <button onClick={() => move(i, 1)} disabled={i === draft.length - 1} aria-label={`Move small step ${i + 1} down`}>
              Down
            </button>
            <button onClick={() => remove(i)} aria-label={`Remove small step ${i + 1}`}>
              Remove
            </button>
          </li>
        ))}
      </ol>
      <button onClick={() => onChange([...draft, ""])} disabled={draft.length >= MAX_STEPS}>
        Add a small step
      </button>
      <p className="muted">A step needs {MIN_STEPS} to {MAX_STEPS} small steps.</p>

      {item.current_substeps.length > 0 && (
        <p>Approving replaces the small steps that are there now.</p>
      )}

      <div className="actions">
        <button className="primary" onClick={onApprove} disabled={!valid}>
          Approve and save
        </button>
        <button onClick={onReject}>Reject</button>
      </div>
    </section>
  );
}
