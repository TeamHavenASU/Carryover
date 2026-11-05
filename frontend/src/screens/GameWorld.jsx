import { useEffect, useState } from "react";
import { getGame, getSetup } from "../lib/api";
import { AREAS_PER_WORLD, themeName, worldState } from "../lib/game";

// "My world" (Game mode only). Areas open as tasks are done and are never taken away.
// The next area shows as an outline, unless the person turned on "Surprise me".
export default function GameWorld({ personId, settings, onBack }) {
  const [game, setGame] = useState(null);
  const [known, setKnown] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getGame(personId).then(setGame).catch((e) => setError(e.message));
    getSetup()
      .then((qs) => setKnown((qs.find((q) => q.id === "interests") || { answers: [] }).answers))
      .catch(() => {});
  }, [personId]);

  if (error) return <div className="card status" role="alert">{error}</div>;
  if (!game) return <p className="muted">Loading…</p>;

  const theme = themeName(settings.interests, known);
  const { unlocked, next } = worldState(game.tasks_done, game.new_area_every_tasks_done);

  return (
    <section>
      <h1>{theme}</h1>
      <p className="muted">Tasks done: {game.tasks_done}</p>
      {Array.from({ length: unlocked }, (_, i) => (
        <div key={i} className="card area"><p>{theme}: area {i + 1}</p></div>
      ))}
      {next && !settings.surpriseMe && (
        <div className="card area next">
          <p>{theme}: area {unlocked + 1}</p>
          <p>Opens after {next.moreNeeded} more {next.moreNeeded === 1 ? "task" : "tasks"}</p>
        </div>
      )}
      {game.milestones_reached.length > 0 && (
        <div className="card">
          <h2>Milestones</h2>
          <ul>{game.milestones_reached.map((m) => <li key={m}>{m.replace(/^./, (c) => c.toUpperCase())}</li>)}</ul>
        </div>
      )}
      <p className="muted">There are {AREAS_PER_WORLD} areas in a world.</p>
      <button className="btn primary" onClick={onBack}>Back to the task list</button>
    </section>
  );
}
