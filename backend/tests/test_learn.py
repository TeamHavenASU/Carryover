"""Tests for logic/learn.py. Small made-up scores and sessions, plus one run on the real events.csv."""
import json
import re

import pytest

from logic import learn
from logic.data_io import LIVE_EVENTS_PATH, load_definitions, load_events

DEFS = {
    "help_levels": {"most_help": "split", "some_help": "hint", "no_help": "hide", "week_1_level": "some_help"},
    "defaults": {"start_time_seconds": 60, "long_pause_seconds": 45, "opens_without_start_for_trouble_starting": 2},
    "fading_rules": {
        "rule_2_show_less_after_done_alone": 3,
        "rule_2_ask_again_after_keep_it": 3,
        "rule_4_more_help_after_struggled_in_a_row": 2,
        "rule_5_offer_up_front_after_opened_in_a_row": 3,
        "start_push_remove_after_started_alone": 3,
        "start_push_back_after_trouble_starting_in_a_row": 2,
    },
    "used_help_events": ["stuck_pressed", "hint_requested", "more_help_requested", "show_all_pressed", "ask_sent"],
    "take_a_break": {"new_session_after_hours": 12},
}

TASK = {
    "task_id": "toast",
    "start_time_seconds": 60,
    "long_pause_seconds": 40,
    "steps": [{"step_id": "s1", "text": "Put bread in"}, {"step_id": "s2", "text": "Press the lever"}],
}

STUCK_S4 = {"code": "stuck_at_step", "step_id": "s4", "evidence": ""}
CANT_START = {"code": "cant_start", "step_id": None, "evidence": ""}


def counts(tried, worked):
    return {"tried": tried, "worked": worked}


# ---- estimate and choose_help


def test_a_new_person_gets_the_everyone_based_choice():
    scores = {"_everyone": {"start_push": counts(40, 28), "show_step:s1": counts(40, 36)}}
    # no history of their own: w = 0, so the everyone rate 28/40 = 0.7 is used
    assert learn.estimate("new", "start_push", scores) == pytest.approx(0.7)
    assert learn.choose_help("new", CANT_START, scores, DEFS) == "start_push"


def test_own_history_takes_over_as_it_builds():
    # everyone: hint:s4 works 30 of 40 (0.75). This person keeps failing with it.
    everyone = {"hint:s4": counts(40, 30), "split_step:s4": counts(40, 36)}
    estimates = []
    for tried in (0, 5, 20):
        scores = {"_everyone": everyone, "p": {"hint:s4": counts(tried, 0)}}
        estimates.append(learn.estimate("p", "hint:s4", scores))
    # w = 0, 5/10 = 0.5, 20/25 = 0.8
    # estimate = 0.75, 0.5*0 + 0.5*0.75 = 0.375, 0.8*0 + 0.2*0.75 = 0.15
    assert estimates == pytest.approx([0.75, 0.375, 0.15])

    new_scores = {"_everyone": everyone}
    failing = {"_everyone": everyone, "p": {"hint:s4": counts(20, 0)}}
    assert learn.choose_help("p", STUCK_S4, new_scores, DEFS) == "hint:s4"
    assert learn.choose_help("p", STUCK_S4, failing, DEFS) == "split_step:s4"


def test_own_success_lifts_a_help_everyone_else_finds_weak():
    # everyone: start_push works 10 of 40 (0.25). This person: 10 of 10.
    scores = {"_everyone": {"start_push": counts(40, 10)}, "p": {"start_push": counts(10, 10)}}
    # w = 10/15 = 0.667; estimate = 0.667*1.0 + 0.333*0.25 = 0.75
    assert learn.estimate("p", "start_push", scores) == pytest.approx(0.75)
    assert learn.choose_help("p", CANT_START, scores, DEFS) == "start_push"


def test_the_lightest_help_that_is_good_enough_wins_not_the_heaviest():
    scores = {"_everyone": {"hint:s4": counts(10, 7), "split_step:s4": counts(10, 10)}}
    # hint 0.7 clears 0.6, so it is chosen even though split scores 1.0
    assert learn.choose_help("p", STUCK_S4, scores, DEFS) == "hint:s4"


def test_when_nothing_is_good_enough_the_highest_estimate_wins():
    scores = {"_everyone": {"hint:s4": counts(10, 3), "split_step:s4": counts(10, 5)}}
    assert learn.choose_help("p", STUCK_S4, scores, DEFS) == "split_step:s4"


def test_no_data_anywhere_is_a_coin_flip():
    assert learn.estimate("p", "refresher", {}) == 0.5
    assert learn.estimate("p", "refresher", {"_everyone": {}, "p": {}}) == 0.5
    # every rung ties at 0.5, under 0.6: the lightest of the tie
    assert learn.choose_help("p", STUCK_S4, {}, DEFS) == "hint:s4"
    assert learn.choose_help("p", {"code": "rusty_after_gap", "step_id": None}, {}, DEFS) == "refresher"


def test_none_gets_no_help():
    assert learn.choose_help("p", {"code": "none", "step_id": None, "evidence": ""}, {}, DEFS) is None


def test_ladders_use_the_detections_step():
    assert learn.ladder(STUCK_S4) == ["hint:s4", "split_step:s4"]
    assert learn.ladder({"code": "missing_step", "step_id": "s7"}) == ["hint:s7"]
    assert learn.ladder(CANT_START) == ["start_push", "show_step:s1"]


# ---- update_scores on made-up sessions


def row(event, time, step_id="", help_shown="", seconds=None, prompted="", answer="", person="p"):
    return {
        "person_id": person, "task_id": "toast", "session_id": f"{person}-toast-w01", "week": 1,
        "timestamp": time, "event": event, "step_id": step_id, "seconds": seconds,
        "days_since_last": None, "help_shown": help_shown, "answer": answer, "prompted": prompted,
    }


def session(day, s1_shown, s1_result, s2_shown="hide", person="p", refresher=False):
    """One session. s1 goes alone, opened (asked for a hint) or struggled; s2 is done alone."""
    t = f"2026-09-{day:02d}T10:00:"
    rows = [row("task_opened", t + "00", person=person)]
    if refresher:
        rows.append(row("refresher_answer", t + "02", answer="yes", person=person))
    rows.append(row("step_started", t + "05", "s1", s1_shown, person=person))
    if s1_result == "opened":
        rows.append(row("hint_requested", t + "10", "s1", s1_shown, person=person))
    seconds = 90.0 if s1_result == "struggled" else 20.0
    rows.append(row("step_done", t + "25", "s1", s1_shown, seconds, "no", person=person))
    rows.append(row("step_started", t + "30", "s2", s2_shown, person=person))
    rows.append(row("step_done", t + "40", "s2", s2_shown, 10.0, "no", person=person))
    rows.append(row("task_done", t + "50", person=person))
    return rows


@pytest.fixture
def toast(monkeypatch):
    monkeypatch.setattr(learn, "load_task", lambda task_id: TASK)


def test_update_scores_counts_each_help_for_the_person_and_everyone(toast, tmp_path):
    events = session(7, "split", "alone") + session(8, "hint", "opened") + session(9, "hint", "struggled")
    events += session(7, "hint", "alone", person="q")
    path = tmp_path / "scores.json"
    scores = learn.update_scores(events, path=path, defs=DEFS)

    # split worked (alone through its own small steps); hint opened and struggled did not
    assert scores["p"]["split_step:s1"] == counts(1, 1)
    assert scores["p"]["hint:s1"] == counts(2, 0)
    assert scores["p"]["show_step:s1"] == counts(3, 1)
    assert scores["q"]["hint:s1"] == counts(1, 1)
    assert scores["_everyone"]["hint:s1"] == counts(3, 1)
    assert scores["_everyone"]["show_step:s1"] == counts(4, 2)
    # s2 was folded every time: no help shown, nothing counted
    assert not any(code.endswith(":s2") for code in scores["_everyone"])
    assert json.loads(path.read_text()) == scores


def test_refresher_counts_when_said_yes_and_works_without_a_struggle(toast):
    events = session(7, "hint", "alone", refresher=True) + session(8, "hint", "struggled", refresher=True)
    scores = learn.update_scores(events, path=None, defs=DEFS)
    assert scores["p"]["refresher"] == counts(2, 1)


# ---- update_scores on the real events.csv


def test_update_scores_on_the_real_events(tmp_path):
    events = load_events(LIVE_EVENTS_PATH)
    path = tmp_path / "scores.json"
    scores = learn.update_scores(events, path=path, defs=load_definitions())

    assert json.loads(path.read_text()) == scores
    people = {r["person_id"] for r in events}
    assert set(scores) == people | {"_everyone"}
    assert {"jeremiah", "kayla", "sam"} <= set(scores)

    code_pattern = re.compile(r"^(start_push|refresher|(show_step|hint|split_step):s\d+)$")
    for who, codes in scores.items():
        for code, c in codes.items():
            assert code_pattern.match(code), code
            assert 0 <= c["worked"] <= c["tried"], (who, code, c)

    # _everyone is exactly the sum of the people
    for code, c in scores["_everyone"].items():
        tried = sum(scores[p].get(code, {}).get("tried", 0) for p in people)
        worked = sum(scores[p].get(code, {}).get("worked", 0) for p in people)
        assert c == counts(tried, worked)

    # jeremiah has trouble starting, so he has had the start push; sam never has
    assert scores["jeremiah"]["start_push"]["tried"] > 0
    assert "start_push" not in scores["sam"]
