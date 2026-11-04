"""'I'm stuck' (Role D, D2 and D3). Used by POST /ask.

The flow for one request:

    typed text + optional photo
        |
    1. clean up: trim, cut very long text
    2. no text and no photo?          -> ask them to say what is hard
    3. danger words?                  -> needs_person: true, model NOT called
    4. health / allergy / diet?       -> fixed reply, model NOT called
    5. asking us to pick a food?      -> fixed reply, model NOT called
    6. build the prompt (task, steps, current step, help codes, text)
    7. call the model (llm.py)
    8. check the answer in code: valid JSON, under 20 words, no new food
       - bad answer: retry ONCE, with the problem named
       - still bad, or the model call failed: safe fallback
    9. photo is never saved and is dropped from memory when we finish

Privacy: nothing the person typed and no photo is written to disk or logs.
The person's name is never sent to the model, only help codes.
"""
from __future__ import annotations

from . import llm
from .common import (
    BACKEND_DIR,
    extract_json,
    fill,
    load_task,
    read_prompt,
    steps_block,
    task_text,
    top_level_step_id,
)
from .safety import (
    FOOD_CHOICE_REPLY,
    HEALTH_REPLY,
    SAFETY_REPLY,
    danger_check,
    food_choice_check,
    health_check,
    new_food_words,
)

MAX_TEXT_CHARS = 500          # longer messages are cut. The model reads the first 500 characters.
MAX_REPLY_WORDS = 19          # "under 20 words"
MAX_IMAGE_CHARS = 3_000_000   # about 2 MB of image. The screen shrinks photos before sending.

EMPTY_REPLY = "Tell me what is hard, or take a photo of it."
IMAGE_TOO_BIG_REPLY = "That photo is too big. Please try a smaller one."


def _fallback() -> dict:
    """A fresh copy of the safe fallback (so nobody can change the shared one)."""
    return dict(llm.SAFE_FALLBACK)


def _result(reply: str, step_id_guess=None, needs_person: bool = False) -> dict:
    return {"reply": reply, "step_id_guess": step_id_guess, "needs_person": needs_person}


# --------------------------------------------------------------------------------
# Help codes: where this person usually gets stuck (codes only, never a name)
# --------------------------------------------------------------------------------
def _sticking_codes(person_id: str, task_id: str) -> list[str]:
    """Best effort. Reads this person's live events and runs A's detect().

    If B's loader or A's detect() do not exist yet, or anything goes wrong, we
    return an empty list and the AI simply gets no codes. /ask still works.
    """
    try:
        from logic.data_io import load_definitions, load_events  # B1
        from logic.detect import detect  # A3

        live = BACKEND_DIR / "data" / "live" / "events.csv"
        if not live.is_file():
            return []
        events = load_events(str(live), person_id=person_id, task_id=task_id)
        found = detect(events, load_definitions(), 0)
        codes = []
        for item in found:
            code = item.get("code")
            if not code or code == "none":
                continue
            sid = item.get("step_id")
            codes.append(f"{code}:{sid}" if sid else code)
        return codes
    except Exception:  # noqa: BLE001
        return []


# --------------------------------------------------------------------------------
# Building the prompt
# --------------------------------------------------------------------------------
def build_user_prompt(task: dict, step_id, codes: list[str], text: str, has_image: bool) -> str:
    """Fill prompts/ask_user_template.md."""
    current = "not known"
    sid = top_level_step_id(task, step_id)
    if sid:
        step = next(s for s in task["steps"] if s["step_id"] == sid)
        current = f"{sid}. {step['text']}"
    # The person's text sits inside <person_message> tags. Remove any tag they typed,
    # so they cannot close the tag early and write fake instructions after it.
    safe_text = text.replace("<person_message>", "").replace("</person_message>", "")
    return fill(
        read_prompt("ask_user_template.md"),
        task_title=task.get("title", ""),
        steps_block=steps_block(task),
        current_step=current,
        codes=", ".join(codes) if codes else "none yet",
        user_text=safe_text if safe_text else "(no text, see the photo)",
        image_note="A photo is attached. It should show the thing the person is stuck on.\n"
        if has_image
        else "",
    )


# --------------------------------------------------------------------------------
# Checking the model's answer in code
# --------------------------------------------------------------------------------
def validate_reply(raw: str, task: dict) -> tuple[dict | None, str]:
    """Return (clean result, "") if the answer is good, or (None, reason) if not."""
    data = extract_json(raw)
    if data is None:
        return None, "it was not valid JSON"

    reply = data.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        return None, "reply was missing"
    reply = " ".join(reply.split())

    needs = data.get("needs_person", False)
    if isinstance(needs, str):
        needs = needs.strip().lower() == "true"
    if not isinstance(needs, bool):
        return None, "needs_person must be true or false"

    guess = top_level_step_id(task, data.get("step_id_guess"))

    if needs:
        # Always the same words when someone may be in danger.
        return _result(SAFETY_REPLY, guess, True), ""

    if len(reply.split()) > MAX_REPLY_WORDS:
        return None, f"the reply was {len(reply.split())} words, it must be under 20"

    foods = new_food_words(reply, task_text(task))
    if foods:
        return None, "the reply named food that is not in the task: " + ", ".join(foods)

    return _result(reply, guess, False), ""


# --------------------------------------------------------------------------------
# The main function
# --------------------------------------------------------------------------------
def ask(person_id: str, task_id: str, step_id, text: str, image: str | None = None) -> dict:
    """Answer one "I'm stuck" request.

    Returns {"reply": str, "step_id_guess": str or None, "needs_person": bool}.
    Raises TaskNotFound if the task does not exist (the route turns that into a 404).
    """
    task = load_task(task_id)

    text = (text or "").strip()[:MAX_TEXT_CHARS]
    if not text and not image:
        return _result(EMPTY_REPLY)

    # Checks that run before the model. The model is never called for these.
    if danger_check(text):
        return _result(SAFETY_REPLY, None, True)
    if health_check(text):
        return _result(HEALTH_REPLY)
    if food_choice_check(text):
        return _result(FOOD_CHOICE_REPLY)
    if image and len(image) > MAX_IMAGE_CHARS:
        return _result(IMAGE_TOO_BIG_REPLY)

    system_prompt = read_prompt("ask_system.md")
    user_prompt = build_user_prompt(
        task, step_id, _sticking_codes(person_id, task_id), text, bool(image)
    )

    try:
        problem = ""
        for attempt in range(2):  # first try, then ONE retry
            prompt = user_prompt
            if problem:
                prompt += (
                    f"\n\nYour last answer was not accepted because {problem}. "
                    "Reply again with JSON only and a reply under 20 words."
                )
            raw = llm.call_llm(system_prompt, prompt, image)
            if llm.is_fallback(raw):
                break  # the model call itself failed. Retrying would only wait longer.
            result, problem = validate_reply(raw, task)
            if result is not None:
                return result
        return _fallback()
    finally:
        # The photo is not saved anywhere. Drop our reference to it now.
        image = None
