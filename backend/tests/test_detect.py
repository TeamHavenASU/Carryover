"""Tests for logic/detect.py (Role A, Build Spec A3).

Small hand-written event lists, one idea per test. The last tests run detect
on the simulator's data (backend/data/live/events.csv) to check that each fake
resident trips the code they were built for.
"""
from datetime import datetime, timedelta

import pytest

from logic.data_io import LIVE_EVENTS_PATH, load_definitions, load_events, load_task
from logic.detect import detect, skill_cards_to_show, split_sessions, steps_with_breaks, usual_break, _settings

DEFS = load_definitions()
TASK = load_task("heat_meal")
LONG = TASK["long_pause_seconds"]  # 45
START = TASK["start_time_seconds"]  # 60


# --------------------------------------------------------------------------------
# A tiny helper to write sessions by hand
# --------------------------------------------------------------------------------
class Session:
    """Build one session's events. Each add() moves the clock forward."""

    def __init__(self, week=1, start=None, days_since_last=None, person="test"):
        self.t = start or datetime(2026, 11, 2, 12, 0, 0) + timedelta(days=7 * (week - 1))
        self.week = week
        self.person = person
        self.rows = []
        self.add("task_opened", wait=0, days_since_last=days_since_last)

    def add(self, event, step_id="", wait=5, **extra):
        self.t += timedelta(seconds=wait)
        row = {
            "person_id": self.person, "task_id": "heat_meal",
            "session_id": f"{self.person}-heat_meal-w{self.week:02d}", "week": self.week,
            "timestamp": self.t.strftime("%Y-%m-%dT%H:%M:%S"), "event": event, "step_id": step_id,
            "seconds": None, "days_since_last": None, "help_shown": "", "answer": "", "prompted": "",
        }
        row.update(extra)
        self.rows.append(row)
        return self

    def step(self, sid, took=10, prompted="no"):
        self.add("step_started", sid, wait=3)
        self.add("step_done", sid, wait=took, seconds=took, prompted=prompted)
        return self

    def all_steps(self, slow=None, skip_done=None):
        for st in TASK["steps"]:
            sid = st["step_id"]
            if sid == skip_done:
                self.add("step_started", sid, wait=3)
                continue
            self.step(sid, took=(LONG * 2 if sid == slow else 10))
        return self

    def done(self):
        return self.add("task_done", wait=3)


def codes(result):
    return sorted((r["code"], r["step_id"]) for r in result)


def smooth(week, **kw):
    return Session(week, **kw).all_steps().done().rows


# --------------------------------------------------------------------------------
# none
# --------------------------------------------------------------------------------
def test_nothing_found_returns_none():
    events = smooth(1) + smooth(2)
    assert detect(events, DEFS, 7, TASK) == [{"code": "none", "step_id": None, "evidence": ""}]


def test_no_events_and_no_gap_returns_none():
    assert codes(detect([], DEFS, 0, TASK)) == [("none", None)]


# --------------------------------------------------------------------------------
# cant_start
# --------------------------------------------------------------------------------
def opened_twice(week):
    return (Session(week).add("task_closed_no_start", wait=30)
            .add("task_opened", wait=300).all_steps().done().rows)


def test_cant_start_when_opened_twice_in_both_sessions():
    events = opened_twice(1) + opened_twice(2)
    result = detect(events, DEFS, 7, TASK)
    assert ("cant_start", None) in codes(result)
    assert "opened 2 times" in result[0]["evidence"]


def test_cant_start_when_slow_to_start():
    def slow(week):
        s = Session(week)
        s.t += timedelta(seconds=START + 30)  # waits longer than the start time
        return s.all_steps().done().rows
    assert ("cant_start", None) in codes(detect(slow(1) + slow(2), DEFS, 7, TASK))


def test_cant_start_needs_every_session_looked_at():
    # Only the older of the last 2 sessions had trouble: not a pattern.
    events = opened_twice(1) + smooth(2)
    assert ("cant_start", None) not in codes(detect(events, DEFS, 7, TASK))


def test_only_last_two_sessions_count():
    events = opened_twice(1) + opened_twice(2) + smooth(3) + smooth(4)
    assert codes(detect(events, DEFS, 7, TASK)) == [("none", None)]


# --------------------------------------------------------------------------------
# stuck_at_step
# --------------------------------------------------------------------------------
def test_stuck_after_long_pause_in_both_sessions():
    events = (Session(1).all_steps(slow="s4").done().rows
              + Session(2).all_steps(slow="s4").done().rows)
    result = detect(events, DEFS, 7, TASK)
    assert codes(result) == [("stuck_at_step", "s4")]
    assert "long pause at s4" in result[0]["evidence"]


def test_stuck_when_pressed_stuck_or_asked_for_hint():
    def pressed(week, event):
        s = Session(week)
        for st in TASK["steps"]:
            sid = st["step_id"]
            s.add("step_started", sid, wait=3)
            if sid == "s3":
                s.add(event, sid, wait=5)
            s.add("step_done", sid, wait=5, seconds=10)
        return s.done().rows
    events = pressed(1, "stuck_pressed") + pressed(2, "hint_requested")
    assert codes(detect(events, DEFS, 7, TASK)) == [("stuck_at_step", "s3")]


def test_step_own_long_pause_is_used():
    # s1 has its own long pause of 90 s, so 60 s there is fine.
    def s1_slowish(week):
        s = Session(week)
        s.step("s1", took=60)
        for st in TASK["steps"][1:]:
            s.step(st["step_id"])
        return s.done().rows
    assert codes(detect(s1_slowish(1) + s1_slowish(2), DEFS, 7, TASK)) == [("none", None)]


def test_slow_start_is_not_stuck_at_first_step():
    # Waiting before step 1 is cant_start, not stuck_at_step at s1.
    def slow(week):
        s = Session(week)
        s.t += timedelta(seconds=TASK["steps"][0]["long_pause_seconds"] + 60)
        return s.all_steps().done().rows
    found = codes(detect(slow(1) + slow(2), DEFS, 7, TASK))
    assert ("stuck_at_step", "s1") not in found
    assert ("cant_start", None) in found


def test_waiting_steps_never_count_as_long_pause():
    # s5 (stir halfway) is wait: true, so a long time there is fine.
    events = (Session(1).all_steps(slow="s5").done().rows
              + Session(2).all_steps(slow="s5").done().rows)
    assert codes(detect(events, DEFS, 7, TASK)) == [("none", None)]


def test_break_time_is_not_a_long_pause():
    def with_break(week):
        s = Session(week)
        for st in TASK["steps"]:
            sid = st["step_id"]
            s.add("step_started", sid, wait=3)
            if sid == "s4":
                s.add("paused", sid, wait=5)
                s.add("resumed", sid, wait=1800, seconds=1800)  # 30 min break
            s.add("step_done", sid, wait=10)
        return s.done().rows
    assert codes(detect(with_break(1) + with_break(2), DEFS, 7, TASK)) == [("none", None)]


# --------------------------------------------------------------------------------
# missing_step
# --------------------------------------------------------------------------------
def answered(week, answer, sid="s7"):
    """A smooth session where the check question for sid was asked and answered."""
    return Session(week).all_steps().add("check_answer", sid, answer=answer).done().rows


ASK_EVERY = DEFS["check_questions"]["ask_every_n_sessions"]  # 2
LOOK_AT = DEFS["sessions_to_look_at"]  # 2


def test_missing_when_check_answer_no():
    result = detect(answered(1, "no") + answered(2, "no"), DEFS, 7, TASK)
    assert codes(result) == [("missing_step", "s7")]
    assert "said no to the check question for s7" in result[0]["evidence"]


def test_missing_counts_check_asks_not_sessions():
    # Option C: the question is only asked every 2nd session, so "no" at
    # sessions 1 and 3 (not asked at 2 and 4) is two "no"s in a row.
    events = answered(1, "no") + smooth(2) + answered(3, "no") + smooth(4)
    result = detect(events, DEFS, 7, TASK)
    assert codes(result) == [("missing_step", "s7")]
    assert f"last {LOOK_AT} times it was asked" in result[0]["evidence"]


def test_missing_check_resets_on_yes_in_between():
    events = answered(1, "no") + answered(2, "yes") + answered(3, "no")
    assert ("missing_step", "s7") not in codes(detect(events, DEFS, 7, TASK))


def test_missing_check_ignores_old_answers():
    # Both "no"s are older than the last LOOK_AT x ASK_EVERY (4) sessions.
    old = answered(1, "no") + answered(2, "no")
    newer = sum((smooth(w) for w in range(3, 3 + LOOK_AT * ASK_EVERY)), [])
    assert ("missing_step", "s7") not in codes(detect(old + newer, DEFS, 7, TASK))


def test_missing_check_window_comes_from_definitions():
    # With ask_every_n_sessions = 1 the window shrinks to 2 sessions, so the
    # same "no at 1 and 3" pattern no longer counts. Proves the 4 isn't typed in.
    defs = dict(DEFS, check_questions={"ask_every_n_sessions": 1})
    events = answered(1, "no") + smooth(2) + answered(3, "no") + smooth(4)
    assert ("missing_step", "s7") not in codes(detect(events, defs, 7, TASK))


def test_missing_when_started_but_never_finished():
    events = (Session(1).all_steps(skip_done="s7").done().rows
              + Session(2).all_steps(skip_done="s7").done().rows)
    assert codes(detect(events, DEFS, 7, TASK)) == [("missing_step", "s7")]


def test_never_finished_still_needs_every_session_looked_at():
    # The "started but never finished" path is unchanged: only one of the
    # last 2 sessions had it, so no missing_step.
    events = Session(1).all_steps(skip_done="s7").done().rows + smooth(2)
    assert ("missing_step", "s7") not in codes(detect(events, DEFS, 7, TASK))


def test_unfinished_session_is_not_missing_step():
    # They never tapped task_done (maybe still going), so no missing_step.
    events = Session(1).all_steps(skip_done="s7").rows
    assert ("missing_step", "s7") not in codes(detect(events, DEFS, 7, TASK))


# --------------------------------------------------------------------------------
# rusty_after_gap
# --------------------------------------------------------------------------------
def history(gaps):
    """Sessions whose days_since_last are the given gaps."""
    rows, t = [], datetime(2026, 9, 7, 12)
    rows += Session(1, start=t).all_steps().done().rows
    for i, g in enumerate(gaps, start=2):
        t += timedelta(days=g)
        rows += Session(i, start=t, days_since_last=g).all_steps().done().rows
    return rows


def test_usual_break_is_the_median():
    sessions = split_sessions(history([7, 7, 7, 30]), _settings(DEFS))
    assert usual_break(sessions) == 7


@pytest.mark.parametrize("gaps, coming, rusty", [
    ([10, 10], 21, True),    # more than 2 x 10 and at least 14
    ([10, 10], 20, False),   # not MORE than 2 x 10
    ([3, 3], 13, False),     # more than 2 x 3, but under the 14-day minimum
    ([3, 3], 14, True),      # 14 is the minimum
    ([7, 7, 7, 30], 15, True),   # median 7 (one vacation doesn't change "usual")
    ([], 14, True),          # no history: 14 days
    ([], 13, False),
])
def test_rusty_rule(gaps, coming, rusty):
    result = detect(history(gaps), DEFS, coming, TASK)
    assert (("rusty_after_gap", None) in codes(result)) is rusty


def test_zero_days_is_never_rusty():
    # ask.py passes 0.
    assert ("rusty_after_gap", None) not in codes(detect(history([]), DEFS, 0, TASK))


# --------------------------------------------------------------------------------
# Sessions and loading
# --------------------------------------------------------------------------------
def test_reopening_after_closing_is_one_session():
    assert len(split_sessions(opened_twice(1), _settings(DEFS))) == 1


def test_two_sessions_in_the_same_week_are_split():
    a = Session(1).all_steps().done().rows
    b = Session(1, start=datetime(2026, 11, 3, 18)).all_steps().done().rows
    assert len(split_sessions(a + b, _settings(DEFS))) == 2


def test_task_is_loaded_from_events_when_not_given():
    events = Session(1).all_steps(slow="s4").done().rows + Session(2).all_steps(slow="s4").done().rows
    assert codes(detect(events, DEFS, 7)) == [("stuck_at_step", "s4")]


def test_every_result_has_code_step_and_evidence():
    events = opened_twice(1) + opened_twice(2)
    for r in detect(events, DEFS, 30, TASK):
        assert set(r) == {"code", "step_id", "evidence"}
        assert r["code"] in {"cant_start", "stuck_at_step", "missing_step", "rusty_after_gap", "none"}


# --------------------------------------------------------------------------------
# Staff flag: breaks on the same step
# --------------------------------------------------------------------------------
def break_at(week, sid="s4"):
    s = Session(week)
    for st in TASK["steps"]:
        s.add("step_started", st["step_id"], wait=3)
        if st["step_id"] == sid:
            s.add("paused", sid, wait=5)
            s.add("resumed", sid, wait=600, seconds=600)
        s.add("step_done", st["step_id"], wait=10)
    return s.done().rows


def test_breaks_flag_after_three_sessions():
    flags = steps_with_breaks(break_at(1) + break_at(2) + break_at(3), DEFS)
    assert flags == [{"step_id": "s4", "sessions": 3, "evidence": "Took a break at s4 in 3 sessions"}]


def test_breaks_flag_not_before_three():
    assert steps_with_breaks(break_at(1) + break_at(2) + smooth(3), DEFS) == []


def test_breaks_never_change_detect_codes():
    events = break_at(1) + break_at(2) + break_at(3)
    assert codes(detect(events, DEFS, 7, TASK)) == [("none", None)]


# --------------------------------------------------------------------------------
# Skill cards (helper for fade.py's build_view)
# --------------------------------------------------------------------------------
def skill_answers(*answers):
    """One session where the person answered the skill check, e.g. 'read_price:yes'."""
    s = Session(1)
    for a in answers:
        s.add("skill_check_answer", answer=a)
    return s.rows


def test_skill_card_shown_when_latest_answer_is_not_sure():
    cards = skill_cards_to_show(skill_answers("read_cooking_time:not_sure"), TASK)
    assert cards == [{"skill_id": "read_cooking_time", "step_id": "s1",
                      "reason": "answered Not sure to the skill question"}]


def test_skill_card_not_shown_after_later_yes():
    events = skill_answers("read_cooking_time:not_sure") + skill_answers("read_cooking_time:yes")
    assert skill_cards_to_show(events, TASK) == []


def test_skill_card_only_for_skills_this_task_uses():
    # type_address is a buy_online skill; heat_meal never lists it.
    cards = skill_cards_to_show(skill_answers("type_address:not_sure", "use_oven_mitts:no"), TASK)
    assert [c["skill_id"] for c in cards] == ["use_oven_mitts"]
    assert cards[0]["step_id"] == "s5"  # first step in task order that lists it
    assert cards[0]["reason"] == "answered No to the skill question"


def test_skill_cards_empty_when_no_skill_answers():
    assert skill_cards_to_show(smooth(1), TASK) == []
    assert skill_cards_to_show([], TASK) == []


def test_skill_cards_come_back_in_task_step_order_once_each():
    # read_cooking_time is on s1 and s4; it comes back once, at s1.
    cards = skill_cards_to_show(skill_answers("use_oven_mitts:not_sure", "read_cooking_time:not_sure"), TASK)
    assert [(c["skill_id"], c["step_id"]) for c in cards] == [("read_cooking_time", "s1"), ("use_oven_mitts", "s5")]


def test_skill_cards_never_change_detect_codes():
    events = skill_answers("read_cooking_time:not_sure") + smooth(2)
    assert codes(detect(events, DEFS, 7, TASK)) == [("none", None)]


# --------------------------------------------------------------------------------
# Safety card text (heat_meal.json)
# --------------------------------------------------------------------------------
def test_heat_meal_has_safety_card_content():
    assert TASK["safety_card"] == "microwave_never"  # the label fade.py and the demo read
    card = TASK["safety_card_content"]
    for key in ("title", "never_title", "never", "ok_title", "ok", "also", "source"):
        assert card[key], f"safety_card_content.{key} is empty"
    assert isinstance(card["never"], list) and len(card["never"]) > 0
    assert isinstance(card["ok"], list) and len(card["ok"]) > 0
    assert all(isinstance(line, str) and line.strip() for line in card["never"] + card["ok"] + card["also"])


# --------------------------------------------------------------------------------
# The simulator's demo residents
# --------------------------------------------------------------------------------
sim = pytest.mark.skipif(not LIVE_EVENTS_PATH.is_file(), reason="no simulated events yet")


@sim
def test_sim_jeremiah_cant_start_and_stuck_at_s4():
    events = load_events(LIVE_EVENTS_PATH, person_id="jeremiah", task_id="heat_meal")
    found = codes(detect(events, DEFS, 0))
    assert ("cant_start", None) in found
    assert ("stuck_at_step", "s4") in found


@sim
def test_sim_kayla_missing_s7():
    events = load_events(LIVE_EVENTS_PATH, person_id="kayla", task_id="heat_meal")
    assert ("missing_step", "s7") in codes(detect(events, DEFS, 0))
