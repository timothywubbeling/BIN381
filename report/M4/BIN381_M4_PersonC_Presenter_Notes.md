# Timothy — slides 8 to 10, cue card

## Setup

- App running, dashboard open on *How well the screen works* at **0.24**, `messy_households.csv` ready.
- Start the app: double-click **`RunScreeningApp.exe`**. (Or in RStudio, open `BIN381-P1.Rproj` → `shiny::runApp("app")`.)
- If a demo dies: *"I'll use the screenshots"* — they're on the slides. Don't debug on stage.

---

## Slide 8 — one household in ten seconds

**Demo, in order:**

1. Rural example: income **much lower**, traditional, 6 people, **R1,200**, no electricity, 2 grants, pit latrine → **0.80, refer for review**.
2. Change income to **R30,000**, urban, **and income change to "same as a year ago"** → **0.20, lower risk**. (Income alone only drops it to 0.69 — change the income-change answer too, or it doesn't cross.)
3. Upload `messy_households.csv` — 13 broken rows. Scroll the issues table: sentinels recoded, impossible size rejected, duplicate ID flagged, too-much-missing **left unscored, not guessed**.
4. Land on the **limits page**, not on a score.

**Say:** seven questions, askable at a door; the answer comes back with the three reasons, so the officer can justify a referral and a supervisor can disagree. It says *"higher risk: refer for review"*, never "food insecure".

**Killer line:** all 6,279 test households went back through the app's own code path — largest difference from the saved predictions: **zero**.

---

## Slide 9 — five actions

| Action | Number | Who |
|---|---|---|
| Outreach triage; resource the referral rate | refers 58.9%, 41.9% at risk | Programme managers |
| Ask about income change at intake | AUC drop 0.082, 2.5× the next | Field staff |
| Coordinate with grant registers | 37.6% vs 20.6% | Social development |
| Fund EC, NC, NW, MP first | 43.0 / 40.5 / 37.1 / 35.5 vs 28.3 national | Provincial teams |
| Audit "lower risk" where it's weakest | recall 39.2% and 61.7% | Field officers, monthly |

**Three things to say:** the referral rate is a budget decision, not a technical one · the grant finding is **targeting, not harm** · the audit exists because of what we found about ourselves.

**Close:** an official reviews every referral; a low score is never clearance.

---

## Slide 10 — limits

**Say them before you're asked:** AUC **0.736** is moderate · **58.1%** of referrals aren't food insecure, **19.3%** of at-risk are missed · the target is a **proxy** — we never observed anyone going without food · **no external validation**.

**Next:** capture follow-up outcomes → second survey wave → per-person income, employment, debt, food prices → re-validate each release.

**Final line:** a cheap, interpretable, monitored triage aid that finds four in five at-risk households **and knows which ones it misses**.

---

## Questions

**Why binary, not three tiers?** Middle tier isn't separable — no three-tier model recalls >3.2% of it; CV AUC ~0.67. Fallback was written down in M2 *before* testing.

**Why 0.24 at 41.9% precision?** Rule fixed before evaluation: ≥80% recall at fewest referrals. Only 30.6% are at risk, so a referral is ~1.4× better than random. Workability is capacity, not statistics — hence the slicer.

**Why does recall drop above R11,500 / no grants?** It leans on income and grants, so comfortable-looking households score low (39.2%, 61.7%). Low ≠ clearance; recommendation 5 is a monthly audit of those two groups.

**How did you stop leakage?** The 8 target items plus 8 related columns are excluded, asserted in code — the notebook stops if one appears. Rudi re-checked it independently.

**How would you know it drifted?** PSI >0.25 act · missing income >5% · unscored >5% · referred ±10 points from 58.9% · recall <0.707 · subgroup gap >10 points. Retrain on any alert or annually; retire below 0.65 for any group >500. **The sneaky one:** income is in rands, so inflation alone makes it under-refer — a 25% nominal rise drops referrals 59.8% → 51.9% with no change in real need.

**Dashboard vs app?** App = "what about this household?". Dashboard = population questions with survey weights: where the budget goes, who gets missed, what a threshold costs.

**Which decision changed?** The "duplicate IDs" were 18-digit IDs read as numbers · three tiers → binary · mine: rebuilt my M1 pages on integrated data, and dropped a map bound to a US shape file.

**Real household IDs?** In memory, never written to disk, never returned; monitoring keeps totals only.

**Is it fair?** Equal opportunity; gaps published, not patched — a lower threshold for richer households means treating people differently by income on a proxy.

**Does the dashboard agree with R?** Reconciliation page subtracts the R output from itself: 0.0 across all nine provinces.
