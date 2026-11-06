import { useState } from "react";
import { supportName } from "../lib/settings";

// Help screen, opened by "Help with this step". The AI part (type, speak or photo) is Role D's
// AskForHelp component; it hands off to the support person for risky questions. Below it, the
// person can always ask their support person (name from Settings, "staff" if none).
export default function HelpScreen({ step, settings, canShowSmall, onShowSmall, stuckPanel, onBack }) {
  const [asked, setAsked] = useState(false);
  const name = supportName(settings);
  const contact = (settings.supportContact || "").trim();
  return (
    <section>
      <div className="card"><p className="muted">Your step</p><p><strong>{step.text}</strong></p></div>

      {canShowSmall && <button className="btn primary" onClick={onShowSmall}>Show the small steps</button>}

      <div className="card">
        <h2>Ask about this step</h2>
        <p className="muted">Type, speak or take a photo. The answer is one short step.</p>
        {stuckPanel}
      </div>

      <button className="btn" onClick={() => setAsked(true)}>Still stuck?</button>
      {asked && (
        <div className="card status" role="status">
          <h2>Ask {name}</h2>
          <p>{contact ? <>How to reach them: <strong>{contact}</strong></> : "You can add how to reach them in Settings."}</p>
          <p className="muted note">Your place is saved. Come back when you are ready.</p>
        </div>
      )}

    </section>
  );
}
