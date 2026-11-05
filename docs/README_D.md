# Role D: AI help ("I'm stuck", voice, photo, step splitting, skill cards)

## What is in here

| File | What it does |
|------|--------------|
| `backend/ai/llm.py` | The only file that calls the model. Reads the key from `backend/.env`. 20 second timeout. Returns a safe fallback on any error. |
| `backend/ai/safety.py` | Safety checks in code: danger, scam, card number or PIN, broken microwave, cooked enough, money, buying, health, food choice, and checks on the model's reply. |
| `backend/ai/ask.py` | The "I'm stuck" flow for `POST /ask`. |
| `backend/ai/high_risk.py` | The label rule for two photo questions: "can this go in the microwave" and "how long do I heat this". Quote the label, ask 3 times, never "safe" from looks. |
| `backend/ai/split.py` | AI step splitting for `POST /split`, with an extra detail version (hand and direction). Writes only to `data/splits_pending.json`. |
| `backend/ai/skill_card.py` | AI drafts a skill card, or names the missing base skill. Writes only to `data/skill_cards_pending.json` until a person approves. |
| `backend/ai/common.py` | Small helpers: load a task, read a prompt, clean up JSON. |
| `backend/api/ai_routes.py` | `/ask`, `/split`, `/draft_skill`, `/skills/pending`, `/skills/<id>/approve`, `/skills/<id>/reject`. |
| `backend/prompts/` | `ask_system.md`, `ask_user_template.md`, `photo_check_system.md`, `split_system.md`, `split_extra_detail.md`, `skill_card_system.md` |
| `backend/tests/` | `test_ai.py` and `test_ai_guardrails.py` (no model or key needed), `run_ai_cases.py`, `run_photo_test.py`, `ai_cases.md` |
| `frontend/src/components/AskForHelp/` | The "I'm stuck" button, text box, microphone, photo and reply. |
| `docs/make_prompts_pdf.py`, `docs/prompts.pdf` | The prompts PDF. |

## The rules, in one place (docs/safety.md, section 4)

The AI never reads a balance, never says whether to buy, never asks for or stores a card number or PIN, never picks a cooking time, never says food is cooked enough, and never says a dish is microwave safe from how it looks. "Can't afford it" goes to the support person. These are checked in code before and after the model, not only in the prompt.

- Before the model (the model is never called): danger, scam, card number or PIN typed, broken microwave door, cooked enough, money, buy or not, health, food choice, empty message.
- After the model: the reply must be under 20 words, name no new food, never say safe, cooked, a time, money or buy, and a photo that shows a person, a card, a receipt, a bank app or a checkout page gets fixed words and no step guess.
- Photos: the label rule in `high_risk.py`. The words shown come from code, never from the model.

## Set up

Everything is already wired in `backend/api/main.py`, `requirements.txt` and `.gitignore`. Only the key is yours to add:

1. Copy `backend/.env.example` to `backend/.env`.
2. Fill in `LLM_PROVIDER`, `LLM_MODEL` and `LLM_API_KEY`. Leave `LLM_BASE_URL` blank for Anthropic. `backend/.env` is in `.gitignore`.
3. The model must be able to read images, or the photo feature will not work.

## Choosing the provider and model

Nothing in the code depends on a provider. Change `backend/.env`:

- Claude API: `LLM_PROVIDER=anthropic`, `LLM_MODEL=<model name>`, `LLM_API_KEY=<key>`
- Any service with an OpenAI style `/chat/completions` API: `LLM_PROVIDER=openai`, `LLM_MODEL=<model name>`, `LLM_API_KEY=<key>`, and `LLM_BASE_URL=<the service's base URL>` if it is not OpenAI itself.

Some models think before they answer, and that uses up output tokens. `MAX_OUTPUT_TOKENS` in `llm.py` is 2000 so there is always room for the short reply.

## Run

From the `backend/` folder:

```
pip install -r requirements.txt
uvicorn api.main:app --reload
pytest tests                         # no key needed
python tests/run_ai_cases.py         # writes tests/ai_cases.md (needs a key for the model cases)
python tests/run_photo_test.py       # the 27 photo safety test (needs a key and your photos)
```

From the repo root: `python docs/make_prompts_pdf.py` rebuilds `docs/prompts.pdf`.

## The 27 photo test

1. The test set is already in `backend/tests/ai_images/photo_test/`: 27 photos, 15 of our own and 12 free web photos with credits in ATTRIBUTION.md. To add more, take photos of your own dishes (no people) and add a row for each to manifest.csv.
2. New photos go in `backend/tests/ai_images/photo_test/`. Git ignores this folder, so add new files with `git add -f`.
3. `manifest.csv` in that folder lists each photo with what is really true (`safe`, `unsafe` or `unknown`). A photo whose printed label clearly says microwave safe is `safe`. The example file is `backend/tests/photo_test_manifest_example.csv`.
4. Run `python tests/run_photo_test.py`. It writes `tests/photo_test_results.md` with how often the AI answered, how many answers were wrong, and the number that matters: wrong SAFE answers. The target is zero.

## Using the component

C places it at the bottom of the resident screen:

```jsx
import AskForHelp from "../components/AskForHelp/AskForHelp";

<AskForHelp
  personId={personId}
  taskId={taskId}          // heat_meal, buy_instore_card, ...
  stepId={currentStepId}   // the step on screen, or null
  week={week}
  sessionId={sessionId}    // person-task-week, like jeremiah-heat_meal-w03
  autoRead={settings.autoRead}
/>
```

It sends `stuck_pressed` when the button is pressed and `ask_sent` (step guess only) after a reply, both through `POST /event`, as 12 column rows that match `EVENT_COLUMNS` in `backend/logic/data_io.py`. Set `VITE_API_URL` if the backend is not at `http://localhost:8000`. The panel tells the person that a photo goes to an AI service and asks for no people, cards, receipts, checkout pages or bank apps. It is styled with CSS variables (`--calm-surface`, `--calm-ink`, `--calm-accent`) so it matches C's look, and it respects the page's text size, a `no-motion` class on the page, and the device's reduce motion setting.

## Connections to other roles

- **A:** `/split` takes its two examples from A's task files. If fewer than two split steps exist, it uses built in examples. Skill cards follow the format of `backend/data/skills/*.json`.
- **B and A:** `/ask` reads this person's help codes with `logic.data_io.load_events` and `logic.detect.detect`. If those fail, the model simply gets no codes.
- **C:** C's `POST /event` writes `stuck_pressed` and `ask_sent`. C passes the hand setting to `/split` (see below).
- **E:** `/split` saves entries in `data/splits_pending.json` as `{split_id, task_id, step_id, substeps, approved: false}`. D creates the `split_id`. E's review routes read this file and write approved substeps into the task file.

### Extra detail (hand setting) and E's review page

`POST /split` with `{"task_id", "step_id", "hand": "left" | "right" | "either"}` makes an extra detail version. The pending entry also holds `"variant": "extra_detail"` and `"hand"`. A person must approve it like any split.

Open question for the team: E's approve route writes the substeps into the shared task file, which would replace the standard substeps for everyone. Extra detail versions should be stored per person or per hand setting instead. Until that is decided, only approve an extra detail version if you want it to replace the standard one.

### Skill cards

`POST /draft_skill` with `{"task_id", "step_id", "skill_title"}` drafts a card. Leave out `skill_title` and the AI names the base skill a person may be missing (use this when someone stays stuck at Most help). Cards wait in `data/skill_cards_pending.json`. A person reads one, then calls `POST /skills/<skill_id>/approve` (writes `data/skills/<skill_id>.json`) or `/reject`. `GET /skills/pending` lists what is waiting. E's review page does not show these yet.
