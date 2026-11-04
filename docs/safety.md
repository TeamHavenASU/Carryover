# Safety rules

These rules apply to every task. Role D puts the AI rules into the prompts. The microwave list is shown in the app.

## 1. Microwave: never put these in

Shown on step 1 of "Heat a meal" and as a caution card the first time someone opens the task. From USDA and FDA guidance.

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

### Taking a break while heating a meal

Opening the door pauses the microwave, so a break mid-heating is safe. If the person comes back **more than 2 hours** later, the app shows: "Your food has been out over 2 hours. USDA says food left out that long may not be safe to eat. Ask staff what to do." (USDA: never leave food out of refrigeration over 2 hours; 1 hour above 90°F.) Set in `heat_meal.json` as `break_note`.

## 2. Photo questions

- The person chooses to take a photo. The camera is never on by itself.
- Photos are used to answer, then deleted. Not saved, not logged.
- No people in photos.
- Never allowed: bank app, card, receipt, checkout page. Explain these with a demo example instead.
- Tell users the photo is sent to an AI service to get the answer.
- A photo question counts as used help. It never counts against them.

| Risk | Examples | What the AI does |
| --- | --- | --- |
| Low | Which button is Start? What's the price? Which is cheaper? What do I press on the card reader? | Answers from what it sees |
| Medium | How long do I heat this? (package) | Reads the time printed on the package. Can't read it: hand off |
| High | Can this dish go in the microwave? | Only the strict rule below |
| Never answers | Is this cooked enough? Should I buy this? Can I afford this? | Hands off. Points to the USDA check (steaming in the middle, 165°F) or the support person |

## 3. When the AI answers vs hands off (high-risk questions)

The AI's own "I'm 90% sure" can't be trusted: AI models are overconfident when they say how sure they are (Xiong et al. 2024), and vision AI can see things that aren't there (Li et al. 2023).

1. **Quote the label.** The AI must quote the words it read (for example, "MICROWAVE SAFE"). Our code checks the quote. No label words = no "safe" answer.
2. **Ask 3 times.** Send the question 3 separate times. Answer only if all 3 agree (Xiong et al. 2024: consistency beats self-reported confidence).
3. **Never "safe" from looks.** The AI may say "don't use it" if it clearly sees metal, foil or foam. It never says "safe" just from how a dish looks.
4. **Otherwise hand off.** "I'm not sure. Please ask [support person], or use a plate you know is safe." (Abstain when unsure: Geifman & El-Yaniv 2017.)

The support person is the support specialist, or someone the resident chose at setup (like a family member or guardian).

### Test before the demo

1. About 30 of our own photos: labeled dishes, unlabeled dishes, foil, foam, takeout boxes, blurry photos.
2. Count (a) how often the AI answered and (b) how many answers were wrong.
3. Target: zero wrong "safe" answers. If there's one, that question type always hands off.

Honest limit: 0 errors in 30 photos only shows the error rate is probably under about 10% (rule of three: 3 ÷ 30). That's why check 1 matters more than the test score.

## 4. Guardrails (things we choose not to build)

- Never reads a balance, connects to a bank, or stores money numbers.
- Never says whether to buy something or what to choose.
- Never asks for or stores a card number or PIN.
- Never picks a cooking time or says food is cooked enough.
- If someone says they can't afford something, suggest talking to their support person. No advice.
- The log records only that a step was done. Never what was bought, the cost, or what was eaten.
- No real bank, card, payment or resident data in the demo.
- No API keys in the repo (use `.env`, which is in `.gitignore`).
