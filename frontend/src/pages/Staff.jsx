import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { get, post } from "../api";
import "./Staff.css";

const labels = {
  cant_start: "Trouble getting started",
  stuck_at_step: "Gets stuck at a step",
  missing_step: "Misses a step",
  rusty_after_gap: "Back after a long break",
};

const HANDS = [["left", "Left hand"], ["right", "Right hand"], ["either", "Either"]];

// "Ask AI for more detail on this step": pick a hand, then POST /split. The AI's small steps are
// saved for a person to approve on the Review page; nothing reaches a resident until then.
function AskMoreDetail({ taskId, stepId }) {
  const [stage, setStage] = useState("idle"); // idle | hand | sending | sent | failed
  const [problem, setProblem] = useState("");

  async function send(hand) {
    setStage("sending");
    try {
      const out = await post("/split", { task_id: taskId, step_id: stepId, hand });
      if (out && out.substeps && out.substeps.length > 0) {
        setStage("sent");
      } else {
        setProblem("The AI did not give usable small steps this time. Nothing was saved. You can try again.");
        setStage("failed");
      }
    } catch (e) {
      setProblem(`The request failed: ${e.message}. Nothing was saved.`);
      setStage("failed");
    }
  }

  if (stage === "sent") {
    return (
      <p className="ask-more-result" role="status">
        Sent. The new small steps are waiting on the <Link to="/review">Review page</Link> for a person to approve.
      </p>
    );
  }
  return (
    <div className="ask-more">
      {stage === "idle" && (
        <button type="button" onClick={() => setStage("hand")}>Ask AI for more detail on this step</button>
      )}
      {stage === "hand" && (
        <div className="ask-more-hands">
          <span className="muted small">Which hand does this resident use?</span>
          {HANDS.map(([value, text]) => (
            <button key={value} type="button" onClick={() => send(value)}>{text}</button>
          ))}
          <button type="button" className="link" onClick={() => setStage("idle")}>Cancel</button>
        </div>
      )}
      {stage === "sending" && <p className="muted small" role="status">Asking the AI...</p>}
      {stage === "failed" && (
        <p className="error small" role="alert">
          {problem} <button type="button" className="link" onClick={() => setStage("hand")}>Try again</button>
        </p>
      )}
    </div>
  );
}

export default function Staff() {
  const [people, setPeople] = useState([]);
  const [onlyFlagged, setOnlyFlagged] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    get("/staff/sticking_points")
      .then(setPeople)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const flagged = people.filter((p) => p.sticking_points.length > 0);
  const shown = onlyFlagged ? flagged : people;

  return (
    <>
      <h1>Staff screen</h1>
      <p className="staff-demo-note">Demo: this page shows all simulated residents. In real use, staff would only see residents who chose to share.</p>
      <p className="muted">
        Where each resident gets stuck, from their last two sessions. A pattern only shows here if it happened
        every time, so one bad day is not flagged. Use it to see who might need a check-in.
      </p>

      {error && <p className="error" role="alert">{error}</p>}

      {!loading && !error && (
        <div className="card staff-summary">
          <p>
            <strong>{flagged.length}</strong> of {people.length} residents have something to look at.
          </p>
          <label className="staff-filter">
            <input type="checkbox" checked={onlyFlagged} onChange={(e) => setOnlyFlagged(e.target.checked)} />
            Only show these residents
          </label>
        </div>
      )}

      {loading && <p className="muted">Loading...</p>}

      <ul className="staff-list">
        {shown.map((p) => (
          <li key={`${p.person_id}-${p.task_id}`} className="card">
            <div className="staff-head">
              <h2>{p.person_id}</h2>
              <span className="muted">
                {p.title} · up to week {p.last_week}
              </span>
            </div>
            {p.sticking_points.length === 0 ? (
              <p className="muted">Nothing to flag.</p>
            ) : (
              <ul className="points">
                {p.sticking_points.map((point, i) => (
                  <li key={i}>
                    <strong>{labels[point.code] || point.code}</strong>
                    {point.step_text && (
                      <>
                        : {point.step_text} ({point.step_id})
                      </>
                    )}
                    <p className="muted small">{point.evidence}</p>
                    {point.step_id && <AskMoreDetail taskId={p.task_id} stepId={point.step_id} />}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </>
  );
}
