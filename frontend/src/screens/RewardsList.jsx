// "My rewards": a drop-down with every reward they have picked in this world and how many of each.
const STILL_BASE = `${import.meta.env.BASE_URL}game/`;

export default function RewardsList({ world, items }) {
  const counts = {};
  items.forEach((id) => { counts[id] = (counts[id] || 0) + 1; });
  const ids = Object.keys(world.items).filter((id) => counts[id]);
  return (
    <details className="card rewards-list">
      <summary>My rewards ({items.length})</summary>
      {ids.length === 0 ? (
        <p className="muted">Rewards you pick after a task show here.</p>
      ) : (
        <ul>
          {ids.map((id) => (
            <li key={id}>
              <img src={`${STILL_BASE}${id}.svg`} alt="" />
              <span>{world.items[id].name}</span>
              <strong aria-label={`${counts[id]} of them`}>× {counts[id]}</strong>
            </li>
          ))}
        </ul>
      )}
    </details>
  );
}
