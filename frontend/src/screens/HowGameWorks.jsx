// What Game mode is and what the person gets, in plain words. It is a drop-down: nothing shows
// until they tap it. Nothing here depends on how much help someone used.
export default function HowGameWorks({ world, every, open = false }) {
  const rewards = Object.values(world.items).map((i) => i.name.toLowerCase()).join(", ");
  return (
    <details className="card how-game" open={open}>
      <summary>How Game mode works</summary>
      <ul>
        <li><strong>Finish a task:</strong> you pick one reward for your world: {rewards}.</li>
        <li><strong>Every {every} tasks:</strong> a new {world.areaWord} opens. The next one shows as an outline, so you know what is coming.</li>
        <li><strong>Asking for help never changes anything.</strong> Nothing is taken away, and nothing is a score.</li>
        <li>You can change your world, or switch back to Normal, in Settings at any time.</li>
      </ul>
    </details>
  );
}
