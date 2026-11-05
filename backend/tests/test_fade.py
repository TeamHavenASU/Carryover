"""Tests for logic/fade.py. They use small made-up sessions and a small set of rules."""
import csv

import pytest

from logic import fade

DEFS = {
    "help_levels": {
        "most_help": "split",
        "some_help": "hint",
        "no_help": "hide",
        "week_1_level": "some_help",
    },
    "defaults": {
        "start_time_seconds": 60,
        "long_pause_seconds": 45,
        "opens_without_start_for_trouble_starting": 2,
    },
    "fading_rules": {
        "rule_2_show_less_after_done_alone": 3,
        "rule_2_ask_again_after_keep_it": 3,
        "rule_3_keep_only_used_small_steps_after": 3,
        "rule_4_more_help_after_struggled_in_a_row": 2,
        "rule_5_offer_up_front_after_opened_in_a_row": 3,
        "rule_6_hint_wait_fractions_of_long_pause": [0.25, 0.5, 0.75],
        "rule_8_skips_before_asking_once": 3,
        "start_push_remove_after_started_alone": 3,
        "start_push_back_after_trouble_starting_in_a_row": 2,
    },
    "check_questions": {"ask_every_n_sessions": 2},
    "used_help_events": ["stuck_pressed", "hint_requested", "more_help_requested", "show_all_pressed", "ask_sent"],
    "take_a_break": {"new_session_after_hours": 12},
}

TASK = {
    "task_id": "toast",
    "title": "Make toast",
    "start_push": "Take out the bread.",
    "start_time_seconds": 60,
    "long_pause_seconds": 40,
    "safety_card": "toaster",
    "steps": [
        {"step_id": "s1", "text": "Put bread in", "hint": "Bread in", "substeps": [{"id": "s1a", "text": "Open the bag"}]},
        {"step_id": "s2", "text": "Wait", "wait": True, "check_question": "Did it pop up?"},
    ],
}
STEP = TASK["steps"][0]


def row(event, session_id="p-toast-w01", week=1, time="2026-09-07T10:00:00", **extra):
    base = {
        "person_id": "p",
        "task_id": "toast",
        "session_id": session_id,
        "week": week,
        "timestamp": time,
        "event": event,
        "step_id": "",
        "seconds": None,
        "days_since_last": None,
        "help_shown": "",
        "answer": "",
        "prompted": "",
    }
    base.update(extra)
    return base


def session(result, shown="hint", day=7, less_help=None):
    """One session where step s1 went a certain way: alone, prompted, opened or struggled.

    less_help adds the person's Rule 2 answer for s1 at the end: "yes" or "keep".
    """
    t = f"2026-09-{day:02d}T10:00:"
    rows = [
        row("task_opened", time=t + "00"),
        row("step_started", time=t + "10", step_id="s1", help_shown=shown),
    ]
    if result == "opened":
        rows.append(row("hint_requested", time=t + "20", step_id="s1", help_shown=shown))
    if result == "struggled":
        rows.append(row("step_done", time=t + "50", step_id="s1", seconds=90.0, help_shown=shown, prompted="yes"))
    else:
        prompted = "yes" if result in ("opened", "prompted") else "no"
        rows.append(row("step_done", time=t + "40", step_id="s1", seconds=20.0, help_shown=shown, prompted=prompted))
    if less_help:
        rows.append(row("end_question", time=t + "52", step_id="s1", answer=less_help))
    rows.append(row("task_done", time=t + "55"))
    return rows


# ---- step_result


@pytest.mark.parametrize("result", ["alone", "prompted", "opened", "struggled"])
def test_step_result_reads_each_kind(result):
    assert fade.step_result(session(result), STEP, TASK, DEFS) == ("hint", result)


def test_step_result_is_none_when_step_not_started():
    assert fade.step_result([row("task_opened")], STEP, TASK, DEFS) == (None, None)


def test_a_no_answer_to_the_check_question_counts_as_struggled():
    rows = session("alone") + [row("check_answer", step_id="s1", answer="no")]
    assert fade.step_result(rows, STEP, TASK, DEFS)[1] == "struggled"


def test_waiting_steps_never_have_a_long_pause():
    wait_step = TASK["steps"][1]
    rows = [
        row("step_started", step_id="s2", help_shown="hint"),
        row("step_done", step_id="s2", seconds=500.0, help_shown="hint", prompted="no"),
    ]
    assert fade.step_result(rows, wait_step, TASK, DEFS)[1] == "alone"


# ---- next_level


def test_no_history_gives_the_week_1_level():
    assert fade.next_level([], STEP, TASK, DEFS) == "hint"


def test_three_alone_in_a_row_asks_but_does_not_show_less_by_itself():
    history = [session("alone", day=d) for d in (7, 8, 9)]
    assert fade.offer_less_help(history, STEP, TASK, DEFS) is True
    assert fade.next_level(history, STEP, TASK, DEFS) == "hint"


def test_two_alone_is_not_enough():
    history = [session("alone", day=d) for d in (7, 8)]
    assert fade.offer_less_help(history, STEP, TASK, DEFS) is False
    assert fade.next_level(history, STEP, TASK, DEFS) == "hint"


def test_yes_shows_one_level_less():
    history = [session("alone", day=d) for d in (7, 8, 9)]
    history += [session("alone", day=10, less_help="yes")]
    assert fade.next_level(history, STEP, TASK, DEFS) == "hide"
    assert fade.offer_less_help(history, STEP, TASK, DEFS) is False


def test_keep_holds_the_level_and_asks_again_after_three_more():
    history = [session("alone", day=d) for d in (7, 8, 9)]
    history += [session("alone", day=10, less_help="keep")]
    assert fade.next_level(history, STEP, TASK, DEFS) == "hint"
    assert fade.offer_less_help(history, STEP, TASK, DEFS) is False
    for day in (11, 12):
        history += [session("alone", day=day)]
        assert fade.next_level(history, STEP, TASK, DEFS) == "hint"
        assert fade.offer_less_help(history, STEP, TASK, DEFS) is False
    history += [session("alone", day=13)]
    assert fade.next_level(history, STEP, TASK, DEFS) == "hint"
    assert fade.offer_less_help(history, STEP, TASK, DEFS) is True


def test_keep_then_yes_shows_less():
    history = [session("alone", day=d) for d in (7, 8, 9)]
    history += [session("alone", day=10, less_help="keep")]
    history += [session("alone", day=d) for d in (11, 12, 13)]
    history += [session("alone", day=14, less_help="yes")]
    assert fade.next_level(history, STEP, TASK, DEFS) == "hide"


def test_a_struggle_resets_the_count_for_less_help():
    history = [session("alone", day=7), session("alone", day=8), session("struggled", day=9), session("alone", day=10)]
    assert fade.offer_less_help(history, STEP, TASK, DEFS) is False
    history += [session("alone", day=d) for d in (11, 12)]
    assert fade.offer_less_help(history, STEP, TASK, DEFS) is True


def test_help_shown_by_itself_is_not_done_alone():
    history = [session("alone", day=7), session("alone", day=8), session("prompted", day=9)]
    assert fade.offer_less_help(history, STEP, TASK, DEFS) is False


def test_a_missing_step_shows_more_help():
    history = [session("alone", shown="hide", day=d) for d in (7, 8)]
    assert fade.next_level(history, STEP, TASK, DEFS) == "hide"
    assert fade.next_level(history, STEP, TASK, DEFS, missing=True) == "hint"


def test_a_missing_step_moves_up_only_one_level():
    # two struggles (Rule 4) and missing_step together still mean one level, not two
    history = [session("struggled", shown="hide", day=d) for d in (7, 8)]
    assert fade.next_level(history, STEP, TASK, DEFS, missing=True) == "hint"


def test_a_missing_step_wins_over_a_yes_to_less_help():
    history = [session("alone", day=d) for d in (7, 8, 9)] + [session("alone", day=10, less_help="yes")]
    assert fade.next_level(history, STEP, TASK, DEFS, missing=True) == "split"


def test_a_missing_step_stops_at_most_help():
    history = [session("alone", shown="split", day=7)]
    assert fade.next_level(history, STEP, TASK, DEFS, missing=True) == "split"


def test_never_offers_less_help_at_the_least_help_level():
    history = [session("alone", shown="hide", day=d) for d in (7, 8, 9)]
    assert fade.offer_less_help(history, STEP, TASK, DEFS) is False


def test_two_struggled_in_a_row_shows_more():
    history = [session("struggled", day=d) for d in (7, 8)]
    assert fade.next_level(history, STEP, TASK, DEFS) == "split"


def test_a_good_session_breaks_the_struggled_run():
    history = [session("struggled", day=7), session("alone", day=8), session("struggled", day=9)]
    assert fade.next_level(history, STEP, TASK, DEFS) == "hint"


def test_opening_help_three_times_moves_it_up_front():
    history = [session("opened", shown="hide", day=d) for d in (7, 8, 9)]
    assert fade.next_level(history, STEP, TASK, DEFS) == "hint"


def test_levels_stop_at_the_ends():
    least = [session("alone", shown="hide", day=d) for d in (7, 8, 9)]
    most = [session("struggled", shown="split", day=d) for d in (7, 8)]
    assert fade.next_level(least, STEP, TASK, DEFS) == "hide"
    assert fade.next_level(most, STEP, TASK, DEFS) == "split"


def test_the_count_starts_again_after_a_level_change():
    # two alone at hint, then the app moved the step to hide: those two no longer count
    history = [session("alone", shown="hint", day=7), session("alone", shown="hint", day=8)]
    history += [session("alone", shown="hide", day=9), session("alone", shown="hide", day=10)]
    assert fade.next_level(history, STEP, TASK, DEFS) == "hide"
    history = history[:2] + [session("alone", shown="hide", day=9)]
    assert fade.next_level(history, STEP, TASK, DEFS) == "hide"


def test_decide_level_matches_the_simulator_arguments():
    history = [session("alone", day=d) for d in (7, 8)] + [session("alone", day=9, less_help="yes")]
    assert fade.decide_level("p", TASK, "s1", 2, history, DEFS) == "hide"
    assert fade.decide_level("p", TASK, "s1", 1, history, DEFS) == "hint"


# ---- Rule 3: small steps

SPLIT_STEP = {
    "step_id": "s1",
    "text": "Put bread in",
    "substeps": [
        {"id": "s1a", "text": "Open the bag"},
        {"id": "s1b", "text": "Take out two slices"},
        {"id": "s1c", "text": "Put them in the slots"},
        {"id": "s1d", "text": "Close the bag"},
    ],
    "tips": ["Bread stuck? Unplug the toaster first"],
}
SPLIT_TASK = dict(TASK, steps=[SPLIT_STEP])


def split_session(opened, day=7, shown="split", answer=None):
    """One session at s1 done alone, opening these small steps. answer is a Rule 3 end_question answer."""
    t = f"2026-09-{day:02d}T10:00:"
    rows = [row("task_opened", time=t + "00"), row("step_started", time=t + "10", step_id="s1", help_shown=shown)]
    for i, sub in enumerate(opened):
        rows.append(row("small_step_opened", time=t + f"{20 + i:02d}", step_id="s1", help_shown=shown, answer=sub))
    rows.append(row("step_done", time=t + "40", step_id="s1", seconds=20.0, help_shown=shown, prompted="no"))
    if answer:
        rows.append(row("end_question", time=t + "50", step_id="s1", answer=answer))
    rows.append(row("task_done", time=t + "55"))
    return rows


def test_the_trim_offer_comes_after_three_sessions_opening_the_same_small_steps():
    history = [split_session(["s1b", "s1c"], day=d) for d in (7, 8)]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is False
    history += [split_session(["s1c", "s1b"], day=9)]  # same set, any order
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is True


def test_a_different_set_of_small_steps_starts_the_count_again():
    history = [split_session(["s1b"], day=7), split_session(["s1b"], day=8), split_session(["s1b", "s1c"], day=9)]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is False
    history += [split_session(["s1b", "s1c"], day=d) for d in (10, 11)]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is True


def test_opening_no_small_steps_never_offers_a_trim():
    history = [split_session([], day=d) for d in (7, 8, 9, 10)]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is False


def test_opening_every_small_step_has_nothing_to_trim():
    every = ["s1a", "s1b", "s1c", "s1d"]
    history = [split_session(every, day=d) for d in (7, 8, 9)]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is False


def test_sessions_not_at_split_break_the_run():
    history = [split_session(["s1b"], day=7), split_session([], day=8, shown="hint"), split_session(["s1b"], day=9)]
    history += [split_session(["s1b"], day=10)]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is False


def test_trim_keeps_only_the_opened_small_steps_in_their_order():
    history = [split_session(["s1d", "s1b"], day=d) for d in (7, 8, 9)]
    history += [split_session(["s1d", "s1b"], day=10, answer="trim")]
    kept = fade.small_steps_for(history, SPLIT_STEP, SPLIT_TASK, DEFS)
    assert [s["id"] for s in kept] == ["s1b", "s1d"]
    assert kept[0] == {"id": "s1b", "text": "Take out two slices"}
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is False


def test_keep_all_leaves_the_small_steps_and_offers_again_after_three_more():
    history = [split_session(["s1b"], day=d) for d in (7, 8, 9)]
    history += [split_session(["s1b"], day=10, answer="keep_all")]
    assert fade.small_steps_for(history, SPLIT_STEP, SPLIT_TASK, DEFS) == SPLIT_STEP["substeps"]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is False
    history += [split_session(["s1b"], day=d) for d in (11, 12)]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is False
    history += [split_session(["s1b"], day=13)]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is True


def test_tips_are_not_small_steps():
    # a stray id that is not a substep (a tip has no id at all) is ignored
    history = [split_session(["s1b", "tip1"], day=d) for d in (7, 8, 9)]
    assert fade.offer_trim_small_steps(history, SPLIT_STEP, SPLIT_TASK, DEFS) is True
    history += [split_session(["s1b"], day=10, answer="trim")]
    assert [s["id"] for s in fade.small_steps_for(history, SPLIT_STEP, SPLIT_TASK, DEFS)] == ["s1b"]


def test_rule_3_answers_do_not_count_as_rule_2_answers():
    history = [split_session(["s1b"], day=d) for d in (7, 8, 9)] + [split_session(["s1b"], day=10, answer="trim")]
    assert fade.next_level(history, SPLIT_STEP, SPLIT_TASK, DEFS) == "split"


def test_with_no_answer_the_small_steps_are_the_task_files_list():
    history = [split_session(["s1b"], day=d) for d in (7, 8, 9, 10, 11)]
    assert fade.small_steps_for(history, SPLIT_STEP, SPLIT_TASK, DEFS) is SPLIT_STEP["substeps"]


# ---- hint waits


def test_hint_waits_use_the_steps_own_long_pause():
    assert fade.hint_waits(STEP, TASK, DEFS) == [10, 20, 30]
    slow = dict(STEP, long_pause_seconds=100)
    assert fade.hint_waits(slow, TASK, DEFS) == [25, 50, 75]


def test_waiting_steps_get_no_hint_waits():
    waiting = TASK["steps"][1]
    assert fade.hint_waits(waiting, TASK, DEFS) == []


# ---- sessions


def test_sessions_split_after_task_done_and_after_a_long_gap():
    rows = session("alone", day=7) + session("alone", day=8)
    assert len(fade.split_sessions(rows, DEFS)) == 2

    rows = [row("task_opened", time="2026-09-07T08:00:00"), row("task_opened", time="2026-09-07T21:00:00")]
    assert len(fade.split_sessions(rows, DEFS)) == 2


def test_opening_again_a_few_minutes_later_stays_in_one_session():
    rows = [
        row("task_opened", time="2026-09-07T10:00:00"),
        row("task_closed_no_start", time="2026-09-07T10:00:30"),
        row("task_opened", time="2026-09-07T10:10:00"),
    ]
    assert len(fade.split_sessions(rows, DEFS)) == 1


# ---- start push


def trouble_session(day):
    t = f"2026-09-{day:02d}T10:00:"
    return [
        row("task_opened", time=t + "00"),
        row("task_closed_no_start", time=t + "20"),
        row("task_opened", time=t + "30"),
        row("step_started", time=t + "59", step_id="s1", help_shown="hint"),
    ]


def easy_session(day):
    return session("alone", day=day)


def test_start_push_needs_trouble_twice_in_a_row():
    assert not fade.start_push_on([trouble_session(7)], TASK, DEFS)
    assert fade.start_push_on([trouble_session(7), trouble_session(8)], TASK, DEFS)


def test_start_push_goes_away_after_three_easy_starts():
    sessions = [trouble_session(7), trouble_session(8)]
    assert fade.start_push_on(sessions + [easy_session(9), easy_session(10)], TASK, DEFS)
    assert not fade.start_push_on(sessions + [easy_session(d) for d in (9, 10, 11)], TASK, DEFS)


def test_a_slow_start_counts_as_trouble():
    rows = [
        row("task_opened", time="2026-09-07T10:00:00"),
        row("step_started", time="2026-09-07T10:02:00", step_id="s1", help_shown="hint"),
    ]
    assert fade.started_with_trouble(rows, TASK, DEFS)


# ---- skipped weeks


def test_skipped_weeks_are_counted_back_from_this_week():
    history = [row("task_opened", week=1)]
    assert fade.trailing_skipped_weeks(history, 4) == 2
    assert fade.trailing_skipped_weeks(history, 5) == 3
    assert fade.trailing_skipped_weeks([], 5) == 0


# ---- build_view


def _write_log(path, weeks):
    """Write one easy session per week. weeks is [(week, day, less_help answer or None, shown)]."""
    rows = []
    for week, day, less_help, shown in weeks:
        for r in session("alone", shown=shown, day=day, less_help=less_help):
            r["week"] = week
            r["session_id"] = f"p-toast-w{week:02d}"
            rows.append(r)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


@pytest.fixture
def view_files(tmp_path, monkeypatch):
    """A one step task and an event log with three weeks of easy sessions."""
    monkeypatch.setattr(fade, "load_task", lambda task_id: TASK)
    return _write_log(tmp_path / "events.csv", [(1, 7, None, "hint"), (2, 14, None, "hint"), (3, 21, None, "hint")])


@pytest.fixture
def view_files_said_yes(tmp_path, monkeypatch):
    """Easy sessions; asked in week 4, the person said "yes", and week 5 showed less help."""
    monkeypatch.setattr(fade, "load_task", lambda task_id: TASK)
    weeks = [(1, 7, None, "hint"), (2, 14, None, "hint"), (3, 21, None, "hint"), (4, 28, "yes", "hint")]
    weeks += [(5, 29, None, "hide")]
    return _write_log(tmp_path / "events.csv", weeks)


def test_view_in_week_1_has_the_starting_level_and_the_safety_card(view_files):
    view = fade.build_view("p", "toast", 1, events_path=view_files, defs=DEFS)
    assert [s["mode"] for s in view["steps"]] == ["hint", "hint"]
    assert view["show_safety_card"] == "toaster"
    assert view["start_push"] is None
    assert view["session_number"] == 1


def test_view_only_uses_earlier_weeks(view_files):
    # three alone sessions exist in weeks 1 to 3. In week 3 only two are known.
    week3 = fade.build_view("p", "toast", 3, events_path=view_files, defs=DEFS)
    week4 = fade.build_view("p", "toast", 4, events_path=view_files, defs=DEFS)
    assert week3["steps"][0]["offer_less_help"] is False
    assert week4["steps"][0]["offer_less_help"] is True
    assert week3["session_number"] == 3
    assert week3["show_safety_card"] is None


def test_view_asks_before_showing_less_help(view_files):
    # three alone sessions: week 4 keeps the level and asks instead of dropping it
    week4 = fade.build_view("p", "toast", 4, events_path=view_files, defs=DEFS)
    assert week4["steps"][0]["mode"] == "hint"
    assert week4["steps"][0]["offer_less_help"] is True


def test_view_gives_a_missing_step_more_help(view_files_said_yes, monkeypatch):
    # s1 is hidden from week 5. If detect reports it missing, week 6 shows it again.
    missing = [{"code": "missing_step", "step_id": "s1", "evidence": "said no to the check question for s1"}]
    monkeypatch.setattr(fade, "detect", lambda *args: missing)
    week6 = fade.build_view("p", "toast", 6, events_path=view_files_said_yes, defs=DEFS)
    assert week6["steps"][0]["mode"] == "hint"
    assert week6["steps"][1]["mode"] == "hint"  # other steps are not touched
    assert week6["sticking_points"] == missing


def test_view_shows_less_help_after_yes(view_files_said_yes):
    week5 = fade.build_view("p", "toast", 5, events_path=view_files_said_yes, defs=DEFS)
    assert week5["steps"][0]["mode"] == "hide"
    assert week5["steps"][0]["offer_less_help"] is False


def test_view_lists_check_questions_for_hidden_steps_every_second_session(view_files_said_yes, monkeypatch):
    with_question = dict(TASK, steps=[dict(STEP, check_question="Is the bread in?"), TASK["steps"][1]])
    monkeypatch.setattr(fade, "load_task", lambda task_id: with_question)

    # s1 is hidden from week 5 (after "yes" in week 4). Session 6 is even: asked.
    week6 = fade.build_view("p", "toast", 6, events_path=view_files_said_yes, defs=DEFS)
    assert week6["session_number"] == 6
    assert week6["check_questions"] == [{"step_id": "s1", "question": "Is the bread in?"}]

    # session 5 is odd: not asked
    week5 = fade.build_view("p", "toast", 5, events_path=view_files_said_yes, defs=DEFS)
    assert week5["session_number"] == 5
    assert week5["check_questions"] == []

    # session 4 is even, but s1 is not hidden yet in week 4
    week4 = fade.build_view("p", "toast", 4, events_path=view_files_said_yes, defs=DEFS)
    assert week4["session_number"] == 4
    assert week4["check_questions"] == []


def test_view_carries_hint_waits_and_substeps(view_files):
    view = fade.build_view("p", "toast", 2, events_path=view_files, defs=DEFS)
    first = view["steps"][0]
    assert first["hint_waits"] == [10, 20, 30]
    assert first["substeps"] == [{"id": "s1a", "text": "Open the bag"}]
    assert first["hint"] == "Bread in"


def _write_rows(path, sessions):
    """Write sessions (lists of rows) to an events file, one session per week."""
    rows = []
    for week, ses in enumerate(sessions, start=1):
        for r in ses:
            rows.append(dict(r, week=week, session_id=f"p-toast-w{week:02d}"))
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_view_offers_the_trim_and_keeps_every_small_step_until_answered(tmp_path, monkeypatch):
    monkeypatch.setattr(fade, "load_task", lambda task_id: SPLIT_TASK)
    sessions = [split_session(["s1b", "s1c"], day=d) for d in (7, 14, 21)]
    path = _write_rows(tmp_path / "events.csv", sessions)
    week4 = fade.build_view("p", "toast", 4, events_path=path, defs=DEFS)
    step = week4["steps"][0]
    assert step["offer_trim_small_steps"] is True
    assert step["substeps"] == SPLIT_STEP["substeps"]
    assert step["tips"] == SPLIT_STEP["tips"]


def test_view_shows_only_the_kept_small_steps_after_trim(tmp_path, monkeypatch):
    monkeypatch.setattr(fade, "load_task", lambda task_id: SPLIT_TASK)
    sessions = [split_session(["s1b", "s1c"], day=d) for d in (7, 14, 21)]
    sessions += [split_session(["s1b", "s1c"], day=28, answer="trim")]
    path = _write_rows(tmp_path / "events.csv", sessions)
    week5 = fade.build_view("p", "toast", 5, events_path=path, defs=DEFS)
    step = week5["steps"][0]
    assert [s["id"] for s in step["substeps"]] == ["s1b", "s1c"]
    assert step["offer_trim_small_steps"] is False
    assert step["tips"] == SPLIT_STEP["tips"]  # tips are never trimmed
