// Remember where the person was in a task, so leaving the Resident tab or reloading
// brings them back to the same step. Stored in this browser only. Cleared when the task ends.
const KEY = "carryover.session.v1";

export function saveSession(s) {
  try { localStorage.setItem(KEY, JSON.stringify(s)); } catch { /* ignore */ }
}
export function loadSession() {
  try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch { return null; }
}
export function clearSession() {
  try { localStorage.removeItem(KEY); } catch { /* ignore */ }
}
