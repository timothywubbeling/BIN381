# Milestone 4 — Person B's reflection, ethics entries and AI log

Rudi Jan du Plessis (601342) · Group P1 · for Timothy to merge into the final
`BIN381_M4_Ethics_and_AI_Usage_Log`, in the same format as the Milestone 3 log.

> **Rudi: read this before it is submitted.** Section 3 below records AI use on *your* Milestone 4
> work. It was drafted from what actually happened in the assistant session, but you are the one
> signing it. Delete anything you did not use, add anything you did separately, and make sure every
> "how it was checked" line describes a check you can personally stand behind. An AI log that
> overstates or understates is an academic-integrity problem, not a formatting one.

---

## 1. Reflection (Task 4, 150–200 words)

What worked was deciding early what each number was *for*. In Milestone 2 most of my time went on
the seven-file join, and the part that mattered was not the code — it was noticing that D05 carried
fifteen placeholder household IDs, the difference between 20,925 households and the 20,940 the
hand-off promised. Integration turned out to be mostly evidence, not merging.

What surprised me was Milestone 3. I expected the best-scoring model to win and it did not: the
random forest beat the logistic regression on AUC and I still recommended the logistic one, because
a tool that refers a household to an official has to be able to say why. I also expected grants to
look protective, and they came out the other way round — which says more about who grants reach
than about grants.

What changed across the milestones was ambition. We started with three severity tiers and finished
with a yes/no screen, because the middle tier simply was not separable with the predictors we had.

What I would improve is honesty about capacity earlier. We fixed an 80% recall rule before asking
anyone what 59% of households actually costs to visit.

*(Word count: 195.)*

---

## 2. Ethics decisions to add (Milestone 4, Person B)

| ID | Date | Stage | Issue | Decision and mitigation | Owner |
|---|---|---|---|---|---|
| E4-01 | 17 Oct | Reporting | The 10-page limit forces most evidence out of the report | Cut the flattering material first. The subgroup recall gaps (39.2% above R11,500, 61.7% for no-grant households) and the reversed grant finding kept their place in Sections 4 and 8; detailed tables moved to appendices and `data/evaluation/` | B |
| E4-02 | 17 Oct | Dashboard | The referral threshold is a policy choice, but it was presented as a fixed model property | A what-if threshold slicer on the model-performance page shows recall, precision and households referred per 1,000 at any threshold, so programme managers can see what their capacity actually costs in missed households | B |
| E4-03 | 17 Oct | Reporting | Two defensible referral rates exist (58.9% on the test set, 59.2% across all 20,925 households) and quoting whichever suits would be misleading | Both documented, the test-set figure used for every performance claim, and `report/M4/check_numbers.py` fails the build if the two are confused | B |
| E4-04 | 17 Oct | Dashboard | Re-identification risk if household-level data is published | `powerbi_households.csv` ships a row-number `HouseholdKey` instead of `HouseholdID`; the build guide forbids adding it back and no visual shows a household identifier | B |

---

## 3. AI use to add (Milestone 4, Person B) — draft for Rudi to confirm

Rudi Jan du Plessis (Person B) used Claude (Anthropic), through the Claude desktop application, as
a coding and writing assistant for the Milestone 4 evaluation, recommendations, limitations,
dashboard specification and slides. The assistant had read and write access to the project folder,
so its output was produced against the team's own data rather than in isolation.

| # | Date, person, tool | Task and what the AI produced | How it was checked | Decisions and changes by the team |
|---|---|---|---|---|
| AI-M4-1 | 17 Oct 2026 · Rudi (B) · Claude (Anthropic) | Project audit. Established that the `BIN381` clone on Rudi's machine had every tracked Milestone 3 file deleted in the working tree, and that `Main Dash.pbix` and several raw files existed only there and in no commit. Set up a clean worktree on a new branch for the Milestone 4 work. | Verified against `git log --all` for each file; the broken checkout was left untouched. | The team was warned that `Main Dash.pbix` is unbacked-up, and the Milestone 4 work was done on a separate branch. |
| AI-M4-2 | 17 Oct 2026 · Rudi (B) · Claude (Anthropic) | Retrieved the official Milestone 4 brief and due date (Monday 19 October 2026, 23:59) from BC Connect, and confirmed the team's own Milestone 4 guideline matched the published 100-mark rubric. | Brief read in full and compared, criterion by criterion, with the team guideline. | Confirmed the A/B/C split and the 10-page limit before any writing started. |
| AI-M4-3 | 17 Oct 2026 · Rudi (B) · Claude (Anthropic) | Report Sections 4, 6 and 8. Wrote `report/M4/build_personB_sections.py`, which reads `data/evaluation/` and `data/powerbi/` and generates the three sections as a `.docx`. No figure is typed into the text; all are read from the CSVs at build time. | Script re-run from a clean state; output checked against the Milestone 3 report and the notebook. Length checked against the 3-page budget. | Rudi reviewed and approved the selection of findings, the recommendations and the way the limitations are stated. |
| AI-M4-4 | 17 Oct 2026 · Rudi (B) · Claude (Anthropic) | Dashboard specification for Person B's three pages: decision questions, page layouts, DAX measures including the what-if threshold, friendly-label columns, and the reconciliation table (`docs/powerbi_m4_person_b_pages.md`). Established that the existing `Main Dash.pbix` is the Milestone 1/2 dashboard built on raw tables, not a Milestone 4 decision-support dashboard. | Every expected value recomputed from `powerbi_households.csv` and matched against `evaluation_matrix.csv`; the `.pbix` page and visual structure read directly from the file. | Rudi builds the pages in Power BI Desktop; the AI did not produce the `.pbix`. |
| AI-M4-5 | 17 Oct 2026 · Rudi (B) · Claude (Anthropic) | Draft of slides 5–7, speaker notes, the dashboard demo script and prepared answers to the likely defence questions. | Every number cross-checked against `data/evaluation/`. | Rudi rehearses and rewrites the notes in his own words; he is responsible for defending every slide. |
| AI-M4-6 | 17 Oct 2026 · Rudi (B) · Claude (Anthropic) | `report/M4/check_numbers.py`: recomputes the headline metrics from the dashboard table, asserts them against `data/evaluation/`, and flags the two population figures that are easy to confuse. | Run; all assertions pass. | Adopted as the pre-submission check for any number quoted in the report, dashboard or slides. |

**Responsibility.** Every analysis decision in these sections — the metric set, the 80% recall rule,
the choice of the logistic model over the random forest, which findings were kept under the page
limit and how the limitations are worded — was made and approved by Rudi du Plessis. All generated
figures were produced by running the team's own code on the team's own data and were checked
against the notebook outputs before submission. Responsibility for the content rests with the
author.
