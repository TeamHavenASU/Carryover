# Future directions

Where Carryover goes after the hackathon, and why. Full references for every source named here are in [sources.md](sources.md).

## Where we are now

The demo has two tasks in four versions: heat a meal (microwave) and buy something (in store with a card, in store with a phone, and online). It runs the fading rules, finds where each person gets stuck, and applies our safety rules. It also has an AI helper for open-ended questions, AI-written extra detail that a person approves before anyone sees it, and an optional Game mode. Everything runs on simulated residents. There is no real resident, card or bank data.

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

The phases are in order: each one builds on what the one before it shows.

### Phase 1: Pilot and co-design with First Place AZ

| What | Why it's needed | Why it might work | Why not now |
| --- | --- | --- | --- |
| A small pilot with residents who choose to join, and their support staff | Our rules and numbers need real use to check them | Prompt fading works when trainers do it (MacDuff et al. 2001); accessibility guidance says to test with users (W3C COGA; Hassell Inclusion & NAS) | We only had staff access. A pilot needs consent and review, which takes longer than a hackathon |
| Co-design with autistic adults: they help shape the screens, words and settings, and are paid for their time | Tools for autistic adults should be shaped by autistic adults | AASPIRE guidelines for including autistic adults in research (Nicolaidis et al. 2019); a co-designed site that 170 autistic users found easy to use (Raymaker et al. 2019) | Same: no resident access yet |
| Ask residents whether the app feels like help or like being watched | Carryover should support choice, not monitoring | Self-determination research (Wehmeyer & Abery 2013) | Needs residents |
| Use residents' feedback from the app: one-tap answers in Settings on movement, sound, colors and amount of help, then follow-up conversations | We need residents' views, not only staff's. One-tap answers tell us that something bothers someone, but not which thing ("too much movement" doesn't say which animation), so the pilot follows up in person | Self-determination: the person can tell the system it isn't right for them (Wehmeyer & Abery 2013); test with users (W3C COGA) | The Settings section is built; the follow-up conversations need residents |

**What we would measure:** help used per step over the weeks, steps done alone, whether skills last after a break, whether staff agree with what the app chose, and what residents say. We would not give anyone less help on purpose just to test it.

### Phase 2: Learn from the pilot

| What | Why it's needed | Why it might work | Why not now |
| --- | --- | --- | --- |
| Tune the numbers for each person (when to fade, when someone is "rusty", how long to wait before offering help) | People differ a lot, and a fixed mastery bar doesn't always keep a skill | Demetriou et al. 2018; Richling et al. 2019; Fuller & Fienup 2018 | Needs real data |
| Let a person's feedback bring forward the offer of less help, or more help, for the task they're doing. The fading rules still decide; the answer just brings the question sooner | Today the "amount of help" answer is recorded and explains how help works, but doesn't change anything | Asking before reducing help already follows self-determination research (Wehmeyer & Abery 2013) | The answer is about the whole app, but help fades per step, so we need to decide which steps it applies to. It also changes the core fading rules, which need careful testing |
| Let the "what worked" scores help choose help | Today they only explain choices, because of the selection effect | Better data from the pilot can compare help levels fairly | Our simulated data can't |
| Build the help level per session, not per week | Today a second session in the same week can't see the first | A simple change to how the view is built | Fine for the demo's weekly slider |
| Skill cards fade too, and come back when someone is stuck at the most help | Skill cards should fade like steps do | Same fading method as the steps | The rules are written; not built yet |
| Flag a step's wording for staff when people keep asking about it | Repeated questions may mean the step is unclear | Our own rule, to test | Rule written; not built yet |
| A bigger photo test for the AI, plus tracking errors during the pilot | 27 photos can only show the error rate is probably under about 11% | Rule of three (Hanley & Lippman-Hand 1983) | Needs many more photos and real use |

### Phase 3: More help and more tasks

| What | Why it's needed | Why it might work | Why not now |
| --- | --- | --- | --- |
| A short point-of-view video for every step (never autoplay, with captions, one at a time, not stacked with other media) | First Place staff asked for video; some people learn better by watching | Video prompting meta-analysis (Aljehany & Bennett 2019); point-of-view clips had larger to very large effects (Wertalik et al. 2025); short clips per step beat one long video (Cannella-Malone et al. 2006); video on phones works (Stierle et al. 2023) | Filming, captions and licenses take time. The video slot exists in every step already |
| Photos of each person's own microwave and devices, taken once at setup (no people in them). The AI reads the button names from the photo, so the steps use that microwave's own words ("press Time Cook"); a person checks it first | A picture of a different device can confuse someone who reads it literally; staff said a new microwave is hard | General case teaching (Smith 1995) | Needs a safe way to take and store photos |
| Extra detail saved for each person (which hand, which way to turn), which residents can also ask for themselves | Some people need much more detail (First Place, Nov 4) | The AI split already does this, with staff approval | Right now, when staff approve extra detail for one step, every resident doing that task sees it, not just the person who needed it |
| Practice tasks for base skills (like opening different packages), linked from the skill card | Skill cards are short; some people need more practice | Same task analysis and fading method as the main tasks | Each one needs writing and testing |
| Retrieval augmented generation (RAG) for the "I'm stuck" helper: before the model answers, the app searches only our own approved content (task steps, skill cards, and notes staff have written and approved) and gives the model the few best matching pieces. The reply can then point to the exact step or skill card it used | Today the helper sees the whole task text and nothing else. As we add more tasks, skill cards and staff notes, the prompt gets too long and the model may miss the right piece. Searching first keeps answers grounded in content a person has already approved, and lets staff fix an answer by editing one note instead of changing a prompt | RAG is a standard way to ground a model in a trusted source and reduce made up answers. It fits our design: a person already approves everything the AI writes, and the model would only get approved text | Needs a larger library of approved content first. It also needs tests that retrieval never brings back anything that breaks our safety rules (food, money, time, buying), and a privacy check. The rules in code before and after the model would stay exactly as they are |
| AI drafts a whole new task from its name (steps, small steps, cautions, base skills and skill cards) for staff to review and approve | So Carryover works for tasks we never wrote by hand | The AI split already works this way, with staff approval | Needs testing for accuracy and safety first |
| More tasks, and tasks that connect to each other. For example, if someone reaches "Pay" in the online buying task and has no card saved, the step can open a separate "Add a card" task, then bring them back to where they left off | Real tasks depend on other tasks | Same task analysis method (Rowe et al. 2011; Barnard-Brak et al. 2023) | Each task needs research, steps and testing |
| More money tasks: budget a week's shopping, compare prices, check a receipt with a support person | Buying is only one part of handling money | CAN-B decision steps (Adams et al. 2026) | Money is high risk. The same guardrails apply: never connect to a bank, read a balance, or say what to buy |
| Voice: read-aloud and a voice helper (a microphone that presses the buttons by voice) are built. Next: spoken answers to check questions, a speech model that understands more wording (only with the person's consent), and paid natural voices | Some people prefer listening or talking, and some find tapping hard | Read-aloud is optional; video prompting worked with or without voice-over (Dawson et al. 2023) | Needs testing with residents; voice data needs a privacy plan; paid voices cost money |
| Fuller Game mode: worlds built from the interests people type in, more themes, artwork (free CC0 art, or AI-drawn art made once, reviewed and saved, never live), co-designed with residents | Staff said a formal app may not get used | Special interests linked to wellbeing (Grove et al. 2018); a gamified app was used longer (Lee et al. 2022) | Evidence with autistic adults is thin, so test in the pilot first. Today there are three fixed worlds (sky, animals, space); worlds from typed interests are not built |

### Phase 4: Beyond First Place

| What | Why it's needed | Why it might work | Why not now |
| --- | --- | --- | --- |
| A separate staff tool with its own login, where a support person reviews AI-written steps and sees the sticking points summary, only if the resident chooses to share | Staff pages should never be part of the resident's app. In the demo there is no login, and the Staff page does not yet check the resident's sharing setting | Keeps the resident in control (Wehmeyer & Abery 2013) | Needs accounts and secure storage |
| A plain-language "How Carryover works" page for residents | People should know what the app does with their taps and photos | NIST AI Risk Management Framework (transparency) | Best written with residents in the pilot |
| Offer Carryover beyond First Place: first to the other communities that license First Place's Learn4Independence curriculum, then to group homes, day programs and school transition programs, and to adults who live on their own and use it with a job coach or family member. Later, other neurodivergent adults, such as people with ADHD or intellectual disability, if testing shows it helps them | First Place staff told us about 75 residents live there; many more people could use it | The same teaching methods are used across these groups (Hume et al. 2021; Stierle et al. 2023) | Needs pilot evidence, testing with each new group, and a way to share task files without copying published assessments such as AFLS |

## How we'll know it's working

- People need less help on a step over the weeks, and help comes back when they struggle.
- Skills last after a long break.
- Residents say it feels like help, not like being watched.
- Staff agree with the help level the app chose.
- Zero wrong "safe" answers from the AI on dishes and food.
