"""Tests for the staff screen route."""
import csv

import pytest
from fastapi.testclient import TestClient

from api import staff_routes
from api.main import app

client = TestClient(app)

FIELDS = [
    "person_id", "task_id", "session_id", "week", "timestamp", "event",
    "step_id", "seconds", "days_since_last", "help_shown", "answer", "prompted",
]


def session(person, week, day, stuck=False, task="heat_meal"):
    """One session: open, start s1 straight away, finish. stuck adds a stuck press at s1."""
    def r(time, event, step="", **kw):
        row = dict.fromkeys(FIELDS, "")
        row.update(person_id=person, task_id=task, session_id=f"{person}-{task}-w{week:02d}",
                   week=week, timestamp=f"2026-09-{day:02d}T{time}", event=event, step_id=step, **kw)
        return row

    rows = [r("10:00:00", "task_opened"), r("10:00:05", "step_started", "s1", help_shown="hint")]
    if stuck:
        rows.append(r("10:00:20", "stuck_pressed", "s1", help_shown="hint"))
    rows += [r("10:00:40", "step_done", "s1", seconds=35, help_shown="hint", prompted="no"), r("10:01:00", "task_done")]
    return rows


@pytest.fixture
def events_file(tmp_path, monkeypatch):
    """amy is stuck at s1 in weeks 2 and 3 but not week 1. bob never is."""
    rows = session("amy", 1, 7) + session("amy", 2, 14, stuck=True) + session("amy", 3, 21, stuck=True)
    rows += session("bob", 1, 7) + session("bob", 2, 14) + session("bob", 3, 21)
    rows += session("cal", 1, 7, task="not_a_task")
    path = tmp_path / "events.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    monkeypatch.setattr(staff_routes, "EVENTS_PATH", path)
    return path


def test_lists_each_resident_with_their_sticking_points(events_file):
    people = client.get("/staff/sticking_points").json()
    assert [p["person_id"] for p in people] == ["amy", "bob"]
    amy = people[0]
    assert amy["last_week"] == 3
    assert [(p["code"], p["step_id"]) for p in amy["sticking_points"]] == [("stuck_at_step", "s1")]
    assert amy["sticking_points"][0]["step_text"]
    assert amy["sticking_points"][0]["evidence"]


def test_a_resident_with_nothing_found_has_an_empty_list(events_file):
    bob = client.get("/staff/sticking_points").json()[1]
    assert bob["sticking_points"] == []


def test_residents_with_sticking_points_come_first(events_file, tmp_path, monkeypatch):
    rows = session("aaron", 1, 7) + session("aaron", 2, 14)
    rows += session("zoe", 1, 7, stuck=True) + session("zoe", 2, 14, stuck=True)
    path = tmp_path / "order.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    monkeypatch.setattr(staff_routes, "EVENTS_PATH", path)
    assert [p["person_id"] for p in client.get("/staff/sticking_points").json()] == ["zoe", "aaron"]


def test_a_week_only_uses_earlier_weeks(events_file):
    # Before week 3 amy was stuck in only one of her last 2 sessions, so nothing is found.
    people = client.get("/staff/sticking_points", params={"week": 3}).json()
    amy = next(p for p in people if p["person_id"] == "amy")
    assert amy["last_week"] == 2
    assert amy["sticking_points"] == []


def test_unknown_tasks_are_left_out(events_file):
    people = client.get("/staff/sticking_points").json()
    assert "cal" not in [p["person_id"] for p in people]
