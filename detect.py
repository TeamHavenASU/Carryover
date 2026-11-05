"""Find where a person gets stuck on a task (Build Spec A3).

detect(events, definitions, days_since_last, task=None) looks at one person's
events for one task and returns a list of sticking points, for example:

    [{"code": "cant_start", "step_id": None, "evidence": "..."},
     {"code": "stuck_at_step", "step_id": "s4", "evidence": "..."}]

Codes (the only five):
    cant_start       trouble starting the task
    stuck_at_step    a long pause, or pressed stuck / asked for help, at a step
    missing_step     answered "no" to a check question, or started a step and
                     never finished it in a session they finished
    rusty_after_gap  the coming session is after a long break
    none             nothing found

Why these codes (research, see docs/sticking_points.md):
    cant_start      -> trouble starting tasks (Buckle et al. 2021; Carmo et al. 2015)
    missing_step    -> remembering steps (Buckle et al. 2021; Hill 2004)
    stuck_at_step   -> switching when things look different (Hill 2004)
    rusty_after_gap -> skills can fade after a break (Richling et al. 2019)

Rules that apply to every code except rusty_after_gap:
    - Only the last `sessions_to_look_at` sessions count (definitions.json, 2).
    - A pattern counts only if it shows up in EVERY session looked at.
      One bad day is not a sticking point.

Every number comes from definitions.json or the task file. Nothing is typed in here.
"""
from __future__ import annotations

import statistics
from datetime import datetime

# Events that mean "I'm stuck / I want help" at a step.
STUCK_EVENTS = ("stuck_pressed", "hint_requested")
# Counts as stuck only in the person's first week (week-1 light check, Build Spec v2).
STUCK_EVENTS_FIRST_WEEK = ("more_help_requested",)


# --------------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------------
def _num(value):
    """Turn a cell into a number. Empty or missing becomes None."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _time(row):
    """The row's timestamp as a datetime, or None if it can't be read."""
    try:
        return datetime.fromisoformat(str(row.get("timestamp", "")))
    except ValueError:
        return None


def _settings(definitions: dict) -> dict:
    """Pull every number detect needs out of definitions.json, in one place."""
    rules = definitions.get("fading_rules", {})
    defaults = definitions.get("defaults", {})
    return {
        "look_at": int(definitions.get("sessions_to_look_at", 2)),
        "opens_for_cant_start": int(defaults.get("opens_without_start_for_trouble_starting", 2)),
        "default_start_time": float(defaults.get("start_time_seconds", 60)),
        "default_long_pause": float(defaults.get("long_pause_seconds", 45)),
        "rusty_times": float(rules.get("rule_7_rusty_times_usual_break", 2)),
        "rusty_min_days": float(rules.get("rule_7_rusty_min_days", 14)),
        "rusty_no_history_days": float(rules.get("rule_7_rusty_days_if_no_history", 14)),
        "new_session_hours": float(definitions.get("take_a_break", {}).get("new_session_after_hours", 12)),
    }


def _long_pause_for(step: dict, task: dict, s: dict) -> float:
    """The step's own long_pause_seconds, else the task's, else the default."""
    return float(step.get("long_pause_seconds", task.get("long_pause_seconds", s["default_long_pause"])))


# --------------------------------------------------------------------------------
# Splitting the events into sessions
# --------------------------------------------------------------------------------
def split_sessions(events: list[dict], s: dict) -> list[list[dict]]:
    """Group events into sessions (one attempt at the task each), oldest first.

    A new session starts when:
      - the session_id changes, or
      - the task is opened again after the last session ended with task_done, or
      - the person was away longer than new_session_after_hours (12).
    Reopening after task_closed_no_start stays in the same session: that is
    one attempt where the person had trouble starting.
    """
    sessions: list[list[dict]] = []
    current: list[dict] = []
    for row in events:
        start_new = False
        if current:
            prev = current[-1]
            if row.get("session_id") != prev.get("session_id"):
                start_new = True
            elif row.get("event") == "task_opened" and any(r.get("event") == "task_done" for r in current):
                start_new = True
            else:
                t0, t1 = _time(prev), _time(row)
                if t0 and t1 and (t1 - t0).total_seconds() > s["new_session_hours"] * 3600:
                    start_new = True
        if start_new:
            sessions.append(current)
            current = []
        current.append(row)
    if current:
        sessions.append(current)
    return sessions


def _gaps(session: list[dict]):
    """Yield (row, seconds since the row before it) for each row in a session.

    The gap that ends at a 'resumed' row is break time and is skipped.
    """
    for prev, row in zip(session, session[1:]):
        if row.get("event") == "resumed" or prev.get("event") == "paused":
            continue
        t0, t1 = _time(prev), _time(row)
        if t0 and t1:
            yield row, (t1 - t0).total_seconds()


# --------------------------------------------------------------------------------
# What happened in one session
# --------------------------------------------------------------------------------
def _cant_start(session: list[dict], task: dict, s: dict) -> str | None:
    """Return a short reason if this session had trouble starting, else None."""
    first_step = next((i for i, r in enumerate(session) if r.get("event") == "step_started"), None)
    before = session if first_step is None else session[:first_step]

    opens = sum(1 for r in before if r.get("event") == "task_opened")
    if opens >= s["opens_for_cant_start"]:
        return f"opened {opens} times before starting"
    if any(r.get("event") == "task_closed_no_start" for r in before):
        return "opened and closed it without starting"

    if first_step is not None:
        start_time = float(task.get("start_time_seconds", s["default_start_time"]))
        waited = sum(gap for row, gap in _gaps(session[: first_step + 1]))
        if waited > start_time:
            return f"took {round(waited)} s to start (start time is {round(start_time)} s)"
    return None


def _stuck_steps(session: list[dict], task: dict, s: dict, first_week: bool) -> dict[str, str]:
    """Return {step_id: reason} for each step this session got stuck on."""
    steps = {st["step_id"]: st for st in task.get("steps", [])}
    found: dict[str, str] = {}

    # 1. A long pause at a step: a gap between taps, or the seconds column.
    # The gap that ends at a row counts toward the step the person is on.
    current = None
    gaps = dict((id(r), g) for r, g in _gaps(session))
    for row in session:
        sid = row.get("step_id") or None
        if row.get("event") == "step_started" and sid:
            current = sid
        step_id = sid or current
        step = steps.get(step_id)
        if not step or step.get("wait"):
            continue  # waiting steps never count as long pauses
        limit = _long_pause_for(step, task, s)
        # The gap before step_started is time before the step (or before the
        # task, which cant_start checks), not a pause on this step.
        pause = 0 if row.get("event") == "step_started" else gaps.get(id(row), 0)
        if row.get("event") != "resumed":
            col = _num(row.get("seconds"))
            if col is not None:
                pause = max(pause, col)
        if pause > limit and step_id not in found:
            found[step_id] = f"long pause at {step_id} ({round(pause)} s, limit {round(limit)} s)"

    # 2. Pressed stuck or asked for a hint at a step.
    stuck_events = STUCK_EVENTS + (STUCK_EVENTS_FIRST_WEEK if first_week else ())
    for row in session:
        sid = row.get("step_id")
        if row.get("event") in stuck_events and sid in steps and sid not in found:
            found[sid] = f"asked for help at {sid} ({row['event']})"
    return found


def _missing_steps(session: list[dict]) -> dict[str, str]:
    """Return {step_id: reason} for each step this session missed."""
    found: dict[str, str] = {}
    for row in session:
        if row.get("event") == "check_answer" and str(row.get("answer", "")).lower() == "no" and row.get("step_id"):
            found[row["step_id"]] = f"said no to the check question for {row['step_id']}"

    if any(r.get("event") == "task_done" for r in session):
        started = [r["step_id"] for r in session if r.get("event") == "step_started" and r.get("step_id")]
        done = {r["step_id"] for r in session if r.get("event") == "step_done" and r.get("step_id")}
        for sid in started:
            if sid not in done and sid not in found:
                found[sid] = f"started {sid} but never finished it"
    return found


# --------------------------------------------------------------------------------
# Rusty
# --------------------------------------------------------------------------------
def usual_break(sessions: list[list[dict]]) -> float | None:
    """The person's usual break in days: the middle value (median) of past breaks.

    The median is used so one long break (like a vacation) doesn't change what
    counts as usual. None if there are no past breaks yet (no history).
    """
    breaks = []
    for session in sessions:
        value = next((_num(r.get("days_since_last")) for r in session if _num(r.get("days_since_last")) is not None), None)
        if value is not None and value > 0:
            breaks.append(value)
    return statistics.median(breaks) if breaks else None


def _rusty(days_since_last, sessions, s) -> str | None:
    """Return a reason if the coming session is after a long break, else None."""
    days = _num(days_since_last)
    if days is None or days <= 0:
        return None
    usual = usual_break(sessions)
    if usual is None:
        if days >= s["rusty_no_history_days"]:
            return f"{round(days)} days since last time (no history yet; {round(s['rusty_no_history_days'])}+ counts)"
        return None
    if days > s["rusty_times"] * usual and days >= s["rusty_min_days"]:
        return (f"{round(days)} days since last time; usual break is {usual:g} days "
                f"(rusty means more than {s['rusty_times']:g}x that and at least {round(s['rusty_min_days'])})")
    return None


# --------------------------------------------------------------------------------
# Staff flag: breaks on the same step (not a sticking-point code)
# --------------------------------------------------------------------------------
def steps_with_breaks(events, definitions):
    """Return the steps where the person took a break in 3 or more sessions.

    This is a flag for staff (Take a break rule), NOT one of the five detect
    codes, so it never changes the help the app shows. A break is never
    counted as struggling. A step that keeps needing breaks may be too long or
    tiring, so staff may want to look at it. E's staff screen calls this.

    The number 3 comes from definitions.json:
    take_a_break.breaks_on_same_step_to_flag_for_staff. It counts every session
    in the events given, so pass the window you want staff to see.

    Returns e.g. [{"step_id": "s4", "sessions": 3,
                   "evidence": "Took a break at s4 in 3 sessions"}]
    """
    s = _settings(definitions)
    need = int(definitions.get("take_a_break", {}).get("breaks_on_same_step_to_flag_for_staff", 3))
    events = sorted(events or [], key=lambda r: str(r.get("timestamp", "")))
    counts: dict[str, int] = {}
    for session in split_sessions(events, s):
        paused_here = {r["step_id"] for r in session if r.get("event") == "paused" and r.get("step_id")}
        for sid in paused_here:
            counts[sid] = counts.get(sid, 0) + 1
    return [
        {"step_id": sid, "sessions": n, "evidence": f"Took a break at {sid} in {n} sessions"}
        for sid, n in sorted(counts.items())
        if n >= need
    ]


# --------------------------------------------------------------------------------
# Main function
# --------------------------------------------------------------------------------
def _load_task_for(events):
    """Load the task file from the task_id on the events (ask.py passes no task)."""
    if not events or not events[0].get("task_id"):
        return {"steps": []}
    from logic.data_io import load_task  # imported here so tests can run without it
    return load_task(events[0]["task_id"])


def _in_every(per_session: list[dict[str, str]]) -> dict[str, list[str]]:
    """Keep only the steps found in every session. Returns {step_id: [reasons]}."""
    if not per_session:
        return {}
    common = set(per_session[0])
    for found in per_session[1:]:
        common &= set(found)
    return {sid: [found[sid] for found in per_session] for sid in common}


def _evidence(reasons: list[str], n: int) -> str:
    """Join the reasons from each session into one sentence for the staff screen."""
    unique = list(dict.fromkeys(reasons))
    where = "last session" if n == 1 else f"each of the last {n} sessions"
    return f"In {where}: " + "; ".join(unique)


def detect(events, definitions, days_since_last, task=None):
    """Return this person's sticking points for one task.

    events          this person's rows for this task (load_events output), oldest first
    definitions     definitions.json as a dict
    days_since_last days since they last did this task, for the coming session
    task            the task file as a dict; loaded from the events if not given
    """
    s = _settings(definitions)
    events = sorted(events or [], key=lambda r: str(r.get("timestamp", "")))
    if task is None:
        task = _load_task_for(events)

    sessions = split_sessions(events, s)
    recent = sessions[-s["look_at"]:]
    n = len(recent)
    first_week = None
    weeks = [_num(r.get("week")) for r in events if _num(r.get("week")) is not None]
    if weeks:
        first_week = min(weeks)
    order = {st["step_id"]: i for i, st in enumerate(task.get("steps", []))}
    results = []

    if recent:
        # cant_start: in every session looked at
        reasons = [_cant_start(ses, task, s) for ses in recent]
        if all(reasons):
            results.append({"code": "cant_start", "step_id": None, "evidence": _evidence(reasons, n)})

        # stuck_at_step: same step in every session looked at
        stuck = [
            _stuck_steps(ses, task, s, first_week is not None and _num(ses[0].get("week")) == first_week)
            for ses in recent
        ]
        for sid, why in sorted(_in_every(stuck).items(), key=lambda kv: order.get(kv[0], 99)):
            results.append({"code": "stuck_at_step", "step_id": sid, "evidence": _evidence(why, n)})

        # missing_step: same step in every session looked at
        missing = [_missing_steps(ses) for ses in recent]
        for sid, why in sorted(_in_every(missing).items(), key=lambda kv: order.get(kv[0], 99)):
            results.append({"code": "missing_step", "step_id": sid, "evidence": _evidence(why, n)})

    # rusty_after_gap: about the coming session, uses all of their history
    why = _rusty(days_since_last, sessions, s)
    if why:
        results.append({"code": "rusty_after_gap", "step_id": None, "evidence": why})

    return results or [{"code": "none", "step_id": None, "evidence": ""}]
