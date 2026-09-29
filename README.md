# Household Food-Insecurity Screening — BIN381 Group P1 (SDHSA)

Alexander Solomon · Rudi Jan du Plessis · Timothy Wubbeling
Belgium Campus iTversity · BIN381 Project · Milestone 3 (Modelling, Evaluation, Deployment)

A classification model that estimates how likely a South African household is to be
food insecure, built on the Stats SA General Household Survey 2024, and an R/Shiny
screening tool for prioritising households for follow-up. **It is a screening aid,
not an eligibility test** — see *Responsible use* below.

## Repository layout

| Folder | Contents |
|---|---|
| `data/raw/` | Stats SA source CSVs D01–D10 (included; this repo is private). D11 is not used and not included. |
| `data/clean/` | Milestone 2 cleaned files (`D04_clean.rds` … `D10_clean.rds`) and the QA log |
| `R/` | Numbered pipeline scripts: `01_prepare.R`, `02_model.R`, `03_evaluate.R`, `<...>` |
| `notebook/` | `<M3_notebook.qmd>` — the full pipeline with output, runs end to end; `M1_EDA.Rmd` — Milestone 1 EDA |
| `models/` | `final_workflow.rds` (fitted tidymodels workflow), `reference.rds` (training reference for explanations and drift checks) |
| `app/` | Shiny app: `app.R` plus `R/validate.R`, `R/score.R`, `R/monitor.R` |
| `tests/` | `messy_households.csv` — deliberately bad input for testing validation |
| `monitoring/` | `batch_log.csv` — per-batch aggregates only, no household rows |
| `docs/` | Ethics and Responsible AI Usage Log, milestone reports |

## Requirements

- R `<4.6.1>` and RStudio (tested on Windows 11)
- Package versions are pinned in `renv.lock`

## Reproduce everything

1. **Clone** the repository and open `BIN381-P1.Rproj` in RStudio.
   ```
   git clone https://github.com/timothywubbeling/BIN381.git
   ```
2. **Restore the packages** (installs the exact versions in `renv.lock`):
   ```r
   install.packages("renv")
   renv::restore()
   ```
3. **Data.** D01–D10 are already in `data/raw/`. Nothing to copy (D11 is not needed).
4. **Run the pipeline** (cleaning → integration → features → models → evaluation):
   ```r
   quarto::quarto_render("notebook/<M3_notebook.qmd>")
   # or run the scripts in order: source("R/01_prepare.R"), source("R/02_model.R"), ...
   ```
   Check: the integrated dataset has `<20,940>` households and the test-set metrics
   match the report (`<recall = ..., ROC-AUC = ...>`).
5. **Launch the app:**
   ```r
   shiny::runApp("app")
   ```
6. **Try it:** open *Batch upload*, upload `tests/messy_households.csv`, and check that
   the issues table lists the sentinel codes, the unseen code, the text value and the
   duplicate ID.

## How new data is handled

`validate → clean → preprocess → score`

1. **Validate** (`app/R/validate.R`): required columns present, all columns read as text
   so 18-digit HouseholdIDs stay exact, food-insecurity items dropped (leakage rule).
2. **Clean**: the Milestone 2 rules — sentinel codes to missing, text tokens to missing,
   household size 0 to missing (8 and 9 are valid sizes), valid code ranges; unseen
   codes and impossible values mean the row is not scored.
3. **Preprocess**: done inside the saved workflow's recipe, with values learned from
   the training data only (log income, factor levels, imputation).
4. **Score** (`app/R/score.R`): probability, class at the agreed threshold
   (`<0.xx>`), and the three factors that move the probability most.

## Model version and monitoring

- Current model: `<name / version>`, trained `<date>` on GHS 2024.
- Each batch upload appends one row of aggregates to `monitoring/batch_log.csv`
  (reject rate, missing-income rate, PSI for income, settlement type and household size).
- Retraining and retirement triggers are in the Milestone 3 report, section `<x>`.

## Responsible use

- For screening and prioritising follow-up by trained officials. Never use it on its own to
  approve, refuse or withdraw a grant, service or support.
- Uploads are processed in memory and not stored. HouseholdID is never shown or returned.
- Accuracy differs between subgroups; see the fairness section of the report.

## Data and licence

Source: Statistics South Africa (2026). *General Household Survey 2024* (split into 11 files
for BIN381). https://isibaloweb.statssa.gov.za/

## AI use

AI assistance is recorded in `docs/<Ethics_and_Responsible_AI_Usage_Log.xlsx>`.
