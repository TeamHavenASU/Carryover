// Game mode helpers. The rules (a new area every N tasks, the milestones, the settings and their
// defaults) come from definitions.json through GET /game. Nothing here is a resident's data.

// How many areas a world has. Our own choice, not from definitions.json.
export const AREAS_PER_WORLD = 5;

const label = (v) => String(v).replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
export { label };

// The world's theme comes from the first interest. A typed one (not in the setup list) is "Your town".
export function themeName(interests, knownInterests) {
  const first = (interests || [])[0];
  if (!first) return "Your world";
  return knownInterests.includes(first) ? label(first) : "Your town";
}

// Areas open as tasks are done. The next one opens after `every` more tasks. Never taken away.
export function worldState(tasksDone, every) {
  const unlocked = Math.min(AREAS_PER_WORLD, 1 + Math.floor(tasksDone / every));
  const moreNeeded = every - (tasksDone % every);
  return { unlocked, next: unlocked < AREAS_PER_WORLD ? { moreNeeded } : null };
}

// Sounds are made in code (Web Audio), no files. Only plays when volume is not off.
const VOLUME = { very_soft: 0.03, soft: 0.08, normal: 0.2 };
const TONES = {
  chime: [660, 880],
  nature: [392, 523],
  theme: [440, 554, 659],
};

export function playSound(volume, type) {
  const gain = VOLUME[volume];
  if (!gain) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    (TONES[type] || TONES.chime).forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const amp = ctx.createGain();
      const t = ctx.currentTime + i * 0.25;
      osc.type = type === "nature" ? "triangle" : "sine";
      osc.frequency.value = freq;
      amp.gain.setValueAtTime(0, t);
      amp.gain.linearRampToValueAtTime(gain, t + 0.05);
      amp.gain.linearRampToValueAtTime(0, t + 0.45);
      osc.connect(amp).connect(ctx.destination);
      osc.start(t);
      osc.stop(t + 0.5);
    });
  } catch { /* sound is optional */ }
}
