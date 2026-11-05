"""Write one event from the resident screens to the event log.

Role C. Uses EVENT_COLUMNS and ALL_EVENTS from data_io.py, never retyped.
Rules enforced here:
- event must be in ALL_EVENTS
- prompted only on step_done, value "yes" or "no"
- answer only on the events data_io.py lists as using the answer column
- person_id, task_id, session_id and week are required. The one exception is
  task_id on feedback_answer, which may be empty: it is about the app, not a task
- no other column data (never log what was bought, the cost, or what was eaten)
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from logic.data_io import ALL_EVENTS, EVENT_COLUMNS, LIVE_EVENTS_PATH

# The events that use the answer column (see the Format 2 notes in data_io.py).
ANSWER_EVENTS = (
    "check_answer",
    "end_question",
    "refresher_answer",
    "help_offer_answer",
    "still_want_answer",
    "small_step_opened",
    "setup_answer",
    "device_check_answer",
    "skill_check_answer",
    "skill_card_shown",
    "skill_card_not_needed",
    "feedback_answer",  # Settings feedback: question_id:value
)


def log_event(event: dict, path: str | Path = LIVE_EVENTS_PATH) -> dict:
    """Validate and append one event row. Returns the row as written."""
    unknown = sorted(set(event) - set(EVENT_COLUMNS))
    if unknown:
        raise ValueError(f"Unknown column(s) {unknown}. Allowed: {', '.join(EVENT_COLUMNS)}")
    name = event.get("event")
    if name not in ALL_EVENTS:
        raise ValueError(f"Unknown event {name!r}. Allowed: {', '.join(ALL_EVENTS)}")
    if event.get("prompted") not in (None, "") and name != "step_done":
        raise ValueError("prompted is only allowed on step_done")
    if name == "step_done" and event.get("prompted") not in ("yes", "no"):
        raise ValueError('step_done needs prompted = "yes" or "no"')
    if event.get("answer") not in (None, "") and name not in ANSWER_EVENTS:
        raise ValueError(f"answer is only allowed on {', '.join(ANSWER_EVENTS)}")
    # task_id may be empty only on feedback_answer: it is about the app, not a task.
    needed = ["person_id", "session_id", "week"] + ([] if name == "feedback_answer" else ["task_id"])
    for required in needed:
        if event.get(required) in (None, ""):
            raise ValueError(f"{required} is required")

    row = {c: ("" if event.get(c) is None else event[c]) for c in EVENT_COLUMNS}
    if not row["timestamp"]:
        row["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.is_file() or path.stat().st_size == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EVENT_COLUMNS)
        if new_file:
            w.writeheader()
        w.writerow(row)
    return row
