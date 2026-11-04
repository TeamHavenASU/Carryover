"""The two routes Role D owns: POST /ask and POST /split.

E creates api/main.py. Add these two lines to it:

    from api.ai_routes import router as ai_router
    app.include_router(ai_router)

Run the backend from the backend/ folder:  uvicorn api.main:app --reload
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai.ask import ask
from ai.common import StepNotFound, TaskNotFound
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
        return split_step(req.task_id, req.step_id)
    except (TaskNotFound, StepNotFound):
        raise HTTPException(status_code=404, detail="Task or step not found")
