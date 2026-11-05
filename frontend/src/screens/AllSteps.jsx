// "See all steps": every step's short name, always one tap away.
export default function AllSteps({ today, inTask, onStart, onBack }) {
  return (
    <section>
      <h1>{today.title}: all steps</h1>
      <ol className="steps-list">
        {today.steps.map((s) => <li key={s.step_id}>{s.text}</li>)}
      </ol>
      {inTask
        ? <button className="btn primary" onClick={onBack}>Back to my step</button>
        : <><button className="btn primary" onClick={onStart}>Start</button>
            <button className="btn link" onClick={onBack}>Back</button></>}
    </section>
  );
}
