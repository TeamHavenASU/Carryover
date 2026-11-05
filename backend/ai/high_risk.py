"""High risk photo questions (Role D). Rules are in docs/safety.md, section 3.

Two questions are handled here, only when the person sends a photo:

  "Can this dish go in the microwave?"  -> microwave_safe(image)
  "How long do I heat this?"            -> cook_time(image)

The model's own "I'm sure" cannot be trusted, so the code makes the decision:

  1. Quote the label. The model must give the exact words printed on the dish or
     package. The code checks them. No label words, no "safe" answer.
  2. Ask 3 times. The same photo is sent 3 separate times. We answer only if all 3
     agree. One different answer, or one failed call, means a hand off.
  3. Never "safe" from looks. The model may say "don't use it" if it clearly sees
     metal, foil or foam, or if the label says not to. It can never say "safe"
     from how a dish looks.
  4. Otherwise hand off to the support person.

The model's own sentence is never shown. The reply is built here from fixed words,
so a photo with writing on it cannot make the app say something else.
The photo is never saved. It is not logged.
"""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor

from . import llm
from .common import extract_json, read_prompt
from .safety import (
    MICROWAVE_HANDOFF_REPLY,
    PHOTO_PERSON_REPLY,
    PHOTO_PRIVATE_REPLY,
    PHOTO_UNCLEAR_REPLY,
)

ASKS = 3  # the same photo is sent this many times. All must agree.

UNSAFE_REPLY = "Don't put it in the microwave. Use a plate you know is safe."
COOK_TIME_HANDOFF_REPLY = "I can't read one clear time. Please ask your support person."

# Words on a label that mean "this is OK in the microwave".
SAFE_PHRASES = [
    "microwave safe",
    "microwavable",
    "microwaveable",
    "safe for microwave",
    "safe for use in microwave",
    "microwave use",
    "microwave oven safe",
]
# These words mean the label says NOT to use it.
HARD_NEGATIONS = {"not", "no", "dont", "don't", "never", "unsafe", "cannot", "cant", "can't", "avoid"}
# These words limit the label. "Microwave safe lid only" does not make the whole dish
# safe, so we do not call it safe, and we do not call it unsafe either. We hand off.
SOFT_NEGATIONS = {"only", "except", "unless", "without", "bottom", "base", "lid", "top"}


def _normalize(text) -> str:
    text = str(text or "").lower().replace("’", "'")
    text = re.sub(r"[-_/]", " ", text)
    text = re.sub(r"[^a-z0-9': ]", " ", text)
    return " ".join(text.split())


def label_kind(quote) -> tuple[str, str]:
    """Read a label quote. Returns (kind, phrase).

    kind is "safe" (a safe phrase and no negation), "unsafe" (the label says not to),
    or "none" (no usable words). phrase is the safe phrase found, or "".
    """
    words = _normalize(quote)
    if not words:
        return "none", ""
    tokens = set(words.replace("'", "").split()) | set(words.split())
    found = next((p for p in SAFE_PHRASES if p in words), "")
    if tokens & HARD_NEGATIONS and "microwave" in words:
        return "unsafe", ""
    if found and not tokens & SOFT_NEGATIONS:
        return "safe", found
    return "none", ""


def _one_run(system_prompt: str, user_prompt: str, image: str) -> dict | None:
    raw = llm.call_llm(system_prompt, user_prompt, image)
    if llm.is_fallback(raw):
        return None
    data = extract_json(raw)
    return data if isinstance(data, dict) else None


def _ask_three_times(mode: str, image: str) -> list[dict] | None:
    system_prompt = read_prompt("photo_check_system.md")
    user_prompt = f"Mode: {mode}\nReply with JSON only."
    with ThreadPoolExecutor(max_workers=ASKS) as pool:
        futures = [pool.submit(_one_run, system_prompt, user_prompt, image) for _ in range(ASKS)]
        runs = [f.result() for f in futures]
    if any(r is None for r in runs):
        return None  # one failed call is enough to hand off
    return runs


def _result(reply: str) -> dict:
    return {"reply": reply, "step_id_guess": None, "needs_person": False}


def _photo_issue_reply(runs: list[dict]) -> str:
    """If any of the 3 runs says the photo is a problem, return the fixed words."""
    issues = {str(r.get("photo_issue", "none")).strip().lower() for r in runs}
    if "person" in issues:
        return PHOTO_PERSON_REPLY
    if "private" in issues:
        return PHOTO_PRIVATE_REPLY
    if "unclear" in issues:
        return PHOTO_UNCLEAR_REPLY
    return ""


# --------------------------------------------------------------------------------
# Can this dish go in the microwave?
# --------------------------------------------------------------------------------
def microwave_safe(image: str) -> dict:
    runs = _ask_three_times("microwave_safe", image)
    if runs is None:
        return _result(MICROWAVE_HANDOFF_REPLY)
    issue = _photo_issue_reply(runs)
    if issue:
        return _result(issue)

    verdicts = []
    phrases = []
    for run in runs:
        kind, phrase = label_kind(run.get("label_quote"))
        metal = run.get("sees_metal_foil_or_foam") is True
        if metal or kind == "unsafe":
            verdicts.append("unsafe")
        elif kind == "safe":
            verdicts.append("safe")
            phrases.append(phrase)
        else:
            verdicts.append("unknown")

    if len(set(verdicts)) != 1:
        return _result(MICROWAVE_HANDOFF_REPLY)  # the 3 answers did not agree
    if verdicts[0] == "unsafe":
        return _result(UNSAFE_REPLY)
    if verdicts[0] == "safe" and phrases:
        return _result(f'The label says "{phrases[0]}". You can use this dish.')
    return _result(MICROWAVE_HANDOFF_REPLY)


# --------------------------------------------------------------------------------
# How long do I heat this? (read the time printed on the package, nothing else)
# --------------------------------------------------------------------------------
_TIME_RE = re.compile(
    r"^(?:(?P<m1>\d{1,2})\s?(?:min|mins|minute|minutes|m)\b)?\s*"
    r"(?:(?P<s1>\d{1,2})\s?(?:sec|secs|second|seconds|s)\b)?$"
    r"|^(?P<m2>\d{1,2}):(?P<s2>\d{2})$"
)


def parse_seconds(value) -> int | None:
    """'2 min 30 sec', '2:30' or '45 sec' -> seconds. None if it is not a clear time."""
    text = _normalize(value).replace(":", ":")
    text = re.sub(r"\s*:\s*", ":", text)
    if not text:
        return None
    match = _TIME_RE.match(text)
    if not match:
        return None
    if match.group("m2") is not None:
        total = int(match.group("m2")) * 60 + int(match.group("s2"))
    else:
        minutes, seconds = match.group("m1"), match.group("s1")
        if minutes is None and seconds is None:
            return None
        total = int(minutes or 0) * 60 + int(seconds or 0)
    return total if 10 <= total <= 30 * 60 else None


def _digits(text) -> list[str]:
    return re.findall(r"\d+", str(text or ""))


def cook_time(image: str) -> dict:
    runs = _ask_three_times("cook_time", image)
    if runs is None:
        return _result(COOK_TIME_HANDOFF_REPLY)
    issue = _photo_issue_reply(runs)
    if issue:
        return _result(issue)

    totals = []
    for run in runs:
        seconds = parse_seconds(run.get("time_value"))
        quote_numbers = _digits(run.get("label_quote"))
        value_numbers = _digits(run.get("time_value"))
        if seconds is None or not value_numbers or not all(n in quote_numbers for n in value_numbers):
            return _result(COOK_TIME_HANDOFF_REPLY)  # no label words to back the time
        totals.append(seconds)
    if len(set(totals)) != 1:
        return _result(COOK_TIME_HANDOFF_REPLY)

    minutes, seconds = divmod(totals[0], 60)
    spoken = " ".join(
        part for part in (f"{minutes} min" if minutes else "", f"{seconds} sec" if seconds else "") if part
    )
    return _result(f"The package says {spoken}. Set that time, or ask your support person.")
