# Milestone 4 presentation — Person C's slides (8, 9, 10)

Timothy Wubbeling · Group P1 · for the 10-slide executive deck

The audience is a decision-maker, not a data scientist. One message per slide, and the message is
the slide title. Every number below comes from `data/evaluation/` and `data/powerbi/` and is
verified by `report/M4/check_numbers.py`.

Timing: roughly 2–3 minutes on the slide 8 demo, 1.5 minutes on slide 9, 1 minute on slide 10.
That lands the whole deck at about 12 minutes.

**Before you present:** app already running at `shiny::runApp("app")`, the merged `.pbix` already
open on the performance page with the threshold at 0.24, `tests/messy_households.csv` open in a
file dialog you have already navigated to, and `docs/figures/app_*.png` on the slides as backup.

---

## Slide 8 — "An official can score one household in about ten seconds"

**On the slide** — three screenshots across the top, nothing else but the caption.

| | |
|---|---|
| `app_1_single_household.png` | the form and one scored household |
| `app_2_batch_upload.png` | a batch upload with the issues table |
| `app_3_about_and_limits.png` | the limits page |

Footer line: *Seven questions in. A probability, a recommendation and the three reasons out.*

**The live demo, in this order**

1. **One household.** Type the rural example: income fell sharply, no electricity, six people,
   R1,200 a month, two grant recipients, pit latrine. Score it. Point at the three factors the app
   gives back, and at the words it uses — **"Higher risk: refer for review"**, never
   "food insecure".
2. **The contrast.** Change income to R30,000 and settlement to urban, re-score, and let the
   probability drop. That is the whole model in one gesture.
3. **The batch.** Upload `tests/messy_households.csv` — 13 deliberately broken rows. Scroll the
   issues table: sentinel codes recoded, an impossible household size rejected, a duplicate
   identifier flagged, rows with too much missing left unscored rather than guessed.
4. **The limits page.** Land here, not on a score. Read the two lines about which households the
   screen misses.

**Speaker notes**

> This is the part a field officer actually touches. Seven questions, which is a short enough list
> that it can be asked at a door, and the answer comes back as a probability with the three things
> that drove it — so the officer can say why a household was referred, and a supervisor can
> disagree with it.
>
> The wording is deliberate. It says "higher risk: refer for review", not "food insecure", because
> the tool has not measured whether anyone went hungry. It estimates how likely that is from seven
> proxies, and a human decides what happens next.
>
> Now the messy file. Thirteen rows, every one broken in a different way, and this is the behaviour
> we care most about: where a value is impossible the app refuses to score the row and says why,
> rather than quietly imputing something and returning a confident number. A screening tool that
> guesses when it does not know is worse than one that abstains.
>
> One number ties this back to Rudi's slide: we pushed all 6,279 test households back through this
> app's own code path and compared the output with the saved evaluation predictions. Largest
> difference: zero. The app, the notebook, the dashboard and the report quote one set of numbers,
> and that was checked, not assumed.

**Likely question — "what happens if someone uploads real household IDs?"**
> They stay in the file and never leave the machine. Uploads are processed in memory and are not
> written to disk, identifiers are never returned in the download, and the monitoring log keeps
> totals only — row counts and distributions, never a household.

---

## Slide 9 — "Five actions, each with the caution attached"

**On the slide** — five lines, each a verb and a number. No paragraphs.

| Action | The number behind it | Who acts |
|---|---|---|
| Use it for outreach triage, and resource the referral rate | refers **58.9%** of households; **41.9%** of referrals are at risk | Programme managers |
| Ask about income change over the past year at intake | strongest single predictor, AUC drop **0.082**, about 2.5× the next | Field staff |
| Coordinate relief with the grant registers | **37.6%** of grant-receiving households at risk against **20.6%** without | Social development |
| Fund the four highest-risk provinces first | Eastern Cape **43.0%**, Northern Cape **40.5%**, North West **37.1%**, Mpumalanga **35.5%**, against **28.3%** nationally | Provincial teams |
| Audit "lower risk" households where the screen is weakest | recall **39.2%** above R11,500 and **61.7%** with no grants | Field officers, monthly |

Footer line, in the attention colour: *A screening aid. An official reviews every referral, and a
low score is never clearance.*

**Speaker notes**

> Each of these starts from a number on Rudi's slides, and each has a limit attached, because the
> limits are what make them safe to act on.
>
> The first one is a budget decision disguised as a technical one. At our threshold the tool refers
> about three households in five, and about four in ten of those referrals turn out to be food
> secure. That is the cost of finding four in five of the households that are at risk. Managers
> should size follow-up capacity against that rate before go-live — or move the threshold
> knowingly, which the dashboard lets them do, and accept that they will miss more people.
>
> The second is the cheapest thing on this list. One question about whether income has fallen
> carries more signal than anything else we measured, and it can be asked without the model at all.
>
> The third needs the caution said out loud. Grant-receiving households are at higher risk because
> grants are targeted at poor households. That is a reason to use the grant registers to find
> people quickly. It is not evidence that grants cause food insecurity, and nothing here should be
> read as a case for withdrawing one.
>
> The last one is there because of what we found about ourselves. The screen is weakest for
> households that do not look poor on our seven inputs — higher earners, and households with no
> grants. We chose not to patch that with a different threshold for richer households, because
> that means treating people differently by income on the basis of a proxy. We publish the gap
> instead, and we ask for a monthly audit of low-score households in exactly those groups. Keep
> self-referral open.

---

## Slide 10 — "What this cannot tell you, and what we would do next"

**On the slide** — two columns, four lines each. No chart.

| The limits | What we would do next |
|---|---|
| Moderate discrimination: **ROC-AUC 0.736** | Capture follow-up outcomes, so the next model trains on what was found |
| **58.1%** of referrals are not food insecure; **19.3%** of at-risk households are missed | Add a second survey wave for within-household change |
| A **proxy target** from eight self-reported items, on one cross-sectional wave — association, never cause | Bring in per-person income, employment, debt and local food prices |
| **No external validation**, and recall is weakest where risk is least expected | Re-validate on a new release before extending the threshold to it |

Footer line: *Survey data, not a census. A screening aid, not an eligibility test.*

**Speaker notes**

> We would rather say these ourselves than have them found.
>
> An AUC of 0.736 is moderate. It separates risk better than chance by a useful margin, and it is
> nowhere near good enough to decide anything on its own — which is exactly why the design keeps a
> person in the loop and why we talk about referrals rather than decisions.
>
> The deeper limitation is the target. We never observed whether a household went without food. We
> built a proxy out of eight survey answers and predicted that, from seven other survey answers
> about the same household at the same moment. That tells you who looks like the households that
> report hunger. It does not tell you why, and it cannot tell you what would change if you
> intervened. The reversed grant result is the clearest case: targeting and effect cannot be
> separated in one cross-section.
>
> So the first thing on the right matters most. The moment officials record what they actually
> found when they visited, we can retrain on real outcomes instead of a survey proxy, and we can
> finally measure precision in the field rather than against our own label.
>
> Until then, the honest summary is this: a cheap, interpretable, monitored triage aid that finds
> four in five at-risk households and knows which ones it misses.

---

## Final deck check (Person C owns this)

- [ ] **10 slides or fewer.** Count them. Title slide counts.
- [ ] Every number on a slide appears in the report, and `check_numbers.py` passes.
- [ ] One message per slide, and it is the slide title.
- [ ] Screenshots replaced with the merged dashboard's (`pbi_m4_*.png`), not Rudi's pre-merge
      `pbi_b*.png`.
- [ ] Threshold slicer back at **0.24** in the open `.pbix` before the demo.
- [ ] No household identifier visible in any screenshot or in either live demo.
- [ ] Screenshot backups on the slides for both demos, in case the live run fails.
- [ ] Rehearsed once with a timer and once with the demos actually running.
- [ ] All three members can answer on any slide — walk the seven prepared questions in
      `BIN381_M4_Team_Guideline.docx` §8 together.
