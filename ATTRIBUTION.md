# Attribution

## Role A

**Libraries:** none beyond the Python standard library (statistics, datetime,
json, pathlib). Tests use pytest, which is already in requirements.txt.

**Prior work this builds on:**
- Task steps: our own task analyses. The method follows published task
  analyses for microwave use (Jones et al., 1997) and buying in a store
  (Rowe, 2011). The Decide part of buying draws on the CAN-B strategy
  (Adams et al., 2025). Wording is our own. No AFLS text was copied.
- Safety content: the microwave "never" list and the 2-hour food rule come
  from USDA and FDA guidance (plastic bags: Clemson HGIC, based on USDA).
  Placing safety facts inside the steps follows Jones et al. (1997).
- Detection codes: the codes and their thresholds are the team's own
  choices. Research supports the idea behind each: skills can fade after a
  break (Richling et al., 2019; Fuller & Fienup, 2018); executive function
  differences affect remembering and starting steps (Hill, 2004;
  Demetriou et al., 2018). The research does not give our exact numbers.
- Partner input: base skills, the always-shown caution line, pictures, the
  different-microwave question and Game mode came from our Nov 3 and Nov 4
  meetings with First Place AZ staff (docs/partner_research.md).
- UI rules: W3C COGA guidance and the papers listed in docs/ui_guidelines.md.
- Full citations for everything above are in docs/sources.md.

**Pictures:** the 16 step pictures in frontend/public/img/ are simple
diagrams made from basic shapes by tools/make_pictures.py, a script written
with AI help. No outside images or photos. They are placeholders; real
photos or short videos are on the roadmap.

**AI assistance:** I used Claude (Anthropic) to help research sources, draft
the task step wording, skill cards and docs, and write detect.py,
test_detect.py and make_pictures.py. I decided the rules, the step content
and the detection logic, reviewed every line, and can explain what each
file does and why.

## Role B

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
