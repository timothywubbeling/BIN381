# Presenting — Timothy (Person C), slides 8 to 10

Everything here is checked against `data/evaluation/`, `data/powerbi/` and the final report.
Your slides carry these notes in the speaker-notes pane too.

---

## Before you start

- [ ] **App running** (see below) with the *Score one household* tab open.
- [ ] **Dashboard open** in a second window, on *How well the screen works*, threshold at **0.24**.
- [ ] `tests/messy_households.csv` already navigated to in a file dialog.
- [ ] Screenshots on the slides as backup — if a demo dies, say *"I'll use the screenshots"* and
      keep going. Do not debug on stage.
- [ ] No household identifier visible anywhere.

### Starting the Shiny app

1. Open **`BIN381-P1.Rproj`** in RStudio. This activates `renv` automatically — you'll see it
   print the project library on load.
2. First time on a machine only:
   ```r
   renv::restore()
   ```
3. From the console, at the project root:
   ```r
   shiny::runApp("app")
   ```
4. It opens in a browser window. Check the form appears on *Score one household*.

**Gotcha:** the app loads the model from `../models/final_workflow.rds`, a path relative to
`app/`. Launch it with `runApp("app")` from the project root, or with RStudio's **Run App** button
while `app/app.R` is open. Sourcing `app.R` from somewhere else fails on the model path.

Quick confidence check before the room fills: upload `tests/messy_households.csv` on *Batch
upload* and confirm the issues table lists the sentinel codes, the unseen code, the text value and
the duplicate ID.

---

## Slide 8 — "An official can score one household in about ten seconds"

**The message:** this is the part a field officer actually touches, and it abstains rather than
guesses.

**Demo, in this order — do not improvise:**

1. **One household.** Type the rural example: income *much lower* than a year ago, traditional/
   tribal, 6 people, R1,200 a month, no electricity, 2 grant recipients, pit latrine. Score it.
   Point at the three contributing factors, and at the words: **"Higher risk: refer for review"**,
   never "food insecure".
2. **The contrast.** Change income to R30,000 and settlement to urban, re-score, watch the
   probability drop. That is the whole model in one gesture.
3. **The batch.** Upload `tests/messy_households.csv` — 13 deliberately broken rows. Scroll the
   issues table: sentinel codes recoded, an impossible household size rejected, a duplicate
   identifier flagged, rows missing too much left **unscored rather than guessed**.
4. **Land on the limits page**, not on a score. Read the two lines about which households the
   screen misses.

**What to say:** seven questions, short enough to ask at a door, and the answer comes back with
the three things that drove it — so the officer can say why a household was referred, and a
supervisor can disagree with it. A screening tool that guesses when it does not know is worse than
one that abstains.

**The line that ties back to Rudi:** all 6,279 test households were pushed back through the app's
own code path and compared with the saved evaluation predictions. **Largest difference: zero.**

---

## Slide 9 — "Five actions, each with the caution attached"

One line each, with the number and who acts. Do not read the table out.

| Say this | The number |
|---|---|
| Use it for outreach triage, and resource it for the referral rate it actually produces | refers **58.9%**; **41.9%** of referrals are at risk |
| Ask about income change at intake — the cheapest thing on the list | AUC drop **0.082**, about 2.5× the next variable |
| Coordinate relief with the grant registers | **37.6%** of grant households at risk vs **20.6%** without |
| Fund the four highest-risk provinces first | EC **43.0%**, NC **40.5%**, NW **37.1%**, MP **35.5%**, national **28.3%** |
| Audit "lower risk" households where the screen is weakest | recall **39.2%** above R11,500, **61.7%** with no grants |

**The three things to say out loud:**

- The first is **a budget decision disguised as a technical one**. Three households in five get
  referred and four in ten of those are food secure. That is the cost of finding four in five of
  the households at risk. Size capacity against that rate, or move the threshold knowingly — the
  dashboard lets you.
- The grant finding is **targeting, not harm**. Grants are means-tested, so they mark households
  that were already poor. Nothing here is a case for withdrawing one.
- The last one exists **because of what we found about ourselves**. We did not patch the gap with
  a lower threshold for richer households — that means treating people differently by income on
  the basis of a proxy. We publish the gap and ask for a monthly audit instead.

**Close on:** a screening aid; an official reviews every referral; a low score is never clearance.

---

## Slide 10 — "What this cannot tell you, and what we would do next"

**Say these yourself before anyone asks.**

- AUC **0.736** is moderate. Better than chance by a useful margin, nowhere near good enough to
  decide anything alone — which is exactly why a person stays in the loop.
- **58.1%** of referrals are not food insecure; **19.3%** of at-risk households are missed.
- The deeper limit is **the target**. We never observed whether a household went without food. We
  built a proxy from eight survey answers and predicted it from seven others about the same
  household at the same moment. That tells you who *looks like* the households that report hunger.
  It cannot tell you why, or what would change if you intervened.
- **No external validation**, and recall is weakest where risk is least expected.

**Next, in order of value:** capture follow-up outcomes so the next model trains on what officials
actually found; add a second survey wave for within-household change; bring in per-person income,
employment, debt and local food prices; re-validate on each new release.

**Final line:** a cheap, interpretable, monitored triage aid that finds four in five at-risk
households **and knows which ones it misses**.

---

## Questions you may get

These are the seven in the team guideline plus the ones your own sections invite.

**1. Why binary when the project began with three tiers?**
The middle tier is not separable with these eight predictors — no three-tier model recalls more
than 3.2% of mildly-to-moderately insecure households, and the best-ranking one managed 0.3%.
Three-tier CV ROC-AUC was about 0.67. We wrote the fallback down in Milestone 2 *before* testing,
so we switched on a rule rather than on a result. The app also needs one probability per household.

**2. Why 0.24, and is referring 58.9% useful at 41.9% precision?**
The rule was fixed before evaluation: at least 80% recall at the fewest referrals. Precision is
41.9% because only 30.6% of households are at risk to begin with — a referral is about 1.4 times
as likely to find an at-risk household as visiting at random. Whether 59% is workable is a capacity
question, not a statistical one, which is why the threshold is a slicer. At 0.30 you visit 43.8%
and lose 13 points of recall, knowingly.

**3. Why does recall drop above R11,500 and for no-grant households, and what should officials do?**
The model leans on income and grant receipt, so households that look comfortable on paper score
low: 39.2% and 61.7% recall. Officials must not read a low score as clearance for those groups.
The report recommends a monthly audit sample of lower-risk households in exactly those two groups,
and self-referral stays open.

**4. How did you stop the model learning from the items it was meant to predict?**
The target counts eight food-access items, so those eight plus eight related columns — two older
hunger questions, four "number of days" follow-ups, the FI Score and its answered-items count —
are excluded from the predictors, and the notebook *asserts* it and stops if one appears. Rudi
re-checked it independently in evaluation, and the app drops those columns from any upload.

**5. How would you know it has drifted, and when would you retrain or retire it?** *(your section)*
Monitoring is baselined on the test set: PSI 0.10–0.25 watch and above 0.25 act; missing income
above 5%; unscored rows above 5%; share referred moving more than 10 points from 58.9%; recall
below 0.707; calibration clearly worse than Brier 0.180; any subgroup gap above 10 points.
**Retrain** on any alert, on a change to one of the eight predictor items, or annually at each
release. **Retire** if recall for any group above 500 households falls below 0.65.
The sneaky one: income enters in rands, so **inflation alone makes it under-refer** — a simulated
25% nominal income rise drops the referral rate from 59.8% to 51.9% with no change in real need.
That is the most likely way this tool quietly stops working.

**6. What does the dashboard let a decision-maker do that the app does not?** *(your section)*
The app answers "what about this household?" — one household or a batch, with the three reasons.
The dashboard answers population questions with the survey weights applied: where to send the
budget, which groups get missed, and what a different threshold costs. Different questions,
different tools.

**7. Which decision did you change, and what evidence changed it?**
Three. The "256 to 272 duplicate household IDs" from Milestone 1 were 18-digit IDs read as
numbers, not duplicates. The three-tier target became a binary screen when the middle tier proved
unseparable. And mine: I rebuilt my Milestone 1 dashboard pages on the integrated data instead of
bolting them on, because they read the raw files and would have put pre-cleaning numbers beside
final ones — and I dropped a map I was proud of, which was bound to a United States shape file and
had never drawn South African provinces.

**8. What happens if someone uploads real household IDs?** *(likely, on your demo)*
They stay in the file and never leave the machine. Uploads are processed in memory and not written
to disk, identifiers are never returned in the download, and the monitoring log keeps totals only —
row counts and distributions, never a household.

**9. Is the screen fair?**
Equal opportunity was the criterion, and recall is measured per subgroup. The gaps are published
in section 4 and on the dashboard rather than patched, because the obvious patch — a lower
threshold for higher-income households — means treating people differently by income on the basis
of a proxy.

**10. How do you know the dashboard agrees with the analysis?** *(if the Reconciliation page comes up)*
It recomputes each figure from the household rows and subtracts the R output from itself in front
of the user: 0.0 for all nine provinces. It is also how we caught the what-if slider disagreeing
with the report by three tenths of a point, because a table built by adding 0.01 at a time stored
0.24 as slightly more than 0.24 and dropped the 26 households sitting exactly on it.

---

## If something breaks

- **App won't start:** check you opened the `.Rproj` (for `renv`) and used `runApp("app")` from the
  project root. Fall back to the three screenshots on slide 8 — they show the same three things.
- **Dashboard won't open:** it needs a short folder path; `C:\BIN381\` is safe, a deep OneDrive
  path is not. Rudi's pre-merge `.pbix` is the backup.
- **A number on screen disagrees with a slide:** say so, and say which one is authoritative —
  `data/evaluation/` is, and `check_numbers.py` asserts it. Do not argue with the room.
