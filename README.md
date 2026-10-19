# Household Food-Insecurity Screening — BIN381 Group P1 (SDHSA)

Alexander Solomon · Rudi Jan du Plessis · Timothy Wubbeling
Belgium Campus iTversity · BIN381 Project · Milestone 4 (final synthesis: report, dashboard, hand-over)

A classification model that estimates how likely a South African household is to be
food insecure, built on the Stats SA General Household Survey 2024, and an R/Shiny
screening tool for prioritising households for follow-up. **It is a screening aid,
not an eligibility test** — see *Responsible use* below.

## Repository layout

| Folder | Contents |
|---|---|
| `data/raw/` | Stats SA source CSVs D01–D10 (included; this repo is private). D11 is not used and not included. |
| `data/clean/` | Milestone 2 cleaned files (`D04_clean.rds` … `D10_clean.rds`) and the QA log |
| `data/reference/` | Inputs to the Milestone 2 notebooks: the Milestone 1 column dictionary and the hand-written dictionary entries for the six derived variables |
| `data/integrated/` | Milestone 2 integrated household dataset (20,940 households), the modelling dataset (20,925 households with an FI Score), the train/test split and the data dictionary |
| `data/modelling/` | Person A: fitted candidate workflows, CV and test predictions, model parameter table, input schema, class-weight comparison |
| `data/evaluation/` | Person B: evaluation matrix, metrics, thresholds, calibration, subgroup performance, monitoring baseline, figures |
| `data/powerbi/` | Tables for the Power BI dashboard: all 20,925 households scored by the deployed model, model summary, subgroup performance, drivers, and the R reconciliation table |
| `notebook/` | `BIN 381 Milestone 4 - CRISP-DM Driver (Group P1).Rmd` maps the whole project onto the six CRISP-DM phases and points at the file that carries each decision — **start here**; `BIN 381 Milestone 3 - Full Notebook (Group P1).Rmd` runs Parts A, B and C end to end; the three part notebooks (A modelling, B evaluation, C deployment, monitoring and ethics) with knitted HTML; the three Milestone 2 notebooks (C cleaning, B integration, A preparation for modelling); `M1_EDA.Rmd` |
| `models/` | `final_workflow.rds` (the deployed model, a copy of `data/modelling/final_workflow_binary.rds`), `reference.rds` (training reference for explanations and drift checks) and `CHANGELOG.md` (model versions, how to add one and how to roll back) |
| `app/` | Shiny app: `app.R` plus `R/validate.R`, `R/score.R`, `R/monitor.R` |
| `R/` | Person C checks: `check_app_matches_model.R`, `fairness_check.R`, `review_monitoring.R`, `make_reference.R`; `export_powerbi.R` builds `data/powerbi/` |
| `tests/` | `messy_households.csv` (deliberately bad input) and `test_validation.R` |
| `monitoring/` | `batch_log.csv`, written by the app at run time (not committed): per-upload totals only, no household rows |
| `docs/` | `figures/` (app and dashboard screenshots and the deployment workflow diagram used in the report), `powerbi_build_guide.md` (first-iteration dashboard) and `powerbi_m4_person_b_pages.md` (the Milestone 4 performance, subgroup and driver pages, with their DAX) |
| `powerbi/` | `M4_Merged_Dashboard/` — the nine-page group dashboard as a PBIP project, with its own `README.md`, the `scripts/` that generate it and the data embedded in the model, so it opens anywhere; `BIN381_M4_Dashboard.pbix` is the pre-merge Person B file, kept as the record of the first iteration |
| `report/` | The Milestone 3 report and Ethics and AI Usage Log (`.pdf` and `.docx`), and `M4/`: the final report, the ethics and AI log, the hand-over notes, each member's sections and slide notes, and the scripts that build them |
| `renv/`, `renv.lock` | Pinned package versions (R 4.6.1, 225 packages) |

## Requirements

- R 4.6.1 and RStudio (tested on Windows 11)
- Package versions are pinned in `renv.lock`; `renv` activates automatically when the project opens

## Reproduce everything

1. **Clone** the repository and open `BIN381-P1.Rproj` in RStudio.
   ```
   git clone https://github.com/timothywubbeling/BIN381.git
   ```
2. **Restore the packages** (installs the exact versions in `renv.lock` into the project library):
   ```r
   renv::restore()
   ```
3. **Data.** D01–D10 are already in `data/raw/`, and the Milestone 2 outputs are in
   `data/clean/` and `data/integrated/`. Nothing to copy (D11 is not needed).
4. **Run the pipeline.** Knit `notebook/BIN 381 Milestone 3 - Full Notebook (Group P1).Rmd`, which
   runs the three parts in order from a clean session (or knit the part notebooks one at a time):
   1. Person A, modelling → fits the models, writes `data/modelling/`
   2. Person B, evaluation → evaluates them, writes `data/evaluation/`
   3. Person C, deployment, monitoring and ethics → checks the app against the evaluation

   The Milestone 2 inputs can be rebuilt from `data/raw/` by knitting the Milestone 2 notebooks
   in this order (each reproduces the committed files exactly):
   1. `BIN 381 Milestone 2 Person C - Data Selection and Cleaning.Rmd` → `data/clean/`
   2. `BIN 381 Milestone 2 Person B - Integration, Construction and Data Dictionary.Rmd` →
      `data/integrated/household_integrated`, the join and key-repair logs and the data dictionary
   3. `BIN 381 Milestone 2 Person A - Prepare for Modelling.Rmd` → the modelling dataset and the
      train/test split (`M2_train.rds`, `M2_test.rds`)

   Check: 20,925 modelled households (train 14,646 / test 6,279). Final model: binary
   logistic regression (glmnet), threshold 0.24. Test recall 0.807, precision 0.419,
   ROC-AUC 0.736, PR-AUC 0.550, Brier score 0.180, 58.9% of households flagged.
5. **Check the app** gives the same numbers as the evaluation:
   ```r
   source("tests/test_validation.R")          # validation rules
   source("R/check_app_matches_model.R")      # app = model on all scored test rows
   ```
6. **Launch the app:**
   ```r
   shiny::runApp("app")
   ```
7. **Power BI tables** (optional): `source("R/export_powerbi.R")` rebuilds `data/powerbi/`; build the
   dashboard with `docs/powerbi_build_guide.md`.
8. **Try it:** open *Batch upload*, upload `tests/messy_households.csv`, and check that
   the issues table lists the sentinel codes, the unseen code, the text value and the
   duplicate ID.

## Milestone 4 deliverables, and what rebuilds each one

The report, the ethics log and the dashboard are **generated**, not hand-edited: every figure in them
is read from `data/evaluation/`, `data/modelling/` or `data/powerbi/` at build time, so they cannot
drift from the notebooks. The build scripts are Python and need `python-docx`
(`pip install python-docx`); everything else in the project is R.

| Deliverable | File | Rebuild with |
|---|---|---|
| Final report | `report/M4/BIN381_M4_Report_Group_P1.docx`, and `.pdf` beside it | `python report/M4/merge_final_report.py` (merges Alexander's sections 1–4, 6, 8 with Timothy's 5 and 7, puts the dashboard figure into §5 and appends the ethics log), then `report\M4\export_pdf.ps1` from a PowerShell window — it rebuilds the contents page, exports the PDF and fails if the main content passes 10 pages. A4, 2 cm margins: 10 pages of main content, 20 in total |
| Ethics report and AI log | `report/M4/BIN381_M4_Ethics_and_AI_Usage_Log.docx` (and `.md`) | `python report/M4/build_ethics_and_ai_log.py` |
| Report sections | `report/M4/BIN381_M4_PersonB_Sections_4_6_8.docx`, `..._PersonC_Sections_5_7.docx` | `python report/M4/build_personB_sections.py`, `build_personC_sections.py` |
| Every quoted figure | — | `python report/M4/check_numbers.py` — exits non-zero if any deliverable stops reconciling with `data/evaluation/` |
| Power BI dashboard | `powerbi/M4_Merged_Dashboard/` (PBIP source) → save as `powerbi/BIN381_M4_Dashboard_Group_P1.pbix` | `powerbi/M4_Merged_Dashboard/README.md` — open the `.pbip`, **Refresh**, check the Threshold slicer reads 0.24, then *Save as* the `.pbix`. Hand the markers the `.pbix` |
| Presentation | `report/M4/BIN381_M4_Slides_Group_P1.pptx` | `python report/M4/build_slides.py` — appends Person C's slides 8–10, from `..._PersonC_Slides_8_to_10.md`, to Alexander's slides 1–7 in `BIN381_M4_PersonA_Slides_1_4.pptx`, in his layout |
| Analysis by CRISP-DM phase | `notebook/BIN 381 Milestone 4 - CRISP-DM Driver (Group P1).Rmd` | Knit it; it also checks every artifact it names is present |
| Final dataset and dictionary | `data/integrated/M2_final_modelling_dataset.rds`, `BIN381_M2_Data_Dictionary.csv` | Knit the Milestone 2 notebooks (see *Reproduce everything*) |
| Shiny app | `app/` | `shiny::runApp("app")` |
| Hand-over notes | `report/M4/BIN381_M4_Handover_and_Maintenance.md` | Model version and rollback, monitoring rules and thresholds, retraining and retirement triggers, who owns what, known issues |

**After a retrain**, follow the order in `powerbi/M4_Merged_Dashboard/README.md` (*Maintenance*): the
dashboard holds its own snapshot of `data/powerbi/`, so it has to be rebuilt and re-saved or it will
keep showing the previous numbers while the report shows the new ones.

## How new data is handled

`validate → clean → preprocess → score`

1. **Validate** (`app/R/validate.R`): required columns present, all columns read as text
   so 18-digit HouseholdIDs stay exact, food-insecurity items dropped (leakage rule).
2. **Clean**: the Milestone 2 rules — sentinel codes to missing, text tokens to missing,
   household size 0 to missing (8 and 9 are valid sizes), valid code ranges; unseen
   codes and impossible values mean the row is not scored.
3. **Preprocess** (`app/R/score.R`, `to_model_input()`): raw codes become the model's
   features exactly as in Person A's notebook (labelled factors, `Income_Log = log1p(income)`,
   `Income_PerCapita = income / household size`); the saved workflow's recipe then imputes,
   encodes and scales with values learned from the training data only.
4. **Score** (`app/R/score.R`): probability of food insecurity, "Higher risk: refer for
   review" at or above the threshold of 0.24, and the three inputs that move the
   probability most.

## Model version and monitoring

- Current model: binary logistic regression (glmnet), version `binary-glmnet-v1`,
  fitted by Person A on 1 October 2026 on the GHS 2024 training set. Version history,
  how to add a version and how to roll back are in `models/CHANGELOG.md`.
- Each batch upload appends one row of totals to `monitoring/batch_log.csv`
  (rows not scored, missing-income rate, PSI for income, settlement type and household
  size, share flagged). `R/review_monitoring.R` applies the alert rules.
- Baselines are in `data/evaluation/monitoring_baseline.csv`; recall alert below 0.707.
  Retraining and retirement triggers, rollback and ownership are in
  `report/M4/BIN381_M4_Handover_and_Maintenance.md`.

## Responsible use

- For screening and prioritising follow-up by trained officials. Never use it on its own to
  approve, refuse or withdraw a grant, service or support.
- Uploads are processed in memory and not stored. HouseholdID is never shown or returned.
- Accuracy differs between subgroups: recall is lower for households with incomes above
  R11,500 a month (0.39) and households with no grant recipients (0.62). See the fairness
  section of the report.

## Data and licence

Source: Statistics South Africa (2026). *General Household Survey 2024* (split into 11 files
for BIN381). https://isibaloweb.statssa.gov.za/

## AI use

Generative AI (Claude, Anthropic) was used during this project. It is acknowledged in section 7 of
the final report and every use is recorded in `report/M4/BIN381_M4_Ethics_and_AI_Usage_Log.docx`,
which continues the Milestone 3 log.
