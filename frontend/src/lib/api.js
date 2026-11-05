// Calls to the backend (Role C routes). Uses the shared get/post in src/api.js.
import { get, post } from "../api";

export const getTasks = () => get("/tasks");

export const getSetup = () => get("/setup");
export const getSkill = (id) => get(`/skills/${encodeURIComponent(id)}`);

export const getGame = (personId) => get("/game", { person_id: personId });

export const getToday = (personId, taskId, week) =>
  get("/today", { person_id: personId, task_id: taskId, week });

// Local time like "2026-11-16T18:02:10" (Format 2).
export function nowStamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

export const sessionId = (personId, taskId, week) =>
  `${personId}-${taskId}-w${String(week).padStart(2, "0")}`;

// Send one event. Only event names, step ids and numbers. Never items, prices or food.
// A failed log never blocks the person, so errors are swallowed.
export async function logEvent(fields) {
  try {
    await post("/event", { timestamp: nowStamp(), ...fields });
  } catch { /* logging must never get in the person's way */ }
}
