# UI guidelines for Carryover

Rules for every screen a resident sees (Role C, and Role E for the demo). Each rule says why, with its source. Full references are in `docs/sources.md`. The team's shared copy, with a prompt to paste into an AI tool, is the "Carryover: UI Guide for the Screen Builder" doc. Keep the two the same.

Labels: **COGA** (W3C), **Hassell** (Hassell Inclusion & National Autistic Society 2026), **Home Office** (UK Home Office 2016), **Research** (published study), **Ours** (our choice, with the reason).

## Data rule

All step text comes from `backend/data/tasks/*.json`. The help level for each step comes from `today.py`. The screens never hard-code step text and never decide the help level.

## The rules

| # | Rule | On screen | Why (source) |
| --- | --- | --- | --- |
| 1 | One step at a time, same layout every time | One step per screen. Done, Help with this step, Repeat, Take a break always in the same place | COGA; Hassell; Home Office |
| 2 | Show only what's needed | Short name first. Small steps and tips only when opened or when today's level says so. "See all steps" one tap away | COGA; Hassell; Research: Grynszpan et al. 2008 |
| 3 | Plain, literal words | Short sentences, no idioms, about 7th-grade reading level. Use task file text as is | Hassell; Home Office; Research: Barnard-Brak et al. 2023 |
| 4 | Buttons say what they do, with text | Every icon has a text label. Large tap targets | Home Office; Hassell; WCAG 2.2 |
| 5 | Familiar patterns | Normal controls, no new gestures | COGA |
| 6 | Calm colors, readable text | Soft background, no bright or clashing colors, WCAG AA contrast, never color alone | Hassell; Home Office; WCAG 2.2 |
| 7 | The person can change how it looks | Text size, font, colors, dark mode, pictures on/off | Hassell; COGA |
| 8 | Nothing moves or plays by itself | No autoplay, flashing, bouncing or confetti. Read-aloud only if turned on | Hassell |
| 9 | Pictures only when they help | Pictures that show the action; no decorative or childish images | Hassell; Ours: a different microwave's picture can confuse (Smith 1995) |
| 10 | No time pressure | No countdowns or timeouts. Help offered after a wait, never forced. Breaks save the place | Hassell; COGA; Ours |
| 11 | Don't make people remember | "Step 3 of 7"; "You were on: …" after a break. Start screen always has "Quick look at all steps" next to Start. If rusty, ask first: "It's been a while since you did this. Want a quick look at all the steps first?" (Yes, show me / No, let's start); log `refresher_answer` | COGA; Research: Buckle et al. 2021; Fuller & Fienup 2018 (skills can fade); Wehmeyer & Abery 2013 (the person chooses) |
| 12 | Easy to fix mistakes | "Tapped Done by mistake? Go back" on every step | COGA |
| 13 | Help comes to the person | After a wait the hint or small steps appear (fading rules). Asking is always one tap | Research: Grynszpan et al. 2008; MacDuff et al. 2001 |
| 14 | Human help is easy to reach | "Ask [support person]" on every step; AI hands off when unsure | COGA; safety.md |
| 15 | The person decides | Ask before less help; person picks support person, sharing (off by default) and breaks | Research: Wehmeyer & Abery 2013; Wehmeyer 1999; Shogren et al. 2015; Wehmeyer 2020 |
| 16 | Asking for help is never bad | No red, no "wrong," no score drop | Ours |
| 17 | Test with autistic users | Pilot (roadmap) | COGA; Hassell; Research: Nicolaidis et al. 2019; Raymaker et al. 2019 |

## Help levels on screen

| Level | Shows | Source |
| --- | --- | --- |
| Most help (split) | Step plus small steps, open | MacDuff et al. 2001 |
| Some help (hint) | Short name only; small steps one tap away | MacDuff et al. 2001 |
| No help (hide) | Folded into "Next: …"; one tap to open | MacDuff et al. 2001 |
| Hint wait | Offer help at 1/4, 1/2, 3/4 of `long_pause_seconds` | MacDuff et al. 2001 (time delay); fractions ours |
| Phone pay | Only the person's phone type from `substeps_by_phone` | Apple; Google |
| Tips | Under a "Tips" fold | COGA; Hassell |

Log events only (step shown, done, help opened, hint shown, paused, resumed, skipped, check answer). Never log what was bought, the cost, or what was eaten.

## Praise, breaks, safety, photos

| Part | Do this | Why |
| --- | --- | --- |
| Praise | Short and factual ("Step 4 done"). No points, streaks, badges, stars, confetti | Research: Deci, Koestner & Ryan 1999 |
| Praise style | Calm (default) / Cheerful / Off | Research: Weyman & Sy 2018 |
| Take a break | On every step; saves place; break time never counts as stuck | Decided rule; COGA |
| Break note | After 120 minutes away from a meal, show `break_note` | Official: USDA 2-hour rule |
| Safety card | Microwave list, first time and step 1, exact task file text | Official: USDA, FDA, Clemson |
| Photo question | Camera only when tapped; say it goes to an AI service; delete after; no people | Ours; safety.md |
| Never photograph | Bank app, card, receipt, checkout page | Ours |
| AI not sure | "I'm not sure. Please ask [support person]." | Research: Xiong et al. 2024; Li et al. 2023; Geifman & El-Yaniv 2017 |
| Money screens | No balance, no card number or PIN, no advice on what to buy | Ours |

## Don't

- Points, streaks, badges, confetti, "Great job!!" stickers
- Timers, countdowns, timeouts
- Bright, flashing or moving things; autoplay
- Cartoon or childish style
- Red or "wrong" when help is used
- Step text in screen code
- Real resident, card or bank data; photos of residents
- API keys in the code (use `.env`)
