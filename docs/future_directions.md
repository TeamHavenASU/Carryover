# Future directions

Where Carryover goes after the hackathon, and why. Full references for every source named here are in [sources.md](sources.md).

## Where we are now

The demo has two tasks: heat a meal (microwave) and buy something (in store with a card, in store with a phone, and online). It runs the fading rules, finds where each person gets stuck, and applies our safety rules. Everything runs on simulated residents. There is no real resident, card or bank data.

Our research so far is from published studies and three sessions with First Place AZ staff (see [partner_research.md](partner_research.md)). We have not yet heard from residents themselves.

## What research doesn't answer yet

These gaps are the main reason the next step is a pilot, not more features.

| Gap | What it means for us |
| --- | --- |
| We found no studies of app-based or AI prompt fading for autistic adults | Prompt fading is well studied when trainers do it (MacDuff et al. 2001). Whether it works the same way in an app is something we have to test |
| Much of the evidence is from children, or from people with intellectual disability rather than autistic adults | Several of our numbers lean on studies of children (Richling et al. 2019; Fuller & Fienup 2018) or students with intellectual disability (Stierle et al. 2023; Burke et al. 2024). They may not carry over exactly |
| Our numbers are starting points, not proven values | "Show less help after 3 times done alone," "more help after 2 struggles" and "rusty after 14 days" are backed by research on the idea, not the exact values. Staff can change them in `definitions.json` |
| People differ a lot | Executive function difficulties are common in autistic adults but not universal (Johnston et al. 2019; Demetriou et al. 2018). That is why Carryover learns each person instead of assuming |
| Evidence for games with autistic adults is thin | One small trial found a gamified app was used longer (Lee et al. 2022), but rewards can also lower interest (Deci, Koestner & Ryan 1999). Game mode stays optional until a pilot shows how people respond |
| Rich screens can make things harder | Autistic teens did worse on screens that combined text, speech, images and animated agents (Grynszpan et al. 2008). As we add video and voice, we need to check they help rather than overload |
| Our own data can't yet tell which help works best | In the simulated data, the most help looks less successful, but only because people get it when they are already struggling (a selection effect). Only real use, with consent, can answer this |

## Roadmap

We don't give dates. Each phase depends on the one before it.

### Phase 1: Pilot and co-design with First Place AZ

| What | Why it's needed | Why it might work | Why not now |
| --- | --- | --- | --- |
| A small pilot with residents who choose to join, and their support staff | Our rules and numbers need real use to check them | Prompt fading works when trainers do it (MacDuff et al. 2001); accessibility guidance says to test with users (W3C COGA; Hassell Inclusion & NAS) | We only had staff access. A pilot needs consent and review, which takes longer than a hackathon |
| Co-design with autistic adults: they help shape the screens, words and settings, and are paid for their time | Tools for autistic adults should be shaped by autistic adults | AASPIRE guidelines for including autistic adults in research (Nicolaidis et al. 2019); a co-designed site that 170 autistic users found easy to use (Raymaker et al. 2019) | Same: no resident access yet |
| Ask residents whether the app feels like help or like being watched | Carryover should support choice, not monitoring | Self-determination research (Wehmeyer & Abery 2013) | Needs residents |
| Ask First Place staff which tasks they want next | Staff know which skills matter most for moving out | Partner input shaped the current design | Planned for after the hackathon |
| Use residents' feedback from the app: one-tap answers in Settings on movement, sound, colors and amount of help, then follow-up conversations | We need residents' views, not only staff's. One-tap answers tell us that something bothers someone, but not which thing ("too much movement" doesn't say which animation), so the pilot follows up in person | Self-determination: the person can tell the system it isn't right for them (Wehmeyer & Abery 2013); test with users (W3C COGA) | Needs residents |

**What we would measure:** help used per step over the weeks, steps done alone, whether skills last after a break, whether staff agree with what the app chose, and what residents say. We would not give anyone less help on purpose just to test it.

### Phase 2: Learn from the pilot

| What | Why it's needed | Why it might work | Why not now |
| --- | --- | --- | --- |
| Tune the numbers for each person (when to fade, when someone is "rusty") | People differ a lot, and a fixed mastery bar doesn't always keep a skill | Demetriou et al. 2018; Richling et al. 2019; Fuller & Fienup 2018 | Needs real data |
| Let a person's feedback bring forward the offer of less help, or more help, for the task they're doing. The fading rules still decide; the answer just brings the question sooner | Today the "amount of help" answer is recorded and explains how help works, but doesn't change anything | Asking before reducing help already follows self-determination research (Wehmeyer & Abery 2013) | The answer is about the whole app, but help fades per step, so we need to decide which steps it applies to. It also changes the core fading rules, which need careful testing |
| Let the "what worked" scores help choose help | Today they only explain choices, because of the selection effect | Better data from the pilot can compare help levels fairly | Our simulated data can't |
| Build the help level per session, not per week | Today a second session in the same week can't see the first | A simple change to how the view is built | Fine for the demo's weekly slider |
| Skill cards fade too, and come back when someone is stuck at the most help | Skill cards should fade like steps do | Same fading method as the steps | The rules are written; not built yet |
| Flag a step's wording for staff when people keep asking about it | Repeated questions may mean the step is unclear | Our own rule, to test | Rule written; not built yet |
| A bigger photo test for the AI, plus tracking errors during the pilot | 30 photos can only show the error rate is probably under about 10% | Rule of three (Hanley & Lippman-Hand 1983) | Needs many more photos and real use |

### Phase 3: More help and more tasks

| What | Why it's needed | Why it might work | Why not now |
| --- | --- | --- | --- |
| A short point-of-view video for every step (never autoplay, with captions, one at a time, not stacked with other media) | First Place staff asked for video; some people learn better by watching | Video prompting meta-analysis (Aljehany & Bennett 2019); point-of-view clips had larger to very large effects (Wertalik et al. 2025); short clips per step beat one long video (Cannella-Malone et al. 2006); video on phones works (Stierle et al. 2023) | Filming, captions and licenses take time. The video slot exists in every step already |
| Photos of each person's own microwave and devices, taken once at setup (no people in them) | A picture of a different device can confuse someone who reads it literally; staff said a new microwave is hard | General case teaching (Smith 1995) | Needs a safe way to take and store photos |
| Extra detail saved for each person (which hand, which way to turn) | Some people need much more detail (First Place, Nov 4) | The AI split already does this, with staff approval | Today the extra detail is shared by everyone who uses the task |
| Practice tasks for base skills (like opening different packages), linked from the skill card | Skill cards are short; some people need more practice | Same task analysis and fading method as the main tasks | Each one needs writing and testing |
| AI suggests base skills and skill cards for any new task; staff approve | So Carryover works for tasks we never wrote by hand | The AI split already works this way, with staff approval | Needs testing for accuracy and safety first |
| More tasks, and linked tasks (for example laundry, add a card to a phone, find an item in a store). A step can open another task ("No card saved? Add a card") | Real life links tasks together | Same task analysis method (Rowe et al. 2011; Barnard-Brak et al. 2023) | Each task needs research, steps and testing |
| More money tasks: budget a week's shopping, compare prices, check a receipt with a support person | Buying is only one part of handling money | CAN-B decision steps (Adams et al. 2026) | Money is high risk. The same guardrails apply: never connect to a bank, read a balance, or say what to buy |
| Voice: read-aloud and spoken answers to check questions; paid natural voices later | Some people prefer listening or talking | Read-aloud is optional; video prompting worked with or without voice-over (Dawson et al. 2023) | Time; voice data needs a privacy plan; paid voices cost money |
| Fuller Game mode: worlds built from the interests people type in, more themes, artwork (free CC0 art, or AI-drawn art made once, reviewed and saved, never live), co-designed with residents | Staff said a formal app may not get used | Special interests linked to wellbeing (Grove et al. 2018); a gamified app was used longer (Lee et al. 2022) | Evidence with autistic adults is thin, so test in the pilot first. The typed-interest world has one saved example today; the AI version is not built |

### Phase 4: Beyond First Place

| What | Why it's needed | Why it might work | Why not now |
| --- | --- | --- | --- |
| A separate staff tool with its own login, where a support person reviews AI-written steps and sees the sticking points summary, only if the resident chooses to share | Staff pages should never be part of the resident's app. In the demo there is no login | Keeps the resident in control (Wehmeyer & Abery 2013) | Needs accounts and secure storage |
| A plain-language "How Carryover works" page for residents | People should know what the app does with their taps and photos | NIST AI Risk Management Framework (transparency) | Best written with residents in the pilot |
| Offer Carryover to other group homes and day programs | First Place has about 75 residents; many more people could use it | Pilot results from Phase 1 | Needs pilot evidence, and a way to share task files without copying published assessments such as AFLS |

## How we'll know it's working

- People need less help on a step over the weeks, and help comes back when they struggle.
- Skills last after a long break.
- Residents say it feels like help, not like being watched.
- Staff agree with the help level the app chose.
- Zero wrong "safe" answers from the AI on dishes and food.
