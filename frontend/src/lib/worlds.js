// Game mode worlds. For the prototype there are four: Sky, Space, Animals and Fruits.
// Animals and Fruits ask one more question (which animal, which fruit), and the background and
// the rewards follow that choice. Backgrounds exist for light and dark mode (screens/Backdrops.jsx).
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

const FRUITS = {
  apple: {
    family: "fruits", key: "fruits:apple", name: "Apples", variant: "apple",
    areaWord: "row", shape: "crate", area: (n) => `Orchard row ${n}`,
    rewardQuestion: "You finished a task. Pick something for your orchard.",
    items: { apple: item("An apple", "apple"), "apple-leaf": item("A leaf", "apple-leaf"), blossom: item("A blossom", "blossom"),
      "apple-basket": item("A basket of apples", "apple-basket"), "apple-pie": item("An apple pie", "apple-pie") },
  },
  strawberry: {
    family: "fruits", key: "fruits:strawberry", name: "Strawberries", variant: "strawberry",
    areaWord: "patch", shape: "crate", area: (n) => `Berry patch ${n}`,
    rewardQuestion: "You finished a task. Pick something for your berry patch.",
    items: { strawberry: item("A strawberry", "strawberry"), daisy: item("A daisy", "daisy"), jar: item("A jar of jam", "jar"),
      "berry-basket": item("A basket of berries", "berry-basket"), shortcake: item("A strawberry shortcake", "shortcake") },
  },
  mango: {
    family: "fruits", key: "fruits:mango", name: "Mangoes", variant: "mango",
    areaWord: "grove", shape: "crate", area: (n) => `Mango grove ${n}`,
    rewardQuestion: "You finished a task. Pick something for your mango grove.",
    items: { mango: item("A mango", "mango"), "mango-slice": item("A mango slice", "mango-slice"), "mango-leaf": item("A leaf", "mango-leaf"),
      "mango-glass": item("A mango smoothie", "mango-glass"), "mango-bowl": item("A bowl of mango", "mango-bowl") },
  },
};

// What the person can choose in "Choose your game world" and in Settings.
export const WORLD_CHOICES = [
  { id: "sky", name: "Sky", blurb: "Clouds, a sun and a moon" },
  { id: "space", name: "Space", blurb: "Planets and stars" },
  { id: "animals", name: "Animals", blurb: "Pick a cat, a dog or a fox", sub: "animalChoice",
    options: [["cat", "Cat"], ["dog", "Dog"], ["fox", "Fox"]] },
  { id: "fruits", name: "Fruits", blurb: "Pick an apple, a strawberry or a mango", sub: "fruitChoice",
    options: [["apple", "Apple"], ["strawberry", "Strawberry"], ["mango", "Mango"]] },
];

// The world this person plays in, from their settings. Sky until they choose.
export function resolveWorld(settings) {
  switch (settings.gameWorld) {
    case "space": return SPACE;
    case "animals": return ANIMALS[settings.animalChoice] || ANIMALS.cat;
    case "fruits": return FRUITS[settings.fruitChoice] || FRUITS.apple;
    default: return SKY;
  }
}
