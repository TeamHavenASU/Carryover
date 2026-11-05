import { useEffect, useRef } from "react";

// A small one-time question in the middle of the screen. It never moves, can always be
// dismissed, and is asked once. Nothing is chosen for the person.
export default function Tip({ title, children, yesLabel, noLabel, onYes, onNo }) {
  const first = useRef(null);
  useEffect(() => { if (first.current) first.current.focus(); }, []);
  return (
    <div className="overlay" role="dialog" aria-modal="true" aria-label={title}>
      <div className="card">
        <p><strong>{title}</strong></p>
        {children}
        {yesLabel && <button ref={first} className="btn primary" onClick={onYes}>{yesLabel}</button>}
        <button className="btn" onClick={onNo}>{noLabel}</button>
      </div>
    </div>
  );
}
