# Carryover

**The right amount of help, for each person, on each step.**

Carryover helps autistic adults practice everyday tasks, like heating a meal or buying something, on their own. It shows one step at a time, learns from each person's own use where they get stuck, gives the smallest help that works, and fades it as they improve. If they struggle again, the help comes back. It always asks before reducing help, and safety cautions are always shown.

Built by Team Haven for the North American AI Challenge for Neurodiverse Learning, with First Place AZ as our Challenge Partner (see [docs/partner_research.md](docs/partner_research.md)). Everything runs on simulated residents: there is no real resident, card or bank data.

The code is a React front end and a FastAPI back end. All data is in plain files under `backend/data/`.

## How AI is used

The decisions about help (where someone is stuck, how much help, when to fade) are clear rules on the person's own history, so they can be explained and checked. AI is used where fixed screens can't help:

- **"I'm stuck" helper:** the person types, speaks or takes a photo (for example of their own microwave) and gets one short step back.
- **More detail for people who need it:** staff ask the AI to break a step into smaller steps; a person approves them on the Review page before any resident sees them. AI-drafted skill cards go through the same review.
- **Safety:** risky questions (is it cooked, should I buy this, is this dish microwave safe) are caught by rules in code before the AI answers. Photo safety questions are asked three times and must quote the label; otherwise the helper hands off to a person.

The prompts are in `backend/prompts/` and collected in [docs/prompts.pdf](docs/prompts.pdf). See [docs/responsible_ai.md](docs/responsible_ai.md) for the full rules and limits.

## Team

| Role | Who | What |
| --- | --- | --- |
| A | Hima | Tasks, detection, research and docs |
| B | Mrudula | Event data, the simulator, fading rules and learning |
| C | Krutika | The resident app |
| D | Manaswi | AI help and safety guardrails |
| E | Vaishnavi | Backend setup, fading logic, staff, demo and review pages |

Each role's section below explains its files. [ATTRIBUTION.md](ATTRIBUTION.md) lists libraries, sources and how AI tools were used, by role.

## What is in the repo

| Folder | What is in it |
| --- | --- |
| `backend/api/` | `main.py` and the routes |
| `backend/logic/` | `data_io.py` (reading and writing files), `detect.py` (where someone gets stuck), `fade.py` (help levels and the daily view) |
| `backend/ai/` | The "I'm stuck" help and AI step splitting |
| `backend/sim/` | Makes the fake event history the demo runs on |
| `backend/data/` | Task files, `definitions.json`, skill cards (`skills/`), the event log, the AI steps waiting for review |
| `backend/prompts/` | The prompts sent to the AI model |
| `backend/tests/` | Tests |
| `frontend/src/` | The React app: `screens/` (the resident app), `lib/` (its settings and helpers), `pages/` (Staff, Demo, Review), the demo chart, the "I'm stuck" panel on the Help screen |
| `tools/` | Scripts that draw the step pictures and the game art |
| `docs/` | Research notes, safety rules, UI rules, the architecture diagram |
| `ATTRIBUTION.md` | Libraries, images, sources and how AI tools were used, by role |

See [docs/architecture.md](docs/architecture.md) for how the parts fit together.

## Set up

You need Python 3.11 or newer and Node 18 or newer.

Back end, from the repo root:

```
cd backend
python3 -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate (and use python instead of python3)
pip install -r requirements.txt
cp .env.example .env
```

Open `backend/.env` and fill in your own values. This file is in `.gitignore`, so it never gets committed. See "Choosing the AI provider and model" in the Role D section for what to put there. The tests and everything except the AI helper work without a key.

Front end, in a second terminal from the repo root:

```
cd frontend
npm install
cp .env.example .env
```

## Run

Back end (from `backend/`):

```
uvicorn api.main:app --reload
```

Front end (from `frontend/`):

```
npm run dev
```

Then open http://localhost:5173. The plain address opens the resident app. To open a simulated resident at a given week, add the person and week, for example http://localhost:5173/resident?person=ana&week=5. On Windows PowerShell use `npm.cmd` instead of `npm`. The pages are:

| Page | What it is |
| --- | --- |
| `/resident` | The resident app (phone-sized screens) |
| `/staff` | The staff screen: where each simulated resident gets stuck |
| `/demo` | The demo: pick a resident, move the week, see the real app in a phone frame, "Why this changed", the help chart and a "Help over time" grid |
| `/review` | Approve or edit AI suggested small steps and skill cards before residents see them |

The API docs are at http://localhost:8000/docs.

## Demo data

The demo reads `backend/data/live/events.csv`. To make it again (same result every time):

```
cd backend
python -m sim.simulate --force
```

## Tests

From `backend/`:

```
pytest
```

The tests don't need an API key.

## Keys and secrets

API keys go in `backend/.env` only. Never put them in code, and never commit `.env`. Only `.env.example` (no secrets) is committed.

## More

- [docs/safety.md](docs/safety.md): safety rules
- [docs/ui_guidelines.md](docs/ui_guidelines.md): rules for every resident screen
- [docs/sticking_points.md](docs/sticking_points.md) and [docs/sources.md](docs/sources.md): the research
- [docs/lit_review.md](docs/lit_review.md): the literature review
- [docs/partner_research.md](docs/partner_research.md): what First Place AZ staff told us
- [docs/responsible_ai.md](docs/responsible_ai.md): how the AI is kept safe
- [docs/future_directions.md](docs/future_directions.md): what comes next
- [docs/architecture.md](docs/architecture.md): how the parts fit together
- [ATTRIBUTION.md](ATTRIBUTION.md): libraries, images, sources and how AI tools were used
- Limits: the "Limits" section of [docs/responsible_ai.md](docs/responsible_ai.md) and "What research doesn't answer yet" in [docs/future_directions.md](docs/future_directions.md)

## Role A (Hima): tasks, detection and research

### What the files are
| File | What it holds |
| --- | --- |
| `backend/data/tasks/*.json` | The 4 tasks: Heat a meal, and Buy something (in store with card, in store with phone, online). Each step has its text, small steps, tips, CAUTION line, picture, base skills and timing |
| `backend/data/skills/*.json` | 10 skill cards: one base skill each (like reading the cooking time), 2–4 small steps |
| `backend/data/definitions.json` | Every rule and number the app uses: help levels, fading rules 2–9, check questions, skill cards, first-time setup, Game mode |
| `backend/logic/detect.py` | Finds where someone gets stuck, from the event log |
| `docs/` | Sticking points, safety rules, UI rules, sources, partner research |

### How detect.py works
It reads one person's events for one task, splits them into sessions, and looks at the last 2 sessions. A pattern has to show in both before it counts, so one bad day doesn't change anything. It returns:

| Code | Means |
| --- | --- |
| `cant_start` | Opened the task but didn't get going |
| `stuck_at_step` | A long pause at the same step |
| `missing_step` | Started a step but never finished it, or said "no" to its check question the last 2 times it was asked |
| `rusty_after_gap` | Coming back after a break more than 2× their usual (and at least 14 days) |
| `none` | Nothing found |

It also has `skill_cards_to_show()` (which skill cards to show before which steps) and `steps_with_breaks()` (a flag for staff: computed, not shown on the Staff page yet).

### Adding a new task
Write a new JSON file in `backend/data/tasks/` with the same fields. No code changes needed: detect, fade and the screens read everything from the file.

### Limitations
- The numbers (2 sessions, 14 days, 45-second pause) are our starting points, backed by research on the idea but not the exact values. Staff can change them in definitions.json.
- Check questions only cover steps with no help. Two "no"s give the help back, so the question stops there. A step missed after help returns is caught by the other signals.
- The task steps were checked with First Place staff, but not yet tested with residents.

## Role B (Mrudula): data, fading and learning

### What the modules do

**backend/logic/data_io.py** is the single place the project reads and writes
data. EVENT_COLUMNS here is the one definition of the event log format and
ALL_EVENTS the one list of event names; the Python code imports them rather
than keeping its own copy. It also loads task files and definitions.json.

**backend/sim/simulate.py** writes backend/data/live/events.csv: ten weeks of
usage for nineteen residents across all four tasks. We have no real users, so
the demo runs on generated data.

**backend/logic/fade.py** (shared with Role E) turns a person's event history
into the help level for each step. Written by Vaishnavi Bhairishetty; Rules 2
and 3, the missing_step response and their tests were added by me.

**backend/logic/learn.py** scores how often each help has been tried and has
worked, both for a person and across everyone, and blends the two:
estimate = w * (their rate) + (1 - w) * (everyone's rate), with
w = tried / (tried + 5). A new resident starts from what has worked for
everyone and shifts toward their own history as it builds.

### Data flow

simulate.py -> events.csv -> detect.py -> fade.build_view ->
api/demo_routes.py -> the /demo page. learn.py reads the same events and
writes scores.json; nothing reads scores.json yet (see Limitations).

### Regenerating the data

```
cd backend
python -m sim.simulate --force
python -m logic.learn
```

The seed is fixed, so every run produces an identical file. --force is
required because the app's POST /event will append live taps to the same file
and regenerating would discard them.

### Two rules that keep the demo honest

**Nothing reads the simulator's intentions.** The residents' patterns exist
only inside simulate.py. detect.py works them out from the event log alone,
exactly as it would with real users.

**Nothing can see the future.** The view for week N is built from weeks 1 to
N-1 only. This is enforced in load_events by up_to_week, which refuses to
return later rows, rather than by convention in each caller.

### Limitations

- Help levels are computed per week, not per session. A second session in the
  same week cannot see the first. Fine for a weekly slider; the fix is to
  build the view per session rather than per week.
- Rule 3 learns depth, not selection. Small steps reveal one at a time, so
  the set someone opens is always a run from the start. It learns how far
  into a step a person needs it broken down, not which individual small steps
  they use. It is implemented and tested but does not trigger on the current
  data. Rule 3's trim question is computed in the backend; the Done screen
  does not ask it yet.
- The scores in learn.py are descriptive, not causal. Heavier help shows a
  lower success rate because a step only reaches Most help when someone keeps
  struggling there. That is a selection effect, so the scores are not used to
  choose help.

## Role C (Krutika): the resident app

The phone-sized app a resident uses, in `frontend/src/screens/` and `frontend/src/lib/`, with its backend routes in `backend/api/resident_routes.py`, `backend/logic/today.py` and `backend/logic/event_log.py`.

| Part | What it does |
| --- | --- |
| First-time setup | A few short questions (skippable), then everything can be changed in Settings |
| Task list and start | Pick a task; a short start push, a refresher after a long break, and a first-time safety card for Heat a meal |
| Step screen | One step at a time at the help level the backend chose. Done, Help with this step and Take a break stay in the same place; Read aloud and Replay with the spoken word highlighted; CAUTION lines always show; a calm "Want help with this step?" offer appears after a pause (never on waiting steps) |
| Help screen | Small steps, the AI "I'm stuck" panel (Role D), and the support person's name and how to reach them |
| Done screen | Check questions, and "Want to try with less help next time?" when the rules say so |
| Settings | Support person, colors and text size, sound and animations, praise style, reading voice and speed (with previews), sharing with staff, and "Tell us what you think" |
| Voice helper (written by Manaswi, Role D) | Optional microphone in the top bar: spoken commands press the same buttons the person could tap, it confirms "Did you finish this step?" before Done, and never presses buttons that erase things. Chrome or Safari. See [docs/voice_helper.md](docs/voice_helper.md) |
| Game mode (optional) | A world the person chooses, rewards they pick after each task, new areas as they go. Rewards never depend on using less help |

The screens never choose a help level: they show what `GET /today` returns and log every tap with `POST /event`. They follow [docs/ui_guidelines.md](docs/ui_guidelines.md).

## Role D (Manaswi): AI help and safety guardrails

### What the files are

| File | What it does |
| --- | --- |
| `backend/ai/llm.py` | The only file that calls the model. Reads the key from `backend/.env`, 20 second timeout, returns a safe fallback on any error |
| `backend/ai/safety.py` | Safety checks in code: danger, scam, card number or PIN, broken microwave, cooked enough, money, buying, health, food choice, and checks on the model's reply |
| `backend/ai/ask.py` | The "I'm stuck" flow (`POST /ask`) |
| `backend/ai/high_risk.py` | The label rule for photo questions ("can this go in the microwave", "how long do I heat this"): quote the label, ask 3 times, never "safe" from looks |
| `backend/ai/split.py` | AI step splitting (`POST /split`), with an extra detail version (which hand, which way). Writes only to `data/splits_pending.json` |
| `backend/ai/skill_card.py` | AI drafts a skill card, or names the missing base skill (`POST /draft_skill`). Writes only to `data/skill_cards_pending.json` (created on first use) |
| `backend/ai/common.py` | Small helpers: load a task, read a prompt, clean up JSON |
| `backend/api/ai_routes.py` | `/ask`, `/split`, `/draft_skill` |
| `backend/prompts/` | The prompts sent to the model, also collected in `docs/prompts.pdf` (rebuild with `python docs/make_prompts_pdf.py` from the repo root) |
| `frontend/src/components/AskForHelp/` | The "I'm stuck" panel on the Help screen: text box, microphone, photo and reply |

### The safety rules

The AI never reads a balance, never says whether to buy, never asks for or stores a card number or PIN, never picks a cooking time, never says food is cooked enough, and never says a dish is microwave safe from how it looks. These are checked in code, not only in the prompt:

- **Before the model** (the model is never called): danger, scam, a card number or PIN typed, a broken microwave door, cooked enough, money, buy or not, health, food choice, an empty message.
- **After the model:** the reply must be under 20 words, name no new food, and never say safe, cooked, a time, money or buy. A photo that shows a person, a card, a receipt, a bank app or a checkout page gets fixed words and no step guess.
- **Photos:** for high risk questions the code sends the photo three times. It only answers "safe" if all three answers quote a label with a safe phrase and none says anything negative. Clear metal, foil or foam gets a fixed warning when all three reads agree. Everything else is handed off to a person. The words shown come from code, never from the model.

The full rules are in [docs/safety.md](docs/safety.md) and [docs/responsible_ai.md](docs/responsible_ai.md).

### Choosing the AI provider and model

Nothing in the code depends on one provider. In `backend/.env`:

- Claude API: `LLM_PROVIDER=anthropic`, `LLM_MODEL=<model name>`, `LLM_API_KEY=<key>`. Leave `LLM_BASE_URL` blank.
- Any service with an OpenAI style `/chat/completions` API: `LLM_PROVIDER=openai`, `LLM_MODEL=<model name>`, `LLM_API_KEY=<key>`, and `LLM_BASE_URL=<the service's base URL>` if it is not OpenAI itself.

The model must be able to read images, or the photo feature will not work.

### The photo test

27 photos in `backend/tests/ai_images/photo_test/`: 12 free web images with credits in ATTRIBUTION.md, and 15 photos we took ourselves. Each has its true answer (`safe`, `unsafe` or `unknown`) in `manifest.csv`.

Latest result: 27 photos, 14 answered, 13 handed off, 0 wrong safe answers. Full table in `backend/tests/photo_test_results.md`.

This test is a sanity check, not proof. With 0 wrong answers on 27 images, the true error rate is still only known to be under about 11%. Safety comes from the code rules, not from the test.

Two package photos (a silicone bag package and a paper baking pan box) are marked `safe` because the printed label says microwave safe.

### Run the AI checks

From `backend/`:

```
pytest tests                         # no key needed
python tests/run_ai_cases.py         # writes tests/ai_cases.md (needs a key for the model cases)
python tests/run_photo_test.py       # the 27 photo test (needs a key)
```

### Limits

- Approving an extra detail split writes it into the shared task file, so it replaces the standard small steps for everyone doing that task. Saving extra detail per person is on the roadmap.
- No button in the app calls `/draft_skill` yet; it is called through the API (http://localhost:8000/docs).

AI tools helped build parts of this section. See "How AI tools were used (Role D)" in ATTRIBUTION.md for which files and what was done by hand.

## Role E (Vaishnavi): the staff, demo and review pages

The pages the team and staff use, outside the resident's phone:

| Page | What it does | Where |
| --- | --- | --- |
| `/staff` | Where each simulated resident gets stuck, from `GET /staff/sticking_points`, with a button to ask the AI for more detail on a step (`POST /split`) | `frontend/src/pages/Staff.jsx`, `backend/api/staff_routes.py` |
| `/demo` | Pick a resident and a week: the real resident app in a phone frame, "Why this changed" (the sticking points behind that week), the help chart and the "Help over time" grid, all from `GET /demo/...` | `frontend/src/pages/Demo.jsx`, `backend/api/demo_routes.py` |
| `/review` | Approve, edit or reject AI-suggested small steps and skill cards before any resident sees them | `frontend/src/pages/Review.jsx`, `backend/api/review_routes.py`, `skill_routes.py` |

`backend/api/main.py` wires every router together. The fading rules in `backend/logic/fade.py` are shared with Role B (see above).
