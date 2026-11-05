"""Safety checks that run in code, not only in the prompt (Role D).

Checks that run BEFORE the model is called (the model is never called for these):
  1. danger_check        -> needs_person: true, fixed reply (hurt, fire, sparks, scared)
  2. scam_check          -> needs_person: true (someone asks for a card, PIN or code)
  3. secret_check        -> the message holds a card number or PIN: never sent on
  4. microwave_broken    -> needs_person: true (door will not close, cracked)
  5. cooked_check        -> we never say food is cooked or hot enough
  6. money_check         -> we never read a balance or say if they can afford it
  7. buy_decision_check  -> we never say whether to buy
  8. health_check        -> no medical, allergy or diet advice
  9. food_choice_check   -> we never pick foods for people
  10. cook_time_question -> we never pick a cooking time (a photo of the package may be read)
  11. microwave_safe_question -> high risk, see high_risk.py (label quote, ask 3 times)

Checks that run AFTER the model answers:
  new_food_words, reply_breaks_rules -> the reply must not add a food, call anything
  safe or cooked, name money, or tell the person to buy

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
MONEY_REPLY = "I can't help with your money. Please ask your support person."
BUY_DECISION_REPLY = "I can't say what to buy. You choose, or ask your support person."
COOKED_REPLY = "I can't tell if it's cooked. Check it is steaming hot inside, or ask your support person."
COOK_TIME_REPLY = "I can't pick a time. Use the time printed on your package, or ask your support person."
SECRET_REPLY = "Never share your card number or PIN, even here. Please ask your support person."
SCAM_REPLY = "This may be a scam. Do not share your card or PIN. Please tell your support person now."
MICROWAVE_BROKEN_REPLY = "Please don't use the microwave. Tell your support person."
MICROWAVE_HANDOFF_REPLY = "I'm not sure. Please ask your support person, or use a plate you know is safe."
PHOTO_PERSON_REPLY = "Please take a photo of the thing you are stuck on."
PHOTO_PRIVATE_REPLY = "I can't use photos of cards, receipts, bank apps or checkout pages. Ask your support person."
PHOTO_UNCLEAR_REPLY = "I can't see it well. Please try a clearer photo."

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
    # microwave and kitchen
    r"\bsparks?\b",
    r"\bsparking\b",
    r"\barcing\b",
    r"\bexplod(e|ed|ing)\b",
    r"\bburning smell\b",
    r"\bsmells? (burnt|burned)\b",
    r"\b(melt(ed|ing)|warp(ed|ing)) (in|inside) the microwave\b",
    r"\b(dish|bowl|plate|cup|container|plastic|tray) (is |was |has |started )?(melt(ed|ing)|warp(ed|ing))\b",
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



# ---- New for the heat a meal and buying tasks (docs/safety.md, section 4) ----------
# Someone asks for a card, PIN or code, or the person tells us about it. Scam.
SCAM_PATTERNS = [
    r"\b(someone|somebody|a man|a woman|a person|caller|they|he|she)\b.{0,50}\b(called|texted|emailed|messaged|asked|wants?|said|told)\b.{0,70}\b(card|pin|password|passcode|code|gift card|money|account)\b",
    r"\bgift cards?\b.{0,30}\b(pay|send|buy|give)\b",
    r"\b(send|wire|give) (them |him |her )?money\b",
    r"\bverification code\b",
    r"\bwon (a |the )?(prize|lottery|gift)\b",
    r"\bscam(s|med)?\b",
    r"\bfraud\b",
]

# The message itself holds a secret (a card number, or a PIN after the word PIN).
# These are never sent to the model.
SECRET_PATTERNS = [
    r"(?:\d[ -]?){13,19}",                       # a card-like run of digits
    r"\bpin\b.{0,15}\d{4}",                       # "my pin is 1234"
    r"\b\d{4}\b.{0,15}\bis my pin\b",
    r"\bcard number\b",
    r"\b(cvv|cvc|security code)\b",
    r"\b(my|the) (pass ?code|password) (is|:)",
    r"\bexpir(y|ation) date\b",
]

# The door is broken, or will not close. Safety rule: do not use it, tell staff.
MICROWAVE_BROKEN_PATTERNS = [
    r"\bdoor\b.{0,20}\b(won'?t|doesn'?t|does not|will not|can'?t|cannot|not)\b.{0,12}\b(close|shut|latch|lock)\b",
    r"\bdoor\b.{0,15}\b(is |looks |seems )?(broken|cracked|loose|bent|damaged)\b",
    r"\bmicrowave\b.{0,20}\b(is |looks |seems )?(broken|cracked|damaged)\b",
]

# Is it cooked, done, hot enough? We never say. (Never answers: safety.md section 2.)
COOKED_PATTERNS = [
    r"\bcooked (enough|through|all the way|right|properly|well)\b",
    r"\b(is|are|was) (it|this|that|the food|my food) (cooked|done|ready|hot enough|hot|warm enough)\b",
    r"\b(fully|completely|all the way) (cooked|heated|hot)\b",
    r"\bready to eat\b",
    r"\bhot enough\b",
    r"\bdone yet\b",
    r"\bfinished cooking\b",
    r"\b(how|what) (hot|warm) (should|does|is)\b",
    r"\bwhat temperature\b",
    r"\bsafe to eat\b",
]

# "How long do I heat it?" We never pick a time. A photo of the package may be read
# (high_risk.py). Without a photo, the person is sent to the package.
COOK_TIME_PATTERNS = [
    r"\bhow (long|many (minutes?|mins?|seconds?|secs?))\b.{0,50}\b(heat|microwave|cook|warm|reheat|put|set|press|go|run)\b",
    r"\bhow (long|many (minutes?|mins?|seconds?|secs?))\b",
    r"\bwhat (time|power|level|setting)\b.{0,30}\b(set|use|put|press|choose|pick|heat|cook)\b",
    r"\bhow much time\b",
]

# "Can this go in the microwave?" High risk. Only the label rule may answer.
_DISH = (r"(this|these|foil|metal|foam|styrofoam|takeout|take-out|plastic|paper|cardboard|"
         r"tupperware|container|tray|bowl|plate|mug|cup|dish|glass|ceramic|box|bag|jar|lid|wrap)")
MICROWAVE_SAFE_PATTERNS = [
    r"\bmicrowave[- ]?(safe|able|proof)\b",
    r"\b(safe|ok|okay|fine|allowed)\b (to|for) (microwave|microwaving)\b",
    rf"\b(put|use|heat|cook|warm|reheat|microwave)\b.{{0,30}}\b{_DISH}\b.{{0,25}}\b(in|into|inside|for)\b.{{0,10}}\bmicrowave\b",
    rf"\b{_DISH}\b.{{0,30}}\b(in|into|inside)\b.{{0,8}}\bmicrowave\b",
    rf"\bin the microwave\b.{{0,30}}\b{_DISH}\b",
]
# "How do I put the dish in the microwave?" is step help, not a safety question.
_HOW_TO = r"\b(how|where)\b.{0,15}\b(do|can|to)\b"

# Money. We never read a balance and never say if something can be afforded.
MONEY_PATTERNS = [
    r"\bcan'?t afford\b",
    r"\bcannot afford\b",
    r"\bcan i afford\b",
    r"\b(do|did|will) i (really )?have enough( money)?\b",
    r"\bhave i got enough\b",
    r"\b(not enough|no) money\b",
    r"\bhow much (money|do i have|cash|is in my)\b",
    r"\b(what'?s|what is|tell me|read|show) (my|the) (balance|account)\b",
    r"\bmy balance\b",
    r"\bam i (broke|poor)\b",
    r"\b(is|are) (it|this|that|these) too (expensive|much|pricey)\b",
]

# Buying decisions. We never say yes or no. (Which is cheaper? is OK: the AI may
# compare two prices that are visible, but it never says which to buy.)
BUY_DECISION_PATTERNS = [
    r"\bshould i (buy|get|order|purchase|pay for)\b",
    r"\b(buy|get|order) (it|this|that) or not\b",
    r"\bwhat should i (buy|get|order|purchase)\b",
    r"\bwhich (one )?should i (buy|get|pick|choose|order)\b",
    r"\b(is|are) (it|this|that|these) (worth|a good (deal|price|buy|idea))\b",
    r"\bworth (it|buying|the money)\b",
    r"\bdo i need (it|this|that)\b",
    r"\btell me (to buy|what to buy)\b",
]

# After the model answers: replies we never accept.
REPLY_BREAK_PATTERNS = [
    r"\b(is|are|it'?s|looks|seems) (microwave[- ]?safe|safe to (use|microwave|eat)|ok(ay)? to (use|microwave|eat))\b",
    r"\bmicrowave[- ]?safe\b",
    r"\b(cooked|done|ready|hot) enough\b",
    r"\b(fully|completely) cooked\b",
    r"\bsafe to (eat|use|microwave)\b",
    r"\b(card number|cvv|security code|expiry|expiration date)\b",
    r"\b(your |the |account )?balance\b",
    r"\bafford\b",
    r"\$\s?\d",
    r"\b\d+\s?(dollars?|bucks)\b",
    r"\b(you should|you must|i('d| would)|go ahead and|please) (buy|purchase|get) (it|this|that)\b",
    r"\b(don'?t|do not) buy\b",
    r"\bworth (it|buying)\b",
    r"\bheat (it |this |the \w+ )?for \d",
    r"\bmicrowave (it |this )?for \d",
    r"\bset (the )?(time|timer) (to|for) \d",
    r"\bfor \d+\s?(minutes?|mins?|seconds?|secs?)\b",
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


def scam_check(text: str) -> bool:
    """True if someone is asking the person for a card, PIN, code or money."""
    return _matches(SCAM_PATTERNS, text)


def secret_check(text: str) -> bool:
    """True if the message holds a card number, a PIN or similar. Never sent on."""
    return _matches(SECRET_PATTERNS, text)


def microwave_broken_check(text: str) -> bool:
    """True if the microwave door or oven looks broken."""
    return _matches(MICROWAVE_BROKEN_PATTERNS, text)


def cooked_check(text: str) -> bool:
    """True if the person asks whether food is cooked, done or hot enough."""
    return _matches(COOKED_PATTERNS, text)


def cook_time_question(text: str) -> bool:
    """True if the person asks how long to heat something."""
    return _matches(COOK_TIME_PATTERNS, text)


def microwave_safe_question(text: str) -> bool:
    """True if the person asks whether a dish or container can go in the microwave."""
    lowered = (text or "").lower().replace("’", "'")
    if re.search(_HOW_TO, lowered) and not re.search(r"\bsafe\b|microwave[- ]?able", lowered):
        return False
    return _matches(MICROWAVE_SAFE_PATTERNS, text)


def money_check(text: str) -> bool:
    """True if the person asks about their balance or whether they can afford something."""
    return _matches(MONEY_PATTERNS, text)


def buy_decision_check(text: str) -> bool:
    """True if the person asks us to decide whether to buy."""
    return _matches(BUY_DECISION_PATTERNS, text)


def reply_breaks_rules(reply: str) -> str:
    """Return the matching phrase if a model reply breaks a guardrail, else "".

    Safe, cooked, money and buying claims are never allowed from the free text
    model. Times are also refused: a time may only come from high_risk.py, which
    reads the package label three times.
    """
    lowered = (reply or "").lower().replace("’", "'")
    for pattern in REPLY_BREAK_PATTERNS:
        found = re.search(pattern, lowered)
        if found:
            return found.group(0)
    return ""
