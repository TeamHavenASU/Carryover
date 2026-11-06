import { motion, useReducedMotion } from "framer-motion";
import { Lottie } from "lottie-react";
import Companion from "./Companion";

const BASE = import.meta.env.BASE_URL;
const ANIM_BASE = `${BASE}animations/`;
const STILL_BASE = `${BASE}game/`;

// The areas of a world (islands, planets, spots, rows...) and the rewards sitting on them. The
// background itself is Backdrops.jsx. Areas open as tasks are done (definitions.json) and are
// never taken away. Movement follows the Animations setting; Off or reduced motion shows
// still pictures.

function Item({ id, world, moving, lively }) {
  const item = world.items[id];
  if (!item) return null;
  if (moving && item.animation) {
    return (
      <span className="sky-item" aria-hidden="true">
        <Lottie src={`${ANIM_BASE}${item.animation}.json`} loop autoplay speed={lively ? 1 : 0.6} />
      </span>
    );
  }
  return <span className="sky-item"><img src={`${STILL_BASE}${id}.svg`} alt="" /></span>;
}

function Shape({ kind, outline }) {
  const stroke = outline ? "currentColor" : "#b8c4cf";
  const dash = outline ? "8 6" : undefined;
  if (kind === "planet") {
    return (
      <svg viewBox="0 0 200 80" className="island-shape" aria-hidden="true">
        <ellipse cx="100" cy="42" rx="92" ry="12" fill="none" stroke={stroke} strokeWidth="3" strokeDasharray={dash} />
        <circle cx="100" cy="40" r="30" fill={outline ? "none" : "#e5a97a"} stroke={stroke} strokeWidth="3" strokeDasharray={dash} />
        {!outline && <path d="M72 34 Q100 28 128 34 M70 46 Q100 52 130 46" fill="none" stroke="#c98558" strokeWidth="3" />}
      </svg>
    );
  }
  if (kind === "platform") {
    return (
      <svg viewBox="0 0 200 80" className="island-shape" aria-hidden="true">
        <ellipse cx="100" cy="50" rx="84" ry="22" fill={outline ? "none" : "#ffffff"} stroke={stroke} strokeWidth="3" strokeDasharray={dash} />
        {!outline && <ellipse cx="100" cy="50" rx="62" ry="14" fill="#e8eee6" />}
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 200 80" className="island-shape" aria-hidden="true">
      <path d="M20 50 C10 50 8 36 22 34 C22 20 44 16 52 26 C60 10 92 10 100 26 C110 14 140 16 142 32 C160 26 178 36 172 50 Z"
        fill={outline ? "none" : "#ffffff"} stroke={outline ? "currentColor" : "#c9d8e4"} strokeWidth="3" strokeDasharray={dash} />
      {!outline && <path d="M40 50 C70 72 130 72 160 50 Z" fill="#dfe9f1" />}
    </svg>
  );
}

function Area({ n, world, items, outline, note, arriving, moving, lively }) {
  const body = (
    <>
      <Shape kind={world.shape} outline={outline} />
      <div className="island-items">
        {items.map((it, i) => <Item key={i} id={it} world={world} moving={moving} lively={lively} />)}
      </div>
      <p className="island-label">{outline ? note : world.area(n)}</p>
    </>
  );
  const cls = `island ${outline ? "outline" : ""} ${n % 2 ? "left" : "right"}`;
  // A new area slides in once. Without motion it is simply there.
  if (arriving && moving) {
    return (
      <motion.div className={cls} initial={{ x: 40, opacity: 0 }} animate={{ x: 0, opacity: 1 }}
        transition={{ duration: lively ? 0.9 : 1.6, ease: "easeOut" }}>
        {body}
      </motion.div>
    );
  }
  return <div className={cls}>{body}</div>;
}

// Animals worlds: the animal itself, with the latest reward, and everything it has been given.
function CompanionStage({ world, items, moving, lively }) {
  const latest = items[items.length - 1];
  const item = latest ? world.items[latest] : null;
  // Earlier rewards sit on the ground beside the animal: each kind once, newest first, never the
  // one in its mouth. The full list with counts is in "My rewards".
  const earlier = [...new Set(items.slice(0, -1).reverse())].filter((id) => id !== latest);
  return (
    <div className="companion-stage" data-world="animals">
      <Companion animal={world.animal} holding={latest} item={item} moving={moving} lively={lively} earlier={earlier} earlierItems={world.items} />
      <p className="companion-caption">
        {item ? `Your ${world.animal} has ${item.name.toLowerCase()}.` : `Your ${world.animal} is waiting for its first reward.`}
      </p>
    </div>
  );
}

export default function WorldArt({ world, unlocked, moreNeeded, surpriseMe, items, animations, arrivingArea, compact }) {
  const reduce = useReducedMotion();
  const moving = animations !== "off" && !reduce;
  const lively = animations === "lively";
  if (world.companion) return <CompanionStage world={world} items={items} moving={moving} lively={lively} />;
  // Each reward they chose sits on one of their areas, in order.
  const onArea = (n) => items.filter((_, i) => (i % unlocked) + 1 === n);
  const shown = compact ? Math.min(unlocked, 2) : unlocked;
  const first = unlocked - shown + 1;
  const word = world.areaWord;
  return (
    <div className="sky-stage" data-world={world.family} role="img"
      aria-label={`${world.name}: ${unlocked} ${unlocked === 1 ? word : `${word}s`}${moreNeeded ? `, the next opens after ${moreNeeded} more` : ""}`}>
      {Array.from({ length: shown }, (_, i) => first + i).map((n) => (
        <Area key={n} n={n} world={world} items={onArea(n)} arriving={n === arrivingArea} moving={moving} lively={lively} />
      ))}
      {moreNeeded && !surpriseMe && (
        <Area n={unlocked + 1} world={world} items={[]} outline moving={false}
          note={`Opens after ${moreNeeded} more ${moreNeeded === 1 ? "task" : "tasks"}`} />
      )}
    </div>
  );
}

// After finishing a task, the person picks one reward for their world. It fades in gently when
// animations are on.
export function RewardChoice({ world, animations, onPick }) {
  const reduce = useReducedMotion();
  const moving = animations !== "off" && !reduce;
  const Wrap = moving ? motion.div : "div";
  const motionProps = moving ? { initial: { opacity: 0, y: 8 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.8 } } : {};
  return (
    <Wrap className="card" {...motionProps}>
      <p><strong>{world.rewardQuestion}</strong></p>
      <p className="muted">It stays in your world. Nothing is ever taken away.</p>
      {Object.entries(world.items).map(([id, item]) => (
        <button key={id} className="btn reward-btn" onClick={() => onPick(id)}>
          <span className="reward-art" aria-hidden="true"><img src={`${STILL_BASE}${id}.svg`} alt="" /></span>
          {item.name}
        </button>
      ))}
    </Wrap>
  );
}
