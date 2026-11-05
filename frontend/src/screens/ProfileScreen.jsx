import { useEffect, useState } from "react";
import { Star } from "lucide-react";
import { getGame } from "../lib/api";
import { STAR_EVERY, starMessage, starsFor, totalRewards } from "../lib/rewards";

// Profile: who is using the app, and in Game mode their rewards and stars. A star is earned for
// every 10 rewards and stays for good. Rewards come from finishing tasks, never from using less help.
export default function ProfileScreen({ settings }) {
  const [game, setGame] = useState(null);
  useEffect(() => {
    getGame(settings.personId).then(setGame).catch(() => {});
  }, [settings.personId]);

  const isGame = settings.style === "game";
  const total = totalRewards(settings);
  const stars = starsFor(total);
  const toNext = STAR_EVERY - (total % STAR_EVERY);

  return (
    <section>
      <div className="card profile-head">
        <span className="avatar" aria-hidden="true">{(settings.personId || "?").charAt(0).toUpperCase()}</span>
        <div>
          <h1>{settings.personId || "Your profile"}</h1>
          {game && <p className="muted">Tasks done: {game.tasks_done + (Number(settings.demoDone) || 0)}</p>}
        </div>
      </div>

      {isGame ? (
        <div className="card">
          <h2>Your stars</h2>
          <p className="card-text">{starMessage(stars)}</p>
          {stars > 0 && (
            <div className="stars-row" role="img" aria-label={`${stars} ${stars === 1 ? "star" : "stars"}`}>
              {Array.from({ length: Math.min(stars, 6) }, (_, i) => <Star key={i} size="2rem" fill="#e5c66b" stroke="#a8872f" aria-hidden="true" />)}
              {stars > 6 && <strong>× {stars}</strong>}
            </div>
          )}
          <p className="muted">Rewards collected: {total}</p>
          {!settings.surpriseMe && <p className="muted">{toNext} more {toNext === 1 ? "reward" : "rewards"} for your next star.</p>}
          <p className="muted">Stars come from finishing tasks. Asking for help never changes them, and they are never taken away.</p>
        </div>
      ) : (
        <div className="card">
          <p>Game mode is off. Turn it on in Settings to collect rewards and earn stars.</p>
        </div>
      )}
    </section>
  );
}
