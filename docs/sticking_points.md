# Sticking points

Where people are likely to get stuck in each task, why, and what the app does about it. Based on research, on trying the tasks ourselves, and on comparing different devices (general case analysis, Smith 1995).

## Why people get stuck (research)

Each detect code in `backend/logic/detect.py` matches a difference in executive function (the skills for planning, remembering, starting and switching; Hill 2004a). Full references are in `docs/sources.md`.

| detect code | Why it happens | What the app does | Source |
| --- | --- | --- | --- |
| `cant_start` | Trouble starting a task, even when the person wants to ("autistic inertia"). A cue or a first step helps | Start push: one small first step | Buckle et al. 2021; Carmo et al. 2015, 2017 |
| `missing_step` | Trouble remembering a step or remembering to do something later (working memory, prospective memory) | Check questions; "stir halfway" reminder | Buckle et al. 2021; Hill 2004a |
| `stuck_at_step` | Trouble switching when a button, screen or store looks different from usual (flexibility) | Tips that name other button words; general case steps | Hill 2004a; Yon-Hernández et al. 2023; Smith 1995 |
| `rusty_after_gap` | A learned skill can fade after a break | More help after a long gap | Richling et al. 2019; Fuller & Fienup 2018 |

Executive function differences are broad and fairly stable in autism (Demetriou et al. 2018) and predict daily living skills in autistic adults (Yon-Hernández et al. 2023). Findings are mixed and people differ a lot (Hill 2004b), which is why Carryover learns each person's sticking points instead of assuming them.

## How we found them

- **Tried the task ourselves** on a real microwave (Nov 4). A fluent run took about **1:30 of active steps** (not counting heating time), so about 15–20 seconds per active step.
- **Compared two real microwaves** plus the microwaves described in Smith (1995) and Sigafoos et al. (2005).
- **Read published microwave task analyses** (Smith 1995, Table 4; Sigafoos et al. 2005, Table II).

## Heat a meal

| Sticking point | What we saw or read | Which step | What the app does |
| --- | --- | --- | --- |
| Too many buttons | Panels have 15–25 buttons; most aren't needed. Sigafoos et al. covered every button except the two needed | 4 | Small steps name only Cook Time, numbers, Start. Tip: ignore the other buttons |
| Timer looks like it cooks | Both microwaves have a Timer button that counts down without heating. Pressing it gives a countdown with no heat | 4 | Tip: "Timer does not heat food. Use Cook Time." Small step: check the time is counting down |
| Button names differ | Cook Time vs Time Cook; Cancel vs Clear/Off; +30 Sec vs Add 30 Sec (Smith also lists Clear, End) | 4 | Steps say both names ("Cook Time (it may say Time Cook)") |
| Number buttons can start cooking | On microwaves with "Express Cook," pressing 1–6 alone usually starts cooking at once | 4 | Always press Cook Time first |
| Presets and Delay Start | Popcorn, Reheat, Pizza, Delay Start etc. each lead to different next steps by model | 4 | Tip: ignore them |
| Controls locked | A lock (e.g. hold Cancel 3 s) makes buttons stop working; looks broken | 4 | Tip: unlock, or ask staff |
| No light inside | Light may not come on; the light button on over-the-range models is for the stove below | 4 | Small step: check the time is counting down, listen for a hum |
| Packaging | Box/sleeve, tray vs dish, film to peel or poke. Sigafoos: a participant never removed the wrapper before training | 1–2 | "Read the package" step; small steps for sleeve, tray, film |
| Wrong time | Setting more than the package time burned food (Smith) | 1, 4 | Use the exact package time; Cancel to fix a wrong time |
| Stir or not | Not every food needs stirring; package decides; leftovers do | 5 | "Stir halfway, if the package says so"; tip for leftovers |
| Pausing | Our microwave has no Stop button; opening the door pauses it | 5 | "Open the door. It pauses the microwave" |
| Door | Pull handle vs door button | 3 | "Pull the handle or press the door button" |
| Repeating beeps | Some microwaves keep beeping until the door is opened | 6 | Tip: "It may keep beeping until you open the door. That's OK" |
| Steam and hot spots | Steam under the cover; hot dish; food hotter in some spots | 5–7 | CAUTION line on steps 5–7, always shown at every help level, no tap needed (Jones et al. 1997) |
| Not hot in the middle | Food not done needs more time (Smith) | 7 | Tip: +30 Sec and check again; 165°F (USDA) |
| Food already inside | Listed as a possible error by Smith | 3 | "Check nothing else is inside" |
| How much fits | Dish too big to turn | 2 | Tip: one dish that fits and can turn freely |
| Needs a break | Not everyone wants to do a task in one go | Any | "Take a break" button: clock stops, place is saved, never counts as struggling. After 2+ hours, a food safety note (USDA 2-hour rule) |
| Missing a base skill | First Place (Nov 4): clear steps don't help if someone can't yet do what a step assumes (read "2 min 30 sec", find a button by its name, open a package) | 1, 2, 4, 5, 6 | `base_skills` per step; "Can you do these?" the first time; skill card before the step if "Not sure" or stuck at Most help 2 sessions |
| A new or different microwave | First Place (Nov 4): residents struggle with a device they haven't used, or one that differs from the one they learned on | All | `first_time_question`: "Is this a microwave you've used before?" No: start at Most help. Roadmap: photos of their own microwave |
| Starting at all (opening the fridge, packages) | General skills; differ by home | Start | Start push only. Roadmap: ask why they're stuck and link to a short task for that skill |

## General case analysis: how microwaves differ

| Step | Our microwave | Second microwave | Smith (1995) | Sigafoos et al. (2005) |
| --- | --- | --- | --- | --- |
| Open door | Pull handle | Push button | Varies | Pull handle |
| Set time | Cook Time → numbers | Time Cook → numbers (numbers alone = Express Cook) | Push button or turn dial | POPCORN preset |
| Start | START | START/PAUSE | START, POWER or ON | START |
| Add time | +30 Sec | Add 30 Sec. | — | — |
| Cancel | CANCEL | CLEAR/OFF | Clear, End | — |
| Timer trap | Timer Set/Off | Timer On/Off | — | — |
| Lock | Hold Cancel 3 s (labeled) | Not labeled | — | — |
| Pause | Open door | Open door or START/PAUSE | Turn oven off to stir | — |
| Done signal | Beep (repeats) | Beep | Bell / light | Bell |

## Buy something

> **Online run (Nov 4, food delivery app):** choosing took about **5 minutes** when sure what to order, and can take **hours** when unsure. Checkout took about **2 minutes**; checking the address (apartment number) and the payment took longest, and the tip needed a decision. Adding a card would take much longer (separate task). Internet problems can stall checkout. These set the online long pauses: Decide steps 4–5 = 300 s, "Check the address, then pay" = 120 s.
>
> **In store:** not timed. Decide steps 4–5 use 300 s (from our online run, assumed similar in store); "Do you need it?" 180 s (guess); paying 60 s (ours: allows for PIN, Debit/Credit, tip and cash-back screens). Waiting in line is a waiting step and never counts as struggling. All to be checked in a pilot. Steps are based on Rowe (2011) Appendices C and G and the LSU task analysis.

| Sticking point | What we saw | Which step | What the app does |
| --- | --- | --- | --- |
| Comparing options needs math | Same item in different sizes, or different items for the same purpose | 4 | Compare total price of two options only. Tip: price per ounce on the tag or listing; photo question can read prices. The app never says which to buy |
| Usual (safe) foods | Many people buy the same items; comparing every time isn't needed | 4 | Tip: "Buying your usual item? You can skip this step" |
| Delivery or pickup | Pickup needs a way to get there and the store open; delivery needs someone home | 7 (online) | Small steps for each; "Choose pickup only if you already know how to get there" (no maps: transit is out of scope) |
| Delivery speed and time | Priority, standard, scheduled | 7 (online) | Tip: priority usually costs more |
| Talking to the driver | Driver may call or knock | 7 (online) | Tip: "Leave at door" option |
| Fees, tax, tip | The total is more than the item price | 8 (online), 7 (in store) | Small steps list each part of the total |
| Promotions | Searching for codes can take a long time | 8 (online) | Tip only: enter a code if you have one; don't search long |
| Wrong address | Saved address may be old | 9 (online) | Small step: check the delivery address |
| Gift cards | Different place to enter; may not cover the total | 8 (in store), 9 (online) | Tip |
| No card saved | Adding a card means typing card numbers; risk of scams | 9 (online) | Separate "Add a card" task (roadmap), on their own or with their support person. The app never sees or stores card numbers |
| Finding the item in a store | Aisles, signs, items moved | Before step 1 (in store) | Tip on step 1: look at the aisle signs or ask a store worker. Roadmap: linked task "Find an item in a store" |
| Waiting in line | Line can be long; cashier may be busy | 6 (in store) | Marked as a waiting step, so long waits never count as struggling. Tip for self-checkout |
| Finding things in the app | Every app is different (restaurant, menu, buttons) | — | Out of scope for these steps: the "I'm stuck" helper (type, speak or photo) can help; roadmap: linked tasks for common apps |
| Rides (cab stops) | A transit task | — | Out of scope |
| Can't decide | Choosing can take hours when unsure | 5 | Tip: choose your usual, or leave it for now. Long pause 300 s online so thinking isn't counted as struggling |
| Address details | Apartment or unit number missing or old | 9 (online) | Small step: check the apartment or unit number |
| Tip amount | A decision at checkout | 8 (online) | Small step: choose an amount you're OK with. The app never suggests how much |
| Internet problems | Page stalls or errors at checkout | 9 (online) | Tip: don't press Place Order again; check orders or email first, so you don't pay twice |
| Card declined or reader error | Payment doesn't go through | 8 (in store) | Tip: try once more, or ask the cashier |
| Missing a base skill (buying) | Reading a price, comparing prices, reading the total, tapping or inserting a card, paying with a phone, typing an address | 1, 4, 7–9 | Skill cards: read_price, compare_two_prices, read_total_on_screen, tap_or_insert_card, pay_with_phone, type_address |
| New card reader or app | Readers and apps all look different | Pay steps | `first_time_question` per buying task; No: start at Most help |
| Pictures that don't match | A picture of a different device or a different color can confuse someone who reads it literally | All | Roadmap: photos of the person's own microwave, taken once at setup (no people). Until then, pictures show the action, with a note "Your microwave may look different" on device pictures. Plain adult style, nothing childish |
