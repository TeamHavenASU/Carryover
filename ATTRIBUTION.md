# Attribution

## Hima 

**Libraries:** none beyond the Python standard library (statistics, datetime,
json, pathlib). Tests use pytest, which is already in requirements.txt.

**Prior work this builds on:**
- Task steps: our own task analyses. The method follows published task
  analyses for microwave use (Jones & Collins, 1997) and buying in a store
  (Rowe, 2011). The Decide part of buying draws on the CAN-B strategy
  (Adams et al., 2026). Wording is our own. No AFLS text was copied.
- Safety content: the microwave "never" list and the 2-hour food rule come
  from USDA and FDA guidance (plastic bags: Clemson HGIC, based on USDA).
  Placing safety facts inside the steps follows Jones & Collins (1997).
- Phone pay steps: the Apple Support and Google Wallet help pages listed in
  docs/sources.md.
- Detection codes: the codes and their thresholds are the team's own
  choices. Research supports the idea behind each: skills can fade after a
  break (Richling et al., 2019; Fuller & Fienup, 2018); executive function
  differences affect remembering and starting steps (Hill, 2004a;
  Demetriou et al., 2018). The research does not give our exact numbers.
- Partner input: base skills, the always-shown caution line, pictures, the
  different-microwave question and Game mode came from our Nov 3 and Nov 4
  meetings with First Place AZ staff (docs/partner_research.md).
- UI rules: W3C COGA guidance and the papers listed in docs/ui_guidelines.md.
- Full citations for everything above are in docs/sources.md.

**Pictures:** the first placeholder pictures were made by tools/make_pictures.py, a script written with AI help (since removed). The step pictures are now Role C's (tools/make_detailed_pictures.py, see the Role C section); no outside images or photos.

**AI assistance:** I used Claude (Anthropic) to help research sources, draft
the task step wording, skill cards and docs, and write detect.py,
test_detect.py and make_pictures.py (the first placeholder pictures, since removed). I decided the rules, the step content
and the detection logic, reviewed every line, and can explain what each
file does and why.

How I used AI, with the main requests (lightly edited for typos):
- Research and sources: "Check the citations in the lit review and sources.md against these abstracts I pasted. Tell me if any claim doesn't match the paper." "Write a literature review following the Purdue OWL guide, in plain English but research-based."
- Docs: "Draft future_directions.md and responsible_ai.md, and explain how the design accounts for privacy, safety and autonomy." "Review the Business Model Canvas: fix claims that don't match what First Place staff said."
- Checks: "Write a Claude Code prompt to audit every button in the resident app against our UI guidelines. Report only." "Go through the repo and find where the docs don't match what the app does."
- Code, with Claude Code: the help offer timing change in definitions.json; the Demo page phone frame, "Why this changed" and "Help over time" grid (Demo.jsx, Demo.css); the "Ask AI for more detail on this step" button and demo note on the Staff page (Staff.jsx, Staff.css); the plain-address redirect in App.jsx; the resident feedback section (with Role C's agreement). I checked every diff, ran the backend tests and the frontend build, and checked the pages in the browser.

## Mrudula

**Libraries:** none beyond the Python standard library (csv, json, pathlib,
random, statistics). No third-party dependencies were added for the
simulator, data_io, learn or the fading rules.

**Prior work this builds on:** Rules 1, 2, 4 and 6 implement procedures
described in MacDuff, Krantz & McClannahan (2001), "Prompts and Prompt-Fading
Strategies for People with Autism", in Maurice, Green & Foxx (eds), Making a
Difference: Behavioral Intervention for Autism. Rule 3 and the other numbers
are the team's own choices; the "3 times" counts and the rusty check are
supported by Richling, Williams & Carr (2019) and Fuller & Fienup (2018).
Full citations are in docs/sources.md. No code was taken from any existing
product.

**fade.py** was written by Vaishnavi Bhairishetty. My contributions are Rules
2 and 3, the missing_step response, and the accompanying tests.

**AI assistance:** data_io.py, simulate.py, learn.py, my additions to
fade.py, and their tests were written with the help of an AI coding
assistant. I specified the behaviour and the data formats, reviewed every
line, and can explain the logic and the design decisions in each file.

## Krutika

**Libraries:** the resident screens use React and the existing frontend setup
(Vite, React Router) from Role E's package.json. Added by Role C:
- framer-motion (MIT): the logo screen when the app opens, and in Game mode an
  island sliding in and the reward appearing.
- lottie-react (MIT, uses lottie-web, MIT): the Game mode animations.
- lucide-react (ISC): the one icon set used on every resident screen.
Browser features: localStorage for settings, sessionStorage for the logo
screen, speechSynthesis for read-aloud and Web Audio for Game mode sounds (made
in code, no sound files).
Backend: Python standard library, plus FastAPI and pytest, which were already
in the project.

**Pictures and animations:** the step pictures in frontend/public/img/ and
the skill card picture were redrawn in more detail by
tools/make_detailed_pictures.py, a script written with AI help (Claude).
Plain shapes only: no brands, no people (hands only), no card numbers. The
16 Lottie animations in frontend/public/animations/, the 21 game drawings in
frontend/public/game/ and the Carryover logo (an inline SVG in
SplashScreen.jsx) are our own, made with tools/make_game_art.py and
other AI-assisted code. No LottieFiles or Kenney downloads, so no outside licence
applies.

**Prior work this builds on:** the screens follow docs/ui_guidelines.md (the
UI Guide) and the sources listed there. The colour choices follow the AASPIRE
web accessibility guidelines (Raymaker et al., 2019), which recommend a
low-contrast neutral palette and both light and dark options. The exact
colour values are our own choice, checked against WCAG 2.2 AA contrast. The
help-level logic is not mine: it comes from fade.py and detect.py. Step and
safety text comes from the task files. No code was taken from any existing
product.

**Other people's code:** AskForHelp (Role D) is used as it was written. The
resident page is mounted in Role E's pages/Resident.jsx and uses Role E's
src/api.js. today.py wraps fade.build_view (Vaishnavi and Mrudula). My parts
are today.py, event_log.py, resident_routes.py, test_resident.py,
frontend/src/screens/ and frontend/src/lib/ (except the voice helper files,
see the Role D section).

**AI assistance:** Claude (Anthropic) helped write the resident screens in
frontend/src/screens/ and frontend/src/lib/, today.py, and the drawing scripts
tools/make_detailed_pictures.py and tools/make_game_art.py. The screen design
follows docs/ui_guidelines.md and the team's decisions. The code was reviewed
and tested before it was committed: backend tests, and 71 click-through checks
at phone size.

## Manaswi: AI help, guardrails and photo test

### Libraries
FastAPI (MIT), Uvicorn (BSD-3), httpx (BSD-3), python-dotenv (BSD-3), pytest (MIT), ReportLab (BSD-3) and pydantic (MIT, comes with FastAPI). See requirements.txt.

### Files (Role D)
`backend/ai/ask.py`, `common.py`, `llm.py`, `photo_check.py`, `skill_card.py`, `split.py`, `safety.py`, `high_risk.py`; the prompts in `backend/prompts/`; `backend/api/ai_routes.py`; `backend/tests/test_ai.py`, `test_ai_guardrails.py`, `run_ai_cases.py`, `run_photo_test.py` and `conftest.py`; `frontend/src/components/AskForHelp/`; `docs/make_prompts_pdf.py`, which generates `docs/prompts.pdf` (built-in fonts only, no outside assets).

### Photo safety test images (backend/tests/ai_images/photo_test)
These 27 images are used only to test the app: 12 from free sources and 15 our own photos. Nothing was generated by AI. The photo test is a sanity check. Safety comes from the code rules.

Free web images (12):
- web_foam_01.jpg: Photo by Oliur on Unsplash (Unsplash License). https://unsplash.com/photos/burger-inside-styrofoam-container-M-fA89yvx2I
- web_foam_02.jpg: "Hefty square styrofoam food container open" by BrokenSphere, via Wikimedia Commons, CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/). Not edited. https://commons.wikimedia.org/wiki/File:Hefty_square_styrofoam_food_container_open.JPG
- web_foam_03.jpg: Photo by RDNE Stock project on Pexels (Pexels License). Cropped. https://www.pexels.com/photo/dipping-of-fries-on-a-sauce-5779543/
- web_foil_01.jpg: Photo by Christian Moises Pahati on Pexels (Pexels License). https://www.pexels.com/photo/assorted-foods-in-aluminum-container-5724559/
- web_foil_02.jpg: Photo by Fenghua on Unsplash (Unsplash License). https://unsplash.com/photos/small-servings-of-food-in-foil-containers-CLyrWfoKjoY
- web_foil_03.jpg: Photo by Engin Akyurt on Pexels (Pexels License). https://www.pexels.com/photo/wrinkled-aluminum-surface-10221753/
- web_takeout_01.jpg: Photo by Kelly Sikkema on Unsplash (Unsplash License). https://unsplash.com/photos/small-brown-cardboard-box-with-handle-5R5Trsu1aIM
- web_goldtrim_01.jpg: Photo by Andrey Soldatov on Unsplash (Unsplash License). https://unsplash.com/photos/a-white-plate-with-blue-flowers-and-gold-trim-NuiifabiRmA
- web_goldtrim_02.jpg: "Serenity" by Tamara Harhai on Unsplash (Unsplash License). https://unsplash.com/photos/silver-fork-on-white-round-plate-NgLO-4P2uok
- web_plain_01.jpg: Photo by Katrin Bolovtsova on Pexels (Pexels License). Cropped. https://www.pexels.com/photo/plain-white-mugs-on-a-white-surface-6312177/
- web_plain_02.jpg: Photo by Eva Bronzini on Pexels (Pexels License). Cropped. https://www.pexels.com/photo/white-ceramic-bowl-in-close-up-shot-6944482/
- web_plain_03.jpg: Photo by Anna Tukhfatullina on Pexels (Pexels License). Cropped. https://www.pexels.com/photo/flatlay-photography-of-white-ceramic-bowl-2611817/

Our own photos (15), taken by the team:
- web_labeled_01.jpg, web_notformicrowave_01.jpg, web_package_01.jpg, web_package_02.jpg (team photos; the web_ prefix is a naming leftover, not a source)
- own_labeled_04.jpg, own_labeled_05.jpg, own_labeled_06.jpg
- own_notformicrowave_02.jpg, own_notrecommended_01.jpg, own_nolabel_01.jpg
- own_metal_lid_01.jpg, own_dishwasher_safe_01.jpg, own_paperbox_01.jpg
- own_blurry_01.jpg, own_blurry_02.jpg

Brand names on packaging in our own photos belong to their owners. We use them only to test label reading.

### How AI tools were used (Role D)

I used Claude as a coding assistant for Role D. I decided what the help feature should do and what counts as safe. Claude helped me write and fix code, test scripts and documentation, and I tested and reviewed each change before committing it.

The photo test set is my own work. I took 15 of the 27 photos myself, found and checked the licence of each of the 12 web photos by hand, rejected 8 images whose source I could not confirm, and set the true answer for every photo. Claude wrote the helper scripts that build the manifest and check the credits (one-off scripts, not committed).

Claude helped with these specific parts:

- `AskForHelp.jsx`: the `toggleMic` function (the Safari speech fix and resetting the button after an error) and the `sendEvent` function (sending `null` instead of empty text for `seconds` and `days_since_last`, so the server stops rejecting the log).
- `run_ai_cases.py`: the image paths for the dish, foil, blurry and package time cases, the change that lets the blurry case accept either safe reply, and the photo table text. `ai_cases.md` is generated by this script.
- the Role D README section (formerly docs/README_D.md) and `make_prompts_pdf.py`: the photo test section and the paragraph in the PDF, updated to 27 photos and under about 11%.
- `manifest.csv` and the credits in `ATTRIBUTION.md`: Claude wrote the scripts that built the manifest and appended the credit lines (one-off scripts, not committed), from the truth values and licence details I gave it.
- The Role D sections of `README.md` and `ATTRIBUTION.md`: Claude drafted the text and I checked every claim.

I wrote the earlier Role D files (`safety.py`, `high_risk.py`, the prompts, `ai_routes.py` and the tests) myself. Claude reviewed the code and suggested fixes, which I tested and applied.

I reproduced the bugs, tested in Safari and Chrome, re ran the AI cases against the live model, read every reply, and checked every number against the results.

### Voice helper
**Files:** frontend/src/components/VoiceAgent/ (VoiceAgent.jsx and VoiceAgent.css), frontend/src/lib/voiceCommands.js, frontend/src/lib/voiceDom.js, docs/voice_helper.md, the voice listener in frontend/src/screens/StepScreen.jsx, and the runCommand function in frontend/src/screens/ResidentApp.jsx.

**Libraries:** none. It uses the browser's built-in Web Speech API for speech to text. In Chrome that service is run by Google, and in Safari by Apple. The command matching is plain code with a fixed list of commands. No language model is used.

**AI assistance:** I wrote the voice helper with Claude as a coding assistant. I decided how it should behave: the microphone is off until the person turns it on, the browser asks permission first, it turns itself off after 3 minutes, it never marks a step Done without asking "Did you finish this step?" and waiting for a yes, and the app says plainly that the browser's speech service receives the audio. Claude helped write the code, and I tested each change in the browser, checked the commands by speaking them, and can explain how every part works.

## Vaishnavi

**Files:** `backend/api/main.py`; the demo, staff, review and skill routes
(`backend/api/demo_routes.py`, `staff_routes.py`, `review_routes.py`,
`skill_routes.py`) and their tests; `frontend/src/pages/` (Staff, Demo,
Review, Resident), `frontend/src/components/DemoChart/`,
`frontend/src/components/ResidentPreview/`, `frontend/src/App.jsx` and the
frontend setup (`package.json`, `vite.config.js`, `index.css`); and most of
`backend/logic/fade.py` (Rules 2 and 3 and the missing_step response are
Role B's, see above).

**Libraries:** React and react-dom (MIT), react-router-dom (MIT), Vite and
@vitejs/plugin-react (MIT), FastAPI (MIT) and Uvicorn (BSD-3). The chart on
the Demo page is plain SVG, no chart library.

**Prior work this builds on:** the fading rules follow MacDuff, Krantz &
McClannahan (2001), as in the Role B section; the pages follow
docs/ui_guidelines.md. No code was taken from any existing product.

**Added by Role A, agreed with Role E:** the phone frame with the real
resident app, "Why this changed" and the "Help over time" grid in Demo.jsx and
Demo.css; the "Ask AI for more detail on this step" button and demo note in
Staff.jsx and Staff.css; the plain-address redirect in App.jsx. These were
written with Claude Code (see the Role A section).

**AI assistance:** where AI coding assistants were used for Role E, the code
was reviewed and tested by the team before it was committed (backend tests and
the frontend build), and the team can explain how each page and route works.
