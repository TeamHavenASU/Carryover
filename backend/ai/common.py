"""Small shared helpers for ask.py and split.py (Role D).

Nothing here talks to the model. It only loads task files and prompt files and
cleans up the model's text.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = Path(os.getenv("TASKS_DIR", BACKEND_DIR / "data" / "tasks"))
PROMPTS_DIR = BACKEND_DIR / "prompts"
PENDING_FILE = Path(
    os.getenv("SPLITS_PENDING_FILE", BACKEND_DIR / "data" / "splits_pending.json")
)


class TaskNotFound(Exception):
    """The task file does not exist (or the task id is not a safe name)."""


class StepNotFound(Exception):
    """The step id is not in the task."""


def load_task(task_id: str) -> dict:
    """Read data/tasks/<task_id>.json (Format 1).

    The task id is checked so nobody can ask for ../../something.
    """
    if not isinstance(task_id, str) or not re.fullmatch(r"[a-z0-9_]+", task_id):
        raise TaskNotFound(task_id)
    path = TASKS_DIR / f"{task_id}.json"
    if not path.is_file():
        raise TaskNotFound(task_id)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_prompt(name: str) -> str:
    """Read a prompt file from backend/prompts/."""
    return (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()


def fill(template: str, **values: str) -> str:
    """Replace {{name}} markers. Plain replace, so braces in task text are safe."""
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", str(value))
    return out


def extract_json(text: str):
    """Pull a JSON object out of the model's reply.

    Handles ```json fences and a little text around the object. Returns a dict,
    or None if no valid JSON object is found.
    """
    if not isinstance(text, str):
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    for candidate in (cleaned, _between_braces(cleaned)):
        if not candidate:
            continue
        try:
            data = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None


def _between_braces(text: str) -> str:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return ""
    return text[start : end + 1]


def task_text(task: dict) -> str:
    """All the words in a task, lower case. Used to check the model adds no new food."""
    parts = [task.get("title", ""), task.get("start_push") or ""]
    for step in task.get("steps", []):
        parts += [step.get("text", ""), step.get("hint") or "", step.get("check_question") or ""]
        for sub in step.get("substeps", []):
            parts.append(sub.get("text", "") if isinstance(sub, dict) else str(sub))
    return " ".join(parts).lower()


def steps_block(task: dict) -> str:
    """Every step and substep as plain lines for the prompt."""
    lines = []
    for step in task.get("steps", []):
        lines.append(f"{step['step_id']}. {step['text']}")
        for sub in step.get("substeps", []):
            if isinstance(sub, dict):
                lines.append(f"    {sub['id']}. {sub['text']}")
    return "\n".join(lines)


def top_level_step_id(task: dict, step_id):
    """Return the top level step id for a step or substep id, or None if unknown.

    The model may answer "s3a" (a substep). The app only tracks "s3".
    """
    if not isinstance(step_id, str):
        return None
    for step in task.get("steps", []):
        if step["step_id"] == step_id:
            return step_id
        for sub in step.get("substeps", []):
            if isinstance(sub, dict) and sub.get("id") == step_id:
                return step["step_id"]
    return None
