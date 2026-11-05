"""The two routes Role C owns: GET /today and POST /event.

E creates api/main.py. Add these two lines to it:

    from api.resident_routes import router as resident_router
    app.include_router(resident_router)

Run the backend from the backend/ folder:  uvicorn api.main:app --reload
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import json
import re

from logic.data_io import DATA_DIR, LIVE_EVENTS_PATH, available_tasks, load_definitions, load_events
from logic.event_log import log_event
from logic.today import build_today

router = APIRouter()


class EventRequest(BaseModel):
    person_id: str
    task_id: str
    session_id: str
    week: int
    event: str
    timestamp: str | None = None
    step_id: str | None = None
    seconds: float | None = None
    days_since_last: int | None = None
    help_shown: str | None = None
    answer: str | None = None
    prompted: str | None = None


@router.get("/tasks")
def tasks_route():
    """Task ids the resident can pick from. Titles come from the task files via /today."""
    return {"tasks": available_tasks()}


@router.get("/setup")
def setup_route():
    """The first-time setup questions, as written in definitions.json."""
    return load_definitions()["first_time_setup"]["questions"]


@router.get("/skills/{skill_id}")
def skill_route(skill_id: str):
    """One skill card, as written in backend/data/skills/."""
    skills = DATA_DIR / "skills"
    known = {p.stem for p in skills.glob("*.json")}
    if skill_id not in known:
        raise HTTPException(status_code=404, detail="Unknown skill")
    return json.loads((skills / f"{skill_id}.json").read_text(encoding="utf-8"))


def _milestones(rules: list[str], total_done: int, per_task: dict, skill_cards_not_needed: int) -> list[str]:
    """The milestones from definitions.json that have happened. Read from the text of each rule."""
    reached = []
    for text in rules:
        low = text.lower()
        times = re.search(r"done (\d+) times", low)
        if low.startswith("first task done"):
            ok = total_done >= 1
        elif times:
            ok = any(n >= int(times.group(1)) for n in per_task.values())
        elif "skill card" in low:
            ok = skill_cards_not_needed >= 1
        else:
            ok = False
        if ok:
            reached.append(text)
    return reached


@router.get("/game")
def game_route(person_id: str):
    """Game mode: the rules from definitions.json and this person's progress from the event log."""
    game = load_definitions()["game_mode"]
    rows = load_events(LIVE_EVENTS_PATH, person_id)
    per_task: dict[str, int] = {}
    for row in rows:
        if row["event"] == "task_done":
            per_task[row["task_id"]] = per_task.get(row["task_id"], 0) + 1
    total = sum(per_task.values())
    not_needed = sum(1 for r in rows if r["event"] == "skill_card_not_needed")
    return {
        "new_area_every_tasks_done": game["new_area_every_tasks_done"],
        "defaults": game["defaults"],
        "settings": game["settings"],
        "tasks_done": total,
        "per_task": per_task,
        "milestones_reached": _milestones(game["milestones"], total, per_task, not_needed),
    }


@router.get("/today")
def today_route(person_id: str, task_id: str, week: int):
    """Out: today's view (Format 3, draft). See logic/today.py."""
    try:
        return build_today(person_id, task_id, week)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/event")
def event_route(req: EventRequest):
    """In: one event row (Format 2). Out: the row as written."""
    try:
        return log_event(req.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
