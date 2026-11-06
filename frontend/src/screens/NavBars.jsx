import { Icon } from "../lib/icons";

// Top bar: "← Back" on the left (every screen except My tasks), the screen's name in the
// middle, and an optional link on the right (for example "All steps").
export function TopBar({ title, onBack, onHome, right }) {
  return (
    <header className="topbar">
      <div className="topbar-side left">
        {onHome && (
          <button className="icon-btn" onClick={onHome} aria-label="Home" data-tip="Home"><Icon.home /></button>
        )}
        {onBack && (
          <button className="icon-btn" onClick={onBack} aria-label="Back" data-tip="Back">
            <Icon.back />
          </button>
        )}
      </div>
      <h2 className="topbar-title" title={title}>{title}</h2>
      <div className="topbar-side right">{right}</div>
    </header>
  );
}

// Bottom bar on top-level screens only: My tasks, My world (Game mode only), Settings.
// Never shown during a task. Every icon has its words.
export function BottomNav({ current, showWorld, onTasks, onWorld, onSettings }) {
  const tab = (id, icon, label, onClick) => (
    <button className={`navtab ${current === id ? "on" : ""}`} onClick={onClick} aria-current={current === id ? "page" : undefined}>
      <span className="navtab-icon">{icon}</span>
      <span>{label}</span>
    </button>
  );
  return (
    <nav className="bottom-nav" aria-label="Main">
      {tab("tasks", <Icon.tasks />, "My tasks", onTasks)}
      {showWorld && tab("world", <Icon.world />, "My world", onWorld)}
      {tab("settings", <Icon.settings />, "Settings", onSettings)}
    </nav>
  );
}
