import { useState } from "react";

// Start push, Start, and "Quick look at all steps" (always there, rule 11).
// If today's view says refresher: true, ask first and log refresher_answer.
export default function StartScreen({ today, onStart, onLook, onRefresherAnswer, onBack, askAboutSkips, onSkipAnswer }) {
  const [askedSkips, setAskedSkips] = useState(!askAboutSkips);
  const [asked, setAsked] = useState(!today.show_refresher);

  // Ask once whether they still want this task (the view says when).
  if (!askedSkips) {
    return (
      <section>
        <h1>{today.title}</h1>
        <div className="card">
          <p>Do you still want to do this task?</p>
          <button className="btn primary" onClick={() => { onSkipAnswer("yes"); setAskedSkips(true); }}>Yes</button>
          <button className="btn" onClick={() => { onSkipAnswer("no"); onBack(); }}>No, not now</button>
        </div>
      </section>
    );
  }


  if (!asked) {
    return (
      <section>
        <h1>{today.title}</h1>
        <div className="card">
          <p>It's been a while since you did this. Want a quick look at all the steps first?</p>
          <button className="btn primary" onClick={() => { onRefresherAnswer("yes"); setAsked(true); onLook(); }}>
            Yes, show me
          </button>
          <button className="btn" onClick={() => { onRefresherAnswer("no"); setAsked(true); }}>
            No, let's start
          </button>
        </div>
      </section>
    );
  }

  return (
    <section>
      <h1>{today.title}</h1>
      {today.start_push && <div className="card"><p>{today.start_push}</p></div>}
      <button className="btn primary" onClick={onStart}>Start</button>
      <button className="btn" onClick={onLook}>Quick look at all steps</button>
      <button className="btn link" onClick={onBack}>Back to the task list</button>
    </section>
  );
}
