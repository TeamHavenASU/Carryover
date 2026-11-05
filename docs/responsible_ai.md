# Responsible AI

How Carryover protects people's privacy, safety and autonomy, where it uses AI and where it doesn't, and the limits we know about. Full references are in [sources.md](sources.md). The safety rules in full are in [safety.md](safety.md).

We organize this around the NIST AI Risk Management Framework (AI RMF 1.0, 2023), which lists what makes AI trustworthy: valid and reliable, safe, secure, accountable and transparent, explainable, privacy-enhanced, and fair.

## Where we use AI, and where we don't

Most of Carryover is plain rules, not an AI model. Rules are explainable, safe, and work with little data. We use an AI model only for open-ended moments no fixed screen can handle.

| Part | How it works | Uses an AI model? |
| --- | --- | --- |
| Finding where someone gets stuck (`detect.py`) | Rules on the person's own tap history | No |
| Choosing how much help to show, and fading it (`fade.py`) | Rules per person, per step | No |
| Scoring what help has worked (`learn.py`) | Counts per person and across everyone | No |
| "I'm stuck" helper (type, speak or take a photo) | AI model, with safety rules before and after | Yes |
| Extra detail for a small step (which hand, which way) | AI model; a person approves it before anyone sees it | Yes |
| AI-written skill cards and small steps | AI model; a person approves them before anyone sees them | Yes |
| Game mode worlds and art | A list of themes, free art and our own animation code | No |

## Privacy

- **Photos:** the person chooses to take a photo; the camera is never on by itself. Photos are used to answer, then deleted. They are not saved or logged.
- **No people in photos.** Never photos of a bank app, card, receipt or checkout page.
- **We say when data leaves the app.** Users are told that a photo is sent to an AI service to get the answer.
- **Typed questions are not saved.**
- **Feedback answers are taps only,** with no typed text, and are shared only if sharing is on.
- **The log records only that a step was done.** Never what was bought, what it cost, or what was eaten.
- **No money data.** Carryover never reads a balance, connects to a bank, or asks for or stores a card number or PIN.
- **Sharing is off by default.** Staff see a person's sticking points only if that person chooses to share.
- **No real data in the demo.** Every resident is simulated. No real resident, card or bank data.
- **No secrets in the repo.** API keys live in `.env`, which git ignores.

**Next:** a written data plan for any pilot: what is stored, where, for how long, and who can see it.

## Safety

### When the AI answers and when it hands off

AI models are overconfident when they say how sure they are (Xiong et al. 2024), and vision AI can name objects that aren't there (Li et al. 2023). So we don't trust the AI's own "I'm sure." For high-risk questions:

1. **Quote the label.** The AI must quote the words it read, such as "MICROWAVE SAFE." Our code checks the quote. No label words, no "safe" answer.
2. **Ask 3 times.** The question is sent 3 separate times. It answers only if all 3 agree.
3. **Never "safe" from looks.** It may say "don't use it" if it clearly sees metal, foil or foam. It never says "safe" just from how a dish looks. This rule is our design choice; the research shows why it's needed.
4. **Otherwise hand off.** "I'm not sure. Please ask [support person], or use a plate you know is safe." Staying quiet when unsure keeps errors low (Geifman & El-Yaniv 2017).

| Risk | Examples | What the AI does |
| --- | --- | --- |
| Low | Which button is Start? What's the price? Which is cheaper? What do I press on the card reader? | Answers from what it sees |
| Medium | How long do I heat this? | Reads the time printed on the package. If it can't read it, hands off |
| High | Can this dish go in the microwave? | Only the strict rule above |
| Never answers | Is this cooked enough? Should I buy this? Can I afford this? | Hands off to the support person, or points to the USDA check (steaming in the middle, 165°F) |

### Testing the AI

A 30-photo test (labeled and unlabeled dishes, foil, foam, takeout boxes, blurry photos) with a target of zero wrong "safe" answers. If there is one, that kind of question always hands off. Zero errors in 30 photos only shows the error rate is probably under about 10% (rule of three, 3 ÷ 30; Hanley & Lippman-Hand 1983). That is why the quote-the-label rule matters more than the test score.

**Next:** test on more photos (different lighting, labels and languages) before any real use, and track errors during a pilot.

### Safety in the tasks

- **Cautions are always shown,** at every help level, even when the person no longer needs help with the step. Help fading never hides a caution. First Place staff asked for this, and adults learn safety facts placed inside the instructions (Jones & Collins 1997).
- **Payment cautions:** the card step says never tell anyone your PIN and cover the keypad; the phone step says never tell anyone your passcode; the online step says press Place Order only once and never give your card number to someone who calls, texts or emails you. The card step also says to press No if the reader asks about cash back.
- **Food:** a "never put these in the microwave" card from USDA and FDA guidance, and a note if food has been out more than 2 hours.
- **It never picks a cooking time or says food is cooked enough.**
- **It never says whether to buy something or what to choose.** If someone says they can't afford something, it suggests talking to their support person. No advice.
- **Not an emergency tool.** The support person is one tap away for anything the app shouldn't answer.

## Autonomy

Self-determination research puts choice and control at the center (Wehmeyer & Abery 2013; Shogren et al. 2015). Carryover follows that:

- **The person decides how much help.** The app asks before showing less help ("Want to try with less help next time?"), and they can say no.
- **Residents can tell the app what isn't working for them** in Settings (movement, sound, colors, amount of help). The help answer never changes the help level.
- **Asking for help never counts against them.**
- **They choose their support person.** It can be a staff member, a family member or someone else they pick.
- **They choose whether to share** their progress with staff. Off by default.
- **They can take a break any time.** Break time never counts as being stuck.
- **Preferences are asked, not assumed.** A short first-time setup (with Skip) asks about interests, Game or Normal mode, sound and which hand. Other questions come up only when they matter.
- **No pressure to perform.** No points, streaks or badges in Normal mode. Praise is short and factual ("Step 4 done"), with a Calm, Cheerful or Off setting. Rewards can lower interest (Deci, Koestner & Ryan 1999).

### Game mode without pressure

First Place staff told us a formal app may not get used, so Game mode exists, but it is built to avoid pressure:

- It is opt-in. People try Game and Normal at setup, then pick, and can switch any time.
- Rewards never depend on using less help, and there is no reward for doing a step "on your own." That could make someone avoid asking for help.
- The reward is a choice the person makes (for example, a bird, a balloon or a kite). Interest content is never taken away.
- Sound and motion follow the person's settings. Nothing flashes, and no sudden sounds.
- No brands or known characters.
- We don't claim research proves Game mode helps autistic adults. The evidence is thin (Lee et al. 2022), so it is something to test in a pilot.

**Next:** ask residents in a pilot whether the app feels like help or like being watched.

## Human oversight

- **A person approves AI-written content** (extra detail, small steps, skill cards) before anyone sees it.
- **Staff see flags, the app doesn't decide for them,** for example a step where someone often takes breaks.
- **Staff can change every rule's number** in `definitions.json`.
- **The "what worked" scores explain choices; they don't make them.** The fading rules decide the help (see Limits).

**Next:** a separate staff tool with its own login. In the demo there is no login, and residents never see staff pages.

## Fairness and accessibility

- Plain, literal words, one step per screen, the same layout every time (W3C COGA; Hassell Inclusion & National Autistic Society).
- Settings for colors, light or dark, text, pictures, reading voice, sound and animation.
- WCAG 2.2 contrast and tap size. Nothing flashes or plays by itself, and motion follows the device's reduced-motion setting.
- Carryover adapts to each person instead of assuming everyone has the same difficulties.

**Next:** co-design and test with autistic adults, following the AASPIRE guidelines (Nicolaidis et al. 2019; Raymaker et al. 2019).

## Transparency

- Every rule has a stated reason and a source (see [sources.md](sources.md) and the README).
- Users are told when a photo goes to an AI service.
- This document lists what we chose not to build and what we don't know yet.

**Next:** a plain-language "How Carryover works" page for residents.

## Limits we know about

- **Reading our own data carefully.** Carryover scores how often each kind of help works. In our simulated data, the most help (the step plus small steps) has a lower success rate than lighter help. That isn't evidence that more help is worse: a step only gets the most help because the person was already struggling with it, so those attempts start out harder. Data collected this way can't tell us which help works better. So we don't let these scores choose the help; the fading rules do that. The scores only explain choices and give a starting guess for someone new. To learn what really works, we would run a pilot with consent. We would not give anyone less help on purpose to test it.
- **Check questions stop themselves.** Check questions only cover steps with no help. Two "no" answers bring the help back, so the question stops there. A step missed after help returns is caught by the other signals (stuck, or started but never finished).
- **A small photo test.** 30 photos can only show the error rate is probably under about 10%.
- **Simulated data.** Every result in the demo comes from simulated residents. The app never reads the simulator's patterns; it works them out from taps alone, as it would with real people.
- **Staff only.** Our partner research was with First Place staff. We haven't heard from residents yet.
- **Starting numbers.** Our rule numbers are starting points backed by research on the idea, not tested values, and much of that research is with children or people with intellectual disability.
- **Not everyone has the same difficulties.** About a third of autistic adults in one study showed no executive function difficulties on tests (Johnston et al. 2019).
- **More media isn't always better.** Richer screens made things harder for autistic teens (Grynszpan et al. 2008), so we show one step at a time and don't stack video, voice and text at once.
