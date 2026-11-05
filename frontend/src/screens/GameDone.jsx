import { useEffect, useState } from "react";
import { getGame, getSetup } from "../lib/api";
import { AREAS_PER_WORLD, label, playSound, themeName, worldState } from "../lib/game";

// Game mode extras on the done screen: a calm line, a new area if one opened, milestones that
// happened, and a sound and animation only as the person's settings allow. The first time a
// sound or animation would play, ask which one they want.
export default function GameDone({ personId, title, settings, update, donePromise }) {
  const [game, setGame] = useState(null);
  const [known, setKnown] = useState([]);
  const [played, setPlayed] = useState(false);

  useEffect(() => {
    Promise.resolve(donePromise).then(() => getGame(personId)).then(setGame).catch(() => {});
    getSetup()
      .then((qs) => setKnown((qs.find((q) => q.id === "interests") || { answers: [] }).answers))
      .catch(() => {});
  }, [personId, donePromise]);

  const soundWouldPlay = settings.sound !== "off";
  const needSound = game && soundWouldPlay && !settings.soundTypeAsked;
  const needAnim = game && !needSound && !settings.animationsAsked;
  const ready = game && !needSound && !needAnim;

  useEffect(() => {
    if (ready && !played) {
      setPlayed(true);
      playSound(settings.sound, settings.soundType);
    }
  }, [ready, played]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!game) return null;

  const pick = (heading, options, key, askedKey) => (
    <div className="card">
      <p>{heading}</p>
      {options.map((o) => (
        <button key={o} className="btn" onClick={() => update({ [key]: o, [askedKey]: true })}>{label(o)}</button>
      ))}
    </div>
  );

  if (needSound) return pick("Which sound do you want when you finish a task?", game.settings.sound_type, "soundType", "soundTypeAsked");
  if (needAnim) return pick("How much should things move?", game.settings.animations, "animations", "animationsAsked");

  const every = game.new_area_every_tasks_done;
  const theme = themeName(settings.interests, known);
  const { unlocked } = worldState(game.tasks_done, every);
  const opened = game.tasks_done > 0 && game.tasks_done % every === 0 && unlocked <= AREAS_PER_WORLD;
  const anim = settings.animations === "calm" ? "anim-calm" : settings.animations === "lively" ? "anim-lively" : "";

  return (
    <div className={`card status ${anim}`}>
      <p>You finished {title}.</p>
      {opened && <p>A new area opened: {theme}, area {unlocked}.</p>}
      {game.milestones_reached.length > 0 && (
        <ul>{game.milestones_reached.map((m) => <li key={m}>{m.replace(/^./, (c) => c.toUpperCase())}</li>)}</ul>
      )}
    </div>
  );
}
