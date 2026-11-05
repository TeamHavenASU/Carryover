import { useEffect, useState } from "react";
import { getGame } from "../lib/api";
import { worldState } from "../lib/game";
import SkyWorld, { RewardChoice } from "./SkyWorld";

// My world (Game mode only): their sky, the reward choice if one is waiting, and milestones.
export default function GameWorld({ personId, settings, update, dark, world }) {
  const [game, setGame] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getGame(personId).then(setGame).catch(() => setError("Your world could not load. Check that the app is connected, then try again."));
  }, [personId]);

  if (error) return <div className="card status" role="alert"><p>{error}</p></div>;
  if (!game) return <p className="muted" role="status">Loading your world…</p>;

  const { unlocked, next } = worldState(game.tasks_done, game.new_area_every_tasks_done);
  const items = settings.skyItems || [];
  const choiceWaiting = items.length < unlocked - 1; // one choice for each island after the first

  return (
    <section>
      <p className="muted">Tasks done: {game.tasks_done}</p>
      {choiceWaiting && <RewardChoice world={world} animations={settings.animations} onPick={(id) => update({ skyItems: [...items, id] })} />}
      <SkyWorld world={world} unlocked={unlocked} moreNeeded={next && next.moreNeeded} surpriseMe={settings.surpriseMe}
        items={items} dark={dark} animations={settings.animations} />
      <div className="card">
        <h2>Milestones</h2>
        {game.milestones_reached.length
          ? <ul>{game.milestones_reached.map((m) => <li key={m}>{m.replace(/^./, (c) => c.toUpperCase())}</li>)}</ul>
          : <p className="muted">Milestones show here after they happen.</p>}
      </div>
    </section>
  );
}
