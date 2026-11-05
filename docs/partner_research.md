# Partner research: First Place AZ

> DRAFT for Hima to check and edit. Wording below is paraphrased from our notes, not exact quotes. Add exact quotes only with the person's OK and how they want to be named.

First Place AZ supports autistic adults moving toward independent living. We met with staff (not residents). Residents were not interviewed, and no resident data was collected.

## Meeting 1 (Nov 3): how tasks are taught now

| What we heard | What we did because of it |
| --- | --- |
| Staff teach daily tasks with AFLS and other task analyses: the same steps for everyone | Carryover learns where each person gets stuck and changes help per step, per person |
| Help that adapts to each person would be useful | Prompt fading engine: help levels per step that fade, and come back after struggling |
| They'd like text, voice and animations, and text, voice or video input | Read-aloud, "Ask for help" by typing, speaking or photo (Role D), pictures per step |

## Meeting 2 (Nov 4): feedback on the design

| What we heard | What we changed | Where |
| --- | --- | --- |
| Show cautions without having to click | Caution sentences now always show on the step, at every help level | Task files `safety`; safety.md; UI guide |
| A photo and a video of how each step is done would help | Each step has a picture of the action (our own drawings) and a slot for a short point-of-view video. Research: video prompting works for daily living skills (Aljehany & Bennett 2019; 2022 review) | Task files `picture`, `video`; `frontend/public/img/` |
| If it feels formal they may not use it: gamify it | Optional Game mode: a world themed on their interests that opens as they learn skills, milestones, unlockables. Normal mode stays available | definitions.json `game_mode`; Game components |
| Sudden sounds or surprises may bother people: ask preferences first | Short first-time setup (at most 4 questions, Skip allowed): what they love, Game or Normal after trying both, sound volume (Off / Very soft / Soft / Normal), which hand. Next game area is shown ahead of time unless they turn on "Surprise me" | definitions.json `first_time_setup` |
| Problem solving is a big hurdle: clear steps don't help if someone lacks the base skill the steps assume | Each step lists its base skills. The person is asked "Can you do these?" the first time; "Not sure", or staying stuck at Most help, shows a short skill card first. Cards fade like steps | `backend/data/skills/`; task files `base_skills`; definitions.json `skill_cards` |
| Skills learned at First Place should carry over to living on their own | Checks are done by the resident, not staff. Roadmap: photos of each person's own devices, practice tasks for base skills | Roadmap doc |
| New or different devices (two different microwaves) are hard | Each task asks the first time: "Is this a microwave you've used before?" No or Not sure starts at Most help | Task files `first_time_question` |
| Some people need much more detail (peanut butter: which hand holds the jar, which way to turn the lid) | Help levels already differ per person. New: an AI "extra detail" option that splits a small step down to which hand and which direction, using their right/left hand setting. Staff approve before anyone sees it | Role D (AI split); setup "Which hand" |

## Still to add

- [ ] Exact quotes (with permission) and how to name the staff member
- [ ] Their answers about the wait time before help is offered (about 10 seconds now) and showing small steps one at a time
- [ ] Whether a small pilot later is possible
