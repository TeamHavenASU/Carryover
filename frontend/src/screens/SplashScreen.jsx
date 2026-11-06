import { useEffect } from "react";
import { motion, useReducedMotion } from "framer-motion";

// The first screen when the app opens: the logo, then the app. It moves on by itself after a
// moment when motion is allowed, and the "Continue" button always works. Shown once per visit.
export function Logo({ size = 112 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 112 112" role="img" aria-label="Carryover logo">
      <rect width="112" height="112" rx="26" fill="var(--accent)" />
      {/* a small step being carried over to the next: a dot, an arc and an arrow */}
      <circle cx="30" cy="68" r="9" fill="var(--accent-text)" />
      <path d="M36 58 C44 20 78 20 86 56" fill="none" stroke="var(--accent-text)" strokeWidth="8" strokeLinecap="round" />
      <path d="M72 50 L87 58 L94 42" fill="none" stroke="var(--accent-text)" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
      <rect x="28" y="82" width="56" height="8" rx="4" fill="var(--accent-text)" opacity="0.55" />
    </svg>
  );
}

export default function SplashScreen({ onDone, autoAdvance }) {
  const reduce = useReducedMotion();
  const auto = autoAdvance && !reduce;
  useEffect(() => {
    if (!auto) return undefined;
    const t = setTimeout(onDone, 2400);
    return () => clearTimeout(t);
  }, [auto, onDone]);
  const Wrap = auto ? motion.div : "div";
  const fade = auto ? { initial: { opacity: 0, y: 8 }, animate: { opacity: 1, y: 0 }, transition: { duration: 1 } } : {};
  return (
    <section className="splash">
      <Wrap className="splash-inner" {...fade}>
        <Logo />
        <h1 className="splash-name">Carryover</h1>
        <p className="splash-line">Daily tasks, at your pace.</p>
      </Wrap>
      <button className="btn primary splash-btn" onClick={onDone}>Continue</button>
    </section>
  );
}
