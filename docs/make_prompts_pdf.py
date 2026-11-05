"""Builds docs/prompts.pdf from the files in backend/prompts/ (Role D, D6).

Run from the repo root:   python docs/make_prompts_pdf.py
Needs:                    pip install reportlab

The prompts, the safety word lists and the example prompts are read from the real
files and code, so the PDF always matches what the app does. Run it again after
you change a prompt.
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from ai import common, high_risk, llm, safety, skill_card  # noqa: E402
from ai.ask import (  # noqa: E402
    EMPTY_REPLY,
    IMAGE_TOO_BIG_REPLY,
    MAX_IMAGE_CHARS,
    MAX_REPLY_WORDS,
    MAX_TEXT_CHARS,
    build_user_prompt as build_ask_prompt,
)
from ai.split import (  # noqa: E402
    MAX_SUBSTEPS,
    MAX_WORDS,
    MIN_SUBSTEPS,
    build_user_prompt as build_split_prompt,
    pick_examples,
)

# The prompts PDF uses A's real task files (Heat a meal and the Buy versions).

OUT = ROOT / "docs" / "prompts.pdf"

# ------------------------------------------------------------------ styles
base = getSampleStyleSheet()
INK = colors.HexColor("#1f2d2b")
ACCENT = colors.HexColor("#2f6f6a")
SOFT = colors.HexColor("#eef4f3")

H1 = ParagraphStyle("H1", parent=base["Title"], fontName="Helvetica-Bold", fontSize=22, textColor=INK, alignment=TA_LEFT, spaceAfter=4)
H2 = ParagraphStyle("H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=14, textColor=ACCENT, spaceBefore=14, spaceAfter=6)
H3 = ParagraphStyle("H3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=11, textColor=INK, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=10, leading=14, textColor=INK, spaceAfter=5)
SMALL = ParagraphStyle("Small", parent=BODY, fontSize=9, leading=12)
MONO = ParagraphStyle("Mono", parent=BODY, fontName="Courier", fontSize=8.3, leading=10.6, spaceAfter=0, leftIndent=0)
MONO_H = ParagraphStyle("MonoH", parent=MONO, fontName="Courier-Bold", spaceBefore=5)
CELL = ParagraphStyle("Cell", parent=BODY, fontSize=9, leading=12, spaceAfter=0)
CELL_B = ParagraphStyle("CellB", parent=CELL, fontName="Helvetica-Bold")


def p(text, style=BODY):
    return Paragraph(text, style)


def bullets(items, style=BODY):
    return [Paragraph("&bull;&nbsp;&nbsp;" + escape(i), ParagraphStyle("b", parent=style, leftIndent=14, firstLineIndent=-10, spaceAfter=2)) for i in items]


def code_box(text):
    """Show prompt text in a shaded box. One Paragraph per line, so long lines wrap."""
    rows = []
    for line in text.strip("\n").split("\n"):
        if not line.strip():
            rows.append([Spacer(1, 4)])
            continue
        style = MONO_H if line.startswith("## ") else MONO
        indent = len(line) - len(line.lstrip(" "))
        text_line = escape(line.strip())
        rows.append([Paragraph(text_line, ParagraphStyle("m", parent=style, leftIndent=indent * 4.5))])
    table = Table(rows, colWidths=[6.9 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SOFT),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#b7cfca")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    table.splitByRow = 1
    return table


def grid(rows, widths, header=True):
    data = [[Paragraph(escape(str(c)), CELL_B if (header and r == 0) else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[w * inch for w in widths], repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b7cfca")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), SOFT))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5b6f6c"))
    canvas.drawString(0.8 * inch, 0.5 * inch, "Carryover  |  AI prompts and safety rules")
    canvas.drawRightString(letter[0] - 0.8 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def main():
    story = []

    # ---------------------------------------------------------------- 1. overview
    story += [
        p("Carryover: AI prompts and safety rules", H1),
        p("Everything the language model is told, and every check around it. The prompts, word lists and examples in this PDF are read from the real files in the repo.", BODY),
        p("Where the AI is used", H2),
        p("Carryover uses a language model in four places. Everything else in the app (finding where someone is stuck, choosing help, fading help) is plain code and fixed rules. Whenever the AI writes something that a resident could later see (split steps, skill cards), a person must approve it first.", BODY),
        grid(
            [
                ["Feature", "What the model does", "Route and file"],
                ["I'm stuck", "Reads what the person typed or said (or a photo of the thing they are stuck on) and replies with ONE small step, under 20 words.", "POST /ask   backend/ai/ask.py"],
                ["Step splitting", "Breaks one hard step into 3 to 6 smaller steps. With the hand setting on, it writes an extra detail version (which hand, which direction). A person must approve every version before any resident sees it.", "POST /split   backend/ai/split.py"],
                ["Label reading", "For two high risk photo questions only (can this go in the microwave, how long do I heat it), reads the words printed on the dish or package. The code makes the decision, not the model.", "backend/ai/high_risk.py"],
                ["Skill cards", "Drafts a skill card for a base skill a step assumes, or names the skill a person may be missing. A person must approve every card.", "POST /draft_skill   backend/ai/skill_card.py"],
            ],
            [1.2, 3.9, 1.8],
        ),
        Spacer(1, 6),
        p("All model calls go through one file, backend/ai/llm.py. It reads the key from backend/.env (never from code), times out after "
          f"{llm.TIMEOUT_SECONDS} seconds, and on any error returns a safe fallback. Changing provider or model only means changing .env.", BODY),
    ]

    # ---------------------------------------------------------------- 2. safety rules
    story += [p("The AI safety rules", H2), p("These thirteen rules are inside the ask system prompt. The split, label and skill card prompts carry the ones that apply to them. The most important ones are also enforced in code, shown in section 5, because a prompt can fail.", BODY)]
    rules = [
        "Reply with one small step, in plain words, under 20 words.",
        "Never suggest foods or ingredients. Never give medical, allergy or diet advice.",
        'If the person mentions being hurt, danger, fire, sparks, feeling unsafe or very upset: set needs_person: true and reply "Please get your support person or someone you trust now."',
        'No guilt, no streaks, no "you failed". Calm and kind.',
        "Never guess the person's feelings or diagnosis.",
        "If unsure, say so and suggest asking a person.",
        "Always reply in the exact JSON format asked for.",
        "Never say how long to heat or cook something. Never pick a time, power level or temperature. Never say food is cooked, done, hot enough or safe to eat.",
        "Never say a dish, container or food is safe for the microwave. Hand off to the support person.",
        "Never read, guess or talk about the person's money, balance or bank. Never say if they can afford something. \"Can't afford it\" goes to the support person.",
        "Never say whether to buy something, which one to pick, or that it is a good deal.",
        "Never ask for, repeat or store a card number, PIN, password, passcode or security code.",
        "If someone is asking the person for a card number, PIN, code or money, say it may be a scam and set needs_person: true.",
    ]
    story.append(grid([["#", "Rule"]] + [[str(i), r] for i, r in enumerate(rules, 1)], [0.4, 6.5]))

    # ---------------------------------------------------------------- 3. ask prompts
    ask_system = common.read_prompt("ask_system.md")
    ask_template = common.read_prompt("ask_user_template.md")
    story += [
        p('3. "I\'m stuck" system prompt', H2),
        p("File: backend/prompts/ask_system.md. Sent as the system prompt on every /ask call.", SMALL),
        code_box(ask_system),
        p('"I\'m stuck" user template', H2),
        p("File: backend/prompts/ask_user_template.md. The {{...}} markers are filled in each time. The person's name is never included, only help codes. What they typed sits inside <person_message> tags, and any tag they type themselves is removed so they cannot close it early.", SMALL),
        code_box(ask_template),
    ]

    task = common.load_task("heat_meal")
    filled = build_ask_prompt(task, "s4", ["cant_start", "stuck_at_step:s4"], "I can't find the Start button", False)
    story += [
        p("One filled in example", H3),
        p("A resident on the Heat a meal task, on step 4, with two help codes, typing: I can't find the Start button.", SMALL),
        code_box(filled),
        p("Expected reply", H3),
        code_box('{"reply": "Look for the button that says Start. Press it once.", "step_id_guess": "s4", "needs_person": false, "photo_issue": "none"}'),
    ]

    # ---------------------------------------------------------------- 4. formats
    story += [
        p("4. JSON output formats", H2),
        p("/ask reply (also the format the model must return):", BODY),
        code_box('{"reply": "<one small step, under 20 words>", "step_id_guess": "<step id like s3, or null>", "needs_person": false, "photo_issue": "none"}'),
        p('photo_issue is "none", "person", "private" (a bank app, card, receipt or checkout page) or "unclear". For any value except "none" the app ignores the model\'s sentence and shows fixed words.', SMALL),
        p("The safe fallback, used when the model fails or answers badly twice:", BODY),
        code_box(llm.FALLBACK_TEXT),
        p("/split reply (the model returns only substeps; the route adds approved):", BODY),
        code_box('{"substeps": ["<step 1>", "<step 2>", "<step 3>"], "approved": false}'),
        p("Entry saved for a person to review in data/splits_pending.json:", BODY),
        code_box('{"split_id": "heat_meal-s2-3fa9c1", "task_id": "heat_meal", "step_id": "s2",\n "substeps": ["..."], "approved": false,\n "variant": "extra_detail", "hand": "left"}   (variant and hand only for extra detail)'),
        p("Skill card saved for a person to review in data/skill_cards_pending.json (same format as data/skills/*.json, plus approved: false):", BODY),
        code_box('{"skill_id": "find_the_start_button", "title": "Find the Start button", "why": "...",\n "steps": [{"id": "find_the_start_button_1", "text": "..."}], "tips": [],\n "used_by": ["heat_meal:s4"], "picture": null, "video": null, "approved": false}'),
    ]

    # ---------------------------------------------------------------- 5. code checks
    story += [
        p("5. Safety checks in code", H2),
        p("The prompt asks the model to be safe, but a prompt can fail. So the most important rules are also checked in code. The checks in the table run BEFORE the model, and for those the model is never called.", BODY),
        grid(
            [
                ["Check", "What it catches", "What the person gets"],
                ["1. Danger", 'Someone hurt, in danger or very upset. Examples: "I cut my finger", "there\'s smoke", "sparks in the microwave", "the dish melted", "I\'m very upset".', f'needs_person: true and "{safety.SAFETY_REPLY}"'],
                ["2. Scam", 'Someone is asking them for a card number, PIN, code, gift cards or money.', f'needs_person: true and "{safety.SCAM_REPLY}"'],
                ["3. Card number or PIN typed", 'The message holds a card number, a PIN, a CVV or a password. The text is dropped and never sent to the model.', f'"{safety.SECRET_REPLY}"'],
                ["4. Broken microwave", 'The door will not close, or looks cracked or broken.', f'needs_person: true and "{safety.MICROWAVE_BROKEN_REPLY}"'],
                ["5. Cooked or hot enough?", '"is it cooked enough?", "is this hot enough", "ready to eat".', f'"{safety.COOKED_REPLY}"'],
                ["6. Money", '"I can\'t afford this", "what\'s my balance", "do I have enough money?".', f'"{safety.MONEY_REPLY}"'],
                ["7. Buy or not", '"should I buy it?", "is this a good deal?".', f'"{safety.BUY_DECISION_REPLY}"'],
                ["8. How long to heat (no photo)", '"how long do I heat it". Only in a task that uses a microwave.', f'"{safety.COOK_TIME_REPLY}"'],
                ["9. Microwave safe? (no photo)", '"can I put this plate in the microwave?", "is foil ok".', f'"{safety.MICROWAVE_HANDOFF_REPLY}"'],
                ["10. Health", 'Allergy, medicine, diet and similar.', f'"{safety.HEALTH_REPLY}"'],
                ["11. Food choice", 'Asking us to pick a food. Examples: "what should I eat for dinner?", "give me a recipe".', f'"{safety.FOOD_CHOICE_REPLY}"'],
                ["12. Empty message", "No text and no photo.", f'"{EMPTY_REPLY}"'],
                ["13. Photo too big", "A photo over about 2 MB (the screen shrinks photos first, so this is a backstop).", f'"{IMAGE_TOO_BIG_REPLY}"'],
            ],
            [1.4, 3.3, 2.2],
        ),
        Spacer(1, 6),
        p('Why phrases and not single words. The word list in the plan includes "cut", "burn" and "fire". But "How do I cut the bread?" and "I burnt the toast" are normal kitchen questions, and treating them as emergencies would make the app useless. So the checks match phrases about a person being hurt, and tests (backend/tests/test_ai.py and test_ai_guardrails.py) make sure ordinary microwave and buying questions are not treated as emergencies. "How do I put the dish in the microwave?" is step help, so it goes to the model, while "can I put this plate in the microwave?" is a safety question and never does.', BODY),
        p("After the model answers, the reply is checked in code:", H3),
    ]
    story += bullets(
        [
            "It must be valid JSON in the exact format. Code fences around the JSON are removed.",
            f"The reply must be under 20 words (at most {MAX_REPLY_WORDS}).",
            "The reply must not name a food that is not already in the task steps.",
            "The reply must not say anything is microwave safe or cooked, give a cooking time, name money or a balance, or say whether to buy. If it does, the reply is retried once and then replaced by the fallback.",
            "If the model sets photo_issue to person, private or unclear, its sentence is thrown away and fixed words are shown, with no step guess.",
            "step_id_guess must be a real step in the task. A smaller step like s3a is mapped to its main step s3. Anything else becomes null.",
            "If the model says needs_person is true, the reply is replaced with the fixed safety words, so the wording is always the same.",
            f"What the person typed is cut to {MAX_TEXT_CHARS} characters before it is sent.",
        ],
        BODY,
    )
    story += [
        p("Retry and fallback flow", H3),
        code_box(
            "person sends text and/or photo\n"
            "  -> trim, cut to 500 characters\n"
            "  -> nothing sent?              reply: ask what is hard (no model call)\n"
            "  -> danger, scam, broken door? needs_person: true (no model call)\n"
            "  -> card number or PIN typed?  fixed reply, text dropped (no model call)\n"
            "  -> cooked? money? buy it?     fixed reply (no model call)\n"
            "  -> health or allergy?         reply: ask a person (no model call)\n"
            "  -> asks us to pick a food?    reply: they choose (no model call)\n"
            "  -> can it go in the microwave? / how long to heat?\n"
            "       with a photo:            label rule, 3 asks (section 8)\n"
            "       no photo:                fixed reply (no model call)\n"
            "  -> build prompt, call model (20 second timeout)\n"
            "       model call failed?       safe fallback (no retry, no extra waiting)\n"
            "       answer checked in code\n"
            "         good                   return it\n"
            "         bad                    retry ONCE, naming the problem\n"
            "           good                 return it\n"
            "           bad                  safe fallback"
        ),
    ]
    story.append(p("The exact patterns", H3))
    story.append(p("Danger patterns (regular expressions, matched against lower case text):", SMALL))
    story.append(code_box("\n".join(safety.DANGER_PATTERNS)))
    story.append(p("Health patterns:", SMALL))
    story.append(code_box("\n".join(safety.HEALTH_PATTERNS)))
    story.append(p("Food choice patterns:", SMALL))
    story.append(code_box("\n".join(safety.FOOD_CHOICE_PATTERNS)))
    for title, pats in [
        ("Scam patterns:", safety.SCAM_PATTERNS),
        ("Card number or PIN patterns:", safety.SECRET_PATTERNS),
        ("Broken microwave patterns:", safety.MICROWAVE_BROKEN_PATTERNS),
        ("Cooked or hot enough patterns:", safety.COOKED_PATTERNS),
        ("Money patterns:", safety.MONEY_PATTERNS),
        ("Buy decision patterns:", safety.BUY_DECISION_PATTERNS),
        ("Cooking time question patterns:", safety.COOK_TIME_PATTERNS),
        ("Microwave safe question patterns:", safety.MICROWAVE_SAFE_PATTERNS),
        ("Replies we never accept from the model:", safety.REPLY_BREAK_PATTERNS),
    ]:
        story.append(p(title, SMALL))
        story.append(code_box("\n".join(pats)))

    # ---------------------------------------------------------------- 6. privacy and photos
    story += [p("6. Privacy and photos", H2)]
    story += bullets(
        [
            "What a person types and any photo are never saved to disk or written to logs. The app only logs an ask_sent event that holds the step guess.",
            "Photos are shrunk to 800 pixels on the device, sent once, and dropped from memory when the answer is returned.",
            'The screen says: "Take a photo of the thing you\'re stuck on, not yourself." It also says the photo goes to an AI service, and not to photograph people, cards, receipts, checkout pages or bank apps. If a photo shows one anyway, the model flags it (photo_issue) and the app shows fixed words instead of describing it.',
            "Nothing is read from a card, a receipt, a bank app or a checkout page. A photo question counts as used help. It never counts against the person.",
            "The person's name is never sent to the model. It only sees help codes like stuck_at_step:s3.",
            "The model is told to ignore any instruction inside the person's message that asks it to change these rules.",
            "The API key lives in backend/.env, which is in .gitignore. backend/.env.example holds a blank key only.",
        ],
        BODY,
    )

    # ---------------------------------------------------------------- 7. split
    split_system = common.read_prompt("split_system.md")
    t2 = common.load_task("heat_meal")
    s2 = next(s for s in t2["steps"] if s["step_id"] == "s2")
    split_prompt = build_split_prompt(t2, s2, pick_examples("heat_meal", "s2", s2["text"]))
    story += [
        p("7. Step splitting prompt", H2),
        p("File: backend/prompts/split_system.md. This answers a worry from First Place staff: AI might miss the hidden steps inside a step. So the model is shown two steps that a person already split, and every answer must be approved by a person.", BODY),
        code_box(split_system),
        p("The user message and its two examples", H3),
        p("The two examples are real split steps taken from the task files, never the step being split. If fewer than two exist, built in examples are used. Below is a filled in example for the Heat a meal step Get it ready for the microwave.", SMALL),
        code_box(split_prompt),
        p("Checks on the answer, in code", H3),
    ]
    story += bullets(
        [
            f"Valid JSON with a substeps list of {MIN_SUBSTEPS} to {MAX_SUBSTEPS} items.",
            f"Each item is {MAX_WORDS} words or fewer (the plan says under 8).",
            'One action each: items with "and", "then" or commas are rejected.',
            "No two items the same.",
            "No food that is not already in the task steps.",
            "No cooking time, money amount, \"safe\" or \"cooked\" claim, or buying advice, unless the task's own steps already use that phrase.",
            "If the answer fails a check, retry once. If it fails again, nothing is saved and an empty list is returned.",
        ],
        BODY,
    )
    story += [
        p("Human approval", H3),
        p("New splits are saved to data/splits_pending.json with approved: false. A person edits and approves them on the Review page (/review). Only then are they written into the task file. The resident app only ever shows substeps that are in the task file, so nothing from the AI reaches a resident without a person approving it. Extra detail versions are marked variant: extra_detail with the hand they were written for, and also wait for a person.", BODY),
    ]

    label_system = common.read_prompt("photo_check_system.md")
    extra_prompt = common.read_prompt("split_extra_detail.md")
    skill_system = common.read_prompt("skill_card_system.md")
    story += [
        p("8. The label rule for high risk photo questions", H2),
        p("Two questions are too risky for the model to answer on its own judgment: \"Can this dish go in the microwave?\" and \"How long do I heat this?\". An AI is often overconfident when it says how sure it is, and vision AI can see things that are not there. So for these two questions, when a photo is sent, the CODE decides (docs/safety.md, section 3):", BODY),
    ]
    story += bullets(
        [
            "Quote the label. The model only copies the words printed on the dish or package. The code checks them. No label words, no \"safe\" answer.",
            f"Ask {high_risk.ASKS} times. The same photo is sent {high_risk.ASKS} separate times, and we answer only if all {high_risk.ASKS} agree. One different answer or one failed call means a hand off.",
            "Never \"safe\" from looks. The model may report clear metal, foil or foam, or a label that says not to, and the app then says do not use it. It can never say safe because a dish looks fine.",
            "A limited label (\"microwave safe lid only\") is not safe. It is a hand off.",
            "Otherwise hand off: \"" + safety.MICROWAVE_HANDOFF_REPLY + "\"",
            "The words shown to the person are built by the code from fixed text. The model's own sentence is never shown, so writing on a dish cannot make the app say something else.",
            "For the cooking time, the model may only copy a time printed on the package. The time must appear in the quote, all 3 reads must give the same time, and a package with more than one time hands off. The model never works out a time.",
        ],
        BODY,
    )
    story += [
        p("Label reading prompt", H3),
        p("File: backend/prompts/photo_check_system.md.", SMALL),
        code_box(label_system),
        p("Accepted label phrases and the replies", H3),
        code_box(
            "Safe phrases: " + ", ".join(high_risk.SAFE_PHRASES) + "\n"
            "Words that mean the label says NO: " + ", ".join(sorted(high_risk.HARD_NEGATIONS)) + "\n"
            "Words that limit a label (hand off): " + ", ".join(sorted(high_risk.SOFT_NEGATIONS)) + "\n"
            "All 3 safe  -> The label says \"<phrase>\". You can use this dish.\n"
            "All 3 no    -> " + high_risk.UNSAFE_REPLY + "\n"
            "Anything else -> " + safety.MICROWAVE_HANDOFF_REPLY
        ),
        p("The 27 photo test", H3),
        p("python backend/tests/run_photo_test.py runs 27 photos, 15 of our own and 12 free web photos with credits (labeled dishes, unlabeled dishes, foil, foam, takeout boxes, blurry photos, no people) through the label rule. It counts how often the AI answered and how often an answer was wrong. The target is zero wrong \"safe\" answers. If there is one, that question type always hands off. Honest limit: 0 errors in 27 photos only shows the error rate is probably under about 11%, which is why the label quote check matters more than the test score.", BODY),

        p("9. Extra detail split", H2),
        p("When the resident's hand setting is on, POST /split with hand: left, right or either adds this to the split prompt. The version waits for a person, like every split. Each small step may be up to 11 words.", BODY),
        code_box(extra_prompt),

        p("10. Skill card drafting", H2),
        p("POST /draft_skill writes a card for a base skill that a step assumes. With no skill name it names the skill a person may be missing (for example when someone stays stuck at Most help). A card that already exists is never copied. Cards wait in data/skill_cards_pending.json and are written to data/skills/ only when a person approves them (POST /skills/<id>/approve).", BODY),
        code_box(skill_system),
        p("Checks on the card, in code: 2 to " + str(skill_card.MAX_STEPS) + " steps, each " + str(skill_card.MAX_WORDS) + " words or fewer, no new food, no times, money, safe or cooked words, no buying advice, no brand names.", BODY),
    ]

    doc = SimpleDocTemplate(
        str(OUT), pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
        topMargin=0.7 * inch, bottomMargin=0.8 * inch, title="Carryover: AI prompts and safety rules",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
