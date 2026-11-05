import { motion, useReducedMotion } from "framer-motion";

const STILL = `${import.meta.env.BASE_URL}game/`;

// The companion animal in the Animals worlds (dog, cat or fox). A simple, calm illustration, not a
// cartoon. When the person picks a reward, the animal has it: in its mouth, on its collar or in
// front of it, and looks content. Motion is slow (a tail that sways, a slow blink, quiet
// breathing) and stops when Animations is Off or motion is reduced. Nothing here depends on how
// much help anyone used.

const PALETTE = {
  dog: { body: "#c9955a", light: "#efd9b8", ear: "#98693a", dark: "#2f2a26", tail: "#c9955a" },
  cat: { body: "#8f9aa8", light: "#dde2e8", ear: "#e8b4be", dark: "#2b2f35", tail: "#8f9aa8" },
  fox: { body: "#d9733a", light: "#f8eddc", ear: "#5a3a2a", dark: "#2f2420", tail: "#d9733a" },
};

// Where each kind of attachment sits, in the 240 x 230 picture.
const SPOT = {
  mouth: { x: 120, y: 114, size: 62 },
  front: { x: 120, y: 206, size: 56 },
  collar: { x: 120, y: 142, size: 30 },
};

function Head({ animal, p, happy, blink }) {
  const eyes = happy ? (
    <>
      <path d="M94 78 q9 -9 18 0" fill="none" stroke={p.dark} strokeWidth="3.5" strokeLinecap="round" />
      <path d="M128 78 q9 -9 18 0" fill="none" stroke={p.dark} strokeWidth="3.5" strokeLinecap="round" />
    </>
  ) : (
    <motion.g animate={blink} style={{ transformOrigin: "120px 78px" }}>
      <ellipse cx="104" cy="78" rx="4.5" ry="5.5" fill={p.dark} />
      <ellipse cx="136" cy="78" rx="4.5" ry="5.5" fill={p.dark} />
    </motion.g>
  );
  if (animal === "cat") {
    return (
      <g>
        <polygon points="76,60 80,16 108,44" fill={p.body} /><polygon points="164,60 160,16 132,44" fill={p.body} />
        <polygon points="84,52 85,28 100,44" fill={p.ear} /><polygon points="156,52 155,28 140,44" fill={p.ear} />
        <ellipse cx="120" cy="84" rx="48" ry="42" fill={p.body} />
        <ellipse cx="120" cy="100" rx="24" ry="17" fill={p.light} />
        {eyes}
        <polygon points="114,92 126,92 120,100" fill={p.ear} />
        <path d="M120 100 v5 M120 105 q-8 6 -14 1 M120 105 q8 6 14 1" fill="none" stroke={p.dark} strokeWidth="2.2" strokeLinecap="round" />
        <path d="M74 96 h-22 M74 104 l-20 6 M166 96 h22 M166 104 l20 6" stroke={p.light} strokeWidth="2" strokeLinecap="round" />
      </g>
    );
  }
  if (animal === "fox") {
    return (
      <g>
        <polygon points="72,62 70,10 108,42" fill={p.body} /><polygon points="168,62 170,10 132,42" fill={p.body} />
        <polygon points="80,54 79,26 98,42" fill={p.ear} /><polygon points="160,54 161,26 142,42" fill={p.ear} />
        <ellipse cx="120" cy="84" rx="48" ry="40" fill={p.body} />
        <polygon points="76,92 120,128 164,92 120,76" fill={p.light} />
        {eyes}
        <ellipse cx="120" cy="108" rx="8" ry="5.5" fill={p.dark} />
        <path d="M120 113 v4 M120 117 q-8 6 -14 1 M120 117 q8 6 14 1" fill="none" stroke={p.dark} strokeWidth="2.2" strokeLinecap="round" />
      </g>
    );
  }
  return (
    <g>
      <ellipse cx="74" cy="82" rx="15" ry="32" fill={p.ear} transform="rotate(16 74 82)" />
      <ellipse cx="166" cy="82" rx="15" ry="32" fill={p.ear} transform="rotate(-16 166 82)" />
      <ellipse cx="120" cy="84" rx="46" ry="42" fill={p.body} />
      <ellipse cx="120" cy="102" rx="27" ry="20" fill={p.light} />
      {eyes}
      <ellipse cx="120" cy="93" rx="9.5" ry="6.5" fill={p.dark} />
      <path d="M120 99 v6 M120 105 q-8 7 -15 2 M120 105 q8 7 15 2" fill="none" stroke={p.dark} strokeWidth="2.4" strokeLinecap="round" />
    </g>
  );
}

function Tail({ animal, p, wag }) {
  const turn = { transformOrigin: "176px 168px" };
  if (animal === "cat") {
    return <motion.path d="M174 176 C214 170 224 134 200 118" fill="none" stroke={p.tail} strokeWidth="15" strokeLinecap="round" animate={wag} style={turn} />;
  }
  if (animal === "fox") {
    return (
      <motion.g animate={wag} style={turn}>
        <ellipse cx="206" cy="146" rx="22" ry="44" fill={p.tail} transform="rotate(34 206 146)" />
        <ellipse cx="226" cy="116" rx="11" ry="17" fill={p.light} transform="rotate(34 226 116)" />
      </motion.g>
    );
  }
  return <motion.ellipse cx="196" cy="150" rx="12" ry="34" fill={p.tail} transform="rotate(28 196 150)" animate={wag} style={turn} />;
}

// Spots on the ground, beside the animal, for the rewards it was given earlier.
const GROUND = [{ x: 38, y: 202 }, { x: 204, y: 208 }, { x: 14, y: 166 }, { x: 226, y: 190 }];

export default function Companion({ animal, holding, item, moving, lively, earlier = [], earlierItems = {} }) {
  const reduce = useReducedMotion();
  const live = moving && !reduce;
  const p = PALETTE[animal] || PALETTE.dog;
  const happy = Boolean(holding);
  const slow = lively ? 0.7 : 1; // seconds are multiplied: lively is a little quicker, never fast

  const wag = live ? { rotate: [0, 9, 0, -5, 0] } : undefined;
  const blink = live ? { scaleY: [1, 1, 0.1, 1, 1] } : undefined;
  const breathe = live ? { scaleY: [1, 1.012, 1] } : undefined;
  const spot = item && SPOT[item.attach || "mouth"];
  const alt = holding
    ? `Your ${animal} looks content and has ${item ? item.name.toLowerCase() : "a reward"}.`
    : `Your ${animal} is waiting for its first reward.`;

  return (
    <svg className="companion" viewBox="0 0 240 230" role="img" aria-label={alt} data-holding={holding || ""} data-animal={animal}>
      <ellipse cx="120" cy="222" rx="74" ry="7" fill="rgba(0,0,0,0.12)" />
      {earlier.slice(0, GROUND.length).map((id, i) => (
        <image key={id} href={`${STILL}${id}.svg`} width="44" height="44" x={GROUND[i].x - 22} y={GROUND[i].y - 22}>
          <title>{earlierItems[id] ? earlierItems[id].name : id}</title>
        </image>
      ))}
      <Tail animal={animal} p={p} wag={wag && { ...wag, transition: { duration: 5 * slow, repeat: Infinity, ease: "easeInOut" } }} />
      <motion.g animate={breathe} transition={{ duration: 7 * slow, repeat: Infinity, ease: "easeInOut" }} style={{ transformOrigin: "120px 210px" }}>
        <ellipse cx="120" cy="156" rx="58" ry="52" fill={p.body} />
        <ellipse cx="120" cy="164" rx="30" ry="34" fill={p.light} />
        <ellipse cx="96" cy="196" rx="15" ry="22" fill={p.light} /><ellipse cx="144" cy="196" rx="15" ry="22" fill={p.light} />
      </motion.g>
      <motion.g animate={live ? { rotate: [0, 2.5, 0, -2.5, 0] } : undefined}
        transition={{ duration: 9 * slow, repeat: Infinity, ease: "easeInOut" }} style={{ transformOrigin: "120px 130px" }}>
        <Head animal={animal} p={p} happy={happy} blink={blink && { ...blink, transition: { duration: 6 * slow, repeat: Infinity, times: [0, 0.9, 0.93, 0.96, 1] } }} />
      </motion.g>
      {spot && (
        // The reward arrives gently, then stays. A new reward replays this once.
        <motion.image key={holding} href={`${STILL}${holding}.svg`} width={spot.size} height={spot.size}
          x={spot.x - spot.size / 2} y={spot.y - spot.size / 2}
          initial={live ? { opacity: 0, y: 26 } : false} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.6 * slow, ease: "easeOut" }} />
      )}
    </svg>
  );
}
