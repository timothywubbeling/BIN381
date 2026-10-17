# Milestone 4 presentation — Person B's slides (5, 6, 7)

Rudi Jan du Plessis · Group P1 · for the 10-slide executive deck

The audience is a decision-maker, not a data scientist. One message per slide, and the message is
the slide title. Every number below comes from `data/evaluation/` and is verified by
`report/M4/check_numbers.py`.

Timing: roughly 1 minute on slide 5, 1 minute on slide 6, 2–3 minutes on the slide 7 demo.

---

## Slide 5 — "The screen finds 4 in 5 at-risk households, and refers 3 in 5"

**On the slide** — four big numbers, then one chart.

| | |
|---|---|
| **80.7%** | of at-risk households found |
| **41.9%** | of referrals are genuinely at risk |
| **58.9%** | of households sent for follow-up |
| **0.736** | ROC-AUC (0.5 would be a coin flip) |

Chart: the threshold trade-off curve — recall and share-referred against threshold, with a marker
at 0.24. (Screenshot the what-if panel from the dashboard, or plot the table in
`docs/powerbi_m4_person_b_pages.md` §5.)

Footer line: *Measured once on a held-out test set of 6,279 households.*

**Speaker notes**

> We chose the threshold before we looked at the test data, using a rule we agreed with the
> problem in mind: find at least 80% of at-risk households, at the fewest referrals. That lands on
> 0.24. On data the model had never seen it finds 80.7% of at-risk households, and 85.7% of the
> severely food insecure — the ones we least want to miss.
>
> The cost is on the right of that curve. Four in ten referrals are households that turn out to be
> food secure, and we send three in five households for follow-up. That is a real operational
> load, and it is a dial, not a fact: push the threshold up and you visit fewer households but
> miss more. We have built that dial into the dashboard so programme managers can set it against
> the capacity they actually have.
>
> One thing worth saying plainly: a random forest scored very slightly better, by about 0.009 AUC.
> We did not take it. This tool has to justify every referral to an official, and a logistic
> regression gives one interpretable number per factor. We traded a fraction of a point of
> accuracy for an explanation.

---

## Slide 6 — "A recent fall in income is the warning sign — but the screen is blind to the comfortable poor"

**On the slide** — two halves, one message each.

*Left: what drives risk* (horizontal bars, AUC drop)

| Driver | Importance |
|---|---|
| Income change vs a year ago | 0.082 |
| Income per person | 0.033 |
| Number of grant recipients | 0.029 |
| Household income | 0.021 |

> 58.3% of households whose income fell sharply are food insecure, against 18–21% mid-scale.

*Right: where the screen is weakest* (bars against the 80.7% line)

| Group | Recall |
|---|---|
| Earning < R2,500 | 94.0% |
| **Earning > R11,500** | **39.2%** |
| Receives grants | 88.0% |
| **No grants** | **61.7%** |

**Speaker notes**

> The strongest single signal is not income level — it is income *change*. Whether a household is
> worse off than a year ago matters more than any other answer we collect, by a factor of about
> two and a half. That is a cheap question, and it is actionable: it can be asked at intake, in one
> sentence, before anything else.
>
> Two findings surprised us. Grant-receiving households are *more* food insecure, not less —
> 37.6% against 20.6%. That is not evidence that grants cause harm; grants are means-tested, so
> they mark households that were already poor. We cannot separate targeting from effect in a single
> survey wave, and we say so in the report rather than hiding it.
>
> The second is the right-hand side of this slide, and it is the honest limitation of the tool. The
> screen finds 94% of at-risk households at the bottom of the income scale and 39% at the top. It
> is weakest exactly where food insecurity is least expected. So a "lower risk" result is not
> clearance — it is the absence of a flag, and we keep self-referral channels open because of it.

---

## Slide 7 — "Dashboard demo: setting the threshold against real capacity"

**On the slide** — a screenshot of the "How well the screen works" page as the backup, and three
bullet lines naming what you are about to show. Keep the live dashboard already open on a second
window before you start.

- Where the need is, by province and settlement type
- How well the screen works — and what a different threshold would cost
- Which households it misses

**Demo script (2–3 minutes, do not improvise)**

1. **Open on the landing page.** "Six decision questions. Every page answers one of them —
   that was the design rule."
2. **Go to 'How well the screen works'.** Point at the four cards. "These are the numbers from
   slide 5, live from the final dataset."
3. **Move the threshold slicer from 0.24 to 0.30.** "Recall drops from 80.7% to 67.8%, referrals
   drop from 59% to 44%. That is 150 fewer households per thousand to visit, and about one in eight
   at-risk households newly missed. This is the conversation we want programme managers to have
   with us, and it is why the dial is in the tool rather than in a footnote."
4. **Put it back to 0.24.**
5. **Go to 'Who the screen misses'.** Cycle the `variable` slicer: Monthly income → Grant receipt
   → Province. "Same chart, five different cuts. The band is our agreed 10-point tolerance. Income
   above R11,500 sits far outside it, and that is a documented limitation, not a surprise."
6. **Go to 'What drives risk'.** "Income change at the top, and the odds-ratio table underneath
   with confidence intervals, because a direction without an interval is not evidence."
7. **Hand to Timothy** for the Shiny app on slide 8.

**If the live demo fails:** the screenshots on slides 5–7 carry the same three numbers. Say
"I'll use the screenshots" and keep going — do not debug on stage.

---

## Questions Person B should expect

**Why 0.24, and is referring 58.9% of households actually useful at 41.9% precision?**
> The rule was set before evaluation: at least 80% recall at the fewest referrals. Precision of
> 41.9% is low because only 30.6% of households are at risk to begin with — so a referral is about
> 1.4 times as likely to find an at-risk household as visiting at random. Whether 59% is workable is a capacity
> question, not a statistical one, which is why the threshold is a slicer in the dashboard. If the
> institute can visit 30% of households, 0.30 is the right setting and we lose 13 points of recall
> knowingly.

**Why is the final model binary when the project began with three tiers?**
> The middle tier is not separable with these eight predictors. No three-tier model recalls more
> than 3.2% of mildly-to-moderately insecure households, and the best-ranking one (the forest)
> manages 0.3% — effectively none — even with class weights forcing it to look. Three-tier
> ROC-AUC was about 0.67. A screen that answers "at risk or not" is
> something an official can act on; a severity grade we cannot actually measure is not.

**Why does recall drop to 39% above R11,500 and 62% for no-grant households?**
> The model leans on income and grant receipt, so households that look comfortable on paper score
> low even when they are food insecure. Officials should not read a low score as clearance for
> those groups. The report recommends a standing monthly audit sample of lower-risk households in
> exactly those two groups, plus keeping self-referral open.

**How did you stop the model learning from the food-insecurity items it was meant to predict?**
> Person A excluded every D07 food-insecurity item from the predictor set and asserted it in code;
> I re-checked it independently in the evaluation notebook. The eight predictors are income,
> income change, income per person, household size, grant recipients, electricity, settlement type
> and toilet type — none of them is part of the target.

**What does the dashboard let a decision-maker do that the Shiny app does not?**
> The app scores one household or a batch; it answers "what about this household?". The dashboard
> answers "where do we send the budget, and what does a different threshold cost?" — population
> questions, with the survey weights applied. Different questions, different tools.
