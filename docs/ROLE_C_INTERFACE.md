Historical note: this was the Role C handoff written on Nov 4, while the screens were being built. For how the resident app works now, see the Role C (Krutika) section of README.md.

# Role C interface and design notes

Role C reads `fade.build_view()` (Role B) through `logic/today.py`, which adds the task file fields the view leaves out. Screens never decide a help level and never hold step text.

## Out of today.py: `build_today(person_id, task_id, week)`

Everything in `fade.build_view()` (see `backend/data/sample_today.json`), plus per step `number`, `total` and, when the task file has them, `picture`, `video`, `safety`, `base_skills`, `substeps_by_phone`, `part`; and per task `first_time_question` and `safety_card_content`.

## Routes: `api/resident_routes.py`

`GET /tasks`, `GET /today`, `POST /event` (one Format 2 row, validated in `logic/event_log.py`), `GET /setup` (first-time questions from definitions.json), `GET /skills/{id}` (a skill card), `GET /game?person_id=` (game rules from definitions.json plus tasks done and milestones reached, counted from the event log).

## Screens (frontend/src/screens, mounted by pages/Resident.jsx)

Setup (4 questions, Skip, try-both preview), first-open questions (device, skills), task list, start (refresher, "still want this task?"), safety card, skill card, step, all steps, break, done (check questions, "less help next time?", Game extras), My world (Game only), settings (looks, 4 colour palettes, reading voice and speed, game and sounds, support person, sharing, phone type, redo setup).

## Design assumptions to review (Role C chose these; please challenge them)

1. Game world: 5 areas per world (`AREAS_PER_WORLD`, `lib/game.js`), named "<Interest>: area N". Theme is the first interest; a typed one becomes "Your town". No art yet (Kenney assets are optional).
2. Game celebration is one calm line, plus a sound and animation only as the settings allow. The first time each would play, the person is asked which they want. "A skill card no longer needed" is counted from `skill_card_not_needed` events, which nothing logs yet.
3. "Opens after N more tasks" uses the word "tasks" because the definitions say "meals" but the world covers every task.
4. Setup pictures are emoji next to the words, as placeholders. The "try both" preview is a sample card for each style.
5. The picture caption "Your microwave may look different." shows when a picture has `device: true` or its alt text names a microwave. The task files do not mark device pictures yet (Role A could add `device: true`).
6. Video: the screen accepts a file name, address or `{file, credit}` and plays only on tap. Every task has `video: null` today.
7. "Still want this task?" is asked once per person and task (remembered in the browser). The answer is logged as `end_question` with no step_id. Role B: say if you want another event.
8. Reading voice: only voices already on the device that work offline.
9. Colours: Soft light, Calm neutral, Cool blue-green, Dark. All pass WCAG AA (text 9.6 or more on its background). Based on the AASPIRE guidelines (Raymaker et al., 2019); the exact values are ours.
10. "Which hand" and the setup interests are saved but only the interests are used (Game theme). `setup_answer` is not logged because the event log requires a task.

## Open points

- `POST /event` writes to `data/live/events.csv`, the same file fade.py reads.
- Settings (display, support person, sharing) live in the browser. Role E's staff screen cannot read "share with staff" yet.
- Not browser-tested at the time of writing: setup, safety card, skill cards, Game screens, palettes, voice, video, caption, "still want this task?".
