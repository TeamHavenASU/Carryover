"""Routes for the demo screen: the week slider and the help_count chart."""
from fastapi import APIRouter, HTTPException, Query

from logic import fade
from logic.data_io import LIVE_EVENTS_PATH, load_definitions, load_events, load_task

router = APIRouter(prefix="/demo")

# Tests point this at a small file.
EVENTS_PATH = LIVE_EVENTS_PATH


def _title(task_id: str) -> str:
    try:
        return load_task(task_id).get("title", task_id)
    except ValueError:
        return task_id


@router.get("/people")
def people():
    """Every person and task in the event log, with the last week that has events."""
    found: dict[tuple[str, str], int] = {}
    for row in load_events(EVENTS_PATH):
        if not row["task_id"]:
            continue  # feedback_answer rows are about the app, not a task
        key = (row["person_id"], row["task_id"])
        found[key] = max(found.get(key, 0), row["week"] or 0)
    return [
        {"person_id": p, "task_id": t, "title": _title(t), "last_week": last}
        for (p, t), last in sorted(found.items())
    ]


@router.get("/view")
def view(person_id: str, task_id: str, week: int = Query(ge=1)):
    """What the resident sees in this week, built only from earlier weeks."""
    try:
        return fade.build_view(person_id, task_id, week, events_path=EVENTS_PATH)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/help_counts")
def help_counts(person_id: str, task_id: str, up_to_week: int = Query(ge=0)):
    """Times help was used in each week from 1 to up_to_week.

    A week with sessions = 0 was skipped. It is not a week with no help used.
    """
    if up_to_week == 0:
        return []
    defs = load_definitions()
    used = set(defs["used_help_events"])
    rows = load_events(EVENTS_PATH, person_id, task_id, up_to_week=up_to_week)

    sessions_by_week: dict[int, int] = {}
    for session in fade.split_sessions(rows, defs):
        week = session[0]["week"]
        sessions_by_week[week] = sessions_by_week.get(week, 0) + 1

    counts: dict[int, int] = {}
    for row in rows:
        if row["event"] in used:
            counts[row["week"]] = counts.get(row["week"], 0) + 1

    return [
        {"week": w, "sessions": sessions_by_week.get(w, 0), "help_count": counts.get(w, 0)}
        for w in range(1, up_to_week + 1)
    ]
