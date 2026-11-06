// Voice helper: turns what was said into one action the app already has. No AI model, nothing
// leaves the device except the audio the browser's own speech service listens to.
// It is flexible: filler words are ignored, word order does not matter, small spelling slips
// and word endings are tolerated, and several phrasings map to the same action.

const SKIP = new Set(["a", "an", "the", "to", "of", "in", "on", "my", "me", "it", "this", "that", "please", "can", "could", "you",
  "would", "will", "i", "like", "just", "now", "ok", "okay", "hey", "carryover", "so", "um", "uh", "lets", "let", "us", "and", "for", "is"]);

export const normalize = (t) =>
  String(t || "").toLowerCase().replace(/['’]/g, "").replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();

export const words = (t) => normalize(t).split(" ").filter((w) => w && !SKIP.has(w));

const stem = (w) => (w.length > 4 ? w.replace(/(ing|ed|es|s)$/, "") : w);
export function lev(a, b) {
  const m = Array.from({ length: a.length + 1 }, (_, i) => [i]);
  for (let j = 1; j <= b.length; j++) m[0][j] = j;
  for (let i = 1; i <= a.length; i++)
    for (let j = 1; j <= b.length; j++)
      m[i][j] = Math.min(m[i - 1][j] + 1, m[i][j - 1] + 1, m[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return m[a.length][b.length];
}
const same = (a, b) => a === b || stem(a) === stem(b) || (a.length >= 5 && b.length >= 5 && lev(a, b) <= 1);

// Do all the words of the phrase appear in what was said (any order)?
export const hasAll = (spoken, phraseWords) => phraseWords.every((p) => spoken.some((s) => same(s, p)));

// Several ways to say each action. The longest matching phrase wins, so "next small step"
// beats "next step".
const INTENTS = [
  ["stopListening", ["stop listening", "never mind", "nevermind", "cancel that", "close"]],
  ["nextSmall", ["next small step", "another small step", "next small", "show next small step", "one more small step"]],
  ["smallSteps", ["small steps", "smaller steps", "show small steps", "break it down", "split it up", "tiny steps", "more steps", "show me how", "how do i do this", "explain this step", "show steps"]],
  ["done", ["done", "finished", "i finished", "i am done", "im done", "complete", "completed", "i did it", "next step", "next", "move on", "go to the next step", "all done"]],
  ["break", ["take a break", "need a break", "break", "rest", "i am tired", "im tired", "pause the task", "take five"]],
  ["help", ["help", "need help", "help me", "i am stuck", "im stuck", "stuck", "i dont know", "dont understand", "i am confused", "im confused", "what do i do"]],
  ["replay", ["read again", "read it again", "read it to me", "read this", "read to me", "read out loud", "say it again", "repeat", "replay", "again", "start over"]],
  ["pause", ["pause", "stop reading", "stop", "wait", "hold on", "be quiet", "quiet"]],
  ["play", ["play", "resume", "keep reading", "continue reading", "carry on", "continue", "keep going", "go on"]],
  ["home", ["home", "main page", "first page", "start page", "welcome page", "go home", "carryover home"]],
  ["tasks", ["my tasks", "task list", "tasks", "all tasks", "other tasks", "what can i do"]],
  ["allsteps", ["all steps", "show all steps", "list of steps", "overview", "show all"]],
  ["settings", ["settings", "setting", "options", "change settings"]],
  ["back", ["back", "go back", "previous", "previous step"]],
  ["start", ["start", "begin", "start the task", "begin the task", "lets start", "lets begin"]],
  ["examples", ["what can i say", "what can you do", "commands", "help with commands", "how does this work", "how does the microphone work", "voice commands", "information"]],
];
const PHRASES = INTENTS.flatMap(([action, list]) => list.map((p) => ({ action, w: words(p) }))).filter((p) => p.w.length);

const ORDINALS = { first: 0, "1st": 0, second: 1, "2nd": 1, third: 2, "3rd": 2, fourth: 3, "4th": 3 };
const NUMBERS = { one: 0, two: 1, three: 2, four: 3, "1": 0, "2": 1, "3": 2, "4": 3 };

// The task the person named, by its title or by "first task", "task two". Returns
// { id } for one match, { options } when several tasks fit, or null.
function matchTask(spoken, tasks) {
  if (!tasks || !tasks.length) return null;
  const hasTask = spoken.some((s) => same(s, "task") || s === "number");
  for (const s of spoken) {
    if (s in ORDINALS && (hasTask || spoken.length <= 2)) return tasks[ORDINALS[s]] ? { id: tasks[ORDINALS[s]].id } : null;
    if (s === "last" && hasTask) return { id: tasks[tasks.length - 1].id };
    if (s in NUMBERS && hasTask) return tasks[NUMBERS[s]] ? { id: tasks[NUMBERS[s]].id } : null;
  }
  const scored = tasks.map((t) => {
    const tw = words(t.title);
    return { t, hit: tw.filter((w) => spoken.some((s) => same(s, w))).length };
  }).filter((x) => x.hit >= 2);
  if (!scored.length) return null;
  const best = Math.max(...scored.map((x) => x.hit));
  const top = scored.filter((x) => x.hit === best);
  return top.length === 1 ? { id: top[0].t.id } : { options: top.map((x) => x.t) };
}

// -> { action, arg? } where action is one of the names above, "openTask", "clarify" or "unknown"
export function interpret(text, tasks = []) {
  const spoken = words(text);
  if (!spoken.length) return { action: "unknown" };
  const task = matchTask(spoken, tasks);
  if (task && task.id) return { action: "openTask", arg: task.id };
  if (task && task.options) return { action: "clarify", arg: task.options };
  let best = null;
  for (const p of PHRASES) {
    if (!hasAll(spoken, p.w)) continue;
    const exact = normalize(text).includes(p.w.join(" ")) ? 1 : 0;
    const score = p.w.length * 2 + exact;
    if (!best || score > best.score) best = { action: p.action, score };
  }
  return best ? { action: best.action } : { action: "unknown" };
}

// Answer to "Did you finish this step?": "yes", "no" or null.
const YES = ["yes", "yeah", "yep", "yup", "sure", "correct", "right", "i did", "i finished", "finished", "done", "ok", "okay", "all done"];
const NO = ["no", "nope", "not yet", "not done", "not finished", "wait", "cancel", "never mind", "nevermind", "still working", "i didnt", "dont"];
export function yesNo(text) {
  const t = normalize(text);
  const w = t.split(" ");
  if (NO.some((p) => (p.includes(" ") ? t.includes(p) : w.includes(p)))) return "no";
  if (YES.some((p) => (p.includes(" ") ? t.includes(p) : w.includes(p)))) return "yes";
  return null;
}

export const EXAMPLES = [
  "Next step (I will ask if you finished)",
  "Show the small steps",
  "Read it again, pause, play",
  "I need help, or I am stuck",
  "Take a break",
  "Go home, my tasks, settings, go back",
  "Open heat a meal, or first task",
];
