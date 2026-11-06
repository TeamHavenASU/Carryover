
// Take a break: the place is saved. No timer is shown (rule 10).
export default function BreakScreen({ step, settings, onResume, onHome }) {
  return (
    <section>
      <div className="card status">
        <p>Your place is saved.</p>
        <p>You were on: {step.text}</p>
      </div>
      <button className="btn primary" onClick={onResume}>Go back to my step</button>
      <button className="btn" onClick={onHome}>Go to my tasks</button>
    </section>
  );
}
