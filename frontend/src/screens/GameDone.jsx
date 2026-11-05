import { useEffect, useState } from "react";
import { getGame } from "../lib/api";
import { label, playSound, worldState } from "../lib/game";
import SkyWorld, { RewardChoice } from "./SkyWorld";

// Game mode on the done screen: a calm moment in their sky. If a new island arrived, it slides
// in (only if animations are on) and they choose what joins their sky. The first time a sound or
// an animation would play, they are asked which one they want.
export default function GameDone({ personId, settings, update, donePromise, dark, world }) {
  const [game, setGame] = useState(null);
  const [played, setPlayed] = useState(false);

  useEffect(() => {
    Promise.resolve(donePromise).then(() => getGame(personId)).then(setGame).catch(() => {});
  }, [personId, donePromise]);

  const needSound = game && settings.sound !== "off" && !settings.soundTypeAsked;
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
  const { unlocked, next } = worldState(game.tasks_done, every);
  const opened = game.tasks_done > 0 && game.tasks_done % every === 0;
  const items = settings.skyItems || [];
  const choiceWaiting = items.length < unlocked - 1;

  return (
    <>
      {opened && <p>A new {world.areaWord} arrived in your {world.id === "sky" ? "sky" : "world"}.</p>}
      {choiceWaiting && <RewardChoice world={world} animations={settings.animations} onPick={(id) => update({ skyItems: [...items, id] })} />}
      <SkyWorld world={world} unlocked={unlocked} moreNeeded={next && next.moreNeeded} surpriseMe={settings.surpriseMe}
        items={items} dark={dark} animations={settings.animations} arrivingIsland={opened ? unlocked : null} compact />
    </>
  );
}
