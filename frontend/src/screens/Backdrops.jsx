import { motion, useReducedMotion } from "framer-motion";
import { Lottie } from "lottie-react";

const BASE = import.meta.env.BASE_URL;
const ANIM_BASE = `${BASE}animations/`;
const art = (id) => `${BASE}game/${id}.svg`;

// The background of every Game mode screen: one backdrop per world (and per animal or fruit),
// each with a light and a dark version. Everything people read or tap sits on cards above it,
// so text stays readable. Motion is slow, off when Animations is Off or motion is reduced, and
// stars never twinkle.

function Cloud({ cls }) {
  return (
    <svg className={`bg-cloud ${cls}`} viewBox="0 0 120 50" aria-hidden="true">
      <path d="M14 42 C2 42 0 28 14 26 C14 12 34 8 42 18 C48 4 78 4 84 20 C98 14 114 24 108 42 Z" />
    </svg>
  );
}

const Stars = () => <span className="stars" />;

// Pictures scattered over the background (paw prints, toys, fruit...). They float gently if
// motion is on. Each spot is [picture, x%, y%, size, delay].
function Scatter({ spots, moving, cls = "" }) {
  return spots.map(([id, x, y, size, delay], i) => {
    const style = { left: `${x}%`, top: `${y}%`, width: size, height: size };
    return moving ? (
      <motion.img key={i} src={art(id)} alt="" className={`decor-img ${cls}`} style={style}
        animate={{ y: [0, -8, 0] }} transition={{ duration: 7 + delay, repeat: Infinity, ease: "easeInOut" }} />
    ) : (
      <img key={i} src={art(id)} alt="" className={`decor-img ${cls}`} style={style} />
    );
  });
}

// Leaves drifting down slowly (fox world), only if motion is on.
function FallingLeaves({ moving }) {
  if (!moving) return null;
  return [[12, 0], [46, 7], [78, 3]].map(([x, delay], i) => (
    <motion.img key={i} src={art("leaf")} alt="" className="decor-img falling" style={{ left: `${x}%`, top: -40, width: 34, height: 34 }}
      initial={{ y: -40, rotate: 0 }} animate={{ y: 900, rotate: 160 }}
      transition={{ duration: 22 + i * 4, repeat: Infinity, ease: "linear", delay }} />
  ));
}

const PINES = "M0 120 L22 56 L44 120 Z M30 120 L58 36 L86 120 Z M74 120 L98 64 L122 120 Z M112 120 L142 30 L172 120 Z M160 120 L184 60 L208 120 Z M196 120 L224 44 L252 120 Z M240 120 L262 66 L284 120 Z M272 120 L302 34 L332 120 Z M322 120 L346 62 L370 120 Z M356 120 L384 40 L412 120 Z";
const FENCE = "M0 40 H400 M0 62 H400 M20 28 V84 M80 28 V84 M140 28 V84 M200 28 V84 M260 28 V84 M320 28 V84 M380 28 V84";

const CAT = [["paw", 8, 30, 36, 0], ["paw", 70, 52, 40, 2], ["yarn", 14, 58, 84, 1], ["fish", 62, 74, 90, 3], ["bell", 80, 28, 70, 2], ["paw", 36, 88, 34, 1]];
const DOG = [["bone", 8, 22, 90, 0], ["ball", 70, 34, 78, 2], ["paw", 24, 54, 36, 1], ["bone", 64, 62, 84, 3], ["paw", 80, 80, 34, 2]];
const FOX = [["acorn", 10, 26, 76, 0], ["mushroom", 72, 46, 84, 2], ["acorn", 28, 62, 70, 1], ["leaf", 78, 24, 66, 3]];
const FRUIT = {
  apple: ["apple", "apple-leaf", "blossom", "apple-basket"],
  strawberry: ["strawberry", "daisy", "berry-basket", "shortcake"],
  mango: ["mango", "mango-leaf", "mango-slice", "mango-glass"],
};
// Big and varied: the fruit itself, a leaf or flower, and a treat made from it.
const FRUIT_SPOTS = [[0, 5, 14, 120, 0], [1, 70, 18, 100, 2], [2, 8, 40, 96, 1], [0, 66, 44, 124, 3], [3, 30, 56, 104, 2],
                     [1, 4, 70, 100, 1], [0, 70, 76, 116, 2], [2, 38, 84, 96, 3], [3, 84, 62, 88, 1]];

export default function GameBackdrop({ world, dark, animations }) {
  const reduce = useReducedMotion();
  const moving = animations !== "off" && !reduce;
  const lively = animations === "lively";
  const speed = lively ? 1 : 0.6;
  const family = world.family;
  const variant = world.variant || family;

  let decor = null;
  if (family === "sky") {
    decor = (
      <>
        {dark ? <span className="moon" /> : <span className="sun" />}
        {dark && <Stars />}
        <Cloud cls="c1" /><Cloud cls="c2" /><Cloud cls="c3" />
        {moving && (
          <motion.div className="bg-flyer" style={{ top: 190 }} initial={{ x: "-20%" }} animate={{ x: "120vw" }}
            transition={{ duration: lively ? 14 : 26, repeat: Infinity, ease: "linear", repeatDelay: 4 }}>
            <Lottie src={`${ANIM_BASE}bird.json`} loop autoplay speed={speed} />
          </motion.div>
        )}
      </>
    );
  } else if (family === "space") {
    decor = (
      <>
        <span className="nebula" />
        {dark && <span className="galaxy"><span className="galaxy-arms" /><span className="galaxy-core" /></span>}
        <Stars />
        {dark && <span className="stars-dense" />}
        <span className="space-planet" />
        <span className={dark ? "moon" : "space-moon"} />
        {moving && (
          <motion.div className="bg-flyer" style={{ top: 140 }} initial={{ x: "-25%" }} animate={{ x: "125vw" }}
            transition={{ duration: lively ? 12 : 22, repeat: Infinity, ease: "linear", repeatDelay: 6 }}>
            <Lottie src={`${ANIM_BASE}comet.json`} loop autoplay speed={speed} />
          </motion.div>
        )}
      </>
    );
  } else if (family === "animals") {
    decor = (
      <>
        {variant === "cat" && (
          // A window with the sky outside: day or night to match light or dark mode.
          <svg className="scene-window" viewBox="0 0 120 150" aria-hidden="true">
            <rect x="6" y="6" width="108" height="138" rx="8" className="win-frame" />
            <rect x="14" y="14" width="92" height="122" rx="4" className="win-sky" />
            {dark ? <circle cx="78" cy="42" r="14" className="win-moon" /> : <circle cx="78" cy="42" r="14" className="win-sun" />}
            {dark && <><circle cx="34" cy="36" r="2" fill="#fff" /><circle cx="50" cy="70" r="2" fill="#fff" /><circle cx="86" cy="96" r="2" fill="#fff" /></>}
            <path d="M60 14 V136 M14 76 H106" className="win-bar" />
          </svg>
        )}
        {variant === "dog" && (
          <>
            <svg className="scene-hills" viewBox="0 0 400 120" preserveAspectRatio="none" aria-hidden="true">
              <ellipse cx="90" cy="130" rx="190" ry="70" className="hill-a" />
              <ellipse cx="320" cy="140" rx="200" ry="70" className="hill-b" />
            </svg>
            <svg className="scene-fence" viewBox="0 0 400 100" preserveAspectRatio="none" aria-hidden="true">
              <path d={FENCE} className="fence" />
            </svg>
          </>
        )}
        {variant === "fox" && (
          <svg className="scene-pines" viewBox="0 0 412 120" preserveAspectRatio="none" aria-hidden="true">
            <path d={PINES} className="pine" />
          </svg>
        )}
        {variant === "fox" && <FallingLeaves moving={moving} />}
        <Scatter spots={variant === "cat" ? CAT : variant === "dog" ? DOG : FOX} moving={moving} />
        <img src={art(`${variant}-face`)} alt="" className="decor-img big-face" />
      </>
    );
  } else if (family === "fruits") {
    const ids = FRUIT[variant] || FRUIT.apple;
    decor = <Scatter spots={FRUIT_SPOTS.map(([k, ...rest]) => [ids[k], ...rest])} moving={moving} cls="fruit-decor" />;
  }

  return (
    <div className={`game-backdrop ${dark ? "dark" : "light"}`} data-world={family} data-variant={variant}
      data-anim={moving ? animations : "off"} aria-hidden="true">
      {decor}
    </div>
  );
}
