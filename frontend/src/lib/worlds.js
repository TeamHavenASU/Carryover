// Game mode worlds, all in one place. The Sky world is the demo world.
//
// A typed interest (setup "What do you love?" > "other") gets its own world. The plan for that
// world (area names, reward items, picture words) will be written by the AI (Role D).
// TODO(Role D, Manaswi): replace the saved "knitting" example with the AI world plan call.
// Until then, a typed interest that matches a saved world below uses it; any other uses Sky.

export const WORLDS = {
  sky: {
    id: "sky",
    name: "Sky world",
    area: (n) => `Island ${n}`,
    areaWord: "island",
    rewardQuestion: "What joins your sky next?",
    rewardHint: "A bird, a hot-air balloon or a kite.",
    items: {
      bird: { name: "A bird", animation: "bird" },
      balloon: { name: "A hot-air balloon", animation: "balloon" },
      kite: { name: "A kite", animation: "kite" },
    },
  },

  // Saved example of a world made for a typed interest. Hand-written, not from the AI.
  knitting: {
    id: "knitting",
    name: "Knitting world",
    area: (n) => ["Yarn basket", "Needle nook", "Pattern shelf", "Cosy corner", "Wool market"][n - 1] || `Area ${n}`,
    areaWord: "area",
    rewardQuestion: "What joins your world next?",
    rewardHint: "A scarf, a hat or a mitten.",
    items: {
      scarf: { name: "A scarf" },
      hat: { name: "A hat" },
      mitten: { name: "A mitten" },
    },
    pictureWords: ["yarn", "needles", "scarf"], // for the free icon library, once the AI picks them
  },
};

// Which world this person sees. Known interests (trains, space, ...) and no interest use Sky.
export function worldFor(interests, knownInterests) {
  const typed = (interests || []).find((i) => !knownInterests.includes(i));
  const key = typed && typed.trim().toLowerCase();
  return WORLDS[key] || WORLDS.sky;
}
