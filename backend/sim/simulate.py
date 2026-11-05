"""Generate the fake event history the demo runs on.

Writes backend/data/live/events.csv in the format defined in logic/data_io.py.
Run from backend/:

    python -m sim.simulate --force

The app's POST /event appends to the same file, so the simulator refuses to
overwrite it unless --force is given.

The random generator is seeded with SEED, so every run writes a byte-identical
file. All timing numbers (long pauses, start time, help levels, fading counts,
hint waits, rusty rule, skill cards) come from the task files and
definitions.json. Step and substep ids are read from the task files.

When patterns show: fade.build_view(week=N) only reads events up to week N-1,
and detect.py only counts a pattern if it shows up in every one of the last
sessions_to_look_at sessions. So every session from PATTERN_FROM_WEEK on shows
the resident's patterns (and nothing else that could trip a code). Any view
from week PATTERN_FROM_WEEK + 1 onward then finds them.

Session boundaries: detect.py splits sessions at task_done, or when the person
was away longer than take_a_break.new_session_after_hours (12). Every session
here ends with task_done and starts more than 12 hours after the previous one
ended (checked in simulate_resident). fade.py must split sessions the same way.
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path

if __package__ in (None, ""):  # run as a plain script: make logic/ importable
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logic import fade  # noqa: E402
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
END_DATE = date(2026, 11, 4)  # the last session falls on or before this day
WEEKS = 10
START_DATE = END_DATE - timedelta(days=7 * WEEKS - 1)  # first day of week 1
SESSIONS_PER_WEEK = (2, 3, 3, 4)  # picked at random each week: roughly 3
PATTERN_FROM_WEEK = WEEKS - 2  # patterns show in every session of weeks 8, 9 and 10

# ================================================================================
# RESIDENTS: edit names and patterns here. The logic below reads only this dict.
#
#   task_id        the task they do
#   patterns       codes detect.py should find: cant_start, stuck_at_step (step_id),
#                  missing_step (step_id). For missing_step the person forgets the
#                  step: when it is folded they answer "no" to its check question,
#                  otherwise they start it and never finish it.
#   pattern_rate   chance a pattern shows in a session before PATTERN_FROM_WEEK
#   skill_start    chance of doing a step alone in week 1
#   skill_gain     added to that chance each week
#   start_hours    (first, last) hour a session may start, local time
#   away_days      (first, last) day offsets from START_DATE with no sessions.
#                  A gap of 14+ days makes rusty_after_gap fire on return.
#   device_check   answer to the task's first_time_question (default "yes").
#                  "no" starts every step at most help.
#   unsure_skills  base skills answered "not_sure" at the skill check, so their
#                  skill card shows until no longer needed
#   phone          which substeps_by_phone list to use (phone tasks only)
#   keep_less_help {step_id: [n, ...]}: answer "keep" to the n-th Rule 2 offer of
#                  less help on that step. Every other offer is answered "yes".
# ================================================================================
_DEMO = {
    "jeremiah": {
        "task_id": "heat_meal",
        "patterns": [
            {"code": "cant_start"},
            {"code": "stuck_at_step", "step_id": "s4"},
        ],
        "pattern_rate": 0.7,
        "skill_start": 0.35,
        "skill_gain": 0.01,
        "start_hours": (11, 12),
        "away_days": (31, 45),  # a 16+ day gap around week 6: rusty_after_gap
    },
    "kayla": {
        "task_id": "heat_meal",
        "patterns": [
            {"code": "missing_step", "step_id": "s7"},
        ],
        "pattern_rate": 0.4,
        "skill_start": 0.5,
        "skill_gain": 0.04,
        "start_hours": (17, 18),
        # Demo beat: offered less help on s3, she says "keep" and the app respects it.
        # s3 has no check question, so this changes no random draws.
        "keep_less_help": {"s3": [1]},
    },
    "sam": {  # the contrast case: no pattern, improves over the 10 weeks
        "task_id": "heat_meal",
        "patterns": [],
        "pattern_rate": 0.0,
        "skill_start": 0.55,
        "skill_gain": 0.05,
        "start_hours": (12, 18),
    },
}


def _bg(task_id, patterns=(), start_hours=(10, 15), skill=(0.5, 0.04), **extra):
    """A background resident: same fields as the demo three, shorter to write."""
    return {
        "task_id": task_id,
        "patterns": [dict(code=c, step_id=s) if s else dict(code=c) for c, s in patterns],
        "pattern_rate": 0.5,
        "skill_start": skill[0],
        "skill_gain": skill[1],
        "start_hours": start_hours,
        **extra,
    }


# Background residents fill out the staff screens. Each code shows in 3 or 4
# residents in total (demo three included), at different steps and tasks.
_BACKGROUND = {
    "maria": _bg("heat_meal", [("cant_start", None)], (11, 13)),
    "devon": _bg("heat_meal", [("stuck_at_step", "s1")], (17, 19), unsure_skills=["read_cooking_time"]),
    "priya": _bg("heat_meal", [("missing_step", "s2")], (12, 13)),
    "luis": _bg("heat_meal", [], (18, 19), away_days=(14, 30)),  # rusty in week 5
    "ana": _bg("heat_meal", [], (12, 14), skill=(0.6, 0.04)),
    "tom": _bg("buy_instore_card", [("cant_start", None)], (10, 12)),
    "grace": _bg("buy_instore_card", [("stuck_at_step", "s8")], (14, 16), unsure_skills=["tap_or_insert_card"]),
    "omar": _bg("buy_instore_card", [("missing_step", "s9")], (11, 13)),
    "lena": _bg("buy_instore_card", [], (13, 15), device_check="no"),
    "felix": _bg("buy_instore_phone", [("stuck_at_step", "s3")], (15, 17), phone="android"),
    "nina": _bg("buy_instore_phone", [], (10, 12), phone="iphone_face_id", away_days=(52, 66)),  # rusty in week 10
    "jay": _bg("buy_instore_phone", [], (16, 18), phone="iphone_home_button", skill=(0.6, 0.04)),
    "rosa": _bg("buy_online", [("cant_start", None)], (19, 20)),
    "ben": _bg("buy_online", [("missing_step", "s8")], (20, 21), unsure_skills=["read_total_on_screen"]),
    "carl": _bg("buy_online", [], (9, 11), away_days=(24, 40)),  # rusty in week 6
    "mei": _bg("buy_online", [], (13, 15), unsure_skills=["compare_two_prices"], skill=(0.6, 0.04)),
}

RESIDENTS = {**_DEMO, **_BACKGROUND}

WAIT_STEP_SECONDS = (120, 240)  # realistic time on a wait: true step (heating, standing in line)


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


def _start_level(person: str) -> str:
    """The level every step starts at: help_levels.week_1_level, or most help
    if the person said "no" to the task's first_time_question."""
    if RESIDENTS[person].get("device_check") == "no":
        return _levels()[0]
    hl = _defs()["help_levels"]
    return hl[hl["week_1_level"]]


def long_pause(step: dict, task: dict) -> float:
    """The step's own long_pause_seconds, else the task's, else the default."""
    default = _defs()["defaults"]["long_pause_seconds"]
    return step.get("long_pause_seconds", task.get("long_pause_seconds", default))


def start_time(task: dict) -> float:
    """The task's start_time_seconds, else the default."""
    return task.get("start_time_seconds", _defs()["defaults"]["start_time_seconds"])


def offer_times(step: dict, task: dict) -> list[float]:
    """Seconds into the step when Rule 6 offers help. Never on wait: true steps:
    the app never offers help or shows delayed help during a wait."""
    if step.get("wait"):
        return []
    fractions = _defs()["fading_rules"]["rule_6_hint_wait_fractions_of_long_pause"]
    return [f * long_pause(step, task) for f in fractions]


def substep_ids(step: dict, cfg: dict) -> list[str]:
    """The step's small step ids from the task file (by phone type if it has them)."""
    subs = step.get("substeps") or step.get("substeps_by_phone", {}).get(cfg.get("phone"), [])
    return [s["id"] for s in subs if isinstance(s, dict)]


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
    "helped" (prompted, or a used-help event such as skill_card_shown),
    "alone", or None if not started. small_step_opened is not used help: it is
    the level's own content.
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
    Week 1 starts at help_levels.week_1_level (most help after a "no" to the
    device check). It drops one level (toward "hide") only after the person
    answered "yes" to Rule 2's offer of less help (the end_question rows
    written in simulate_session); a "keep" holds it. After struggling
    rule_4_more_help_after_struggled_in_a_row times in a row it rises one level
    (toward "split"). This will be replaced by a call into fade.py, a one-line
    change to the return below.
    """
    levels = _levels()
    rules = _defs()["fading_rules"]
    step = next(s for s in task["steps"] if s["step_id"] == step_id)

    current = _start_level(person)
    since_change: list[str] = []  # results at the current level, oldest first
    said_yes = False  # "yes" to less help since the level last changed
    for session in history:
        shown, result = step_result(session, step, task)
        if shown is None:
            continue
        if shown != current:
            current, since_change, said_yes = shown, [], False
        since_change.append(result)
        answer = _less_help_answer(session, step_id)
        if answer == fade.LESS_HELP_KEEP:
            since_change, said_yes = [], False
        elif answer == fade.LESS_HELP_YES:
            said_yes = True

    if week == 1:
        return _start_level(person)

    i = levels.index(current)
    up = rules["rule_4_more_help_after_struggled_in_a_row"]
    if len(since_change) >= up and all(r == "struggled" for r in since_change[-up:]):
        i = max(i - 1, 0)
    elif said_yes:
        i = min(i + 1, len(levels) - 1)
    return levels[i]


def _less_help_answer(session: list[dict], step_id: str) -> str | None:
    """The Rule 2 answer ("yes" or "keep") for this step in a session, or None."""
    answers = [r["answer"] for r in session if r["event"] == "end_question" and r["step_id"] == step_id]
    return answers[-1] if answers else None


# --------------------------------------------------------------------------------
# One step
# --------------------------------------------------------------------------------
def _pick_outcome(cfg: dict, step: dict, week: int, forced: str | None, in_window: bool, rng: random.Random) -> str:
    """Choose how a step goes: alone, offered, asked, stuck or forgot."""
    if step.get("wait"):
        return "alone"
    if forced:
        return forced
    skill = min(0.95, cfg["skill_start"] + cfg["skill_gain"] * (week - 1))
    if rng.random() < skill:
        return "alone"
    if in_window:
        # From PATTERN_FROM_WEEK on nothing outside the resident's patterns may
        # trip a code: the person accepts the Rule 6 offer but never asks or stalls.
        return "offered"
    return rng.choices(["offered", "asked", "stuck"], weights=[5, 3, 2])[0]


def _step_rows(step: dict, task: dict, cfg: dict, level: str, outcome: str, skill: float, rng: random.Random):
    """Plan one step. Returns (seconds, prompted, [(offset_seconds, event, fields)]).

    prompted is "yes" only when help appeared by itself during the step: the
    person said yes to the Rule 6 offer. What the level shows when the step
    starts (at split, the first small step) is not a prompt.
    """
    lp = long_pause(step, task)
    offers = offer_times(step, task)
    planned: list[tuple[float, str, dict]] = []
    prompted = "no"

    if step.get("wait"):
        seconds = rng.uniform(*WAIT_STEP_SECONDS)
    elif outcome in ("alone", "forgot"):
        seconds = lp * rng.uniform(0.15, 0.7)
        planned += [(o, "help_offer_answer", {"answer": "no"}) for o in offers if o < seconds]
    elif outcome == "offered":
        k = rng.randrange(len(offers))
        planned += [(o, "help_offer_answer", {"answer": "no"}) for o in offers[:k]]
        planned.append((offers[k], "help_offer_answer", {"answer": "yes"}))
        seconds = min(offers[k] + lp * rng.uniform(0.05, 0.25), lp * 0.95)
        prompted = "yes"
    elif outcome == "asked":
        ask_at = offers[0] * rng.uniform(0.3, 0.9)  # asks before the first offer
        event = rng.choice(["hint_requested", "more_help_requested", "show_all_pressed", "repeat_requested"])
        planned.append((ask_at, event, {}))
        seconds = lp * rng.uniform(0.3, 0.8)
    else:  # stuck: a long pause
        seconds = lp * rng.uniform(1.3, 3.5)
        accepts_last = rng.random() < 0.5
        for j, o in enumerate(offers):
            yes = accepts_last and j == len(offers) - 1
            planned.append((o, "help_offer_answer", {"answer": "yes" if yes else "no"}))
        prompted = "yes" if accepts_last else "no"
        if rng.random() < 0.5:
            planned.append((lp * rng.uniform(0.8, 1.2), "stuck_pressed", {}))

    # At split the first small step shows with the step; each "Show next small
    # step" tap is a small_step_opened. People who need more help open more.
    subs = substep_ids(step, cfg)
    if level == _levels()[0] and len(subs) > 1:
        rest = subs[1:]
        if outcome in ("offered", "asked", "stuck"):
            opened = len(rest)
        else:
            opened = rng.randint(0, round(len(rest) * (1 - skill)))
        times = sorted(rng.uniform(0.05, 0.6) * seconds for _ in range(opened))
        planned += [(t, "small_step_opened", {"answer": sub}) for t, sub in zip(times, rest)]

    planned.sort(key=lambda p: p[0])
    return round(seconds, 1), prompted, planned


# --------------------------------------------------------------------------------
# One session
# --------------------------------------------------------------------------------
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
    cards: dict[str, dict],
    rng: random.Random,
) -> list[dict]:
    """Return the event rows for one run through the task, ending with task_done.

    active holds the pattern keys that show this session: "cant_start",
    "stuck_at_step:s4", "missing_step:s7" and so on. in_window is True from
    PATTERN_FROM_WEEK on. cards holds this person's skill card state and is
    updated in place.
    """
    tid = task["task_id"]
    rows: list[dict] = []
    t = start
    skill = min(0.95, cfg["skill_start"] + cfg["skill_gain"] * (week - 1))
    card_rules = _defs()["skill_cards"]

    def add(at: datetime, event: str, **fields) -> None:
        rows.append(_row(person, tid, week, at, event, **fields))

    add(t, "task_opened", days_since_last="" if days_since_last is None else days_since_last)
    if rusty:
        t += timedelta(seconds=rng.randint(5, 15))
        add(t, "refresher_answer", answer="yes")

    # First time only: the device question and the skill check.
    if session_number == 1:
        if task.get("first_time_question"):
            t += timedelta(seconds=rng.randint(3, 6))
            add(t, "device_check_answer", answer=cfg.get("device_check", "yes"))
        for skill_id in cards:
            t += timedelta(seconds=rng.randint(3, 6))
            add(t, "skill_check_answer", answer=f"{skill_id}:{'not_sure' if cards[skill_id]['on'] else 'yes'}")

    # Getting started
    if "cant_start" in active:
        t += timedelta(seconds=rng.randint(20, 90))
        add(t, "task_closed_no_start")
        t += timedelta(minutes=rng.randint(3, 25))
        add(t, "task_opened")
        t += timedelta(seconds=round(start_time(task) * rng.uniform(1.3, 3.0)))
    else:
        t += timedelta(seconds=round(start_time(task) * rng.uniform(0.1, 0.5)))

    # Rule 2 offers for this session, decided from earlier sessions only.
    offered = {s["step_id"]: fade.offer_less_help(history, s, task, _defs()) for s in task["steps"]}

    # The steps
    shown: dict[str, str] = {}
    outcomes: dict[str, str] = {}
    for step in task["steps"]:
        sid = step["step_id"]
        level = decide_help(person, task, sid, week, history)
        shown[sid] = level

        forced = None
        if f"stuck_at_step:{sid}" in active:
            forced = "stuck"
        elif f"missing_step:{sid}" in active:
            forced = "forgot"
        outcome = _pick_outcome(cfg, step, week, forced, in_window, rng)
        outcomes[sid] = outcome
        seconds, prompted, planned = _step_rows(step, task, cfg, level, outcome, skill, rng)

        # A skill card shows before the step for each base skill still needing one.
        step_skills = [s for s in step.get("base_skills", []) if cards.get(s, {}).get("on")]
        for skill_id in step_skills:
            add(t, "skill_card_shown", step_id=sid, help_shown=level, answer=skill_id)
            t += timedelta(seconds=rng.randint(10, 25))

        add(t, "step_started", step_id=sid, help_shown=level)
        for offset, event, fields in planned:
            add(t + timedelta(seconds=offset), event, step_id=sid, help_shown=level, **fields)
        t += timedelta(seconds=seconds)
        # A forgotten step that is not folded is started and never finished.
        # A folded one goes by as done, and the check question below gets a "no".
        if not (outcome == "forgot" and level != _levels()[-1]):
            add(t, "step_done", step_id=sid, seconds=seconds, help_shown=level, prompted=prompted)

        # Skill cards fade like steps: after show_less_after_done_alone, the
        # person is asked and says the card is no longer needed.
        for skill_id in step.get("base_skills", []):
            card = cards.get(skill_id)
            if not card or not card["on"]:
                continue
            card["alone_run"] = card["alone_run"] + 1 if outcome == "alone" else 0
            if card["alone_run"] >= card_rules["show_less_after_done_alone"]:
                card["on"] = False
                t += timedelta(seconds=rng.randint(2, 5))
                add(t, "skill_card_not_needed", step_id=sid, answer=skill_id)
        t += timedelta(seconds=rng.randint(2, 8))

    # Check questions: only folded steps that have one, every n sessions. From
    # PATTERN_FROM_WEEK on a missing_step pattern step is asked every time. With
    # ask_every_n_sessions = 2 alone, a "no" could never show in two sessions in
    # a row, so detect (which needs it in every one of the last 2) never fires.
    every = _defs()["check_questions"]["ask_every_n_sessions"]
    for step in task["steps"]:
        sid = step["step_id"]
        if shown[sid] != _levels()[-1] or not step.get("check_question"):
            continue
        if session_number % every == 0 or (in_window and f"missing_step:{sid}" in active):
            t += timedelta(seconds=rng.randint(3, 10))
            add(t, "check_answer", step_id=sid, help_shown=shown[sid],
                answer="no" if outcomes[sid] == "forgot" else "yes")

    # Rule 2: the screen reads offer_less_help from the view it gets when the
    # task opens, which fade.py works out from earlier sessions only. So the
    # offer belongs to this session if it was due before this session began,
    # and the person answers at the end: an end_question row, "yes" (show me
    # less) or "keep". Fixed spacing (no random draws).
    for step in task["steps"]:
        sid = step["step_id"]
        if not offered[sid]:
            continue
        asked_before = sum(1 for s in history for r in s if r["event"] == "end_question" and r["step_id"] == sid)
        keep = asked_before + 1 in cfg.get("keep_less_help", {}).get(sid, [])
        t += timedelta(seconds=4)
        add(t, "end_question", step_id=sid, help_shown=shown[sid],
            answer=fade.LESS_HELP_KEEP if keep else fade.LESS_HELP_YES)

    t += timedelta(seconds=rng.randint(2, 6))
    add(t, "task_done")
    return rows


# --------------------------------------------------------------------------------
# A resident's 10 weeks
# --------------------------------------------------------------------------------
def _schedule(cfg: dict, rng: random.Random) -> list[tuple[int, datetime]]:
    """Every session's (week, start time), oldest first."""
    out = []
    away = cfg.get("away_days")
    for week in range(1, WEEKS + 1):
        days = [d for d in range(7 * (week - 1), 7 * week) if not (away and away[0] <= d <= away[1])]
        count = min(rng.choice(SESSIONS_PER_WEEK), len(days))
        for day in sorted(rng.sample(days, count)):
            clock = time(rng.randint(*cfg["start_hours"]), rng.randint(0, 59), rng.randint(0, 59))
            out.append((week, datetime.combine(START_DATE + timedelta(days=day), clock)))
    return out


def _is_rusty(days_since_last: int | None, past_gaps: list[int]) -> bool:
    """Rule 7: break over N x the usual (median) break and at least the minimum days."""
    if days_since_last is None:
        return False
    rules = _defs()["fading_rules"]
    if not past_gaps:
        return days_since_last >= rules["rule_7_rusty_days_if_no_history"]
    return (
        days_since_last > rules["rule_7_rusty_times_usual_break"] * statistics.median(past_gaps)
        and days_since_last >= rules["rule_7_rusty_min_days"]
    )


def simulate_resident(person: str, cfg: dict, rng: random.Random) -> list[list[dict]]:
    """Return every session for one resident, oldest first."""
    task = load_task(cfg["task_id"])
    schedule = _schedule(cfg, rng)
    # Skill card state, one entry per base skill the task uses, in step order.
    cards: dict[str, dict] = {}
    for step in task["steps"]:
        for skill_id in step.get("base_skills", []):
            cards.setdefault(skill_id, {"on": skill_id in cfg.get("unsure_skills", ()), "alone_run": 0})

    sessions: list[list[dict]] = []
    gaps: list[int] = []
    for n, (week, start) in enumerate(schedule, start=1):
        in_window = week >= PATTERN_FROM_WEEK
        since = None if not sessions else (start.date() - schedule[n - 2][1].date()).days
        active = {
            p["code"] + (f":{p['step_id']}" if "step_id" in p else "")
            for p in cfg["patterns"]
            if in_window or rng.random() < cfg["pattern_rate"]
        }
        sessions.append(
            simulate_session(person, cfg, task, week, start, since, _is_rusty(since, gaps),
                             active, in_window, n, sessions, cards, rng)
        )
        if since is not None:
            gaps.append(since)

    # Session boundaries must match detect.py: each ends with task_done, and the
    # next starts more than new_session_after_hours later.
    hours = _defs()["take_a_break"]["new_session_after_hours"]
    for a, b in zip(sessions, sessions[1:]):
        assert a[-1]["event"] == "task_done"
        away = datetime.fromisoformat(b[0]["timestamp"]) - datetime.fromisoformat(a[-1]["timestamp"])
        assert away > timedelta(hours=hours), f"{person}: sessions only {away} apart"
    return sessions


# --------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------
def build_events() -> dict[str, list[list[dict]]]:
    """Simulate every resident. Returns {person: [session rows, ...]}.

    The demo three come first in RESIDENTS, so adding background residents
    never changes their random draws.
    """
    rng = random.Random(SEED)
    return {person: simulate_resident(person, cfg, rng) for person, cfg in RESIDENTS.items()}


def main(argv: list[str] | None = None) -> int:
    """Regenerate backend/data/live/events.csv and print a short summary."""
    parser = argparse.ArgumentParser(description="Generate demo events.csv")
    parser.add_argument("--force", action="store_true", help="overwrite an existing events.csv")
    args = parser.parse_args(argv)

    if LIVE_EVENTS_PATH.exists() and not args.force:
        print(
            f"Refusing to overwrite {LIVE_EVENTS_PATH}.\n"
            "The app's POST /event appends live events to this file; regenerating it\n"
            "would lose them. Run again with --force to replace it anyway."
        )
        return 1

    by_person = build_events()
    rows = [r for sessions in by_person.values() for s in sessions for r in s]
    rows.sort(key=lambda r: r["timestamp"])  # stable: keeps order within a session
    write_events(LIVE_EVENTS_PATH, rows)

    print(f"Wrote {len(rows)} rows for {len(by_person)} residents to {LIVE_EVENTS_PATH}")
    print(f"Dates {rows[0]['timestamp'][:10]} to {rows[-1]['timestamp'][:10]}")
    for person, sessions in by_person.items():
        cfg = RESIDENTS[person]
        weeks = sorted({s[0]["week"] for s in sessions})
        missing = [w for w in range(1, WEEKS + 1) if w not in weeks]
        gaps = [s[0]["days_since_last"] for s in sessions if s[0]["days_since_last"] != ""]
        patterns = ", ".join(
            p["code"] + (f" ({p['step_id']})" if "step_id" in p else "") for p in cfg["patterns"]
        ) or "none"
        print(
            f"  {person:9} {cfg['task_id']:18} {len(sessions):2} sessions"
            + (f", no sessions in week {', '.join(map(str, missing))}" if missing else "")
            + f", longest gap {max(gaps)} days. From week {PATTERN_FROM_WEEK}: {patterns}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
