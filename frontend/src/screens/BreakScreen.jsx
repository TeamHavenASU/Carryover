// Take a break: the place is saved. No timer is shown (rule 10).
export default function BreakScreen({ today, step, onResume }) {
  return (
    <section>
      <h1>Taking a break</h1>
      <div className="card">
        <p>Your place is saved.</p>
        <p>You were on: {step.text}</p>
      </div>
      <button className="btn primary" onClick={onResume}>Back to my task</button>
    </section>
  );
}
