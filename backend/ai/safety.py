"""Safety checks that run in code, not only in the prompt (Role D).

Three checks run BEFORE the model is called:
  1. danger_check      -> needs_person: true, fixed reply, model never called
  2. health_check      -> fixed reply: we do not give medical, allergy or diet advice
  3. food_choice_check -> fixed reply: we never pick foods for people

One check runs AFTER the model answers:
  4. new_food_words    -> the reply must not bring in a food the task never mentions

Why phrases and not single words: the spec lists words like "cut", "burn" and
"fire". But "How do I cut the bread?" and "I burnt the toast" are normal sandwich
questions. So we match phrases about a person being hurt, and test them in
tests/test_ai.py so a real sandwich question is never treated as an emergency.
"""
from __future__ import annotations

import re

SAFETY_REPLY = "Please get your support person or someone you trust now."
HEALTH_REPLY = "I can't give health advice. Please ask someone you trust."
FOOD_CHOICE_REPLY = "I can't pick food for you. You choose, or ask someone you trust."

# ---- 1. Danger: someone hurt, in danger, unsafe or very upset -----------------
DANGER_PATTERNS = [
    r"\bhurt(s|ing)?\b",
    r"\bin pain\b",
    r"\binjur(ed|y)\b",
    r"\bcut (myself|my\b)",
    r"\bgot cut\b",
    r"\bbleed(ing|s)?\b",
    r"\bblood\b",
    r"\bburn(ed|t|ing)? (myself|me\b|my (hand|hands|finger|fingers|arm|skin|face))",
    r"\bi('m| am| got) (burned|burnt)\b",
    r"\bfire\b",
    r"\bflames?\b",
    r"\bsmok(e|ing)\b",
    r"\bsmells? like (burning|smoke|gas)\b",
    r"\bgas leak\b",
    r"\bunsafe\b",
    r"\bnot safe\b",
    r"\bdanger(ous)?\b",
    r"\bemergency\b",
    r"\b911\b",
    r"\bchoking\b",
    r"\bcan'?t breathe\b",
    r"\bpassed out\b",
    r"\bfaint(ed|ing)\b",
    r"\bshocked me\b",
    r"\ballergic reaction\b",
    r"\bvery upset\b",
    r"\bpanic(king)?\b",
    r"\bscared\b",
    r"\bafraid\b",
    r"\bwant to die\b",
    r"\bkill myself\b",
    r"\bsuicid",
]

# ---- 2. Health: medical, allergy, diet -------------------------------------------
HEALTH_PATTERNS = [
    r"\ballerg(y|ic|ies)\b",
    r"\bmedic(ine|ation|al)\b",
    r"\bdoctor\b",
    r"\bdiet(ing)?\b",
    r"\bcalories?\b",
    r"\bgluten\b",
    r"\blactose\b",
    r"\bdiabet(es|ic)\b",
    r"\bsick\b",
    r"\bnausea\b",
    r"\bsafe to eat\b",
    r"\bfood poisoning\b",
]

# ---- 3. Asking us to choose food ---------------------------------------------------
# Only fires when a food word is in the question. "What should I put in the washer?"
# is a normal laundry question and must go to the model.
_FOOD_CONTEXT = r"(sandwich|food|meal|lunch|dinner|breakfast|snack|bread|topping|toppings|filling|fillings|ingredient|ingredients|eat)"
FOOD_CHOICE_PATTERNS = [
    rf"\bwhat\b.*\b(put|add|eat|use|have|make)\b.*\b{_FOOD_CONTEXT}\b",
    rf"\bwhat\b.*\b{_FOOD_CONTEXT}\b.*\b(put|add|eat|use|have|make)\b",
    r"\bwhat (should|can|could|do) i (eat|make for)\b",
    r"\brecipe\b",
    r"\bingredients?\b",
    r"\bwhat goes (on|in|with)\b.*\b(sandwich|bread)\b",
]

# ---- 4. Food words, used to catch the model suggesting a new food ----------------
FOOD_WORDS = [
    "peanut", "butter", "jelly", "jam", "cheese", "ham", "turkey", "lettuce",
    "tomato", "mayo", "mayonnaise", "mustard", "honey", "nutella", "chocolate",
    "egg", "eggs", "bacon", "avocado", "cucumber", "pickle", "pickles", "tuna",
    "chicken", "beef", "salami", "hummus", "banana", "apple", "strawberry",
    "sprinkles", "sugar", "syrup", "ketchup", "milk", "juice", "soda", "cereal",
    "pasta", "rice", "soup", "salad", "fruit", "vegetables", "meat", "nuts",
    "almond", "sauce", "cream", "yogurt", "onion", "pepper", "salt", "cinnamon",
]


def _matches(patterns: list[str], text: str) -> bool:
    lowered = (text or "").lower().replace("’", "'")
    return any(re.search(p, lowered) for p in patterns)


def danger_check(text: str) -> bool:
    """True if the person may be hurt, in danger, unsafe or very upset."""
    return _matches(DANGER_PATTERNS, text)


def health_check(text: str) -> bool:
    """True if the question is about health, allergies or diet."""
    return _matches(HEALTH_PATTERNS, text)


def food_choice_check(text: str) -> bool:
    """True if the person asks us to choose what food to use."""
    return _matches(FOOD_CHOICE_PATTERNS, text)


def new_food_words(text: str, allowed_text: str) -> list[str]:
    """Food words in `text` that do not appear in `allowed_text` (the task's own words)."""
    found = set(re.findall(r"[a-z']+", (text or "").lower()))
    allowed = set(re.findall(r"[a-z']+", (allowed_text or "").lower()))
    return sorted(w for w in FOOD_WORDS if w in found and w not in allowed)
