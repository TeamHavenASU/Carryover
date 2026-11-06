# Architecture

Carryover is a React app (port 5173) talking to a FastAPI backend (port 8000). The backend keeps its data in plain files, so there is no database to set up.

```mermaid
flowchart TD
  subgraph Browser["React app (frontend/)"]
    Resident["Resident screens<br/>I'm stuck panel on the Help screen,<br/>voice helper"]
    Staff["Staff screen"]
    Demo["Demo screen<br/>week slider, the real app in a phone frame,<br/>Why this changed, help chart, Help over time grid"]
    Review["Review page<br/>AI small steps and skill cards"]
  end

  subgraph Backend["FastAPI (backend/api/main.py)"]
    Today["Resident routes<br/>GET /tasks, /setup, /today, /game,<br/>/feedback, /skills/{id}; POST /event"]
    AskSplit["AI routes<br/>POST /ask, /split, /draft_skill"]
    StaffRoutes["GET /staff/sticking_points"]
    DemoRoutes["GET /demo/people, /view, /help_counts"]
    ReviewRoutes["Review routes<br/>GET /review/pending, /skills/pending<br/>POST .../approve, .../reject"]
    Health["GET /health"]
  end

  subgraph Logic["backend/logic/"]
    DataIO["data_io.py<br/>reads and writes files"]
    Detect["detect.py<br/>where is the person stuck"]
    Fade["fade.py<br/>help level for each step"]
  end

  subgraph Data["backend/data/"]
    Tasks[("tasks/*.json")]
    Events[("live/events.csv")]
    Defs[("definitions.json")]
    Pending[("splits_pending.json<br/>skill_cards_pending.json")]
    Skills[("skills/*.json<br/>skill cards")]
  end

  Model["AI model<br/>(backend/ai/llm.py)"]

  Resident --> Today
  Resident -->|"POST /ask only"| AskSplit
  Staff --> StaffRoutes
  Staff -->|"POST /split"| AskSplit
  Demo --> DemoRoutes
  Review --> ReviewRoutes

  StaffRoutes --> Detect

  Today --> Fade
  DemoRoutes --> Fade
  Fade --> Detect
  Fade --> DataIO
  Detect --> DataIO
  DataIO --> Tasks
  DataIO --> Events
  DataIO --> Defs

  AskSplit --> Model
  AskSplit -->|"suggested small steps and skill cards<br/>approved: false"| Pending
  ReviewRoutes --> Pending
  ReviewRoutes -->|"after a person approves"| Tasks
  ReviewRoutes -->|"after a person approves"| Skills
```

`GET /health` is a plain liveness check.

## How a day's screen is built

1. The resident screen asks for today's view of a task.
2. `fade.build_view()` loads the task file and the person's earlier events.
3. For each step it works out the help level (`split`, `hint` or `hide`) from how the last sessions went. The rules and numbers are in `definitions.json`. Some help (`hint`) shows the full step text; there are no short names.
4. Each step also carries `safety`, `picture`, `video` and `base_skills`. `safety` is shown as a CAUTION line at every help level, even when the step is folded.
5. The first time a task is opened, the view carries the task's `first_time_question`. The answer is asked and logged (`device_check_answer`). The rules in `fade.py` say that after a No every step starts at most help and `new_device` is true, but this is not yet connected in the resident app: today's view is built from earlier weeks only, so the answer does not reach it. After that the level shown last time carries over and fades the normal way.
6. The view also says whether to show the start push, the safety card, a refresher, and which check questions are due.
7. The screen shows what the view says and never picks a help level itself.

In the demo, the week slider sets the week. Only events from earlier weeks are used, so the app can't see the future.

## How AI steps reach a resident

1. `POST /split` asks the model for small steps for one hard step.
2. The answer is checked in code, then saved to `splits_pending.json` with `approved: false`.
3. A person opens the Review page, edits the words if they want, and approves.
4. Only then are the small steps written into the task file. Until that point no resident sees them.
5. AI-drafted skill cards take the same path: `POST /draft_skill` saves to `skill_cards_pending.json`, and the Review page approves them into `backend/data/skills/`. No button in the app calls `/draft_skill` yet; it is called through the API (see http://localhost:8000/docs).
