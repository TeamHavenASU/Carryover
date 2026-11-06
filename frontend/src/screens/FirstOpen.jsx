import { useEffect, useState } from "react";
import { getSkill } from "../lib/api";

// The first time a task opens: its first_time_question, then "Can you do these?"
// for the task's base skills. Both only log the answer; fade.py decides what changes.
export default function FirstOpen({ today, log, onDone }) {
  const question = today.first_time_question;
  const skillIds = [...new Set(today.steps.flatMap((s) => s.base_skills || []))];
  const [stage, setStage] = useState(question ? "device" : skillIds.length ? "skills" : "none");
  const [cards, setCards] = useState([]);

  useEffect(() => {
    Promise.all(skillIds.map((id) => getSkill(id).catch(() => null)))
      .then((list) => setCards(list.filter(Boolean)));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { if (stage === "none") onDone(); }, [stage]); // eslint-disable-line react-hooks/exhaustive-deps

  const afterDevice = () => (skillIds.length ? setStage("skills") : onDone());

  function answerDevice(a) {
    log("device_check_answer", { answer: a.toLowerCase().replace(/ /g, "_") });
    afterDevice();
  }

  function answerSkills(a) {
    skillIds.forEach((id) => log("skill_check_answer", { answer: `${id}:${a}` }));
    onDone();
  }

  if (stage === "device") {
    return (
      <section className="center-page">
        <h1>{today.title}</h1>
        <div className="card"><p>{question.text}</p></div>
        {question.answers.map((a) => (
          <button key={a} className="btn primary" onClick={() => answerDevice(a)}>{a}</button>
        ))}
      </section>
    );
  }

  if (stage === "skills") {
    return (
      <section className="center-page">
        <h1>Can you do these?</h1>
        <div className="card">
          <ul>{(cards.length ? cards.map((c) => c.title) : skillIds).map((t) => <li key={t}>{t}</li>)}</ul>
        </div>
        <button className="btn primary" onClick={() => answerSkills("yes")}>Yes</button>
        <button className="btn" onClick={() => answerSkills("not_sure")}>Not sure</button>
      </section>
    );
  }
  return null;
}
