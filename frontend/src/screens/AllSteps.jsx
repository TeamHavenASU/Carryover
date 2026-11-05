// All steps: the whole task as a numbered list. Tapping a step goes to it.
export default function AllSteps({ today, inTask, currentIndex, onJump, onStart, onBack }) {
  return (
    <section>
      <ol className="all-steps">
        {today.steps.map((s, i) => (
          <li key={s.step_id}>
            <button className={`btn all-step ${inTask && i === currentIndex ? "on" : ""}`} onClick={() => onJump(i)}
              aria-current={inTask && i === currentIndex ? "step" : undefined}>
              <span className="all-step-n">{i + 1}</span>
              <span>{s.text}{inTask && i === currentIndex ? " (you are here)" : ""}</span>
            </button>
          </li>
        ))}
      </ol>
      {inTask
        ? <button className="btn primary" onClick={onBack}>Go back to my step</button>
        : <button className="btn primary" onClick={onStart}>Start</button>}
    </section>
  );
}
