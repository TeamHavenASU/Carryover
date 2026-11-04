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
python -m sim.simulate
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
