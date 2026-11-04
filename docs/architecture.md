# Architecture

Carryover is a React app (port 5173) talking to a FastAPI backend (port 8000). The backend keeps its data in plain files, so there is no database to set up.

```mermaid
flowchart TD
  subgraph Browser["React app (frontend/)"]
    Resident["Resident screen<br/>+ I'm stuck button"]
    Staff["Staff screen"]
    Demo["Demo screen<br/>week slider + help chart"]
    Review["Review page<br/>AI steps"]
  end

  subgraph Backend["FastAPI (backend/api/main.py)"]
    Today["GET /today, POST /event"]
    AskSplit["POST /ask, POST /split"]
    DemoRoutes["GET /demo/..."]
    ReviewRoutes["GET /review/pending<br/>POST /review/id/approve"]
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
    Pending[("splits_pending.json")]
  end

  Model["AI model<br/>(backend/ai/llm.py)"]

  Resident --> Today
  Resident --> AskSplit
  Staff --> Today
  Demo --> DemoRoutes
  Review --> ReviewRoutes

  Today --> Fade
  DemoRoutes --> Fade
  Fade --> Detect
  Fade --> DataIO
  Detect --> DataIO
  DataIO --> Tasks
  DataIO --> Events
  DataIO --> Defs

  AskSplit --> Model
  AskSplit -->|"suggested small steps<br/>approved: false"| Pending
  ReviewRoutes --> Pending
  ReviewRoutes -->|"after a person approves"| Tasks
```

## How a day's screen is built

1. The resident screen asks for today's view of a task.
2. `fade.build_view()` loads the task file and the person's earlier events.
3. For each step it works out the help level (`split`, `hint` or `hide`) from how the last sessions went. The rules and numbers are in `definitions.json`.
4. The view also says whether to show the start push, the safety card, a refresher, and which check questions are due.
5. The screen shows what the view says and never picks a help level itself.

In the demo, the week slider sets the week. Only events from earlier weeks are used, so the app can't see the future.

## How AI steps reach a resident

1. `POST /split` asks the model for small steps for one hard step.
2. The answer is checked in code, then saved to `splits_pending.json` with `approved: false`.
3. A person opens the Review page, edits the words if they want, and approves.
4. Only then are the small steps written into the task file. Until that point no resident sees them.
