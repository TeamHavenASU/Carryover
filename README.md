# Carryover

Carryover helps autistic adults keep doing everyday tasks they have already learned, like heating a meal or buying something. It shows one step at a time and gives less help as the person needs less. If someone gets stuck, it gives help back.

The code is a React front end and a FastAPI back end. All data is in plain files under `backend/data/`.

## What is in the repo

| Folder | What is in it |
| --- | --- |
| `backend/api/` | `main.py` and the routes |
| `backend/logic/` | `data_io.py` (reading and writing files), `detect.py` (where someone gets stuck), `fade.py` (help levels and the daily view) |
| `backend/ai/` | The "I'm stuck" help and AI step splitting |
| `backend/sim/` | Makes the fake event history the demo runs on |
| `backend/data/` | Task files, `definitions.json`, the event log, the AI steps waiting for review |
| `backend/tests/` | Tests |
| `frontend/src/` | The React app: pages, the demo chart, the "I'm stuck" button |
| `docs/` | Research notes, safety rules, UI rules, the architecture diagram |

See [docs/architecture.md](docs/architecture.md) for how the parts fit together.

## Set up

You need Python 3.11 or newer and Node 18 or newer.

Back end, from the repo root:

```
cd backend
python3 -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `backend/.env` and fill in your own values. This file is in `.gitignore`, so it never gets committed. See [docs/README_D.md](docs/README_D.md) for which provider and model to use.

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

Then open http://localhost:5173. The pages are:

| Page | What it is |
| --- | --- |
| `/resident` | The resident screen |
| `/staff` | The staff screen |
| `/demo` | The demo: pick a resident, move the week, see the help change and the help chart |
| `/review` | Approve or edit AI suggested small steps before residents see them |

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

API keys go in `backend/.env` only. Never put them in code, and never commit `.env`. Only `.env.example` (with blank values) is committed.

## More

- [docs/README_D.md](docs/README_D.md): the AI help
- [docs/safety.md](docs/safety.md): safety rules
- [docs/ui_guidelines.md](docs/ui_guidelines.md): rules for every resident screen
- [docs/sticking_points.md](docs/sticking_points.md) and [docs/sources.md](docs/sources.md): the research

## Role B: data, fading and learning

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
  data.
- The scores in learn.py are descriptive, not causal. Heavier help shows a
  lower success rate because a step only reaches Most help when someone keeps
  struggling there. That is a selection effect, so the scores are not used to
  choose help.
