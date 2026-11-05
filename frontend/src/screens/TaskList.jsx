// My tasks: the task list, plus a "go back to it" card when a task is paused.
export default function TaskList({ taskIds, titles, onOpen, loaded, resume, onResume }) {
  return (
    <section>
      {resume && (
        <div className="card status">
          <p>You were on step {resume.number} of {resume.title}. Your place is saved.</p>
          <button className="btn primary" onClick={onResume}>Go back to my step</button>
        </div>
      )}
      <h1>What do you want to do?</h1>
      {!loaded && <p className="muted" role="status">Loading your tasks…</p>}
      {loaded && taskIds.length === 0 && <div className="card"><p>No tasks yet. Ask staff to add one.</p></div>}
      {taskIds.map((id) => (
        <button key={id} className="btn task-btn" onClick={() => onOpen(id)}>
          {titles[id] || id}
        </button>
      ))}
    </section>
  );
}
