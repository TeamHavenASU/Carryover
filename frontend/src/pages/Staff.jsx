import { useEffect, useState } from "react";
import { get } from "../api";
import "./Staff.css";

const labels = {
  cant_start: "Trouble getting started",
  stuck_at_step: "Gets stuck at a step",
  missing_step: "Misses a step",
  rusty_after_gap: "Back after a long break",
};

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
