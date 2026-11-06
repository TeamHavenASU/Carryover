// Game mode worlds. For the prototype there are three: Sky, Space and Animals.
// Animals asks one more question (which animal), and the background and the rewards follow
// that choice. Backgrounds exist for light and dark mode (screens/Backdrops.jsx).
// Pictures and animations for the rewards are in frontend/public/game/ and public/animations/
// (made by tools/make_game_art.py).
//
// A typed interest (setup "What do you love?" > "other") will get its own world, with the plan
// written by the AI. TODO(Role D, Manaswi): add that AI call; the four worlds below are fixed.

// attach: where the item sits on the companion animal (mouth, front or collar).
const item = (name, animation, attach) => ({ name, animation: animation || null, attach: attach || null });

const SKY = {
  family: "sky", key: "sky", name: "Sky",
  areaWord: "island", shape: "cloud", area: (n) => `Island ${n}`,
  rewardQuestion: "You finished a task. Pick something for your sky.",
  items: { bird: item("A bird", "bird"), balloon: item("A hot-air balloon", "balloon"), kite: item("A kite", "kite"), rainbow: item("A rainbow") },
};

const SPACE = {
  family: "space", key: "space", name: "Space",
  areaWord: "planet", shape: "planet", area: (n) => `Planet ${n}`,
  rewardQuestion: "You finished a task. Pick something for your space.",
  items: { rocket: item("A rocket", "rocket"), satellite: item("A satellite", "satellite"), comet: item("A comet", "comet"), planet: item("A ringed planet", "planet") },
};

const ANIMALS = {
  cat: {
    family: "animals", key: "animals:cat", name: "Cats", variant: "cat", animal: "cat", companion: true,
    areaWord: "spot", shape: "platform", area: (n) => `Cozy spot ${n}`,
    rewardQuestion: "You finished a task. Pick a gift for your cat.",
    items: { yarn: item("A ball of yarn", "yarn", "front"), fish: item("A fish", "fish", "mouth"), bell: item("A bell", "bell", "collar") },
  },
  dog: {
    family: "animals", key: "animals:dog", name: "Dogs", variant: "dog", animal: "dog", companion: true,
    areaWord: "spot", shape: "platform", area: (n) => `Park spot ${n}`,
    rewardQuestion: "You finished a task. Pick a gift for your dog.",
    items: { bone: item("A bone", "bone", "mouth"), ball: item("A ball", "ball", "mouth"), bowl: item("A bowl", "bowl", "front") },
  },
  fox: {
    family: "animals", key: "animals:fox", name: "Foxes", variant: "fox", animal: "fox", companion: true,
    areaWord: "clearing", shape: "platform", area: (n) => `Forest clearing ${n}`,
    rewardQuestion: "You finished a task. Pick a gift for your fox.",
    items: { acorn: item("An acorn", "acorn", "mouth"), leaf: item("A leaf", "leaf", "mouth"), mushroom: item("A mushroom", "mushroom", "front") },
  },
};

// What the person can choose in "Choose your game world" and in Settings.
export const WORLD_CHOICES = [
  { id: "sky", name: "Sky", blurb: "Clouds, a sun and a moon" },
  { id: "space", name: "Space", blurb: "Planets and stars" },
  { id: "animals", name: "Animals", blurb: "Pick a cat, a dog or a fox", sub: "animalChoice",
    options: [["cat", "Cat"], ["dog", "Dog"], ["fox", "Fox"]] },
];

// A plain-words description of a world: what it looks like, what finishing a task gives, and how
// it grows. Used on the setup preview, so it always matches the world they picked.
const INTRO = {
  sky: "The whole app sits in a sky with floating cloud islands.",
  space: "The whole app sits in space, with planets and stars.",
  animals: null, // the animal itself is the world
};
export function describeWorld(world, every = 2) {
  const rewards = Object.values(world.items).map((i) => i.name.toLowerCase()).join(", ");
  if (world.companion) {
    return `Your ${world.animal} stays with you. Finish a task and pick a gift for it: ${rewards}. It keeps every gift you pick.`;
  }
  return `${INTRO[world.family]} Finish a task and pick a reward: ${rewards}. Every ${every} tasks a new ${world.areaWord} opens.`;
}

// The world this person plays in, from their settings. Sky until they choose.
export function resolveWorld(settings) {
  switch (settings.gameWorld) {
    case "space": return SPACE;
    case "animals": return ANIMALS[settings.animalChoice] || ANIMALS.cat;
    default: return SKY;
  }
}
