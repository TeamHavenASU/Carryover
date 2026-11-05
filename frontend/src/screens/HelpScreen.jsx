import { useState } from "react";
import { supportName } from "../lib/settings";
import { Icon } from "../lib/icons";

// Help screen, opened by "Help with this step". The AI part (type, speak or photo) is Role D's
// AskForHelp component; it hands off to the support person for risky questions.
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

      <button className="btn" onClick={() => setAsked(true)}>Still stuck? Ask {name}</button>
      {asked && (
        <div className="card status" role="status">
          <p>Please ask {name}.</p>
          {contact && <p>{contact}</p>}
        </div>
      )}

      <button className="btn link" onClick={onBack}><Icon.back /> Back to my step</button>
    </section>
  );
}
