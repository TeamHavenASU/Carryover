# Role D: AI help ("I'm stuck", voice, photo, step splitting)

## What is in here

| File | What it does |
|------|--------------|
| `backend/ai/llm.py` | The only file that calls the model. Reads the key from `backend/.env`. 20 second timeout. Returns a safe fallback on any error. |
| `backend/ai/safety.py` | Safety checks in code: danger, health, food choice, and "no new foods" in replies. |
| `backend/ai/ask.py` | The "I'm stuck" flow for `POST /ask`. |
| `backend/ai/split.py` | AI step splitting for `POST /split`. Writes only to `data/splits_pending.json`. |
| `backend/ai/common.py` | Small helpers: load a task, read a prompt, clean up JSON. |
| `backend/api/ai_routes.py` | The two routes. |
| `backend/prompts/` | `ask_system.md`, `ask_user_template.md`, `split_system.md` |
| `backend/tests/` | `test_ai.py` (no model needed), `run_ai_cases.py`, `ai_cases.md` |
| `frontend/src/components/AskForHelp/` | The "I'm stuck" button, text box, microphone, photo and reply. |
| `docs/make_prompts_pdf.py`, `docs/prompts.pdf` | The prompts PDF. |

## Set up

1. Add the two lines to `backend/api/main.py` (E creates this file):

   ```python
   from api.ai_routes import router as ai_router
   app.include_router(ai_router)
   ```

2. Add these lines to `backend/requirements.txt`:

   ```
   httpx
   python-dotenv
   pytest
   reportlab
   ```

3. Add these lines to `backend/.env.example` (leave every value blank except the provider):

   ```
   LLM_PROVIDER=anthropic
   LLM_MODEL=
   LLM_API_KEY=
   LLM_BASE_URL=
   ```

   Then copy it to `backend/.env` and fill in your own values. `backend/.env` must stay in `.gitignore`.

4. Add `backend/tests/ai_images/` to `.gitignore` (test photos should not go in the repo).

## Choosing the provider and model

Nothing in the code depends on a provider. Change `backend/.env`:

- Claude API: `LLM_PROVIDER=anthropic`, `LLM_MODEL=<model name>`, `LLM_API_KEY=<key>`
- Any service with an OpenAI style `/chat/completions` API: `LLM_PROVIDER=openai`, `LLM_MODEL=<model name>`, `LLM_API_KEY=<key>`, and `LLM_BASE_URL=<the service's base URL>` if it is not OpenAI itself.

The model must be able to read images, or the photo feature will not work.

## Run

From the `backend/` folder:

```
pip install -r requirements.txt
uvicorn api.main:app --reload
pytest tests/test_ai.py          # no key needed
python tests/run_ai_cases.py     # writes tests/ai_cases.md (needs a key for the model cases)
```

From the repo root: `python docs/make_prompts_pdf.py` rebuilds `docs/prompts.pdf`.

## Using the component

C places it at the bottom of the resident screen:

```jsx
import AskForHelp from "../components/AskForHelp/AskForHelp";

<AskForHelp
  personId={personId}
  taskId={taskId}
  stepId={currentStepId}   // the step on screen, or null
  week={week}
  sessionId={sessionId}    // person-task-week, like jeremiah-sandwich-w03
  autoRead={settings.autoRead}
/>
```

It sends `stuck_pressed` when the button is pressed and `ask_sent` (step guess only) after a reply, both through C's `POST /event`. Set `VITE_API_URL` if the backend is not at `http://localhost:8000`. The component is styled with CSS variables (`--calm-surface`, `--calm-ink`, `--calm-accent`) so it matches C's look, and it respects the page's text size, a `no-motion` class on the page, and the device's reduce motion setting.

## Connections to other roles

- **A:** `/split` takes its two examples from A's task files. If fewer than two split steps exist, it uses built in examples.
- **B and A:** `/ask` tries to read this person's help codes with `logic.data_io.load_events` and `logic.detect.detect`. If those are missing or fail, the model simply gets no codes.
- **C:** C's `POST /event` writes `stuck_pressed` and `ask_sent`.
- **E:** `/split` saves entries in `data/splits_pending.json` as `{split_id, task_id, step_id, substeps, approved: false}`. D creates the `split_id`. E's routes read this file and write approved substeps into the task file.
