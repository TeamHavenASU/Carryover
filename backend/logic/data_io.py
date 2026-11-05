"""The single place the project reads and writes its data.

Everything that needs definitions, task files or the event log goes through
this module, so paths and formats are decided in one place:

- definitions.json  -> load_definitions()
- tasks/<id>.json   -> load_task()
- events.csv        -> load_events() and write_events()

EVENT_COLUMNS below is the one definition of the event log format
(Format 2 v3). The simulator, the app's POST /event, detect.py and fade.py
must all follow it. If the format changes, change it here.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

# --------------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------------
# Built from this file's location, not the current working directory, so the
# code works from the repo root, from backend/, and from a fresh clone.
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
TASKS_DIR = DATA_DIR / "tasks"
DEFINITIONS_PATH = DATA_DIR / "definitions.json"
LIVE_EVENTS_PATH = DATA_DIR / "live" / "events.csv"

# --------------------------------------------------------------------------------
# Event log format (Format 2 v3)
# --------------------------------------------------------------------------------
# Rules for the columns:
# - timestamp is local time, format YYYY-MM-DDTHH:MM:SS (e.g. 2026-11-16T18:02:10).
# - session_id is <person>-<task>-w<NN>, e.g. jeremiah-heat_meal-w03.
# - help_shown holds "split", "hint" or "hide" (the help level shown).
# - answer is used only on check_answer, end_question, refresher_answer,
#   help_offer_answer (yes/no) and small_step_opened (the substep id, e.g. s4b).
# - prompted is used only on step_done, values "yes" or "no".
EVENT_COLUMNS = [
    "person_id",
    "task_id",
    "session_id",
    "week",
    "timestamp",
    "event",
    "step_id",
    "seconds",
    "days_since_last",
    "help_shown",
    "answer",
    "prompted",
]

# Columns turned into numbers when the log is read. Empty strings become None.
_INT_COLUMNS = ("week", "days_since_last")
_FLOAT_COLUMNS = ("seconds",)

# Every event name the log may contain.
#
# "skipped" is deliberately not an event. A skip is a week with no session for
# that task, computed from the log.
#
# The seconds value on a resumed row is break time, not a pause, and must not
# be counted as a long pause.
ALL_EVENTS = [
    # task level
    "task_opened",
    "task_closed_no_start",
    "task_done",
    # step level
    "step_started",
    "step_done",
    # help the person asked for
    "stuck_pressed",
    "hint_requested",
    "more_help_requested",
    "show_all_pressed",
    "ask_sent",
    "help_offer_answer",  # Rule 6 "Want help with this step?". answer holds yes/no
    # Small steps now show one at a time. small_step_opened does NOT count as
    # used help for Rule 2: it is the level's own content, not extra help.
    "small_step_opened",  # answer holds the substep id, e.g. s4b
    "repeat_requested",
    "step_done_undone",  # "Tapped Done by mistake? Go back"
    # break
    "paused",
    "resumed",
    # answers (these use the answer column)
    "check_answer",
    "end_question",
    "refresher_answer",
]


# --------------------------------------------------------------------------------
# Definitions and tasks
# --------------------------------------------------------------------------------
def load_definitions() -> dict:
    """Read backend/data/definitions.json and return it as a dict.

    Raises FileNotFoundError with the full path if the file is missing.
    """
    if not DEFINITIONS_PATH.is_file():
        raise FileNotFoundError(f"definitions.json not found at {DEFINITIONS_PATH}")
    with open(DEFINITIONS_PATH, encoding="utf-8") as f:
        return json.load(f)


def used_help_events() -> list[str]:
    """Return the events that count as "used help", from definitions.json.

    Read from the file, not hardcoded, so the team changes the list in one
    place only. Read on each call rather than at import, so a missing or
    broken definitions.json only fails the code that needs it, not every
    import of this module.
    """
    return list(load_definitions()["used_help_events"])


def available_tasks() -> list[str]:
    """Return the ids of all task files in backend/data/tasks/, sorted."""
    return sorted(p.stem for p in TASKS_DIR.glob("*.json"))


def load_task(task_id: str) -> dict:
    """Read backend/data/tasks/<task_id>.json and return it as a dict.

    Valid ids are the task files that exist: heat_meal, buy_instore_card,
    buy_instore_phone, buy_online. An unknown id raises ValueError listing them.

    This exists because detect.py is called without a task (ask.py passes
    none), so it loads the task itself from the task_id on the events.
    """
    tasks = available_tasks()
    # Checking against the real file list also blocks ids like "../secret".
    if task_id not in tasks:
        raise ValueError(f"Unknown task_id {task_id!r}. Available tasks: {', '.join(tasks)}")
    with open(TASKS_DIR / f"{task_id}.json", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------------
def _to_int(value: str | None) -> int | None:
    """Turn a CSV cell into an int. Empty or missing becomes None."""
    if value is None or value.strip() == "":
        return None
    return int(float(value))


def _to_float(value: str | None) -> float | None:
    """Turn a CSV cell into a float. Empty or missing becomes None."""
    if value is None or value.strip() == "":
        return None
    return float(value)


def _coerce(row: dict) -> dict:
    """Convert week, seconds and days_since_last to numbers. Others stay strings."""
    for col in _INT_COLUMNS:
        row[col] = _to_int(row.get(col))
    for col in _FLOAT_COLUMNS:
        row[col] = _to_float(row.get(col))
    return row


def load_events(
    path: str | Path,
    person_id: str | None = None,
    task_id: str | None = None,
    up_to_week: int | None = None,
) -> list[dict]:
    """Read an events CSV and return its rows as dicts, oldest first.

    - Filters by person_id and task_id when given.
    - up_to_week keeps only rows with week <= up_to_week.
    - week and days_since_last become int, seconds becomes float. Empty
      cells in those columns become None. All other values stay strings.
    """
    path = Path(path)
    # The simulator may not have run yet, so a missing log is an empty log.
    if not path.is_file():
        return []

    with open(path, newline="", encoding="utf-8") as f:
        rows = [_coerce(row) for row in csv.DictReader(f)]

    if person_id is not None:
        rows = [r for r in rows if r.get("person_id") == person_id]
    if task_id is not None:
        rows = [r for r in rows if r.get("task_id") == task_id]

    # This exists so the demo cannot see the future. When the week slider is
    # at week 3, the system must only know what it knew at week 3. Rows with
    # no week are dropped too, since we cannot show they are not later.
    if up_to_week is not None:
        rows = [r for r in rows if r["week"] is not None and r["week"] <= up_to_week]
        assert all(r["week"] <= up_to_week for r in rows), "load_events returned a row after up_to_week"

    # Timestamps are YYYY-MM-DDTHH:MM:SS, so sorting the text sorts by time.
    rows.sort(key=lambda r: r.get("timestamp") or "")
    return rows


def write_events(path: str | Path, events: Iterable[dict[str, Any]]) -> None:
    """Write events to a CSV: a header of EVENT_COLUMNS, then one row per event.

    Creates parent folders if needed. Missing columns and None values are
    written as empty strings. A key that is not in EVENT_COLUMNS raises
    ValueError, so a typo is caught instead of silently dropped.
    """
    events = list(events)
    allowed = set(EVENT_COLUMNS)
    for i, event in enumerate(events):
        unknown = sorted(set(event) - allowed)
        if unknown:
            raise ValueError(
                f"Event {i} has unknown column(s) {unknown}. Allowed columns: {', '.join(EVENT_COLUMNS)}"
            )

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EVENT_COLUMNS, restval="")
        writer.writeheader()
        for event in events:
            writer.writerow({k: ("" if v is None else v) for k, v in event.items()})
