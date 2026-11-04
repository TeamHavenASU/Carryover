"""Generate the fake event history the demo runs on.

Writes backend/data/live/events.csv in the format defined in logic/data_io.py.
Run from backend/:

    python -m sim.simulate

The random generator is seeded with SEED, so every run writes a byte-identical
file. All timing numbers (long pauses, start time, help levels, fading counts,
rusty rule) come from the task file and definitions.json, never from here.

Each resident has patterns that detect.py should find. detect.py only counts a
pattern if it shows up in every one of the person's last sessions_to_look_at
sessions, so every session in the last PATTERN_WINDOW_WEEKS weeks shows the
resident's patterns, and shows nothing else that could trip a code.
"""
from __future__ import annotations

import random
import statistics
import sys
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path

if __package__ in (None, ""):  # run as a plain script: make logic/ importable
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logic.data_io import (  # noqa: E402
    ALL_EVENTS,
    EVENT_COLUMNS,
    LIVE_EVENTS_PATH,
    load_definitions,
    load_task,
    used_help_events,
    write_events,
)

SEED = 20261104
START_DATE = date(2026, 9, 7)  # Monday of week 1
WEEKS = 10
SESSIONS_PER_WEEK = (2, 3, 3, 4)  # picked at random each week: roughly 3
PATTERN_WINDOW_WEEKS = 2  # every session in these last weeks shows the patterns

# ================================================================================
# RESIDENTS: edit names and patterns here. The logic below reads only this dict.
#
#   patterns      codes detect.py should find: cant_start, stuck_at_step (step_id),
#                 missing_step (step_id)
#   pattern_rate  chance a pattern shows in a session before the pattern window
#   skill_start   chance of doing a step alone in week 1
#   skill_gain    added to that chance each week
#   start_hours   (first, last) hour a session may start, local time
#   away_days     (first, last) day offsets from START_DATE with no sessions.
#                 Used to make a long gap so rusty_after_gap fires.
# ================================================================================
RESIDENTS = {
    "jeremiah": {
        "task_id": "heat_meal",
        "patterns": [
            {"code": "cant_start"},
            {"code": "stuck_at_step", "step_id": "s4"},
        ],
        "pattern_rate": 0.7,
        "skill_start": 0.45,
        "skill_gain": 0.03,
        "start_hours": (11, 12),
        "away_days": (31, 45),  # week 5 Thu to week 7 Mon: a 16+ day gap around week 6
    },
    "kayla": {
        "task_id": "heat_meal",
        "patterns": [
            {"code": "missing_step", "step_id": "s7"},
        ],
        "pattern_rate": 0.6,
        "skill_start": 0.5,
        "skill_gain": 0.04,
        "start_hours": (17, 18),
        "away_days": None,
    },
    "sam": {  # the contrast case: no pattern, improves over the 10 weeks
        "task_id": "heat_meal",
        "patterns": [],
        "pattern_rate": 0.0,
        "skill_start": 0.55,
        "skill_gain": 0.05,
        "start_hours": (12, 18),
        "away_days": None,
    },
}


# --------------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _defs() -> dict:
    """definitions.json, read once per run."""
    return load_definitions()


def _levels() -> list[str]:
    """Help modes from most help to least, e.g. ["split", "hint", "hide"]."""
    hl = _defs()["help_levels"]
    return [hl["most_help"], hl["some_help"], hl["no_help"]]


def _week_1_level() -> str:
    """The mode every step starts at in week 1 (help_levels.week_1_level)."""
    hl = _defs()["help_levels"]
    return hl[hl["week_1_level"]]


def long_pause(step: dict, task: dict) -> float:
    """The step's own long_pause_seconds, else the task's, else the default."""
    default = _defs()["defaults"]["long_pause_seconds"]
    return step.get("long_pause_seconds", task.get("long_pause_seconds", default))


def start_time(task: dict) -> float:
    """The task's start_time_seconds, else the default."""
    return task.get("start_time_seconds", _defs()["defaults"]["start_time_seconds"])


def _stamp(t: datetime) -> str:
    """Local time as YYYY-MM-DDTHH:MM:SS."""
    return t.strftime("%Y-%m-%dT%H:%M:%S")


def _row(person: str, task_id: str, week: int, t: datetime, event: str, **fields) -> dict:
    """One event row with every column present (empty when not used)."""
    assert event in ALL_EVENTS, f"unknown event {event}"
    row = dict.fromkeys(EVENT_COLUMNS, "")
    row.update(
        person_id=person,
        task_id=task_id,
        session_id=f"{person}-{task_id}-w{week:02d}",
        week=week,
        timestamp=_stamp(t),
        event=event,
    )
    row.update(fields)
    return row


def step_result(session: list[dict], step: dict, task: dict) -> tuple[str | None, str | None]:
    """How one step went in one past session: (help level shown, result).

    result is "struggled" (long pause, never finished, or check answer "no"),
    "helped" (help showed or was asked for), "alone", or None if not started.
    """
    sid = step["step_id"]
    rows = [r for r in session if r["step_id"] == sid]
    started = next((r for r in rows if r["event"] == "step_started"), None)
    if started is None:
        return None, None
    done = next((r for r in rows if r["event"] == "step_done"), None)
    long = (not step.get("wait")) and done is not None and done["seconds"] > long_pause(step, task)
    said_no = any(r["event"] == "check_answer" and r["answer"] == "no" for r in rows)
    if done is None or long or said_no:
        return started["help_shown"], "struggled"
    used = set(used_help_events())
    if done["prompted"] == "yes" or any(r["event"] in used for r in rows):
        return started["help_shown"], "helped"
    return started["help_shown"], "alone"


# --------------------------------------------------------------------------------
# Help level decider
# --------------------------------------------------------------------------------
def decide_help(person: str, task: dict, step_id: str, week: int, history: list[list[dict]]) -> str:
    """Return the help level shown for this step today: "split", "hint" or "hide".

    history is this person's earlier sessions for the task, oldest first, each
    a list of event rows.

    TEMPORARY: a simple scripted progression so the demo data looks right.
    Week 1 starts at help_levels.week_1_level. After the step is done alone
    rule_2_show_less_after_done_alone times at the current level it drops one
    level (toward "hide"); after struggling
    rule_4_more_help_after_struggled_in_a_row times in a row it rises one level
    (toward "split"). This will be replaced by a call into fade.py, a one-line
    change to the return below.
    """
    levels = _levels()
    rules = _defs()["fading_rules"]
    step = next(s for s in task["steps"] if s["step_id"] == step_id)

    current = _week_1_level()
    since_change: list[str] = []  # results at the current level, oldest first
    for session in history:
        shown, result = step_result(session, step, task)
        if shown is None:
            continue
        if shown != current:
            current, since_change = shown, []
        since_change.append(result)

    if week == 1:
        return _week_1_level()

    i = levels.index(current)
    up = rules["rule_4_more_help_after_struggled_in_a_row"]
    down = rules["rule_2_show_less_after_done_alone"]
    if len(since_change) >= up and all(r == "struggled" for r in since_change[-up:]):
        i = max(i - 1, 0)
    elif len(since_change) >= down and all(r == "alone" for r in since_change[-down:]):
        i = min(i + 1, len(levels) - 1)
    return levels[i]


# --------------------------------------------------------------------------------
# One session
# --------------------------------------------------------------------------------
def _pick_outcome(cfg: dict, step: dict, week: int, forced: str | None, in_window: bool, rng: random.Random) -> str:
    """Choose how a step goes: alone, offered, asked, stuck or missing."""
    if step.get("wait"):
        return "alone"
    if forced:
        return forced
    skill = min(0.95, cfg["skill_start"] + cfg["skill_gain"] * (week - 1))
    if rng.random() < skill:
        return "alone"
    if in_window:
        # In the pattern window nothing outside the resident's patterns may trip
        # a code, so help appears by itself but the person never asks or stalls.
        return "offered"
    return rng.choices(["offered", "asked", "stuck"], weights=[5, 3, 2])[0]


def simulate_session(
    person: str,
    cfg: dict,
    task: dict,
    week: int,
    start: datetime,
    days_since_last: int | None,
    rusty: bool,
    active: set[str],
    in_window: bool,
    session_number: int,
    history: list[list[dict]],
    rng: random.Random,
) -> list[dict]:
    """Return the event rows for one run through the task.

    active holds the pattern keys that show this session: "cant_start",
    "stuck_at_step:s4", "missing_step:s7" and so on.
    """
    tid = task["task_id"]
    rows: list[dict] = []
    t = start

    def add(event: str, **fields) -> None:
        rows.append(_row(person, tid, week, t, event, **fields))

    add("task_opened", days_since_last="" if days_since_last is None else days_since_last)
    if rusty:
        t += timedelta(seconds=rng.randint(5, 15))
        add("refresher_answer", answer="yes")

    # Getting started
    if "cant_start" in active:
        t += timedelta(seconds=rng.randint(20, 90))
        add("task_closed_no_start")
        t += timedelta(minutes=rng.randint(3, 25))
        add("task_opened")
        t += timedelta(seconds=round(start_time(task) * rng.uniform(1.3, 3.0)))
    else:
        t += timedelta(seconds=round(start_time(task) * rng.uniform(0.1, 0.6)))

    # The steps
    shown: dict[str, str] = {}
    results: dict[str, str] = {}
    for step in task["steps"]:
        sid = step["step_id"]
        lp = long_pause(step, task)
        level = decide_help(person, task, sid, week, history)
        shown[sid] = level
        add("step_started", step_id=sid, help_shown=level)

        forced = None
        if f"stuck_at_step:{sid}" in active:
            forced = "stuck"
        elif f"missing_step:{sid}" in active:
            forced = "missing"
        outcome = _pick_outcome(cfg, step, week, forced, in_window, rng)
        results[sid] = outcome

        if step.get("wait"):
            # A legitimate wait never counts as a long pause, so it stays under it.
            seconds = lp * rng.uniform(0.3, 0.95)
        elif outcome == "alone":
            seconds = lp * rng.uniform(0.25, 0.7)
        elif outcome == "offered":
            seconds = lp * rng.uniform(0.6, 0.95)
        elif outcome == "asked":
            seconds = lp * rng.uniform(0.4, 0.95)
        elif outcome == "stuck":
            seconds = lp * rng.uniform(1.3, 3.5)
        else:  # missing: started, then moved on without finishing
            seconds = lp * rng.uniform(0.2, 0.5)
        seconds = round(seconds, 1)

        if outcome == "asked":
            ask_at = t + timedelta(seconds=seconds * rng.uniform(0.3, 0.8))
            event = rng.choice(["hint_requested", "more_help_requested", "show_all_pressed"])
            rows.append(_row(person, tid, week, ask_at, event, step_id=sid, help_shown=level))
        elif outcome == "stuck" and rng.random() < 0.5:
            press_at = t + timedelta(seconds=lp * rng.uniform(0.8, 1.2))
            rows.append(_row(person, tid, week, press_at, "stuck_pressed", step_id=sid, help_shown=level))

        t += timedelta(seconds=seconds)
        if outcome != "missing":
            add(
                "step_done",
                step_id=sid,
                seconds=seconds,
                help_shown=level,
                prompted="no" if outcome == "alone" else "yes",
            )
        t += timedelta(seconds=rng.randint(2, 8))

    # Check questions: only folded steps that have one, every n sessions.
    every = _defs()["check_questions"]["ask_every_n_sessions"]
    if session_number % every == 0:
        for step in task["steps"]:
            sid = step["step_id"]
            if shown[sid] == _levels()[-1] and step.get("check_question"):
                t += timedelta(seconds=rng.randint(3, 10))
                answer = "no" if results[sid] in ("missing", "stuck") else "yes"
                add("check_answer", step_id=sid, help_shown=shown[sid], answer=answer)

    t += timedelta(seconds=rng.randint(2, 6))
    add("task_done")
    return rows


# --------------------------------------------------------------------------------
# A resident's 10 weeks
# --------------------------------------------------------------------------------
def _session_days(cfg: dict, week: int, rng: random.Random) -> list[int]:
    """Day offsets (from START_DATE) of this week's sessions, in order."""
    days = range(7 * (week - 1), 7 * week)
    away = cfg.get("away_days")
    if away:
        days = [d for d in days if not away[0] <= d <= away[1]]
    count = min(rng.choice(SESSIONS_PER_WEEK), len(days))
    return sorted(rng.sample(list(days), count))


def _is_rusty(days_since_last: int | None, past_gaps: list[int]) -> bool:
    """Rule 7: break over N x the usual (median) break and at least the minimum days."""
    if days_since_last is None:
        return False
    rules = _defs()["fading_rules"]
    if not past_gaps:
        return days_since_last >= rules["rule_7_rusty_days_if_no_history"]
    usual = statistics.median(past_gaps)
    return (
        days_since_last > rules["rule_7_rusty_times_usual_break"] * usual
        and days_since_last >= rules["rule_7_rusty_min_days"]
    )


def simulate_resident(person: str, cfg: dict, rng: random.Random) -> list[list[dict]]:
    """Return every session for one resident, oldest first."""
    task = load_task(cfg["task_id"])
    sessions: list[list[dict]] = []
    last_day: date | None = None
    gaps: list[int] = []
    for week in range(1, WEEKS + 1):
        in_window = week > WEEKS - PATTERN_WINDOW_WEEKS
        for day in _session_days(cfg, week, rng):
            hour = rng.randint(*cfg["start_hours"])
            start = datetime.combine(
                START_DATE + timedelta(days=day), time(hour, rng.randint(0, 59), rng.randint(0, 59))
            )
            since = None if last_day is None else (start.date() - last_day).days
            rusty = _is_rusty(since, gaps)

            active = set()
            for p in cfg["patterns"]:
                if in_window or rng.random() < cfg["pattern_rate"]:
                    active.add(p["code"] + (f":{p['step_id']}" if "step_id" in p else ""))

            sessions.append(
                simulate_session(
                    person, cfg, task, week, start, since, rusty, active, in_window,
                    len(sessions) + 1, sessions, rng,
                )
            )
            if since is not None:
                gaps.append(since)
            last_day = start.date()
    return sessions


# --------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------
def build_events() -> dict[str, list[list[dict]]]:
    """Simulate every resident. Returns {person: [session rows, ...]}."""
    rng = random.Random(SEED)
    return {person: simulate_resident(person, cfg, rng) for person, cfg in RESIDENTS.items()}


def main() -> None:
    """Regenerate backend/data/live/events.csv and print a short summary."""
    by_person = build_events()
    rows = [r for sessions in by_person.values() for s in sessions for r in s]
    rows.sort(key=lambda r: r["timestamp"])  # stable: keeps order within a session
    write_events(LIVE_EVENTS_PATH, rows)

    print(f"Wrote {len(rows)} rows to {LIVE_EVENTS_PATH}")
    for person, sessions in by_person.items():
        weeks = sorted({s[0]["week"] for s in sessions})
        missing = [w for w in range(1, WEEKS + 1) if w not in weeks]
        gaps = [s[0]["days_since_last"] for s in sessions if s[0]["days_since_last"] != ""]
        patterns = ", ".join(
            p["code"] + (f" ({p['step_id']})" if "step_id" in p else "") for p in RESIDENTS[person]["patterns"]
        ) or "none"
        print(
            f"  {person}: {len(sessions)} sessions, weeks {weeks[0]}-{weeks[-1]}"
            + (f" (no sessions in week {', '.join(map(str, missing))})" if missing else "")
            + f", longest gap {max(gaps)} days. Expected in last 2 sessions: {patterns}"
        )


if __name__ == "__main__":
    main()
