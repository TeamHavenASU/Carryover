import { useEffect, useState } from "react";

// Display settings live in this browser only (localStorage). Wrapped in try/catch
// because storage can be blocked. Support person and sharing will need the backend
// (open point 8 in docs/ROLE_C_INTERFACE.md).
const KEY = "carryover.settings.v1";

export const DEFAULTS = {
  personId: "",
  week: 1,
  textSize: "medium",   // medium | large | larger
  font: "sans",         // sans | serif | verdana
  theme: "soft",        // soft | neutral | cool | dark
  pictures: true,
  readAloud: false,
  praise: "calm",       // calm | cheerful | off
  supportPerson: "your support person",
  shareWithStaff: false, // off by default
  phoneType: "iphone_face_id", // iphone_face_id | iphone_home_button | android
  // First-time setup (questions and defaults come from definitions.json)
  setupDone: false,
  interests: [],
  style: "normal",
  sound: "soft",
  hand: "right",
  // Game mode (names and defaults come from definitions.json game_mode)
  soundType: "chime",
  soundTypeAsked: false,
  animations: "calm",
  animationsAsked: false,
  surpriseMe: false,
  // Reading voice (a voice already on the device, and a speed)
  voiceName: "",
  voiceSpeed: "normal", // slow | normal
};

// Remember, in this browser, that the "still want this task?" question was asked.
export function askedAboutSkips(personId, taskId) {
  try { return localStorage.getItem(`carryover.askedskips.${personId}.${taskId}`) === "1"; } catch { return false; }
}
export function markAskedAboutSkips(personId, taskId) {
  try { localStorage.setItem(`carryover.askedskips.${personId}.${taskId}`, "1"); } catch { /* ignore */ }
}

// Remember, in this browser, that a task's first-open questions were answered.
export function firstOpenDone(personId, taskId) {
  try { return localStorage.getItem(`carryover.firstopen.${personId}.${taskId}`) === "1"; } catch { return false; }
}
export function markFirstOpenDone(personId, taskId) {
  try { localStorage.setItem(`carryover.firstopen.${personId}.${taskId}`, "1"); } catch { /* ignore */ }
}

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    return { ...DEFAULTS, ...(raw ? JSON.parse(raw) : {}) };
  } catch {
    return { ...DEFAULTS };
  }
}

// Applied to the resident wrapper only, so the staff and demo pages keep their own look.
// Palette choices for Settings. bg, panel and accent are only for the swatch.
export const PALETTES = [
  { id: "soft", name: "Soft light", bg: "#f4f1ea", panel: "#ffffff", accent: "#2f5d7c" },
  { id: "neutral", name: "Calm neutral (low contrast)", bg: "#e9e7e2", panel: "#f2f0ec", accent: "#4a5f70" },
  { id: "cool", name: "Cool blue-green", bg: "#e4eeee", panel: "#f1f7f7", accent: "#2b6a66" },
  { id: "dark", name: "Dark", bg: "#1d242b", panel: "#27313a", accent: "#9cc3de" },
];

export const lookAttributes = (s) => ({
  "data-size": s.textSize,
  "data-font": s.font,
  "data-theme": s.theme,
});

export function useSettings() {
  const [settings, setSettings] = useState(load);
  useEffect(() => {
    try { localStorage.setItem(KEY, JSON.stringify(settings)); } catch { /* ignore */ }
  }, [settings]);
  const update = (patch) => setSettings((s) => ({ ...s, ...patch }));
  return [settings, update];
}

// person and week can also come from the address, e.g. ?person=jeremiah&week=3
export function fromUrl() {
  const q = new URLSearchParams(window.location.search);
  const out = {};
  if (q.get("person")) out.personId = q.get("person");
  if (q.get("week")) out.week = Number(q.get("week")) || 1;
  return out;
}

const SPEEDS = { slow: 0.8, normal: 1 };

// Voices already on the device that work offline.
export function deviceVoices() {
  if (!("speechSynthesis" in window)) return [];
  return window.speechSynthesis.getVoices().filter((v) => v.localService);
}

export function speak(text, settings = {}) {
  if (!("speechSynthesis" in window)) return;
  const u = new SpeechSynthesisUtterance(text);
  const voice = deviceVoices().find((v) => v.name === settings.voiceName);
  if (voice) u.voice = voice;
  u.rate = SPEEDS[settings.voiceSpeed] || 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(u);
}
