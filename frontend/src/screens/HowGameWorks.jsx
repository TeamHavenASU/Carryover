// What Game mode is and what the person gets, in plain words. It is a drop-down: nothing shows
// until they tap it. Nothing here depends on how much help someone used.
export default function HowGameWorks({ world, every, open = false }) {
  const rewards = Object.values(world.items).map((i) => i.name.toLowerCase()).join(", ");
  return (
    <details className="card how-game" open={open}>
      <summary>How Game mode works?</summary>
      <ul>
        <li><strong>Finish a task:</strong> you pick one reward for your world: {rewards}.</li>
        {world.companion
          ? <li>Your {world.animal} stays with you. It has the reward you picked, and keeps every reward after that.</li>
          : <li><strong>Every {every} tasks:</strong> a new {world.areaWord} opens. The next one shows as an outline, so you know what is coming.</li>}
        <li><strong>Every 10 rewards:</strong> you earn a star on your profile. Stars stay for good.</li>
        <li><strong>Asking for help never changes anything.</strong> Nothing is taken away, and nothing is a score.</li>
        <li>You can change your world, or switch back to Normal, in Settings at any time.</li>
      </ul>
    </details>
  );
}
