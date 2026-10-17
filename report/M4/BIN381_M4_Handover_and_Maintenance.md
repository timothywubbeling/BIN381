# Hand-over and maintenance notes — Group P1

**Owner:** Timothy Wubbeling (Person C) · 17 October 2026 · one page, for the repository archive

This is what someone who has never seen the project needs in order to run it, trust it, and know
when to stop trusting it.

## What is in the repository

```
app/                 Shiny application (app.R, R/validate.R, R/score.R, R/monitor.R)
R/                   pipeline scripts: export_powerbi.R, fairness_check.R,
                     check_app_matches_model.R, make_reference.R, review_monitoring.R
notebook/            M1 EDA, three M2 notebooks, the M3 full notebook, and the CRISP-DM driver
data/raw/            the ten GHS 2024 extracts, unmodified
data/clean/          per-file cleaned tables and the QA log
data/integrated/     household_integrated, the modelling dataset, dictionary, train/test splits
data/modelling/      fitted workflows, CV and test predictions, input schema
data/evaluation/     every metric, subgroup table, calibration and bootstrap output, figures
data/powerbi/        the nine dashboard tables, including the reconciliation benchmark,
                     the threshold curve, the dataset inventory and the cleaning log
models/              final_workflow.rds, reference.rds, CHANGELOG.md
powerbi/             BIN381_M4_Dashboard.pbix (first iteration) and
                     M4_Merged_Dashboard/ (the submitted merged dashboard, as a
                     Power BI project plus its generator scripts)
report/              M3 report and ethics log, and report/M4/ for this milestone
tests/              messy_households.csv and test_validation.R
```

## Reproducing it from a clean clone

1. `renv::restore()` from the project root. Three package versions were moved to the next patch
   release so Windows binaries exist and Rtools is not needed (E3-13).
2. Knit `notebook/BIN 381 Milestone 3 - Full Notebook (Group P1).Rmd`. It runs the pipeline and
   re-asserts that the app serves the evaluated model at the evaluated threshold.
3. `shiny::runApp("app")`, then upload `tests/messy_households.csv` — 13 broken rows, each of
   which should be repaired, rejected with a reason, or left unscored.
4. `python report/M4/check_numbers.py`. It exits non-zero if any quoted figure has drifted.
5. Open `powerbi/M4_Merged_Dashboard/BIN381_M4_Dashboard_Group_P1.pbip`, refresh, and check the
   Reconciliation page reads 0.0 for all nine provinces.

Alexander owns the clean-clone test. Anything that breaks goes to Timothy.

## The numbers that must agree

| Figure | Value | Source of truth |
|---|---|---|
| Households modelled | 20,925 | `data/integrated/M2_final_modelling_dataset.csv` |
| At risk, weighted / unweighted | 28.3% / 30.6% | `data/powerbi/powerbi_reconciliation.csv` |
| Test households / at risk in test | 6,279 / 1,919 | `data/integrated/M2_test.rds` |
| Threshold | 0.24 | `data/evaluation/monitoring_baseline.csv` |
| Recall · precision · ROC-AUC | 0.807 · 0.419 · 0.736 | `data/evaluation/evaluation_matrix.csv` |
| Referred, test set | 58.9% | as above |
| Referred, all households | 59.2% | `powerbi_reconciliation.csv` |

The last two are different populations and are both correct. `check_numbers.py` fails if they are
swapped, which is the single most likely way this project contradicts itself in front of a marker.

## Model version and rollback

The deployed artefact is `models/final_workflow.rds`, a lasso binary logistic workflow, identical
by checksum to `data/modelling/final_workflow_binary.rds`. Its version and the test metrics it
achieved are in `models/CHANGELOG.md`; `models/reference.rds` carries the training-data reference
values the app needs for cleaning and explanation. To roll back, restore the previous workflow and
reference pair named in the changelog and re-run step 4 above — the threshold belongs to the model
version and must not be carried across.

## Monitoring

Each upload appends one row of totals, never household rows, to `monitoring/batch_log.csv`.
`R/review_monitoring.R` applies the alert rules monthly.

| Signal | Baseline | Alert |
|---|---|---|
| Input drift (income, settlement type, household size) | PSI 0 | 0.10–0.25 watch, above 0.25 act |
| Missing income | 2.2% | above 5% |
| Rows not scored | 0% | above 5% |
| Share referred | 58.9% | more than 10 points either way |
| Recall (at each survey release) | 0.807 | below 0.707 |
| Calibration (at each survey release) | Brier 0.180 | clearly worse |
| Subgroup recall (at each survey release) | the subgroup table | gap above 10 points |

**Retrain** when any alert fires, when the survey changes one of the eight predictor items, or
annually at each release. **Retire** if recall for any group above 500 households falls below 0.65.
Income enters the model in rands, so inflation alone makes the screen under-refer: a simulated 25%
nominal income rise drops the referral rate from 59.8% to 51.9% with no change in real need. That
is the most likely reason this tool will quietly stop working.

**After any retrain, in order:** `R/export_powerbi.R` → `R/make_threshold_curve.R` →
`python powerbi/M4_Merged_Dashboard/scripts/make_data_foundation.py . data/powerbi` →
`python report/M4/check_numbers.py` → refresh and re-save the dashboard → re-take screenshots.

## Known issues

1. **Recall is weakest where risk is least expected** — 39.2% above R11,500 a month and 61.7% with
   no grant recipients. Published on the "Who the screen misses" page, not patched with group-specific thresholds.
   The standing monthly audit of lower-risk households in those two groups is the mitigation, and
   it is a process obligation, not a code one.
2. **Farm households** (197 in the test set) have a confidence interval too wide to support any
   claim of parity. Do not quote their recall without the interval.
3. **The target is a proxy** from eight self-reported items, on one cross-sectional wave. Every
   finding is an association. The three-tier version was abandoned because the middle tier does
   not separate.
4. **No external validation.** The threshold was chosen on cross-validation predictions and
   measured once on the held-out test set. It has never been checked against field outcomes.
5. **`R/make_threshold_curve.R` has not been executed** — R was not installed on the machine
   where the shipped CSV was generated (the Python equivalent in the dashboard's `scripts/`
   produced it, and it reconciles exactly). Run the R version once and confirm it reproduces the
   same 86 rows.
6. **`Threshold[Threshold]` values drift** in the dashboard's what-if table: the step shown as 0.24
   is stored as 0.24000000000000007. Filter with a range, never `= 0.24`.
7. **Report sections 5 and 7 run to about three pages** against a 2.5-page budget. If the report
   overruns ten pages, cut §5.3's bullet detail and §7's transparency paragraph first — both are
   covered at greater length in the M3 report and the ethics log.

## Who owns what

| Area | Owner |
|---|---|
| Data preparation, integration, modelling; clean-clone test; report §1–3; slides 1–4 | Alexander Solomon |
| Evaluation, findings, recommendations, limitations; report §4, §6, §8; slides 5–7; dashboard performance pages | Rudi Jan du Plessis |
| Dashboard merge and reconciliation; deployment and ethics; report §5, §7; report compilation; slides 8–10; README, hand-over, ethics and AI log | Timothy Wubbeling |

## Outstanding before upload

- [ ] **Alexander's report sections 1–3 and slides 1–4** — not in the repository as of 17 October.
      The report cannot be compiled or page-counted without them.
- [ ] **Rudi's reflection and AI log entries** (`BIN381_M4_PersonB_Reflection_and_AI_Log.md`) —
      referenced in `report/M4/README.md` but not committed.
- [ ] Walk all seven dashboard pages, then save the `.pbix` and take the screenshots.
- [ ] Compile the report: cover with all three names, contents, references, AI acknowledgement,
      then check the main content is ten pages or fewer at 11 pt and 1.15 spacing.
- [ ] Assemble the deck, rehearse once with a timer and once with both demos live.
- [ ] Upload on BC Connect, and have a second member confirm the upload completed.
