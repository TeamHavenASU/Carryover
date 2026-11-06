"""The routes Role D owns: POST /ask, POST /split, POST /draft_skill. The skill card review routes are in api/skill_routes.py.

api/main.py includes this router. Run the backend from the backend/ folder:  uvicorn api.main:app --reload
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai.ask import ask
from ai.common import StepNotFound, TaskNotFound
from ai import skill_card
from ai.split import split_step

router = APIRouter()


class AskRequest(BaseModel):
    person_id: str
    task_id: str
    step_id: str | None = None
    text: str = ""
    image: str | None = None   # data URL or base64, shrunk by the screen. Never saved.


class SplitRequest(BaseModel):
    task_id: str
    step_id: str
    hand: str | None = None   # "left", "right" or "either" turns on the extra detail version


class DraftSkillRequest(BaseModel):
    task_id: str
    step_id: str
    skill_title: str | None = None   # leave out to let the AI name the missing base skill


@router.post("/ask")
def ask_route(req: AskRequest):
    """In: person_id, task_id, step_id, text, image (optional).
    Out: {"reply": "...", "step_id_guess": "s3", "needs_person": false}"""
    try:
        return ask(req.person_id, req.task_id, req.step_id, req.text, req.image)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/split")
def split_route(req: SplitRequest):
    """In: task_id, step_id.  Out: {"substeps": ["..."], "approved": false}"""
    try:
        return split_step(req.task_id, req.step_id, req.hand)
    except (TaskNotFound, StepNotFound):
        raise HTTPException(status_code=404, detail="Task or step not found")


@router.post("/draft_skill")
def draft_skill_route(req: DraftSkillRequest):
    """In: task_id, step_id, skill_title (optional).
    Out: {"status": "pending" | "exists" | "failed", "skill_id": ..., "card": {...}}
    A pending card is saved to data/skill_cards_pending.json. A person must approve it."""
    try:
        return skill_card.draft_skill_card(req.task_id, req.step_id, req.skill_title)
    except (TaskNotFound, StepNotFound):
        raise HTTPException(status_code=404, detail="Task or step not found")
