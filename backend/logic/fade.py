"""Fading: how much help each step shows, and the view for one day.

Help levels go from most to least: split, hint, hide (see definitions.json).
Every number comes from definitions.json or the task file, nothing is set here.

build_view() is what the resident screen and the demo read. It only uses
events from before the week it is asked about.
"""
from __future__ import annotations

from datetime import datetime

from logic.data_io import LIVE_EVENTS_PATH, load_definitions, load_events, load_task
from logic.detect import detect


def levels(defs: dict) -> list[str]:
    """Help levels from most help to least."""
    hl = defs["help_levels"]
    return [hl["most_help"], hl["some_help"], hl["no_help"]]


def first_level(defs: dict) -> str:
    """The level every step starts at in week 1."""
    hl = defs["help_levels"]
    return hl[hl["week_1_level"]]


def long_pause(step: dict, task: dict, defs: dict) -> float:
    """The step's own long pause, else the task's, else the default."""
    default = defs["defaults"]["long_pause_seconds"]
    return step.get("long_pause_seconds", task.get("long_pause_seconds", default))


def _seconds(value) -> float:
    return value if isinstance(value, (int, float)) else 0.0


def split_sessions(events: list[dict], defs: dict) -> list[list[dict]]:
    """Group one person's events for one task into sessions, oldest first.

    A new session starts after task_done, or after a gap longer than
    take_a_break.new_session_after_hours. The session_id column can't be used
    because it only has the week number.
    """
    gap = defs["take_a_break"]["new_session_after_hours"] * 3600
    sessions: list[list[dict]] = []
    last_time = None
    last_event = None
    for row in events:
        when = datetime.fromisoformat(row["timestamp"])
        is_new = (
            last_time is None
            or last_event == "task_done"
            or (when - last_time).total_seconds() > gap
        )
        if is_new:
            sessions.append([])
        sessions[-1].append(row)
        last_time, last_event = when, row["event"]
    return sessions


def step_result(session: list[dict], step: dict, task: dict, defs: dict) -> tuple[str | None, str | None]:
    """How one step went in one session: (help level shown, result).

    result is one of:
      struggled  long pause, never finished, or answered "no" to the check question
      opened     the person opened help themselves
      prompted   help showed up by itself
      alone      done with no help at all
    Both are None if the step was not started.
    """
    sid = step["step_id"]
    rows = [r for r in session if r["step_id"] == sid]
    started = next((r for r in rows if r["event"] == "step_started"), None)
    if started is None:
        return None, None
    shown = started["help_shown"] or None

    done = next((r for r in rows if r["event"] == "step_done"), None)
    too_long = (
        not step.get("wait")
        and done is not None
        and _seconds(done["seconds"]) > long_pause(step, task, defs)
    )
    said_no = any(r["event"] == "check_answer" and r["answer"] == "no" for r in rows)
    if done is None or too_long or said_no:
        return shown, "struggled"

    used = set(defs["used_help_events"])
    if any(r["event"] in used for r in rows):
        return shown, "opened"
    if done["prompted"] == "yes":
        return shown, "prompted"
    return shown, "alone"


def _level_and_streak(history: list[list[dict]], step: dict, task: dict, defs: dict) -> tuple[str, list[str]]:
    """The level the step was last shown at, and the results since it last changed."""
    current = first_level(defs)
    results: list[str] = []
    for session in history:
        shown, result = step_result(session, step, task, defs)
        if result is None:
            continue
        if shown and shown != current:
            current, results = shown, []
        results.append(result)
    return current, results


def _last_all(results: list[str], count: int, wanted: str) -> bool:
    return len(results) >= count and all(r == wanted for r in results[-count:])


def next_level(history: list[list[dict]], step: dict, task: dict, defs: dict) -> str:
    """The help level this step shows in the next session."""
    order = levels(defs)
    rules = defs["fading_rules"]
    current, results = _level_and_streak(history, step, task, defs)
    i = order.index(current) if current in order else order.index(first_level(defs))

    if _last_all(results, rules["rule_4_more_help_after_struggled_in_a_row"], "struggled"):
        i -= 1
    elif _last_all(results, rules["rule_2_show_less_after_done_alone"], "alone"):
        i += 1
    elif _last_all(results, rules["rule_5_offer_up_front_after_opened_in_a_row"], "opened"):
        i -= 1
    return order[max(0, min(i, len(order) - 1))]


def decide_level(person: str, task: dict, step_id: str, week: int, history: list[list[dict]], defs: dict | None = None) -> str:
    """Same arguments as decide_help in the simulator, so it can replace it."""
    defs = defs or load_definitions()
    if week == 1:
        return first_level(defs)
    step = next(s for s in task["steps"] if s["step_id"] == step_id)
    return next_level(history, step, task, defs)


def hint_waits(step: dict, task: dict, defs: dict) -> list[int]:
    """Seconds to wait before offering help, at 1/4, 1/2 and 3/4 of the long pause.

    Waiting steps (food heating, a timer) never offer help, so they get no times.
    """
    if step.get("wait"):
        return []
    pause = long_pause(step, task, defs)
    return [round(f * pause) for f in defs["fading_rules"]["rule_6_hint_wait_fractions_of_long_pause"]]


def started_with_trouble(session: list[dict], task: dict, defs: dict) -> bool:
    """Opened the task but did not get going on the first step."""
    opens = [r for r in session if r["event"] == "task_opened"]
    first_step = next((r for r in session if r["event"] == "step_started"), None)
    if first_step is None or not opens:
        return True
    if any(r["event"] == "task_closed_no_start" for r in session):
        return True
    if len(opens) >= defs["defaults"]["opens_without_start_for_trouble_starting"]:
        return True
    wait = (
        datetime.fromisoformat(first_step["timestamp"])
        - datetime.fromisoformat(opens[0]["timestamp"])
    ).total_seconds()
    return wait > task.get("start_time_seconds", defs["defaults"]["start_time_seconds"])


def start_push_on(sessions: list[list[dict]], task: dict, defs: dict) -> bool:
    """On after trouble starting twice in a row, off after starting alone three times."""
    rules = defs["fading_rules"]
    turn_on = rules["start_push_back_after_trouble_starting_in_a_row"]
    turn_off = rules["start_push_remove_after_started_alone"]
    on = False
    trouble_run = 0
    alone_run = 0
    for session in sessions:
        if started_with_trouble(session, task, defs):
            trouble_run += 1
            alone_run = 0
            if trouble_run >= turn_on:
                on = True
        else:
            alone_run += 1
            trouble_run = 0
            if alone_run >= turn_off:
                on = False
    return on


def trailing_skipped_weeks(history: list[dict], week: int) -> int:
    """Weeks in a row, just before this one, with no session for the task."""
    if not history:
        return 0
    seen = {r["week"] for r in history}
    count = 0
    for w in range(week - 1, 0, -1):
        if w in seen:
            break
        count += 1
    return count


def _days_since_last(all_events: list[dict], week: int) -> int | None:
    """days_since_last from the first task_opened row of this week, if there is one."""
    for row in all_events:
        if row["week"] == week and row["event"] == "task_opened":
            return row["days_since_last"]
    return None


def build_view(
    person_id: str,
    task_id: str,
    week: int,
    events_path=LIVE_EVENTS_PATH,
    defs: dict | None = None,
    days_since_last: int | None = None,
) -> dict:
    """What the resident sees for this task in this week.

    Only events from weeks before `week` are used for the help levels.
    """
    defs = defs or load_definitions()
    task = load_task(task_id)

    history_rows = load_events(events_path, person_id, task_id, up_to_week=week - 1)
    sessions = split_sessions(history_rows, defs)

    if days_since_last is None:
        all_rows = load_events(events_path, person_id, task_id)
        days_since_last = _days_since_last(all_rows, week)

    points = detect(history_rows, defs, days_since_last, task)
    codes = {p["code"] for p in points}

    steps = []
    for step in task["steps"]:
        mode = first_level(defs) if not sessions else next_level(sessions, step, task, defs)
        steps.append(
            {
                "step_id": step["step_id"],
                "text": step["text"],
                "hint": step.get("hint", step["text"]),
                "mode": mode,
                "wait": bool(step.get("wait")),
                "long_pause_seconds": long_pause(step, task, defs),
                "hint_waits": hint_waits(step, task, defs),
                "substeps": step.get("substeps", []),
                "tips": step.get("tips", []),
                "check_question": step.get("check_question"),
            }
        )

    session_number = len(sessions) + 1
    every = defs["check_questions"]["ask_every_n_sessions"]
    hidden = levels(defs)[-1]
    check_questions = []
    if session_number % every == 0:
        check_questions = [
            {"step_id": s["step_id"], "question": s["check_question"]}
            for s in steps
            if s["mode"] == hidden and s["check_question"]
        ]

    return {
        "person_id": person_id,
        "task_id": task_id,
        "title": task.get("title", task_id),
        "week": week,
        "session_number": session_number,
        "start_push": task.get("start_push") if start_push_on(sessions, task, defs) else None,
        "show_refresher": "rusty_after_gap" in codes,
        "show_safety_card": task.get("safety_card") if not sessions else None,
        "break_note": task.get("break_note"),
        "ask_about_skips": trailing_skipped_weeks(history_rows, week)
        >= defs["fading_rules"]["rule_8_skips_before_asking_once"],
        "check_questions": check_questions,
        "sticking_points": points,
        "steps": steps,
    }
