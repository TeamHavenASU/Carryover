import { useState } from "react";
import { supportName } from "../lib/settings";

// Take a break: the place is saved. No timer is shown (rule 10).
export default function BreakScreen({ step, settings, onResume, onHome }) {
  const [asked, setAsked] = useState(false);
  const name = supportName(settings);
  const contact = (settings.supportContact || "").trim();
  return (
    <section>
      <div className="card status">
        <p>Your place is saved.</p>
        <p>You were on: {step.text}</p>
      </div>
      <button className="btn primary" onClick={onResume}>Go back to my step</button>
      <button className="btn" onClick={onHome}>Go to my tasks</button>
      <button className="btn" onClick={() => setAsked(true)}>Ask {name}</button>
      {asked && (
        <div className="card" role="status">
          <p>Please ask {name}.</p>
          {contact && <p>{contact}</p>}
        </div>
      )}
    </section>
  );
}
