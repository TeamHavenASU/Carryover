import { useEffect, useState } from "react";
import { get } from "../api";
import DemoChart from "../components/DemoChart/DemoChart";
import ResidentPreview from "../components/ResidentPreview/ResidentPreview";
import "./Demo.css";

export default function Demo() {
  const [people, setPeople] = useState([]);
  const [choice, setChoice] = useState(0);
  const [week, setWeek] = useState(1);
  const [view, setView] = useState(null);
  const [counts, setCounts] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    get("/demo/people")
      .then(setPeople)
      .catch((e) => setError(e.message));
  }, []);

  const current = people[choice];
  const lastWeek = current ? current.last_week : 1;

  useEffect(() => {
    if (!current) return;
    let stale = false;
    const who = { person_id: current.person_id, task_id: current.task_id };
    Promise.all([
      get("/demo/view", { ...who, week }),
      get("/demo/help_counts", { ...who, up_to_week: week - 1 }),
    ])
      .then(([v, c]) => {
        if (stale) return;
        setView(v);
        setCounts(c);
        setError("");
      })
      .catch((e) => !stale && setError(e.message));
    return () => {
      stale = true;
    };
  }, [current, week]);

  function pickPerson(event) {
    setChoice(Number(event.target.value));
    setWeek(1);
  }

  return (
    <>
      <h1>Demo</h1>
      <p className="muted">
        Move the week to see how the app changes. Each week only uses what happened in the weeks before it.
      </p>

      {error && <p className="error" role="alert">{error}</p>}

      <div className="card controls">
        <label>
          Resident
          <select value={choice} onChange={pickPerson}>
            {people.map((p, i) => (
              <option key={`${p.person_id}-${p.task_id}`} value={i}>
                {p.person_id}: {p.title}
              </option>
            ))}
          </select>
        </label>

        <div className="week-row">
          <button onClick={() => setWeek((w) => Math.max(1, w - 1))} disabled={week <= 1}>
            Earlier week
          </button>
          <label className="week-slider">
            Week {week} of {lastWeek}
            <input
              type="range"
              min={1}
              max={lastWeek}
              value={week}
              onChange={(e) => setWeek(Number(e.target.value))}
            />
          </label>
          <button onClick={() => setWeek((w) => Math.min(lastWeek, w + 1))} disabled={week >= lastWeek}>
            Later week
          </button>
        </div>
      </div>

      <div className="demo-grid">
        <div className="card">
          {view ? <ResidentPreview view={view} /> : <p className="muted">Loading...</p>}
        </div>
        <div className="card">
          <h2>Help used each week</h2>
          <DemoChart data={counts} />
        </div>
      </div>
    </>
  );
}
