import { motion, useReducedMotion } from "framer-motion";
import { Lottie } from "lottie-react";
import { WORLDS } from "../lib/worlds";

// Game mode world (the demo world is the Sky world, see lib/worlds.js). Islands arrive every
// N tasks done (definitions.json) and are never taken away. Movement follows the Animations
// setting: Off, or prefers-reduced-motion, shows still pictures; Calm is slow; Lively a little more.
// Stars never twinkle.

// Still pictures, used when animations are off and as the fallback while a Lottie file loads.
const STILL = {
  bird: (
    <svg viewBox="0 0 40 24" aria-hidden="true"><path d="M2 14 Q10 4 20 12 Q30 4 38 14 Q30 10 20 18 Q10 10 2 14 Z" fill="#3d4a57" /></svg>
  ),
  balloon: (
    <svg viewBox="0 0 30 44" aria-hidden="true">
      <path d="M15 2 C25 2 28 10 28 16 C28 24 20 29 15 30 C10 29 2 24 2 16 C2 10 5 2 15 2 Z" fill="#d9825b" stroke="#a85f3d" />
      <path d="M15 2 C11 8 11 24 15 30 C19 24 19 8 15 2 Z" fill="#e9b27a" />
      <path d="M9 29 L12 36 M21 29 L18 36" stroke="#6b4f3a" />
      <rect x="11" y="36" width="8" height="6" rx="1" fill="#8a6a4f" />
    </svg>
  ),
  kite: (
    <svg viewBox="0 0 30 44" aria-hidden="true">
      <path d="M15 2 L27 16 L15 30 L3 16 Z" fill="#6fae7c" stroke="#4e8a5b" />
      <path d="M15 2 L15 30 M3 16 L27 16" stroke="#e9f3eb" />
      <path d="M15 30 q-4 4 0 7 q4 3 0 6" fill="none" stroke="#4e8a5b" strokeWidth="1.5" />
    </svg>
  ),
};

// Lottie files are our own (frontend/public/animations/), played only in Game mode with motion on.
const ANIM_BASE = `${import.meta.env.BASE_URL}animations/`;

function Item({ id, world, moving, lively }) {
  const item = world.items[id];
  if (moving && item && item.animation) {
    return (
      <span className="sky-item" aria-hidden="true">
        <Lottie src={`${ANIM_BASE}${item.animation}.json`} loop autoplay speed={lively ? 1 : 0.6} />
      </span>
    );
  }
  return STILL[id]
    ? <span className="sky-item">{STILL[id]}</span>
    : <span className="sky-item sky-word">{item ? item.name.replace(/^A /, "") : id}</span>;
}

function Island({ n, world, items, outline, note, arriving, moving, lively }) {
  const body = (
    <>
      <svg viewBox="0 0 200 80" className="island-shape" aria-hidden="true">
        <path d="M20 50 C10 50 8 36 22 34 C22 20 44 16 52 26 C60 10 92 10 100 26 C110 14 140 16 142 32 C160 26 178 36 172 50 Z"
          fill={outline ? "none" : "#ffffff"} stroke={outline ? "currentColor" : "#c9d8e4"} strokeWidth="3"
          strokeDasharray={outline ? "8 6" : undefined} />
        {!outline && <path d="M40 50 C70 72 130 72 160 50 Z" fill="#dfe9f1" />}
      </svg>
      <div className="island-items">
        {items.map((it, i) => <Item key={i} id={it} world={world} moving={moving} lively={lively} />)}
      </div>
      <p className="island-label">{outline ? note : world.area(n)}</p>
    </>
  );
  const cls = `island ${outline ? "outline" : ""} ${n % 2 ? "left" : "right"}`;
  // A new island slides in once (framer-motion). Without motion it is simply there.
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

export default function SkyWorld({ world = WORLDS.sky, unlocked, moreNeeded, surpriseMe, items, dark, animations, arrivingIsland, compact }) {
  const reduce = useReducedMotion();
  const moving = animations !== "off" && !reduce;
  const lively = animations === "lively";
  // Each item they chose sits on one of their islands, in order.
  const onIsland = (n) => items.filter((_, i) => (i % unlocked) + 1 === n);
  const shown = compact ? Math.min(unlocked, 2) : unlocked;
  const first = unlocked - shown + 1;
  const word = world.areaWord;
  return (
    <div className={`sky ${dark ? "night" : "day"}`} data-anim={moving ? animations : "off"} role="img"
      aria-label={`${world.name}: ${unlocked} ${unlocked === 1 ? word : `${word}s`}${moreNeeded ? `, the next opens after ${moreNeeded} more` : ""}`}>
      {dark ? <span className="moon" aria-hidden="true" /> : <span className="sun" aria-hidden="true" />}
      {dark && <span className="stars" aria-hidden="true" />}
      <span className="cloud c1" aria-hidden="true" /><span className="cloud c2" aria-hidden="true" />
      {Array.from({ length: shown }, (_, i) => first + i).map((n) => (
        <Island key={n} n={n} world={world} items={onIsland(n)} arriving={n === arrivingIsland} moving={moving} lively={lively} />
      ))}
      {moreNeeded && !surpriseMe && (
        <Island n={unlocked + 1} world={world} items={[]} outline moving={false}
          note={`Opens after ${moreNeeded} more ${moreNeeded === 1 ? "task" : "tasks"}`} />
      )}
    </div>
  );
}

// The reward after a new island: the person chooses what joins their world. It fades in gently
// when animations are on.
export function RewardChoice({ world = WORLDS.sky, animations, onPick }) {
  const reduce = useReducedMotion();
  const moving = animations !== "off" && !reduce;
  const Wrap = moving ? motion.div : "div";
  const motionProps = moving ? { initial: { opacity: 0, y: 8 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.8 } } : {};
  return (
    <Wrap className="card" {...motionProps}>
      <p><strong>{world.rewardQuestion}</strong></p>
      <p className="muted">{world.rewardHint}</p>
      {Object.entries(world.items).map(([id, item]) => (
        <button key={id} className="btn reward-btn" onClick={() => onPick(id)}>
          {STILL[id] && <span className="reward-art" aria-hidden="true">{STILL[id]}</span>}
          {item.name}
        </button>
      ))}
    </Wrap>
  );
}
