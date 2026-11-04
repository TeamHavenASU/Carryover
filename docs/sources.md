# Sources

What each source is used for in Carryover. All task steps are written in our own words. Nothing is copied from AFLS.

Labels: **Research** = published study. **Official** = government or company guidance. **Ours** = our own choice (reason given in the docs), to be tested in a pilot.

## Fading rules

| Source | Used for |
| --- | --- |
| MacDuff, G. S., Krantz, P. J., & McClannahan, L. E. (2001). Prompts and prompt-fading strategies for people with autism. In *Making a Difference: Behavioral Intervention for Autism*. | Rule 1 (start light), Rule 2 (fade help as soon as possible), Rule 4 (go back one level after errors), Rule 6 (wait before a prompt / time delay) |

## Task steps

| Source | Used for |
| --- | --- |
| Adams et al. (2025), *Journal of Autism and Developmental Disorders*. CAN-B (Cost, Afford, Need, Best). **TODO: full citation** | Buying, Part A (Decide), steps 1–4 |
| Rowe, D. A. (2011). *The effects of classroom simulation using static picture prompts to teach students with disabilities to make purchases with a debit card and track their expenses* (Doctoral dissertation, UNC Charlotte). Appendix G: Task analysis. https://ninercommons.charlotte.edu/record/3458/files/Rowe_uncc_0694D_10219.pdf | Buying, Part B in store (card). **TODO: compare step 8 with Appendix G** |
| Rowe, D. A., & Test, D. W. (2012). Effects of simulation to teach students with disabilities basic finance skills. *Remedial and Special Education*, 34(4), 237–248. https://works.bepress.com/dawn-rowe/13/ | 20-step debit card task analysis; supports Part B in store (card) |
| LSU Human Development Center (LASARD). Using a Debit Card task analysis. https://hdc.lsuhsc.edu/lasard/News/2025-04-09_independence-task-analysis.aspx | Buying, Part B in store (card). **TODO: compare step 8** |
| More (2018), University of South Florida. Debit card steps. **TODO: full citation** | Buying, Part B in store (card) |
| Smith, V. E. (1995). *General case principle applied to microwave cooking: Can severely handicapped students generalize the skills they learn in the classroom?* (Master's thesis, Rowan College of New Jersey). https://rdw.rowan.edu/etd/2295 | Heat a meal: 12-step push-button task analysis (Table 4) close to ours (read the package, follow its directions for taking food out of the packaging, close the door tightly, set the time, press Start, stop to stir if directed, pot holders, let it stand). General case analysis (Table 2): how microwaves differ and likely errors (food already inside, food not done so add time). Students burned food by setting more than the package time; one student at home added time until the food was done. Button words differ by microwave (Time Cook, Clear, End). Basis for our general case approach and step-1 "use the exact time" |
| Sigafoos, J., O'Reilly, M., Cannella, H., Upadhyaya, M., Edrisinha, C., Lancioni, G. E., et al. (2005). Computer-presented video prompting for teaching microwave oven use to three adults with developmental disabilities. *Journal of Behavioral Education*, 14(3), 189–201. https://doi.org/10.1007/s10864-005-6297-2 | Heat a meal: 10-step popcorn task analysis (Table II). They covered every button except POPCORN and START with a template, which supports our "ignore the other buttons" tip. A participant never removed the wrapper before training (supports the packaging step). A bell signals the end (step 6). The trainer waited 30 s before helping on a step (compare with our 45 s long pause) |
| Jones, G. Y., et al. (1997). Teaching microwave skills to adults with disabilities: Acquisition of nutrition and safety facts presented as nontargeted information. *Journal of Developmental and Physical Disabilities*, 9(1), 59–78. https://doi.org/10.1023/A:1024944811896 | Least-to-most prompting taught microwave skills; adults also learned safety facts placed inside the prompts and feedback. Supports putting safety notes (steam, hot dish, hot spots) inside small steps. **TODO: second author's name** |
| Barnard-Brak et al. (2023), *Research in Developmental Disabilities*. Task analysis steps and readability. | About 7 steps or fewer per task, about 7th-grade reading level. Why buying is split into Decide + Pay |

## Safety and payment guidance

| Source | Used for |
| --- | --- |
| USDA FSIS. Cooking with Microwave Ovens. https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/cooking-microwave-ovens | Heat a meal steps 1, 2, 5, 6, 7; the "never put in" list; 165°F |
| USDA FSIS. How Temperatures Affect Food. https://webarchive.library.unt.edu/web/20130216165457/http:/www.fsis.usda.gov/PDF/How_Temperatures_Affect_Food.pdf | 2-hour rule: never leave food out of refrigeration over 2 hours (1 hour above 90°F). Used for the break note in heat_meal |
| FDA consumer update: microwave oven safety (2007). https://webarchive.library.unt.edu/web/20080916230938/http://www.fda.gov/consumer/updates/microwave112107.html | Metal and foil, superheated water, damaged doors; step 3 |
| Clemson HGIC. Microwave food safety. https://hgic.clemson.edu/factsheet/microwave-food-safety/ | Plastic grocery bags, thin storage bags |
| Apple Support. Make purchases using Apple Pay. https://support.apple.com/en-mk/102626 | Phone pay, iPhone small steps |
| Google Wallet Help. Tap to pay with your phone. https://support.google.com/wallet/answer/14188457?hl=en | Phone pay, Android small steps |

## AI reliability (photo questions)

| Source | Used for |
| --- | --- |
| Xiong, M., et al. (2024). Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in LLMs. *ICLR 2024*. https://arxiv.org/abs/2306.13063 | AI self-reported confidence is overconfident; asking several times and checking agreement works better. Why we use the label-quote check and "ask 3 times" |
| Li, Y., et al. (2023). Evaluating object hallucination in large vision-language models. *EMNLP 2023*. https://aclanthology.org/2023.emnlp-main.20/ | Vision AI can "see" things that aren't there. Why the AI never says "safe" from how a dish looks |
| Geifman, Y., & El-Yaniv, R. (2017). Selective classification for deep neural networks. *NeurIPS 2017*. https://arxiv.org/abs/1705.08500 | Abstain when unsure to keep errors low. Why the AI hands off instead of guessing |

## Audio and video

| Source | Used for |
| --- | --- |
| Kellems, R. O., et al. (2024). Does the voice matter? Impact of voice-over instructions on task acquisition and prompting levels in video prompting. *Journal of Health and Rehabilitation Sciences*, 3(1), 10–20. https://jhrs.almamater.si/jhrs/article/view/90/121 | Read-aloud; video prompting worked with or without voice-over |
| Cannella-Malone, H., Sigafoos, J., O'Reilly, M., et al. (2006). Comparing video prompting to video modeling for teaching daily living skills to six adults with developmental disabilities. | Short clip per step (later feature) works better than one long video |

## Pitch wording

Say "prompt fading," not "ABA."
