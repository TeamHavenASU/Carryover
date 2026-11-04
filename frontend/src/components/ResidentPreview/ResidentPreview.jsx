import "./ResidentPreview.css";

const modeLabels = {
  split: "Most help: small steps shown",
  hint: "Some help: short name only",
  hide: "No help: folded under See all steps",
};

// Shows the view from GET /demo/view as a plain list. It only displays what the
// backend sends. It never decides a help level.
export default function ResidentPreview({ view }) {
  return (
    <section className="preview" aria-label="What the resident sees">
      <h2>{view.title}</h2>

      <ul className="notes">
        {view.show_safety_card && <li>First time: show the safety card ({view.show_safety_card}).</li>}
        {view.start_push && <li>Start push: {view.start_push}</li>}
        {view.show_refresher && <li>Ask: "Want a quick look at all the steps first?"</li>}
        {view.ask_about_skips && <li>Ask once if they still want this task.</li>}
        {view.check_questions.length > 0 && (
          <li>At the end, ask: {view.check_questions.map((q) => q.question).join(" / ")}</li>
        )}
      </ul>

      <ol className="steps">
        {view.steps.map((step) => (
          <li key={step.step_id} className="step">
            <div className="step-head">
              <span className="step-text">{step.mode === "split" ? step.text : step.hint}</span>
              <span className="pill">{modeLabels[step.mode] || step.mode}</span>
            </div>
            {step.substeps.length > 0 && (
              <details open={step.mode === "split"}>
                <summary>Small steps ({step.substeps.length})</summary>
                <ul>
                  {step.substeps.map((s) => (
                    <li key={s.id}>{s.text}</li>
                  ))}
                </ul>
              </details>
            )}
            <p className="muted small">
              Offer help after {step.hint_waits.join(", ")} seconds
              {step.wait ? " (waiting step, no long pause)" : ""}
            </p>
          </li>
        ))}
      </ol>
    </section>
  );
}
