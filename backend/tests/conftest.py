"""Shared test setup for Role D tests.

Tests never call the real model. They replace llm.call_llm with a fake, and they
point the task folder at tests/fixtures so they do not depend on A's files.
"""
import json
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from ai import common  # noqa: E402


@pytest.fixture(autouse=True)
def fixtures_and_tmp_pending(monkeypatch, tmp_path):
    """Use the fixture tasks and a temporary pending file."""
    pending = tmp_path / "splits_pending.json"
    monkeypatch.setattr(common, "TASKS_DIR", BACKEND / "tests" / "fixtures")
    monkeypatch.setattr(common, "PENDING_FILE", pending)
    from ai import split

    monkeypatch.setattr(split, "TASKS_DIR", BACKEND / "tests" / "fixtures")
    monkeypatch.setattr(split, "PENDING_FILE", pending)
    return pending


class FakeModel:
    """Stands in for call_llm. Gives replies from a list, one per call."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, system_prompt, user_text, image=None):
        self.calls.append({"system": system_prompt, "user": user_text, "image": image})
        return self.replies.pop(0)


@pytest.fixture
def fake_model(monkeypatch):
    from ai import llm

    def install(replies):
        fake = FakeModel([r if isinstance(r, str) else json.dumps(r) for r in replies])
        monkeypatch.setattr(llm, "call_llm", fake)
        return fake

    return install
