"""Tests for the skill card review routes. They work on a temporary skills folder and pending file."""
import json

import pytest
from fastapi.testclient import TestClient

from api import skill_routes
from api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def temp_skills(tmp_path, monkeypatch):
    skills = tmp_path / "skills"
    skills.mkdir()
    monkeypatch.setattr(skill_routes, "SKILLS_DIR", skills)
    monkeypatch.setattr(skill_routes, "PENDING_FILE", tmp_path / "skill_cards_pending.json")
    return skills


def card(skill_id="read_price", steps=2, approved=False):
    return {
        "skill_id": skill_id,
        "title": "Read a price",
        "why": "Buying starts with the price.",
        "steps": [{"id": f"{skill_id}_{n}", "text": f"Step {n}"} for n in range(1, steps + 1)],
        "tips": ["A sale tag may show a lower price"],
        "used_by": ["buy_online:s1"],
        "approved": approved,
    }


def save_pending(*cards):
    skill_routes.PENDING_FILE.write_text(json.dumps(list(cards)))


def test_pending_is_empty_when_there_is_no_file():
    assert client.get("/skills/pending").json() == []


def test_pending_lists_only_cards_waiting_for_review():
    save_pending(card("read_price"), card("open_package", approved=True))
    listed = client.get("/skills/pending").json()
    assert [c["skill_id"] for c in listed] == ["read_price"]
    assert listed[0]["exists"] is False


def test_pending_flags_a_card_that_is_already_saved(temp_skills):
    (temp_skills / "read_price.json").write_text("{}")
    save_pending(card("read_price"))
    assert client.get("/skills/pending").json()[0]["exists"] is True


def test_approve_saves_the_card_without_the_approved_flag(temp_skills):
    save_pending(card("read_price"))
    assert client.post("/skills/read_price/approve").status_code == 200
    saved = json.loads((temp_skills / "read_price.json").read_text())
    assert saved["title"] == "Read a price"
    assert "approved" not in saved
    assert client.get("/skills/pending").json() == []


def test_approve_does_not_overwrite_an_existing_card(temp_skills):
    (temp_skills / "read_price.json").write_text('{"title": "Original"}')
    save_pending(card("read_price"))
    assert client.post("/skills/read_price/approve").status_code == 409
    assert json.loads((temp_skills / "read_price.json").read_text())["title"] == "Original"


def test_approve_needs_two_to_four_steps(temp_skills):
    save_pending(card("read_price", steps=1), card("open_package", steps=5))
    assert client.post("/skills/read_price/approve").status_code == 400
    assert client.post("/skills/open_package/approve").status_code == 400
    assert list(temp_skills.iterdir()) == []


def test_approve_unknown_or_unsafe_id_is_not_found():
    save_pending(card("read_price"))
    assert client.post("/skills/nothing_here/approve").status_code == 404
    assert client.post("/skills/Bad-Id/approve").status_code == 404


def test_reject_removes_the_card_and_saves_nothing(temp_skills):
    save_pending(card("read_price"), card("open_package"))
    assert client.post("/skills/read_price/reject").status_code == 200
    assert [c["skill_id"] for c in client.get("/skills/pending").json()] == ["open_package"]
    assert list(temp_skills.iterdir()) == []


def test_reject_unknown_card_is_not_found():
    assert client.post("/skills/read_price/reject").status_code == 404
