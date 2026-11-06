// Voice: press any button or choice on the screen by saying its words. This is what lets the
// microphone work on every page (Continue, Next, Skip, Sky, Slow, a task name, and so on).
import { hasAll, lev, normalize, words } from "./voiceCommands";

// Buttons that change or erase things are never pressed by voice.
const NEVER = /redo|reset|stop sharing|delete|remove|clear/i;

const visible = (el) => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== "hidden";
export const labelOf = (el) => (el.getAttribute("aria-label") || el.innerText || el.textContent || "").replace(/\s+/g, " ").trim();

export function findClickable(text) {
  const root = typeof document !== "undefined" && document.querySelector(".resident");
  const spoken = words(text);
  if (!root || !spoken.length) return {};
  const items = [...root.querySelectorAll('button, [role="button"], label.check, label.choice, label.segment, label.palette, summary')]
    .filter((el) => visible(el) && !el.disabled && !el.closest(".voice-panel") && !el.closest(".mic-bar"))
    .map((el) => ({ el, label: labelOf(el) }))
    .filter((i) => i.label && !NEVER.test(i.label))
    .map((i) => ({ ...i, w: words(i.label) }))
    .filter((i) => i.w.length);

  // 1. Exactly the words of a button, e.g. "next", "skip", "sky", "continue", "heat a meal".
  const exact = items.filter((i) => i.w.length === spoken.length && hasAll(spoken, i.w) && hasAll(i.w, spoken));
  if (exact.length) return { exact: exact[0] };

  // 2. Partly: the button's words are inside what was said ("open heat a meal"), or what was
  //    said is inside the button's words ("heat" for "Heat a meal"). One short word only counts
  //    when it points at a single button.
  const scored = items.map((i) => {
    if (hasAll(spoken, i.w)) return { ...i, score: i.w.length * 2 };
    if ((spoken.length >= 2 || spoken[0].length >= 4) && hasAll(i.w, spoken)) return { ...i, score: spoken.length };
    return null;
  }).filter(Boolean);
  if (scored.length) {
    const best = Math.max(...scored.map((s) => s.score));
    const top = scored.filter((s) => s.score === best);
    const labels = [...new Set(top.map((t) => t.label))];
    return labels.length === 1 ? { fuzzy: top[0] } : { options: labels.slice(0, 4) };
  }

  // 3. Sounds close to a button: "get a meal" for "Heat a meal". The closest button wins when it
  //    is clearly closer than the others.
  const said = spoken.join(" ");
  if (said.length >= 6) {
    const sims = items.map((i) => {
      const lab = i.w.join(" ");
      return { ...i, sim: 1 - lev(said, lab) / Math.max(said.length, lab.length) };
    }).sort((a, b) => b.sim - a.sim);
    if (sims[0] && sims[0].sim >= 0.7 && (!sims[1] || sims[0].sim - sims[1].sim >= 0.1)) return { fuzzy: sims[0] };
  }
  return {};
}
