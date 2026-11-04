"""Routes for the review page.

POST /split saves AI suggestions to splits_pending.json with approved false.
A person edits and approves them here, and only then do they go into the task file.
"""
import json
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai import common, split
from ai.common import StepNotFound, TaskNotFound
from ai.split import MAX_SUBSTEPS, MIN_SUBSTEPS

router = APIRouter(prefix="/review")

MAX_LENGTH = 120


class Approval(BaseModel):
    substeps: list[str]


def _read_pending() -> list[dict]:
    try:
        data = json.loads(common.PENDING_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def _write_json(path, data) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def _find_step(task: dict, step_id: str) -> dict:
    for step in task.get("steps", []):
        if step["step_id"] == step_id:
            return step
    raise StepNotFound(step_id)


def _clean(substeps: list[str]) -> list[str]:
    cleaned = [" ".join(s.split()) for s in substeps]
    if any(not s for s in cleaned):
        raise HTTPException(status_code=400, detail="A small step is empty.")
    if any(len(s) > MAX_LENGTH for s in cleaned):
        raise HTTPException(status_code=400, detail=f"Each small step must be under {MAX_LENGTH} characters.")
    if not MIN_SUBSTEPS <= len(cleaned) <= MAX_SUBSTEPS:
        raise HTTPException(
            status_code=400,
            detail=f"A step needs {MIN_SUBSTEPS} to {MAX_SUBSTEPS} small steps.",
        )
    return cleaned


@router.get("/pending")
def pending():
    """Suggestions waiting for a person, with the step as it is now."""
    waiting = []
    for entry in _read_pending():
        if entry.get("approved") is not False:
            continue
        item = dict(entry, task_title="", step_text="", current_substeps=[])
        try:
            task = common.load_task(entry["task_id"])
            step = _find_step(task, entry["step_id"])
            item["task_title"] = task.get("title", entry["task_id"])
            item["step_text"] = step["text"]
            item["current_substeps"] = [s["text"] for s in step.get("substeps", [])]
        except (TaskNotFound, StepNotFound):
            pass  # the page shows these as out of date so they can be rejected
        waiting.append(item)
    return waiting


@router.post("/{split_id}/approve")
def approve(split_id: str, body: Approval):
    """Save the (possibly edited) small steps into the task file."""
    cleaned = _clean(body.substeps)
    with split._write_lock:  # the same lock split.py uses
        entries = _read_pending()
        entry = next((e for e in entries if e.get("split_id") == split_id and e.get("approved") is False), None)
        if entry is None:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        try:
            task = common.load_task(entry["task_id"])
            step = _find_step(task, entry["step_id"])
        except (TaskNotFound, StepNotFound):
            raise HTTPException(status_code=404, detail="That task or step no longer exists")

        step["substeps"] = [
            {"id": f"{entry['step_id']}{chr(ord('a') + i)}", "text": text} for i, text in enumerate(cleaned)
        ]
        _write_json(common.TASKS_DIR / f"{entry['task_id']}.json", task)

        entry["substeps"] = cleaned
        entry["approved"] = True
        _write_json(common.PENDING_FILE, entries)
    return {"split_id": split_id, "approved": True, "substeps": cleaned}


@router.post("/{split_id}/reject")
def reject(split_id: str):
    """Throw a suggestion away. The task file is not touched."""
    with split._write_lock:
        entries = _read_pending()
        kept = [e for e in entries if not (e.get("split_id") == split_id and e.get("approved") is False)]
        if len(kept) == len(entries):
            raise HTTPException(status_code=404, detail="Suggestion not found")
        _write_json(common.PENDING_FILE, kept)
    return {"split_id": split_id, "rejected": True}
