import { useEffect, useState } from "react";
import { getGame } from "../lib/api";
import { worldState } from "../lib/game";
import WorldArt, { RewardChoice } from "./WorldArt";
import HowGameWorks from "./HowGameWorks";

// My world (Game mode only): their world, a reward to pick if one is waiting, and milestones.
// The rewards they picked are kept for each world separately, so switching worlds loses nothing.
export default function GameWorld({ personId, settings, update, world }) {
  const [game, setGame] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getGame(personId).then(setGame).catch(() => setError("Your world could not load. Check that the app is connected, then try again."));
  }, [personId]);

  if (error) return <div className="card status" role="alert"><p>{error}</p></div>;
  if (!game) return <p className="card-text" role="status">Loading your world…</p>;

  const done = game.tasks_done + (Number(settings.demoDone) || 0);
  const { unlocked, next } = worldState(done, game.new_area_every_tasks_done);
  const items = (settings.gameItems || {})[world.key] || [];
  const choiceWaiting = items.length < done; // one reward for every task finished
  const pick = (id) => update({ gameItems: { ...(settings.gameItems || {}), [world.key]: [...items, id] } });

  return (
    <section>
      <p className="card-text">Tasks done: {done}</p>
      <HowGameWorks world={world} every={game.new_area_every_tasks_done} />
      {choiceWaiting && <RewardChoice world={world} animations={settings.animations} onPick={pick} />}
      <WorldArt world={world} unlocked={unlocked} moreNeeded={next && next.moreNeeded} surpriseMe={settings.surpriseMe}
        items={items} animations={settings.animations} />
      <details className="card">
        <summary>Milestones</summary>
        {game.milestones_reached.length
          ? <ul>{game.milestones_reached.map((m) => <li key={m}>{m.replace(/^./, (c) => c.toUpperCase())}</li>)}</ul>
          : <p className="muted">Milestones show here after they happen.</p>}
      </details>
    </section>
  );
}
