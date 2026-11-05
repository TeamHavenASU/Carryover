"""Tests for today.py, event_log.py and the resident routes (Role C)."""
import csv

import pytest
from fastapi.testclient import TestClient

from api import resident_routes
from api.main import app
from logic import event_log
from logic.data_io import EVENT_COLUMNS, available_tasks, load_task
from logic.today import STEP_FIELDS, build_today

client = TestClient(app)


def test_today_has_every_step_with_number_and_total(tmp_path):
    for task_id in available_tasks():
        task = load_task(task_id)
        view = build_today("nobody", task_id, 1, events_path=tmp_path / "none.csv")
        assert [s["step_id"] for s in view["steps"]] == [s["step_id"] for s in task["steps"]]
        assert [s["number"] for s in view["steps"]] == list(range(1, len(task["steps"]) + 1))
        assert {s["total"] for s in view["steps"]} == {len(task["steps"])}


def test_today_passes_task_fields_through_unchanged(tmp_path):
    task = load_task("heat_meal")
    view = build_today("nobody", "heat_meal", 1, events_path=tmp_path / "none.csv")
    for src, step in zip(task["steps"], view["steps"]):
        assert step["text"] == src["text"]
        for field in STEP_FIELDS:
            if field in src:
                assert step[field] == src[field]
    assert view["first_time_question"] == task["first_time_question"]
    assert view["safety_card_content"] == task.get("safety_card_content")


def test_unknown_task_is_404():
    assert client.get("/today", params={"person_id": "x", "task_id": "nope", "week": 1}).status_code == 404


def test_tasks_route_lists_task_files():
    assert client.get("/tasks").json() == {"tasks": available_tasks()}


@pytest.fixture
def log_path(tmp_path, monkeypatch):
    path = tmp_path / "events.csv"
    monkeypatch.setattr(event_log, "LIVE_EVENTS_PATH", path)
    monkeypatch.setattr(event_log.log_event, "__defaults__", (path,))
    return path


def row(**extra):
    base = {"person_id": "p", "task_id": "heat_meal", "session_id": "p-heat_meal-w01", "week": 1}
    return {**base, **extra}


def test_event_is_appended_with_the_event_columns(log_path):
    event_log.log_event(row(event="task_opened"))
    rows = list(csv.DictReader(open(log_path)))
    assert list(rows[0]) == EVENT_COLUMNS and rows[0]["event"] == "task_opened"


@pytest.mark.parametrize("event", ["small_step_opened", "help_offer_answer", "device_check_answer"])
def test_answer_allowed_on_events_that_use_it(log_path, event):
    event_log.log_event(row(event=event, answer="yes"))


def test_bad_events_are_refused(log_path):
    with pytest.raises(ValueError):
        event_log.log_event(row(event="bought_milk"))
    with pytest.raises(ValueError):
        event_log.log_event(row(event="task_opened", answer="yes"))
    with pytest.raises(ValueError):
        event_log.log_event(row(event="step_done"))  # needs prompted
    with pytest.raises(ValueError):
        event_log.log_event(row(event="task_opened", prompted="yes"))


def test_feedback_answer_may_have_an_empty_task_id(log_path):
    # It is about the app, not a task. The session id says "settings" where the task id would go.
    event_log.log_event(row(event="feedback_answer", task_id="", session_id="p-settings-w01", answer="movement:too_much"))
    rows = list(csv.DictReader(open(log_path)))
    assert rows[0]["task_id"] == "" and rows[0]["answer"] == "movement:too_much"


@pytest.mark.parametrize("event", ["task_opened", "step_started", "setup_answer", "check_answer"])
def test_every_other_event_still_needs_a_task_id(log_path, event):
    with pytest.raises(ValueError, match="task_id is required"):
        event_log.log_event(row(event=event, task_id=""))


def test_feedback_event_is_accepted_by_the_route(log_path):
    body = row(event="feedback_answer", task_id="", session_id="p-settings-w01", answer="sound:too_loud")
    assert client.post("/event", json=body).status_code == 200
    assert client.post("/event", json=row(event="task_opened", task_id="")).status_code == 422


def test_setup_questions_come_from_definitions():
    questions = client.get("/setup").json()
    assert [q["id"] for q in questions] == ["interests", "style", "sound", "hand"]


def test_feedback_questions_come_from_definitions():
    feedback = client.get("/feedback").json()
    assert [q["id"] for q in feedback["questions"]] == ["movement", "sound", "colors", "help"]
    assert feedback["check_in"]["after_tasks_done"] == 3
    # The help question is recorded only: no answer may change a setting.
    help_q = next(q for q in feedback["questions"] if q["id"] == "help")
    assert all("action" not in a for a in help_q["answers"])
    assert all(a["note"] for a in help_q["answers"] if a["value"] != "just_right")


def test_skill_card_is_served_and_unknown_is_404():
    assert client.get("/skills/open_package").json()["skill_id"] == "open_package"
    assert client.get("/skills/..%2Fdefinitions").status_code == 404


def test_game_route_counts_done_tasks_and_milestones(tmp_path, monkeypatch):
    path = tmp_path / "events.csv"
    monkeypatch.setattr(resident_routes, "LIVE_EVENTS_PATH", path)
    base = {"person_id": "g", "task_id": "heat_meal", "week": 1}
    for i in range(5):
        event_log.log_event({**base, "session_id": f"g-heat_meal-w0{i}", "event": "task_done"}, path)
    game = client.get("/game", params={"person_id": "g"}).json()
    assert game["tasks_done"] == 5 and game["per_task"] == {"heat_meal": 5}
    assert "first task done" in game["milestones_reached"]
    assert "task done 5 times" in game["milestones_reached"]
    other = client.get("/game", params={"person_id": "nobody"}).json()
    assert other["tasks_done"] == 0 and other["milestones_reached"] == []
