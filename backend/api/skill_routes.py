"""Routes for reviewing AI written skill cards.

New cards wait in skill_cards_pending.json. Nothing reaches a resident until a
person approves one here, and then it is saved as its own file in data/skills/.
"""
import json
import os
import re
import threading
from pathlib import Path

from fastapi import APIRouter, HTTPException

BACKEND_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = Path(os.getenv("SKILLS_DIR", BACKEND_DIR / "data" / "skills"))
PENDING_FILE = Path(
    os.getenv("SKILL_CARDS_PENDING_FILE", BACKEND_DIR / "data" / "skill_cards_pending.json")
)

MIN_STEPS = 2
MAX_STEPS = 4
MAX_LENGTH = 120

router = APIRouter(prefix="/skills")
_lock = threading.Lock()


def _read_pending() -> list[dict]:
    try:
        data = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def _write_json(path: Path, data) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def _safe_id(skill_id) -> bool:
    return isinstance(skill_id, str) and re.fullmatch(r"[a-z0-9_]+", skill_id) is not None


def _find_waiting(entries: list[dict], skill_id: str):
    if not _safe_id(skill_id):
        return None
    for entry in entries:
        if isinstance(entry, dict) and entry.get("skill_id") == skill_id and entry.get("approved") is not True:
            return entry
    return None


def _check_steps(card: dict) -> None:
    steps = card.get("steps")
    if not isinstance(steps, list) or not MIN_STEPS <= len(steps) <= MAX_STEPS:
        raise HTTPException(status_code=400, detail=f"A skill card needs {MIN_STEPS} to {MAX_STEPS} steps.")
    for step in steps:
        text = step.get("text") if isinstance(step, dict) else None
        if not isinstance(text, str) or not text.strip():
            raise HTTPException(status_code=400, detail="A step is empty.")
        if len(text) > MAX_LENGTH:
            raise HTTPException(status_code=400, detail=f"Each step must be under {MAX_LENGTH} characters.")


@router.get("/pending")
def pending():
    """Cards waiting for a person. exists is true if a card with that id is already saved."""
    waiting = []
    for entry in _read_pending():
        if not isinstance(entry, dict) or entry.get("approved") is True or not _safe_id(entry.get("skill_id")):
            continue
        exists = (SKILLS_DIR / f"{entry['skill_id']}.json").is_file()
        waiting.append(dict(entry, exists=exists))
    return waiting


@router.post("/{skill_id}/approve")
def approve(skill_id: str):
    """Save the card into data/skills/ and mark it approved."""
    with _lock:
        entries = _read_pending()
        entry = _find_waiting(entries, skill_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Skill card not found")
        _check_steps(entry)

        path = SKILLS_DIR / f"{skill_id}.json"
        if path.exists():
            raise HTTPException(status_code=409, detail="A skill card with this id already exists")

        card = {key: value for key, value in entry.items() if key != "approved"}
        _write_json(path, card)
        entry["approved"] = True
        _write_json(PENDING_FILE, entries)
    return {"skill_id": skill_id, "approved": True}


@router.post("/{skill_id}/reject")
def reject(skill_id: str):
    """Throw a card away. Nothing is saved to data/skills/."""
    with _lock:
        entries = _read_pending()
        entry = _find_waiting(entries, skill_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Skill card not found")
        _write_json(PENDING_FILE, [e for e in entries if e is not entry])
    return {"skill_id": skill_id, "rejected": True}
