"""AI step splitting (Role D, D4). Used by POST /split.

The AI breaks ONE hard step into 3 to 6 smaller steps. A person must approve them
before any resident sees them:

    POST /split  ->  AI writes substeps  ->  saved to data/splits_pending.json
                     with approved: false  ->  E's /review page  ->  person edits and
                     approves  ->  E's route writes them into the task file.

This file only ever writes to splits_pending.json. It never touches the task
files. The resident app only shows substeps that are in the task file.
"""
from __future__ import annotations

import json
import os
import re
import threading
import uuid

from . import llm
from .common import (
    PENDING_FILE,
    TASKS_DIR,
    StepNotFound,
    extract_json,
    fill,
    load_task,
    read_prompt,
    task_text,
)
from .safety import new_food_words, reply_breaks_rules

MIN_SUBSTEPS = 3
MAX_SUBSTEPS = 6
MAX_WORDS = 7   # "under 8 words"
MAX_WORDS_EXTRA = 11  # extra detail names the hand and the direction, so it needs a few more words
HANDS = ("left", "right", "either")

# Used only if fewer than 2 real examples exist in the task files yet.
# This is the example from the Build Spec (Format 1).
_BUILT_IN_EXAMPLES = [
    {
        "task": "Make a sandwich",
        "step": "Put peanut butter on the bread",
        "substeps": ["Open the jar", "Scoop with the knife", "Spread on one slice", "Close the jar"],
    },
    {
        "task": "Brush your teeth",
        "step": "Put toothpaste on the brush",
        "substeps": ["Pick up the brush", "Open the toothpaste", "Squeeze a small amount on", "Close the toothpaste"],
    },
    {
        "task": "Pour a drink",
        "step": "Fill the glass with water",
        "substeps": ["Pick up a glass", "Turn on the tap", "Fill the glass", "Turn off the tap"],
    },
]

_write_lock = threading.Lock()


# --------------------------------------------------------------------------------
# Examples and prompt
# --------------------------------------------------------------------------------
def pick_examples(task_id: str, step_id: str, step_text: str = "", count: int = 2) -> list[dict]:
    """Two already split steps from the task files, never the step being split."""
    examples = []
    for path in sorted(TASKS_DIR.glob("*.json")):
        try:
            task = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for step in task.get("steps", []):
            if task.get("task_id") == task_id and step.get("step_id") == step_id:
                continue
            subs = [s["text"] for s in step.get("substeps", []) if isinstance(s, dict) and s.get("text")]
            if subs:
                examples.append({"task": task.get("title", ""), "step": step["text"], "substeps": subs})
    for fallback in _BUILT_IN_EXAMPLES:
        if len(examples) >= count:
            break
        if fallback["step"].lower() == step_text.lower():
            continue  # never show the model the answer to the step it is splitting
        if any(e["step"].lower() == fallback["step"].lower() for e in examples):
            continue  # already have this one from the task files
        examples.append(fallback)
    return examples[:count]


def build_user_prompt(task: dict, step: dict, examples: list[dict], hand: str | None = None) -> str:
    lines = []
    for i, ex in enumerate(examples, 1):
        lines.append(f"Example {i}")
        lines.append(f"Task: {ex['task']}")
        lines.append(f"Step: {ex['step']}")
        lines.append("Smaller steps: " + json.dumps({"substeps": ex["substeps"]}))
        lines.append("")
    others = [f"- {s['text']}" for s in task.get("steps", []) if s["step_id"] != step["step_id"]]
    lines.append("Now split this step.")
    lines.append(f"Task: {task.get('title', '')}")
    if others:
        lines.append("Other steps in this task, for context only:")
        lines += others
    lines.append(f"Step to split: {step['text']}")
    if step.get("hint"):
        lines.append(f"Short version of the step: {step['hint']}")
    if hand:
        lines.append("")
        lines.append(
            "Extra detail is on. The person's hand setting is: "
            + ("they use their left hand" if hand == "left"
               else "they use their right hand" if hand == "right"
               else "either hand is fine, so do not name a hand")
            + "."
        )
    lines.append("")
    lines.append("Reply with JSON only.")
    return "\n".join(lines)


# --------------------------------------------------------------------------------
# Checking the model's answer in code
# --------------------------------------------------------------------------------
def validate_substeps(raw: str, task: dict, step: dict, max_words: int = MAX_WORDS) -> tuple[list[str] | None, str]:
    """Return (clean list, "") if the answer is good, or (None, reason) if not."""
    data = extract_json(raw)
    if data is None:
        return None, "it was not valid JSON"
    items = data.get("substeps")
    if not isinstance(items, list) or not all(isinstance(i, str) for i in items):
        return None, "substeps must be a list of text"

    cleaned = [" ".join(i.split()).rstrip(". ") for i in items]
    if any(not c for c in cleaned):
        return None, "a step was empty"
    if not MIN_SUBSTEPS <= len(cleaned) <= MAX_SUBSTEPS:
        return None, f"it gave {len(cleaned)} steps, it must give {MIN_SUBSTEPS} to {MAX_SUBSTEPS}"
    for c in cleaned:
        if len(c.split()) > max_words:
            return None, f'"{c}" is longer than {max_words} words'
        if re.search(r"\b(and|then)\b|[;,]", c.lower()):
            return None, f'"{c}" has more than one action'
    if len({c.lower() for c in cleaned}) != len(cleaned):
        return None, "two steps were the same"

    allowed = task_text(task) + " " + step.get("text", "").lower()
    foods = new_food_words(" ".join(cleaned), allowed)
    if foods:
        return None, "it named food that is not in the task: " + ", ".join(foods)
    # No cooking times, no money numbers, no "safe" or "cooked" claims, no buying advice.
    # (A phrase that the task's own steps already use is fine.)
    broken = reply_breaks_rules(" ".join(cleaned))
    if broken and broken not in allowed:
        return None, f'"{broken}" is not allowed. No times, money, "safe" or "cooked" words, or buying advice'
    return cleaned, ""


# --------------------------------------------------------------------------------
# Saving to the pending file (the only file this module writes)
# --------------------------------------------------------------------------------
def _read_pending() -> list[dict]:
    try:
        data = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def save_pending(task_id: str, step_id: str, substeps: list[str], hand: str | None = None) -> str | None:
    """Add a waiting entry. Returns its split_id, or None if the same one already waits."""
    with _write_lock:
        entries = _read_pending()
        for e in entries:
            if (
                e.get("task_id") == task_id
                and e.get("step_id") == step_id
                and e.get("approved") is False
                and e.get("substeps") == substeps
                and e.get("hand") == hand
            ):
                return None  # same suggestion already waiting for review
        split_id = f"{task_id}-{step_id}-{uuid.uuid4().hex[:6]}"
        entry = {
            "split_id": split_id,
            "task_id": task_id,
            "step_id": step_id,
            "substeps": substeps,
            "approved": False,
        }
        if hand:
            # Extra detail version. A person must approve it. It is marked so the
            # review page can show which hand it was written for.
            entry["variant"] = "extra_detail"
            entry["hand"] = hand
        entries.append(entry)
        PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = PENDING_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        os.replace(tmp, PENDING_FILE)  # write the whole file or nothing
        return split_id


# --------------------------------------------------------------------------------
# The main function
# --------------------------------------------------------------------------------
def split_step(task_id: str, step_id: str, hand: str | None = None) -> dict:
    """Ask the model to split one step. Returns {"substeps": [...], "approved": False}.

    On success the substeps are also saved to splits_pending.json for a person to
    approve. If the model fails or gives bad steps twice, we return an empty list
    and save nothing.
    hand: "left", "right" or "either" turns on the extra detail version, which names
    the hand and the direction. None is the normal split.
    Raises TaskNotFound or StepNotFound (the route turns these into a 404).
    """
    if hand is not None and hand not in HANDS:
        hand = None
    task = load_task(task_id)
    step = next((s for s in task.get("steps", []) if s["step_id"] == step_id), None)
    if step is None:
        raise StepNotFound(step_id)

    system_prompt = read_prompt("split_system.md")
    if hand:
        system_prompt += "\n\n" + read_prompt("split_extra_detail.md")
    max_words = MAX_WORDS_EXTRA if hand else MAX_WORDS
    user_prompt = build_user_prompt(task, step, pick_examples(task_id, step_id, step["text"]), hand)

    problem = ""
    for attempt in range(2):  # first try, then ONE retry
        prompt = user_prompt
        if problem:
            prompt += (
                f"\n\nYour last answer was not accepted because {problem}. "
                "Reply again with JSON only."
            )
        raw = llm.call_llm(system_prompt, prompt)
        if llm.is_fallback(raw):
            break
        substeps, problem = validate_substeps(raw, task, step, max_words)
        if substeps is not None:
            save_pending(task_id, step_id, substeps, hand)
            return {"substeps": substeps, "approved": False}
    return {"substeps": [], "approved": False}
