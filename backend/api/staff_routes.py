"""Routes for the staff screen: where each resident gets stuck."""
from fastapi import APIRouter, Query

from logic.data_io import LIVE_EVENTS_PATH, load_definitions, load_events, load_task
from logic.detect import detect

router = APIRouter(prefix="/staff")

# Tests point this at a small file.
EVENTS_PATH = LIVE_EVENTS_PATH


def _load_task_or_none(task_id: str) -> dict | None:
    try:
        return load_task(task_id)
    except ValueError:
        return None


@router.get("/sticking_points")
def sticking_points(week: int | None = Query(default=None, ge=1)):
    """Sticking points for every resident and task.

    With no week, all events are used. With a week, only events from earlier
    weeks are used, the same as the demo slider.
    """
    defs = load_definitions()
    rows = load_events(EVENTS_PATH)

    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        if week is not None and (row["week"] or 0) >= week:
            continue
        grouped.setdefault((row["person_id"], row["task_id"]), []).append(row)

    result = []
    for (person_id, task_id), events in sorted(grouped.items()):
        task = _load_task_or_none(task_id)
        if task is None:
            continue
        step_text = {s["step_id"]: s["text"] for s in task.get("steps", [])}
        points = [
            dict(p, step_text=step_text.get(p["step_id"]))
            for p in detect(events, defs, None, task)
            if p["code"] != "none"
        ]
        result.append(
            {
                "person_id": person_id,
                "task_id": task_id,
                "title": task.get("title", task_id),
                "last_week": max((r["week"] or 0) for r in events),
                "sticking_points": points,
            }
        )

    # Residents who need attention first, then by name.
    result.sort(key=lambda r: (not r["sticking_points"], r["person_id"]))
    return result
