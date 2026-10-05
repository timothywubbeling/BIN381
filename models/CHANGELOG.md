# Model change log

Every model the app serves gets a version, an entry here and a matching `model_version`
in `models/reference.rds` (shown on every app result and download).

## binary-glmnet-v1 (deployed)

- **Fitted:** 1 October 2026 by Person A (`notebook/BIN 381 Milestone 3 Person A - Modelling Strategy and Implementation.Rmd`, section 1.13).
- **Model:** binary logistic regression (glmnet, lasso: penalty 1.93e-06, mixture 1) on
  `Food_Insecure_Binary` (any food insecurity vs food secure), eight predictors, Milestone 2
  training set (14,646 households), 5-fold stratified CV, seed 381.
- **File:** `models/final_workflow.rds` (identical to `data/modelling/final_workflow_binary.rds`).
- **Threshold:** 0.24, the highest threshold with at least 80% recall on cross-validation
  predictions (Person B, `data/evaluation/thresholds.csv`).
- **Test set (6,279 households):** recall 0.807, precision 0.419, 58.9% flagged, ROC-AUC 0.736,
  PR-AUC 0.550, Brier 0.180, ECE 0.012 (`data/evaluation/monitoring_baseline.csv`).
- **Reference:** `models/reference.rds` built from `data/integrated/M2_train.rds` with `R/make_reference.R`.
- **Deployed:** 5 October 2026. The app reproduces the evaluated probabilities exactly
  (`R/check_app_matches_model.R`: largest difference 0 on all test households).
- **Previous version:** none (a placeholder model was used only while the app was built, and removed).

## Adding a new version

1. Fit and evaluate the new model in the notebooks; save it as `models/final_workflow.rds`.
2. Before overwriting, keep the current file as `models/archive/<version>.rds` so it can be rolled back.
3. Rebuild `models/reference.rds` with `make_reference(<new training data>, "<new version>")`.
4. Update `THRESHOLD` in `app/app.R` if it changed, and run `tests/test_validation.R` and
   `R/check_app_matches_model.R`.
5. Add an entry above with the date, model, threshold and test results.

**Rollback:** copy `models/archive/<version>.rds` back to `models/final_workflow.rds`, rebuild the
reference for that version, and restore its threshold.
