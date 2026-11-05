export default function TaskList({ taskIds, titles, onOpen, showWorld, onWorld }) {
  return (
    <section>
      <h1>What do you want to do?</h1>
      {taskIds.map((id) => (
        <button key={id} className="btn primary" onClick={() => onOpen(id)}>
          {titles[id] || id}
        </button>
      ))}
      {showWorld && <button className="btn" onClick={onWorld}>My world</button>}
    </section>
  );
}
