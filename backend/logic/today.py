"""Today's view for the resident screens (Role C).

    build_today("jeremiah", "heat_meal", 3)

The help levels, start push, refresher, check questions and the rest come from
fade.build_view() (Role B). That view leaves out some task file fields the
screens need, so this adds them as they are: step number and total, picture,
video, safety, base_skills, substeps_by_phone, part, and the task's
first_time_question and safety_card_content. Nothing is decided here and no text is written here.
"""
from __future__ import annotations

from logic import fade
from logic.data_io import LIVE_EVENTS_PATH, load_task

# Step fields in the task file that build_view does not pass on.
STEP_FIELDS = ("picture", "video", "safety", "base_skills", "substeps_by_phone", "part")


def build_today(person_id: str, task_id: str, week: int, events_path=LIVE_EVENTS_PATH) -> dict:
    """The view from fade.build_view, plus the task file fields the screens show."""
    view = fade.build_view(person_id, task_id, week, events_path=events_path)
    task = load_task(task_id)
    by_id = {s["step_id"]: s for s in task["steps"]}
    total = len(view["steps"])

    for number, step in enumerate(view["steps"], start=1):
        source = by_id[step["step_id"]]
        step["number"] = number
        step["total"] = total
        for field in STEP_FIELDS:
            if field in source:
                step[field] = source[field]

    view["first_time_question"] = task.get("first_time_question")
    view["safety_card_content"] = task.get("safety_card_content")
    return view
