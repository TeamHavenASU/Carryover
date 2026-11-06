import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { get } from "../api";
import DemoChart from "../components/DemoChart/DemoChart";
import ResidentPreview from "../components/ResidentPreview/ResidentPreview";
import "./Demo.css";

// ---- "Why this changed" and the "Help over time" grid live in this file (Role E page). ----

// Turns the sticking points in a /demo/view reply into plain sentences.
// Each line is "<cause>, so <effect>." The view for week N is built only from
// the weeks before N, so these are the reasons the help changed for week N.
// It only reads what the backend sent; it never decides a help level itself.

function stepName(steps, stepId) {
  const index = steps.findIndex((s) => s.step_id === stepId);
  if (index < 0) return stepId ? `step ${stepId}` : "a step";
  const text = steps[index].text ? ` (${steps[index].text})` : "";
  return `step ${index + 1}${text}`;
}

function describe(point, steps) {
  const name = stepName(steps, point.step_id);
  switch (point.code) {
    case "cant_start":
      return "Trouble getting started, so a start push is shown.";
    case "stuck_at_step":
      return `Gets stuck at ${name}, so that step gets more help.`;
    case "missing_step":
      return `Misses ${name}, so that step is shown again, not folded.`;
    case "rusty_after_gap":
      return "Back after a long break, so the app asks first: want a quick look at all the steps?";
    default:
      return null;
  }
}

function WhyChanged({ view }) {
  const steps = (view && view.steps) || [];
  const points = ((view && view.sticking_points) || []).filter((p) => p && p.code && p.code !== "none");
  const codes = new Set(points.map((p) => p.code));

  const lines = points
    .map((p, i) => ({ key: `${p.code}-${p.step_id || ""}-${i}`, text: describe(p, steps), evidence: p.evidence }))
    .filter((l) => l.text);

  // Short extra lines for things the view shows that no sticking point explains.
  const extras = [];
  if (view && view.new_device && steps.some((s) => s.mode === "split")) {
    extras.push("New device, so the steps start at most help.");
  }
  if (view && view.start_push && !codes.has("cant_start")) {
    extras.push("A start push is shown this week.");
  }
  if (view && view.show_refresher && !codes.has("rusty_after_gap")) {
    extras.push("The app asks first: want a quick look at all the steps?");
  }

  return (
    <section className="card why-changed" aria-labelledby="why-changed-heading">
      <h2 id="why-changed-heading">Why this changed</h2>
      {lines.length === 0 ? (
        <p className="why-none">No sticking points before this week. Help follows the normal fading rules.</p>
      ) : (
        <ul className="why-list">
          {lines.map((l) => (
            <li key={l.key}>
              <span className="why-line">{l.text}</span>
              {l.evidence && <span className="muted why-evidence">{l.evidence}</span>}
            </li>
          ))}
        </ul>
      )}
      {extras.length > 0 && (
        <ul className="why-list why-extras">
          {extras.map((t) => (
            <li key={t}>
              <span className="why-line">{t}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

// Help level for every step across all weeks: rows are the task's steps,
// columns are weeks 1..lastWeek. Each cell is coloured by help level and also
// says the level in words, so it never relies on colour alone.
// It calls GET /demo/view once per week, all at once, and keeps the result per
// person and task so moving the week slider does not fetch again.

const LEVELS = {
  split: { label: "Most", className: "most" },
  hint: { label: "Some", className: "some" },
  hide: { label: "No help", className: "none" },
};

function shorten(text, max = 48) {
  if (!text) return "";
  return text.length > max ? `${text.slice(0, max - 1).trimEnd()}...` : text;
}

function HelpGrid({ personId, taskId, lastWeek, week }) {
  const [views, setViews] = useState(null);
  const [error, setError] = useState("");
  const cache = useRef(new Map());

  const cacheKey = `${personId}|${taskId}|${lastWeek}`;

  useEffect(() => {
    if (!personId || !taskId) return;
    if (cache.current.has(cacheKey)) {
      setViews(cache.current.get(cacheKey));
      setError("");
      return;
    }
    let stale = false;
    setViews(null);
    setError("");
    const weeks = Array.from({ length: Math.max(1, lastWeek || 1) }, (_, i) => i + 1);
    Promise.all(weeks.map((w) => get("/demo/view", { person_id: personId, task_id: taskId, week: w })))
      .then((all) => {
        if (stale) return;
        cache.current.set(cacheKey, all);
        setViews(all);
      })
      .catch((e) => !stale && setError(e.message));
    return () => {
      stale = true;
    };
  }, [cacheKey, personId, taskId, lastWeek]);

  if (error) return <p className="muted">Could not load the help grid: {error}</p>;
  if (!views) return <p className="muted">Loading...</p>;

  // Steps in the order they first appear, across all weeks.
  const steps = [];
  const seen = new Set();
  views.forEach((v) => {
    ((v && v.steps) || []).forEach((s) => {
      if (s && s.step_id && !seen.has(s.step_id)) {
        seen.add(s.step_id);
        steps.push(s);
      }
    });
  });

  if (steps.length === 0) return <p className="muted">No steps to show.</p>;

  function levelFor(view, stepId) {
    const step = ((view && view.steps) || []).find((s) => s.step_id === stepId);
    return step ? LEVELS[step.mode] || null : null;
  }

  return (
    <div className="help-grid">
      <p className="help-grid-legend">
        <strong>Most help</strong> = step plus small steps; <strong>Some help</strong> = the full step only;{" "}
        <strong>No help</strong> = folded.
      </p>
      <div className="help-grid-scroll">
        <table>
          <caption>Help level for each step, week by week. Week {week} is the week shown above.</caption>
          <thead>
            <tr>
              <th scope="col" className="step-col">Step</th>
              {views.map((v, i) => {
                const w = i + 1;
                const current = w === week;
                return (
                  <th key={w} scope="col" className={current ? "current" : ""} aria-current={current ? "true" : undefined}>
                    Week {w}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {steps.map((s, row) => (
              <tr key={s.step_id}>
                <th scope="row" className="step-col">
                  <span className="step-num">{row + 1}.</span> {shorten(s.text)}
                </th>
                {views.map((v, i) => {
                  const w = i + 1;
                  const level = levelFor(v, s.step_id);
                  const classes = [level ? level.className : "missing", w === week ? "current" : ""].join(" ").trim();
                  return (
                    <td key={w} className={classes}>
                      {level ? level.label : "-"}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


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

  // The real resident app, same origin, at the chosen person and week.
  const residentPath = current
    ? `/resident?person=${encodeURIComponent(current.person_id)}&week=${week}`
    : null;
  const phoneSrc = residentPath;

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

        {residentPath && (
          <Link className="open-resident" to={residentPath}>
            Open this in the resident app
          </Link>
        )}
      </div>

      {view ? <WhyChanged view={view} /> : <div className="card"><p className="muted">Loading...</p></div>}

      <div className="demo-grid">
        <div className="card phone-card">
          <h2>What the resident sees</h2>
          {phoneSrc ? (
            <div className="phone-frame">
              <iframe key={phoneSrc} src={phoneSrc} title="Resident app" className="phone-screen" />
            </div>
          ) : (
            <p className="muted">Loading...</p>
          )}
          {view && (
            <details className="plain-list">
              <summary>Show as a plain list</summary>
              <ResidentPreview view={view} />
            </details>
          )}
        </div>
        <div className="card">
          <h2>Help used each week</h2>
          <DemoChart data={counts} />
        </div>
      </div>

      <div className="card">
        <h2>Help over time</h2>
        {current ? (
          <HelpGrid personId={current.person_id} taskId={current.task_id} lastWeek={lastWeek} week={week} />
        ) : (
          <p className="muted">Loading...</p>
        )}
      </div>
    </>
  );
}
