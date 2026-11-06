// One icon set for the whole resident app (Lucide). Every icon sits next to its words and is
// hidden from screen readers, so the words are what gets read.
import {
  ArrowLeft, Building2, Check, ChevronRight, Earth, ChefHat, Cloud, Gamepad2, House, Leaf, List, ListChecks, Music, Palette,
  Pause, PawPrint, Play, Rocket, RotateCcw, Settings, TrainFront, Trophy, Volume, Volume1, Volume2, VolumeX,
} from "lucide-react";

const props = { size: "1.25em", strokeWidth: 2, "aria-hidden": true, focusable: false };

export const Icon = {
  back: () => <ArrowLeft {...props} />,
  home: () => <House {...props} />,
  speaker: () => <Volume2 {...props} />,
  tasks: () => <ListChecks {...props} />,
  world: () => <Earth {...props} />,
  check: () => <Check {...props} strokeWidth={3} />,
  settings: () => <Settings {...props} />,
  open: () => <ChevronRight {...props} className="chevron" />,
  play: () => <Play {...props} />,
  pause: () => <Pause {...props} />,
  replay: () => <RotateCcw {...props} />,
};

// Pictures for the setup answers (ids come from definitions.json).
// A plain open hand, drawn as an outline like the other icons. Right hand: thumb on the left,
// palm toward you. The left hand is the same drawing mirrored.
const HAND_PATH = "M23 5.5V20c0 2.2-1.8 4-4 4h-7.3c-1.08 0-2.1-.43-2.85-1.19L1 14.83s1.26-1.23 1.3-1.25c.22-.19.49-.29.79-.29.22 0 .42.06.6.16.04.01 4.31 2.46 4.31 2.46V4c0-.83.67-1.5 1.5-1.5S11 3.17 11 4v7h1V1.5c0-.83.67-1.5 1.5-1.5S15 .67 15 1.5V11h1V2.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5V11h1V5.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5z";
const HandDrawing = ({ flip }) => (
  <svg width="1.25em" height="1.25em" viewBox="-1 -1 26 26" fill="none" stroke="currentColor" strokeWidth="1.7"
       strokeLinejoin="round" strokeLinecap="round" aria-hidden="true" focusable="false"
       style={flip ? { transform: "scaleX(-1)" } : undefined}>
    <path d={HAND_PATH} />
  </svg>
);
const RIGHT = () => <HandDrawing />;
const LEFT = () => <HandDrawing flip />;
export const ANSWER_ICON = {
  sky: Cloud,
  trains: TrainFront, space: Rocket, nature: Leaf, animals: PawPrint, music: Music, cooking: ChefHat,
  games: Gamepad2, cities: Building2, sports: Trophy, art: Palette,
  game: Gamepad2, normal: List,
  off: VolumeX, very_soft: Volume, soft: Volume1, normal_sound: Volume2,
  right: RIGHT, left: LEFT,
  both: () => <span className="icon-pair"><LEFT /><RIGHT /></span>,
};

export function AnswerIcon({ id }) {
  const C = ANSWER_ICON[id];
  return C ? <span className="pic"><C {...props} /></span> : null;
}
