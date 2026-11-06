// One icon set for the whole resident app (Lucide). Every icon sits next to its words and is
// hidden from screen readers, so the words are what gets read.
import {
  ArrowLeft, Building2, Check, ChevronRight, Earth, ChefHat, Cloud, Gamepad2, Hand, Leaf, List, ListChecks, Music, Palette,
  PawPrint, Rocket, Settings, TrainFront, Trophy, Volume, Volume1, Volume2, VolumeX,
} from "lucide-react";

const props = { size: "1.25em", strokeWidth: 2, "aria-hidden": true, focusable: false };

export const Icon = {
  back: () => <ArrowLeft {...props} />,
  speaker: () => <Volume2 {...props} />,
  tasks: () => <ListChecks {...props} />,
  world: () => <Earth {...props} />,
  check: () => <Check {...props} strokeWidth={3} />,
  settings: () => <Settings {...props} />,
  open: () => <ChevronRight {...props} className="chevron" />,
};

// Pictures for the setup answers (ids come from definitions.json).
const LEFT = (p) => <Hand {...props} {...p} style={{ transform: "scaleX(-1)" }} />;
export const ANSWER_ICON = {
  sky: Cloud,
  trains: TrainFront, space: Rocket, nature: Leaf, animals: PawPrint, music: Music, cooking: ChefHat,
  games: Gamepad2, cities: Building2, sports: Trophy, art: Palette,
  game: Gamepad2, normal: List,
  off: VolumeX, very_soft: Volume, soft: Volume1, normal_sound: Volume2,
  right: Hand, left: LEFT,
  both: () => <span className="icon-pair"><LEFT /><Hand {...props} /></span>,
};

export function AnswerIcon({ id }) {
  const C = ANSWER_ICON[id];
  return C ? <span className="pic"><C {...props} /></span> : null;
}
