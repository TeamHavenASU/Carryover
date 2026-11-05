"""AI drafts a skill card (Role D). Used by POST /draft_skill.

A skill card teaches one base skill that a task step assumes, like "Read the
cooking time" (backend/data/skills/*.json, docs in data/skills/README.md).

Two jobs, one function:
  - The task has a step and a skill name: draft the card.
  - The person stays stuck at Most help on a step: no skill name is given. The model
    names the base skill that may be missing. If a card for it already exists, we
    only say so. Otherwise it drafts a new card.

A person must approve every AI card before anyone sees it:

    POST /draft_skill -> data/skill_cards_pending.json (approved: false)
    POST /skills/<skill_id>/approve -> writes data/skills/<skill_id>.json
    POST /skills/<skill_id>/reject  -> removes it from the pending file

This module never writes to data/skills/ except in approve_card(), which a person
calls after reading the card. Cards follow the rules in data/skills/README.md:
2 to 4 steps, plain words, one action each, no brands, no money or medical advice.
"""
from __future__ import annotations

import json
import os
import re
import threading

from . import llm
from .common import (
    SKILL_PENDING_FILE,
    SKILLS_DIR,
    StepNotFound,
    extract_json,
    load_task,
    read_prompt,
    steps_block,
    task_text,
)
from .safety import new_food_words, reply_breaks_rules

MIN_STEPS = 2
MAX_STEPS = 4
MAX_WORDS = 14
MAX_TIPS = 2
_lock = threading.Lock()


def existing_skills() -> dict[str, str]:
    """{skill_id: title} for every approved card."""
    found = {}
    for path in sorted(SKILLS_DIR.glob("*.json")):
        try:
            card = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(card, dict) and card.get("skill_id"):
            found[card["skill_id"]] = card.get("title", card["skill_id"])
    return found


def slug(text: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", (text or "").lower())).strip("_")[:40]


def _plain(text: str) -> str:
    """Title or id without small words, so 'Read the cooking time' equals 'read_cooking_time'."""
    words = [w for w in re.split(r"[^a-z0-9]+", (text or "").lower()) if w and w not in {"the", "a", "an", "your", "to"}]
    return " ".join(words)


def find_existing(name: str, known: dict[str, str]) -> str | None:
    """The skill_id of an approved card that already covers this name, or None."""
    wanted = _plain(name)
    for skill_id, title in known.items():
        if wanted and wanted in (_plain(skill_id), _plain(title)):
            return skill_id
    return None


def _read_pending() -> list[dict]:
    try:
        data = json.loads(SKILL_PENDING_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def _write(path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def build_user_prompt(task: dict, step: dict, skill_title: str | None, known: dict[str, str]) -> str:
    lines = [f"Task: {task.get('title', '')}", "Steps:", steps_block(task), ""]
    lines.append(f"The step the person is stuck on: {step['step_id']}. {step['text']}")
    if step.get("base_skills"):
        lines.append("Base skills this step already lists: " + ", ".join(step["base_skills"]))
    lines.append("Skill cards that already exist (do not copy these):")
    lines += [f"- {sid}: {title}" for sid, title in known.items()] or ["- none"]
    lines.append("")
    if skill_title:
        lines.append(f"Write a skill card for this base skill: {skill_title}")
    else:
        lines.append("Name the one base skill this person may be missing, then write its card.")
    lines.append("Reply with JSON only.")
    return "\n".join(lines)


def validate_card(raw: str, task: dict, known: dict[str, str]) -> tuple[dict | None, str]:
    """Return (clean card fields, "") or (None, reason)."""
    data = extract_json(raw)
    if data is None:
        return None, "it was not valid JSON"
    title = " ".join(str(data.get("title", "")).split())
    why = " ".join(str(data.get("why", "")).split())
    steps = data.get("steps")
    tips = data.get("tips", [])
    if not title or len(title.split()) > 8:
        return None, "title must be 1 to 8 words"
    if not why or len(why.split()) > 30:
        return None, "why must be one short sentence"
    if not isinstance(steps, list) or not all(isinstance(x, str) for x in steps):
        return None, "steps must be a list of text"
    steps = [" ".join(x.split()).rstrip(". ") for x in steps]
    if not MIN_STEPS <= len(steps) <= MAX_STEPS or any(not x for x in steps):
        return None, f"it needs {MIN_STEPS} to {MAX_STEPS} steps"
    for x in steps:
        if len(x.split()) > MAX_WORDS:
            return None, f'"{x}" is longer than {MAX_WORDS} words'
    if not isinstance(tips, list) or not all(isinstance(x, str) for x in tips):
        return None, "tips must be a list of text"
    tips = [" ".join(x.split()) for x in tips if x.strip()][:MAX_TIPS]

    text = " ".join([title, why, *steps, *tips])
    allowed = task_text(task)
    foods = new_food_words(text, allowed)
    if foods:
        return None, "it named food that is not in the task: " + ", ".join(foods)
    broken = reply_breaks_rules(text)
    if broken and broken not in allowed:
        return None, f'"{broken}" is not allowed. No times, money, "safe" or "cooked" words, or buying advice'
    if re.search(r"\b(brand|amazon|walmart|visa|mastercard|paypal|venmo|apple pay|google pay)\b", text.lower()):
        return None, "no brand names"
    return {"title": title, "why": why, "steps": steps, "tips": tips}, ""


def draft_skill_card(task_id: str, step_id: str, skill_title: str | None = None) -> dict:
    """Ask the model for a skill card and save it for review.

    Returns {"status": "pending", "skill_id": ..., "card": {...}},
            {"status": "exists", "skill_id": ...} if a card for it is already approved,
            or {"status": "failed"} if the model fails or gives a bad card twice.
    Raises TaskNotFound or StepNotFound.
    """
    task = load_task(task_id)
    step = next((s for s in task.get("steps", []) if s["step_id"] == step_id), None)
    if step is None:
        raise StepNotFound(step_id)

    known = existing_skills()
    system_prompt = read_prompt("skill_card_system.md")
    user_prompt = build_user_prompt(task, step, skill_title, known)

    problem = ""
    for _attempt in range(2):  # first try, then ONE retry
        prompt = user_prompt
        if problem:
            prompt += f"\n\nYour last answer was not accepted because {problem}. Reply again with JSON only."
        raw = llm.call_llm(system_prompt, prompt)
        if llm.is_fallback(raw):
            break
        card, problem = validate_card(raw, task, known)
        if card is None:
            continue
        have = find_existing(skill_title or card["title"], known) or find_existing(card["title"], known)
        if have:
            return {"status": "exists", "skill_id": have}
        skill_id = slug(skill_title or card["title"])
        entry = {
            "skill_id": skill_id,
            "title": card["title"],
            "why": card["why"],
            "steps": [{"id": f"{skill_id}_{i}", "text": t} for i, t in enumerate(card["steps"], 1)],
            "tips": card["tips"],
            "used_by": [f"{task_id}:{step_id}"],
            "picture": None,
            "video": None,
            "approved": False,
        }
        with _lock:
            pending = _read_pending()
            if not any(e.get("skill_id") == skill_id and e.get("approved") is False for e in pending):
                pending.append(entry)
                _write(SKILL_PENDING_FILE, pending)
        return {"status": "pending", "skill_id": skill_id, "card": entry}
    return {"status": "failed"}


# --------------------------------------------------------------------------------
# Review: a person reads the card, then approves or rejects it
# --------------------------------------------------------------------------------
def pending_cards() -> list[dict]:
    return [e for e in _read_pending() if e.get("approved") is False]


def approve_card(skill_id: str) -> dict | None:
    """Write the approved card to data/skills/. Returns the card, or None if not found."""
    if not re.fullmatch(r"[a-z0-9_]+", skill_id or ""):
        return None
    with _lock:
        pending = _read_pending()
        entry = next((e for e in pending if e.get("skill_id") == skill_id and e.get("approved") is False), None)
        if entry is None:
            return None
        card = {k: v for k, v in entry.items() if k != "approved"}
        _write(SKILLS_DIR / f"{skill_id}.json", card)
        entry["approved"] = True
        _write(SKILL_PENDING_FILE, pending)
        return card


def reject_card(skill_id: str) -> bool:
    with _lock:
        pending = _read_pending()
        kept = [e for e in pending if not (e.get("skill_id") == skill_id and e.get("approved") is False)]
        if len(kept) == len(pending):
            return False
        _write(SKILL_PENDING_FILE, kept)
        return True
