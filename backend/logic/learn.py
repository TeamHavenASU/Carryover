"""Learning which help works (Build Spec B4).

A new resident starts from what has worked for everyone, and shifts toward
their own history as it builds.

update_scores(events) counts, for every help code, how often it was tried and
how often it worked: once under the person and once under "_everyone". The
result is written to backend/data/scores.json.

choose_help(person_id, detection, scores, definitions) takes one sticking
point from detect.py and picks the lightest help on its ladder that probably
works for this person.

Help codes (exact strings):
    start_push              the one tiny first action, shown when starting is hard
    show_step:<step_id>     the step shown up front (level hint or split, not folded)
    hint:<step_id>          the step at Some help (mode "hint")
    split_step:<step_id>    the step at Most help (mode "split", small steps)
    refresher               the quick look at all steps after a long break

This module is standalone: nothing in fade.py or the routes calls it yet.
"""
from __future__ import annotations

import json
from pathlib import Path

from logic.data_io import DATA_DIR, LIVE_EVENTS_PATH, load_definitions, load_events, load_task
from logic.fade import split_sessions, start_push_on, started_with_trouble, step_result

SCORES_PATH = DATA_DIR / "scores.json"
EVERYONE = "_everyone"

# These three numbers are not in definitions.json yet. A "learn" block there
# ({"good_enough": ..., "prior_sessions": ..., "no_data_estimate": ...})
# overrides them, so Role A can move them without touching this file.
GOOD_ENOUGH = 0.6  # see choose_help for why
PRIOR_SESSIONS = 5  # how many of the person's own tries it takes to count half
NO_DATA_ESTIMATE = 0.5  # nobody has tried this help yet: a coin flip

# Help ladders, lightest first (Build Spec). "{step}" is the detection's step_id.
LADDERS = {
    "cant_start": ["start_push", "show_step:s1"],
    "stuck_at_step": ["hint:{step}", "split_step:{step}"],
    "missing_step": ["hint:{step}"],
    "rusty_after_gap": ["refresher"],
}

# Help level mode -> help code prefix for that step.
_MODE_CODES = {"hint": "hint", "split": "split_step"}


# --------------------------------------------------------------------------------
# Counting
# --------------------------------------------------------------------------------
def _add(scores: dict, person: str, code: str, worked: bool) -> None:
    """Count one try of a help code, under the person and under everyone."""
    for who in (person, EVERYONE):
        entry = scores.setdefault(who, {}).setdefault(code, {"tried": 0, "worked": 0})
        entry["tried"] += 1
        entry["worked"] += int(worked)


def _session_helps(session: list[dict], earlier: list[list[dict]], task: dict, defs: dict):
    """Yield (help code, worked) for every help shown in one session.

    Why "alone" is the test for a step: it means the level was ENOUGH. The
    person finished the step without reaching past it. "opened" means they
    asked for help beyond the level (a used-help event), not the level's own
    content, so working through a split step's small steps as shown still
    counts as alone. "struggled", "opened" and "prompted" (help had to appear
    by itself) all mean the level was not enough.

    start_push and refresher belong to the whole session, not one step, so
    they get the nearest test of the same idea:
      start_push worked if the person then started without trouble
      refresher  worked if no step in that session was a struggle
    """
    # The start push the app showed: worked out from earlier sessions only.
    if start_push_on(earlier, task, defs):
        yield "start_push", not started_with_trouble(session, task, defs)

    results = {}
    for step in task["steps"]:
        shown, result = step_result(session, step, task, defs)
        if result is None:
            continue
        results[step["step_id"]] = result
        prefix = _MODE_CODES.get(shown)
        if prefix:  # folded steps ("hide") had no help to score
            alone = result == "alone"
            yield f"show_step:{step['step_id']}", alone
            yield f"{prefix}:{step['step_id']}", alone

    # The person said yes to "Want a quick look at all the steps first?"
    if any(r["event"] == "refresher_answer" and r["answer"] == "yes" for r in session):
        yield "refresher", "struggled" not in results.values()


def update_scores(events: list[dict], path: str | Path | None = SCORES_PATH, defs: dict | None = None) -> dict:
    """Count tries and successes for every help code, per person and for everyone.

    events is any mix of people and tasks (load_events output). Returns
    {"_everyone": {code: {"tried", "worked"}}, "<person>": {...}, ...} and
    writes it to path as JSON (backend/data/scores.json by default; None to
    skip writing).
    """
    defs = defs or load_definitions()
    scores: dict = {EVERYONE: {}}
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in events:
        # feedback_answer rows are about the app, not a task, so their task_id is
        # empty. There is no task file to score them against: load_task("") raises.
        if not row.get("task_id"):
            continue
        groups.setdefault((row["person_id"], row["task_id"]), []).append(row)

    for (person, task_id), rows in sorted(groups.items()):
        task = load_task(task_id)
        rows = sorted(rows, key=lambda r: r["timestamp"])
        sessions = split_sessions(rows, defs)
        for i, session in enumerate(sessions):
            for code, worked in _session_helps(session, sessions[:i], task, defs):
                _add(scores, person, code, worked)

    # Stable order: everyone first, then people A-Z, codes A-Z.
    ordered = {who: dict(sorted(scores[who].items())) for who in [EVERYONE] + sorted(k for k in scores if k != EVERYONE)}
    if path is not None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ordered, f, indent=2)
            f.write("\n")
    return ordered


# --------------------------------------------------------------------------------
# Choosing
# --------------------------------------------------------------------------------
def _settings(definitions: dict | None) -> tuple[float, float, float]:
    """(good_enough, prior_sessions, no_data_estimate), from definitions if set there."""
    learn = (definitions or {}).get("learn", {})
    return (
        learn.get("good_enough", GOOD_ENOUGH),
        learn.get("prior_sessions", PRIOR_SESSIONS),
        learn.get("no_data_estimate", NO_DATA_ESTIMATE),
    )


def estimate(person_id: str, code: str, scores: dict, definitions: dict | None = None) -> float:
    """How likely this help is to work for this person, from 0 to 1.

        w        = tried / (tried + 5)          tried = this person's count
        estimate = w * person rate + (1 - w) * everyone rate

    With no tries of their own, w is 0 and the everyone rate is used. As the
    person's tries grow, their own rate takes over: 5 tries count half
    (w = 0.5), 20 tries count 0.8. No everyone data either: 0.5.
    """
    _, prior, no_data = _settings(definitions)
    everyone = scores.get(EVERYONE, {}).get(code)
    base = everyone["worked"] / everyone["tried"] if everyone and everyone["tried"] else no_data
    mine = scores.get(person_id, {}).get(code)
    if not mine or not mine["tried"]:
        return base
    w = mine["tried"] / (mine["tried"] + prior)
    return w * (mine["worked"] / mine["tried"]) + (1 - w) * base


def ladder(detection: dict) -> list[str]:
    """The help codes for a detection, lightest first. Empty for "none"."""
    steps = LADDERS.get(detection.get("code"), [])
    return [code.format(step=detection.get("step_id")) for code in steps]


def choose_help(person_id: str, detection: dict, scores: dict, definitions: dict | None) -> str | None:
    """Pick the help to use for one sticking point from detect.py.

    Walks the ladder lightest first and returns the first help whose estimate
    is GOOD_ENOUGH (0.6) or more. If none reaches it, returns the one with the
    highest estimate (the lightest of any tie). Returns None for "none".

    Why lightest first: heavier help almost always has a better success rate,
    so picking the highest scorer would always land on Most help and fight
    the fading. Walking the ladder lightest first and stopping at the first
    adequate one is what keeps help minimal.

    Why 0.6: we want help that probably works (better than a coin flip), but
    we always try lighter help first, because less help is the goal.

    Worked example: jeremiah's real week 10 detection, stuck_at_step s4,
    with scores from weeks 1 to 9 of the demo data (events.csv):
        hint:s4        everyone 126 worked of 228 tried  -> rate 0.553
                       jeremiah   3 worked of   7 tried  -> rate 0.429
                       w = 7 / (7 + 5) = 0.583
                       estimate = 0.583 * 0.429 + 0.417 * 0.553 = 0.250 + 0.230 = 0.480
        split_step:s4  everyone   5 worked of  21 tried  -> rate 0.238
                       jeremiah   2 worked of  15 tried  -> rate 0.133
                       w = 15 / (15 + 5) = 0.750
                       estimate = 0.750 * 0.133 + 0.250 * 0.238 = 0.100 + 0.060 = 0.160
        Neither reaches 0.6, so the highest estimate wins: hint:s4 (0.480).
        A new resident with the same detection has w = 0 and gets the everyone
        rates, hint:s4 0.553 and split_step:s4 0.238: again hint:s4.
    """
    rungs = ladder(detection)
    if not rungs:
        return None
    good_enough, _, _ = _settings(definitions)
    estimates = [(code, estimate(person_id, code, scores, definitions)) for code in rungs]
    for code, value in estimates:
        if value >= good_enough:
            return code
    best = max(value for _, value in estimates)
    return next(code for code, value in estimates if value == best)


def main() -> None:
    """Recount every help in backend/data/live/events.csv into backend/data/scores.json.

    Run from backend/:  python -m logic.learn
    """
    scores = update_scores(load_events(LIVE_EVENTS_PATH))
    print(f"Wrote {SCORES_PATH}: {len(scores[EVERYONE])} help codes, {len(scores) - 1} residents")


if __name__ == "__main__":
    main()
