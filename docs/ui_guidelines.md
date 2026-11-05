# UI guidelines for Carryover

Rules for every screen a resident sees (Role C, and Role E for the demo). Each rule says why, with its source. Full references are in `docs/sources.md`. The team's shared copy, with a prompt to paste into an AI tool, is the "Carryover: UI Guide for the Screen Builder" doc. Keep the two the same.

Labels: **COGA** (W3C), **Hassell** (Hassell Inclusion & National Autistic Society 2026), **Home Office** (UK Home Office 2016), **Research** (published study), **Ours** (our choice, with the reason).

## Data rule

All step text comes from `backend/data/tasks/*.json`. The help level for each step comes from `today.py`. The screens never hard-code step text and never decide the help level.

## The rules

| # | Rule | On screen | Why (source) |
| --- | --- | --- | --- |
| 1 | One step at a time, same layout every time | One step per screen. Done, Help with this step, Repeat, Take a break always in the same place | COGA; Hassell; Home Office |
| 2 | Show only what's needed | The full step sentence (no short names: they can lose meaning, like "Stir halfway" losing "if the package says so"). Small steps and tips only when opened or when today's level says so. "See all steps" one tap away | COGA; Hassell; Research: Grynszpan et al. 2008 |
| 3 | Plain, literal words | Short sentences, no idioms, about 7th-grade reading level. Use task file text as is | Hassell; Home Office; Research: Barnard-Brak et al. 2023 |
| 4 | Buttons say what they do, with text | Every icon has a text label. Large tap targets | Home Office; Hassell; WCAG 2.2 |
| 5 | Familiar patterns | Normal controls, no new gestures | COGA |
| 6 | Calm colors, readable text | Soft background, no bright or clashing colors, WCAG AA contrast, never color alone | Hassell; Home Office; WCAG 2.2 |
| 7 | The person can change how it looks | Text size, font, colors, dark mode, pictures on/off | Hassell; COGA |
| 8 | Nothing moves or plays by itself | No autoplay, flashing, bouncing or confetti. Read-aloud only if turned on | Hassell |
| 9 | Pictures and video only when they help | Each step's `picture` (our own SVGs in `frontend/public/img/`) shows the action. Under device pictures: "Your microwave may look different." `video` (short point-of-view clip, free license, credited in ATTRIBUTION.md) plays only when tapped. Follows the pictures on/off setting. No decorative or childish images | Hassell; Research: Aljehany & Bennett 2019; 2022 review of video on handheld devices; point-of-view video review; Ours: a different microwave can confuse (Smith 1995) |
| 10 | No time pressure | No countdowns or timeouts. Help offered after a wait, never forced. Breaks save the place | Hassell; COGA; Ours |
| 11 | Don't make people remember | "Step 3 of 7"; "You were on: …" after a break. Start screen always has "Quick look at all steps" next to Start. If rusty, ask first: "It's been a while since you did this. Want a quick look at all the steps first?" (Yes, show me / No, let's start); log `refresher_answer` | COGA; Research: Buckle et al. 2021; Fuller & Fienup 2018 (skills can fade); Wehmeyer & Abery 2013 (the person chooses) |
| 12 | Easy to fix mistakes | "Tapped Done by mistake? Go back" on every step | COGA |
| 13 | Help comes to the person | After a wait the app asks "Want help with this step?" (fading rules). Never on waiting steps (`wait: true`). At Most help, small steps appear by themselves. Asking is always one tap ("Help with this step") | Research: Grynszpan et al. 2008; MacDuff et al. 2001 |
| 14 | Human help is easy to reach | "Ask [support person]" on every step; AI hands off when unsure | COGA; safety.md |
| 15 | The person decides | Ask before less help; person picks support person, sharing (off by default) and breaks | Research: Wehmeyer & Abery 2013; Wehmeyer 1999; Shogren et al. 2015; Wehmeyer 2020 |
| 16 | Asking for help is never bad | No red, no "wrong," no score drop | Ours |
| 17 | Test with autistic users | Pilot (roadmap) | COGA; Hassell; Research: Nicolaidis et al. 2019; Raymaker et al. 2019 |
| 18 | Ask preferences first, briefly | First-time setup: at most 4 questions with pictures (what do you love, Game or Normal after trying both, sound volume, which hand), Skip uses calm defaults. Other questions come in the moment: the task's `first_time_question` and "Can you do these?" the first time a task opens; sound type and animations the first time one would play. A support person may sit with them, but the resident taps | First Place (Nov 4); COGA; Hassell; definitions.json `first_time_setup` |
| 19 | Teach the base skill when needed | If a step needs a base skill the person said "Not sure" about, or they stay stuck at Most help 2 sessions, show that skill card before the step. Cards fade like steps | First Place (Nov 4); definitions.json `skill_cards` |
| 20 | Game mode is the person's choice | Normal mode: no points, stars or game. Game mode (opt-in, switch any time): a world themed on their interests that opens as they learn, next area outlined ahead of time, milestones, unlockables. Rewards never depend on using less help; interest content is never taken away. Sound: Off / Very soft / Soft / Normal; animations: Off / Calm / Lively. No milestone for doing a step "on your own" (it could make someone avoid asking for help) | First Place (Nov 4); Research: Grove et al. 2018 (special interests); Lee et al. 2022 (gamified app, autistic adults); Deci, Koestner & Ryan 1999 (why it's opt-in and never tied to less help) |

| 21 | The person picks the reading voice | Read-aloud uses a voice they pick from the voices already on their device (free, offline), and a speed (Slow / Normal). Offered when read-aloud is first turned on. Paid voices (e.g. ElevenLabs) are roadmap only | Hassell; Ours: privacy and cost |

## Game mode (prototype)

To be built by C and E (a rough prototype exists as a reference, not in the repo). Rules come from `definitions.json` `game_mode`.

| Rule | What it means on screen |
| --- | --- |
| Opt-in | People try Game and Normal at setup, then pick. Switch any time. Normal mode shows no game at all |
| Themed on their interests | The world uses their interests (trains, space, nature, animals, music, cooking, games, cities, sports, art; typed ones get "Your town"). Generic only: no brands or known characters |
| Opens as they learn | A new area every 2 tasks done. The next area shows as an outline: "Opens after 2 more meals". Hidden only if they turn on "Surprise me" |
| Milestones | First task done; a task done 5 times; a skill card no longer needed. Shown only after they happen |
| Never punish help | Rewards come from doing tasks, never from using less help. Asking for help never costs anything. Interest content is never taken away |
| Their settings | Sound volume Off / Very soft / Soft / Normal; sound type Chime / Nature / Theme; animations Off / Calm / Lively; asked the first time one would play. Respects reduced-motion |

**Free add-ons to make it look more like a game (optional):**

- [Kenney.nl](https://kenney.nl/assets): free game art (icons, tiles, vehicles, nature, space), CC0. Still list it in ATTRIBUTION.md.
- [LottieFiles](https://lottiefiles.com): small animations for celebrations. Check each one's license; pick calm ones; follow the animations setting.
- Sounds need no add-on: they're made in code (Web Audio).

## Help levels on screen

| Level | Shows | Source |
| --- | --- | --- |
| Skill card | Before the step: a 2–4 step card that teaches the base skill (`backend/data/skills/`) | First Place (Nov 4) |
| Most help (split) | Step plus small steps, shown one at a time ("Show next small step (2 of 4)"), appearing by themselves | MacDuff et al. 2001; Rule 3 needs one at a time to learn which small steps each person needs |
| Some help (mode `hint`) | The full step sentence only; small steps one tap away | MacDuff et al. 2001 |
| No help (hide) | Folded into "Next: …"; one tap to open | MacDuff et al. 2001 |
| Hint wait | Offer help at 1/4, 1/2, 3/4 of `long_pause_seconds` | MacDuff et al. 2001 (time delay); fractions ours |
| Phone pay | Only the person's phone type from `substeps_by_phone` | Apple; Google |
| Tips | Under a "Tips" fold | COGA; Hassell |

Log events only (step shown, done, help opened, hint shown, paused, resumed, skipped, check answer). Never log what was bought, the cost, or what was eaten.

## Praise, breaks, safety, photos

| Part | Do this | Why |
| --- | --- | --- |
| Praise | Normal mode: short and factual ("Step 4 done"), no points, streaks, badges or stars. Game mode (opt-in): milestones and calm celebrations by their settings | Research: Deci, Koestner & Ryan 1999; Grove et al. 2018 |
| Praise style | Calm (default) / Cheerful / Off | Research: Weyman & Sy 2018 |
| Take a break | On every step; saves place; break time never counts as stuck | Decided rule; COGA |
| Break note | After 120 minutes away from a meal, show `break_note` | Official: USDA 2-hour rule |
| Safety card | Microwave list, first time and step 1, exact task file text | Official: USDA, FDA, Clemson |
| Caution | If a step has a `safety` field, always show it as a **CAUTION** line on that step at every help level, even when folded. No tap needed. heat_meal s5–s7 (oven mitts, steam, hot spots: "may be hot"); buying: PIN, passcode, Place Order once | First Place (Nov 4); Research: Jones et al. 1997 |
| Photo question | Camera only when tapped; say it goes to an AI service; delete after; no people | Ours; safety.md |
| Never photograph | Bank app, card, receipt, checkout page | Ours |
| AI not sure | "I'm not sure. Please ask [support person]." | Research: Xiong et al. 2024; Li et al. 2023; Geifman & El-Yaniv 2017 |
| Money screens | No balance, no card number or PIN, no advice on what to buy. Pictures show generic readers and screens only | Ours |
| New device | First time a task opens, ask its `first_time_question` ("Is this a microwave you've used before?"). No or Not sure: start at Most help | First Place (Nov 4); Smith 1995 |

## Don't

- In Normal mode: points, streaks, badges, stars. In any mode: confetti bursts, "Great job!!" stickers, rewards for using less help
- Timers, countdowns, timeouts
- Bright, flashing or moving things; autoplay
- Cartoon or childish style
- Red or "wrong" when help is used
- Step text in screen code
- Real resident, card or bank data; photos of residents
- API keys in the code (use `.env`)
