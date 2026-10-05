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
| `data/integrated/` | Milestone 2 integrated household dataset (20,940 households), the modelling dataset (20,925 households with an FI Score), the train/test split and the data dictionary |
| `data/modelling/` | Person A: fitted candidate workflows, CV and test predictions, model parameter table, input schema |
| `data/evaluation/` | Person B: evaluation matrix, metrics, thresholds, calibration, subgroup performance, monitoring baseline, figures |
| `notebook/` | Milestone 3 notebooks (Person A modelling, Person B evaluation) with knitted HTML; `M1_EDA.Rmd` (Milestone 1 EDA) |
| `models/` | `final_workflow.rds` (the deployed model, a copy of `data/modelling/final_workflow_binary.rds`) and `reference.rds` (training reference for explanations and drift checks) |
| `app/` | Shiny app: `app.R` plus `R/validate.R`, `R/score.R`, `R/monitor.R` |
| `R/` | Person C checks: `check_app_matches_model.R`, `fairness_check.R`, `review_monitoring.R`, `make_reference.R` |
| `tests/` | `messy_households.csv` (deliberately bad input) and `test_validation.R` |
| `monitoring/` | `batch_log.csv`, written by the app: per-upload totals only, no household rows |
| `docs/` | Ethics and Responsible AI Usage Log |
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
4. **Run the Milestone 3 notebooks in order** (knit in RStudio with *Knit Directory → Project Directory*):
   1. `notebook/BIN 381 Milestone 3 Person A - Modelling Strategy and Implementation.Rmd`
      → fits the models, writes `data/modelling/`
   2. `notebook/BIN 381 Milestone 3 Person B - Evaluation and Interpretation.Rmd`
      → evaluates them, writes `data/evaluation/`

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
7. **Try it:** open *Batch upload*, upload `tests/messy_households.csv`, and check that
   the issues table lists the sentinel codes, the unseen code, the text value and the
   duplicate ID.

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
  fitted by Person A on 1 October 2026 on the GHS 2024 training set.
- Each batch upload appends one row of totals to `monitoring/batch_log.csv`
  (rows not scored, missing-income rate, PSI for income, settlement type and household
  size, share flagged). `R/review_monitoring.R` applies the alert rules.
- Baselines are in `data/evaluation/monitoring_baseline.csv`; recall alert below 0.707.
  Retraining and retirement triggers are in the Milestone 3 report (deployment and monitoring section).

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

AI assistance is recorded in the group's Ethics and Responsible AI Usage Log (`docs/`).
