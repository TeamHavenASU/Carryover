"""Tests for the review and demo routes. The conftest points the tasks and the pending file at temporary copies."""
import csv
import json
import shutil

import pytest
from fastapi.testclient import TestClient

from ai import common
from api import demo_routes
from api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def copy_fixtures(tmp_path, monkeypatch):
    """Work on copies so an approval never changes the real fixture files."""
    tasks = tmp_path / "tasks"
    shutil.copytree(common.TASKS_DIR, tasks)
    monkeypatch.setattr(common, "TASKS_DIR", tasks)
    return tasks


def add_pending(substeps=None, step_id="s2", task_id="sandwich", approved=False):
    entry = {
        "split_id": f"{task_id}-{step_id}-abc123",
        "task_id": task_id,
        "step_id": step_id,
        "substeps": substeps or ["Open the jar", "Scoop it out", "Spread it"],
        "approved": approved,
    }
    entries = []
    if common.PENDING_FILE.exists():
        entries = json.loads(common.PENDING_FILE.read_text())
    entries.append(entry)
    common.PENDING_FILE.write_text(json.dumps(entries))
    return entry


# ---- review


def test_pending_is_empty_when_nothing_waits():
    assert client.get("/review/pending").json() == []


def test_pending_shows_the_step_and_its_current_small_steps():
    add_pending()
    item = client.get("/review/pending").json()[0]
    assert item["step_id"] == "s2"
    assert item["task_title"]
    assert item["step_text"]
    assert item["substeps"] == ["Open the jar", "Scoop it out", "Spread it"]


def test_pending_skips_entries_that_are_already_approved():
    add_pending(approved=True)
    assert client.get("/review/pending").json() == []


def test_pending_still_lists_a_suggestion_whose_step_is_gone():
    add_pending(step_id="s99")
    item = client.get("/review/pending").json()[0]
    assert item["step_text"] == ""


def test_approve_writes_the_edited_steps_into_the_task_file(copy_fixtures):
    entry = add_pending()
    edited = ["Open the jar", "  Scoop   some out ", "Spread on the bread"]
    resp = client.post(f"/review/{entry['split_id']}/approve", json={"substeps": edited})
    assert resp.status_code == 200

    task = json.loads((copy_fixtures / "sandwich.json").read_text())
    step = next(s for s in task["steps"] if s["step_id"] == "s2")
    assert step["substeps"] == [
        {"id": "s2a", "text": "Open the jar"},
        {"id": "s2b", "text": "Scoop some out"},
        {"id": "s2c", "text": "Spread on the bread"},
    ]
    saved = json.loads(common.PENDING_FILE.read_text())
    assert saved[0]["approved"] is True
    assert saved[0]["substeps"][1] == "Scoop some out"
    assert client.get("/review/pending").json() == []


def test_approve_leaves_the_other_steps_alone(copy_fixtures):
    before = json.loads((copy_fixtures / "sandwich.json").read_text())
    entry = add_pending()
    client.post(f"/review/{entry['split_id']}/approve", json={"substeps": ["One", "Two", "Three"]})
    after = json.loads((copy_fixtures / "sandwich.json").read_text())
    for old, new in zip(before["steps"], after["steps"]):
        if old["step_id"] != "s2":
            assert old == new


@pytest.mark.parametrize(
    "substeps",
    [["Only", "Two"], ["a", "b", "c", "d", "e", "f", "g"], ["Fine", "", "Fine too"], ["x" * 121, "b", "c"]],
)
def test_approve_rejects_bad_lists(substeps, copy_fixtures):
    entry = add_pending()
    resp = client.post(f"/review/{entry['split_id']}/approve", json={"substeps": substeps})
    assert resp.status_code == 400
    task = json.loads((copy_fixtures / "sandwich.json").read_text())
    assert next(s for s in task["steps"] if s["step_id"] == "s2")["substeps"] == []
    assert json.loads(common.PENDING_FILE.read_text())[0]["approved"] is False


def test_approve_unknown_id_is_404():
    assert client.post("/review/nope/approve", json={"substeps": ["a", "b", "c"]}).status_code == 404


def test_approve_twice_is_404_the_second_time():
    entry = add_pending()
    body = {"substeps": ["One", "Two", "Three"]}
    assert client.post(f"/review/{entry['split_id']}/approve", json=body).status_code == 200
    assert client.post(f"/review/{entry['split_id']}/approve", json=body).status_code == 404


def test_reject_removes_the_suggestion_and_keeps_the_task_file(copy_fixtures):
    before = (copy_fixtures / "sandwich.json").read_text()
    entry = add_pending()
    assert client.post(f"/review/{entry['split_id']}/reject").status_code == 200
    assert json.loads(common.PENDING_FILE.read_text()) == []
    assert (copy_fixtures / "sandwich.json").read_text() == before
    assert client.post(f"/review/{entry['split_id']}/reject").status_code == 404


# ---- demo

FIELDS = [
    "person_id", "task_id", "session_id", "week", "timestamp", "event",
    "step_id", "seconds", "days_since_last", "help_shown", "answer", "prompted",
]


@pytest.fixture
def events_file(tmp_path, monkeypatch):
    """Two sessions in week 1 (one with help used twice), none in week 2, one in week 3."""
    def r(week, time, event, step="", **kw):
        row = dict.fromkeys(FIELDS, "")
        row.update(person_id="amy", task_id="heat_meal", session_id=f"amy-heat_meal-w{week:02d}",
                   week=week, timestamp=time, event=event, step_id=step, **kw)
        return row

    rows = [
        r(1, "2026-09-07T10:00:00", "task_opened"),
        r(1, "2026-09-07T10:00:10", "hint_requested", "s1"),
        r(1, "2026-09-07T10:00:20", "stuck_pressed", "s1"),
        r(1, "2026-09-07T10:01:00", "task_done"),
        r(1, "2026-09-09T10:00:00", "task_opened"),
        r(1, "2026-09-09T10:01:00", "task_done"),
        r(3, "2026-09-21T10:00:00", "task_opened"),
        r(3, "2026-09-21T10:00:10", "ask_sent", "s2"),
        r(3, "2026-09-21T10:01:00", "task_done"),
    ]
    path = tmp_path / "events.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    monkeypatch.setattr(demo_routes, "EVENTS_PATH", path)
    return path


def test_people_lists_each_person_and_task(events_file):
    people = client.get("/demo/people").json()
    assert people == [{"person_id": "amy", "task_id": "heat_meal", "title": people[0]["title"], "last_week": 3}]


def test_help_counts_have_one_entry_per_week_up_to_the_slider(events_file):
    params = {"person_id": "amy", "task_id": "heat_meal"}
    counts = client.get("/demo/help_counts", params={**params, "up_to_week": 3}).json()
    assert counts == [
        {"week": 1, "sessions": 2, "help_count": 2},
        {"week": 2, "sessions": 0, "help_count": 0},
        {"week": 3, "sessions": 1, "help_count": 1},
    ]


def test_help_counts_do_not_show_later_weeks(events_file):
    params = {"person_id": "amy", "task_id": "heat_meal"}
    counts = client.get("/demo/help_counts", params={**params, "up_to_week": 2}).json()
    assert [c["week"] for c in counts] == [1, 2]
    assert client.get("/demo/help_counts", params={**params, "up_to_week": 0}).json() == []


def test_view_returns_steps_for_the_week(events_file):
    view = client.get("/demo/view", params={"person_id": "amy", "task_id": "heat_meal", "week": 1}).json()
    assert view["week"] == 1
    assert len(view["steps"]) == 7


def test_view_for_an_unknown_task_is_404(events_file):
    resp = client.get("/demo/view", params={"person_id": "amy", "task_id": "nope", "week": 1})
    assert resp.status_code == 404
