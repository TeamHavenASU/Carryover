# Safety rules

These rules apply to every task. The AI rules are written into the prompts and checked in code (`backend/ai/`). The microwave list is shown in the app.

## 1. Microwave: never put these in

Shown on step 1 of "Heat a meal" and as a caution card the first time someone opens the task. From USDA and FDA guidance.

The plain-words version the app shows is in heat_meal.json -> safety_card_content.

| Don't use | Why | Source |
| --- | --- | --- |
| Metal pans, metal twist ties, food fully wrapped in foil | Metal reflects microwaves and can damage the oven | USDA, FDA |
| Takeout containers with metal handles | Metal | USDA |
| Plates or cups with gold or silver paint or trim | Metal | USDA |
| Foam cups, bowls, plates and trays | Not safe for microwave heating | USDA |
| Yogurt cups, butter or margarine tubs, other one-time containers | Can warp or melt; chemicals can get into food | USDA |
| Brown paper bags, newspaper | Not safe | USDA |
| Plastic grocery bags, thin plastic storage bags | Can melt | Clemson HGIC (based on USDA) |
| Any container that warped or melted before | Not safe | USDA |

OK to use: dishes labeled "microwave safe," heatproof glass, glass-ceramic, white paper towels and plates, wax paper, parchment paper.

Also (FDA):
- Plain water heated in a clean cup can boil over suddenly and burn. Don't heat water longer than the microwave's manual says.
- Don't use the microwave if the door doesn't close firmly or looks broken. Tell staff.

### Caution on steps (always shown)

Some steps have a `safety` sentence. The screen always shows it as a **CAUTION** line on that step, at every help level, even when the step is folded. No tap needed (First Place asked for this on Nov 4). Someone who does a step on their own still sees it. (Jones et al. 1997: adults learned safety facts placed inside the instructions.)

| Task | Step | Caution |
| --- | --- | --- |
| Heat a meal | s5 Stir halfway | If you stir, use oven mitts. The dish may be hot. |
| Heat a meal | s6 Take it out and let it sit | Use oven mitts to take the dish out. It may be hot. Lift the cover away from your face. Steam can be hot. |
| Heat a meal | s7 Check it's hot | Take a small first bite. Some spots can be very hot. |
| Buy in store, card | s8 Pay | Never tell anyone your PIN. Cover the keypad with your other hand when you type it. |
| Buy in store, phone | s8 Pay | Never tell anyone your phone passcode. Only hold your phone near the store's card reader. |
| Buy online | s9 Check the address, then pay | Press Place Order only once. Page stuck? Check your orders or email before trying again. Never give your card number to someone who calls, texts or emails you. |

### Pictures and video in the steps

- Step pictures are our own simple drawings (`frontend/public/img/`). Money pictures show generic card readers, phones and screens only: never a real card, card number, bank app or receipt.
- Videos (planned, not in the app yet): only free-license clips, credited in ATTRIBUTION.md, never autoplay, no people's faces.

### Taking a break while heating a meal

Opening the door pauses the microwave, so a break mid-heating is safe. If the person comes back **more than 2 hours** later, the app shows: "Your food has been out over 2 hours. USDA says food left out that long may not be safe to eat. Ask staff what to do." (USDA: never leave food out of refrigeration over 2 hours; 1 hour above 90°F.) Set in `heat_meal.json` as `break_note`.

## 2. Photo questions

- The person chooses to take a photo. The camera is never on by itself.
- Photos are used to answer, then deleted. Not saved, not logged.
- The app asks people not to photograph people, a bank app, a card, a receipt or a checkout page.
- The app tells the person the photo is sent to an AI service to get the answer, and is not saved.
- A photo question counts as used help. It never counts against them.

| Risk | Examples | What the AI does |
| --- | --- | --- |
| Low | Which button is Start? What's the price? Which is cheaper? What do I press on the card reader? | Answers from what it sees |
| Medium | How long do I heat this? (package) | Reads the time printed on the package. Can't read it: hand off |
| High | Can this dish go in the microwave? | Only the strict rule below |
| Never answers | Is this cooked enough? Should I buy this? Can I afford this? | Hands off. Points to the USDA check (steaming in the middle, 165°F) or the support person. These questions are caught by rules in code (`backend/ai/safety.py`) before the AI is called |

## 3. When the AI answers vs hands off (high-risk questions)

The AI's own "I'm 90% sure" can't be trusted: AI models are overconfident when they say how sure they are (Xiong et al. 2024), and vision AI can see things that aren't there (Li et al. 2023).

1. **Quote the label.** The AI must quote the words it read (for example, "MICROWAVE SAFE"). Our code checks the quote. No label words = no "safe" answer.
2. **Ask 3 times.** The question is sent 3 separate times. The AI answers only if all 3 agree (Xiong et al. 2024: consistency beats self-reported confidence).
3. **Never "safe" from looks.** The AI may say "don't use it" if it clearly sees metal, foil or foam. It never says "safe" just from how a dish looks.
4. **Otherwise hand off.** "I'm not sure. Please ask [support person], or use a plate you know is safe." (Abstain when unsure: Geifman & El-Yaniv 2017.)

The support person is the support specialist, or someone the resident chose at setup (like a family member or guardian).

### Photo test

1. 27 photos: 15 taken by the team and 12 free images credited in ATTRIBUTION.md. Labeled and unlabeled dishes, foil, foam, takeout boxes, metal, packages and blurry photos.
2. We counted (a) how often the AI answered and (b) how many answers were wrong.
3. Target: zero wrong "safe" answers. If there were one, that question type would always hand off.

Result: 14 answered, 13 handed off, 0 wrong "safe" answers. Full table in `backend/tests/photo_test_results.md`.

Honest limit: 0 errors in 27 photos only shows the error rate is probably under about 11% (rule of three: 3 ÷ 27). That's why check 1 matters more than the test score.

## 4. Guardrails (things we choose not to build)

- Never reads a balance, connects to a bank, or stores money numbers.
- Never says whether to buy something or what to choose.
- Never asks for or stores a card number or PIN.
- Never picks a cooking time or says food is cooked enough.
- If someone says they can't afford something, suggest talking to their support person. No advice.
- The log records only that a step was done. Never what was bought, the cost, or what was eaten.
- No real bank, card, payment or resident data in the demo.
- No API keys in the repo (use `.env`, which is in `.gitignore`).
