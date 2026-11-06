// The safety card, exactly as written in the task file (safety_card_content).
export default function SafetyCard({ content, onContinue }) {
  return (
    <section>
      <h1>{content.title}</h1>
      <div className="card">
        <h2>{content.never_title}</h2>
        <ul>{content.never.map((t) => <li key={t}>{t}</li>)}</ul>
      </div>
      <div className="card">
        <h2>{content.ok_title}</h2>
        <ul>{content.ok.map((t) => <li key={t}>{t}</li>)}</ul>
      </div>
      {content.also && content.also.length > 0 && (
        <div className="card">
          <h2>{content.also_title || "Also remember"}</h2>
          <ul>{content.also.map((t) => <li key={t}>{t}</li>)}</ul>
        </div>
      )}
      <button className="btn primary" onClick={onContinue}>Continue</button>
    </section>
  );
}
