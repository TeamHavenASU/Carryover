import { useState } from "react";
import { supportName } from "../lib/settings";
import { Icon } from "../lib/icons";

// Help screen, opened by "Help with this step". For the prototype, "I'm stuck" tells the person to
// ask their support person (name from Settings, "staff" if none). It logs stuck_pressed, which
// counts as used help, as it did before.
export default function HelpScreen({ step, settings, canShowSmall, onShowSmall, onStuck, onBack }) {
  const [stuck, setStuck] = useState(false);
  const name = supportName(settings);
  const contact = (settings.supportContact || "").trim();
  return (
    <section>
      <div className="card"><p className="muted">Your step</p><p><strong>{step.text}</strong></p></div>

      {canShowSmall && <button className="btn primary" onClick={onShowSmall}>Show the small steps</button>}

      <button className="btn" onClick={() => { if (!stuck) onStuck(); setStuck(true); }}>I'm stuck</button>
      {stuck && (
        <div className="card status" role="status">
          <p>Please ask {name}.</p>
          {contact && <p>{contact}</p>}
        </div>
      )}

      <button className="btn link" onClick={onBack}><Icon.back /> Back to my step</button>
    </section>
  );
}
