# check_app_matches_model.R  -  run on Thursday after the real model is plugged in.
# Proves the app's path (validate -> clean -> preprocess -> score) gives exactly the
# same probabilities as calling the model directly, so notebook, report and app agree.
library(workflows)
source("app/R/validate.R")
source("app/R/score.R")

MODEL_PATH <- "models/final_workflow.rds"
TEST_PATH  <- "<path to Person A's test set>.rds"   # raw predictor codes + the target
THRESHOLD  <- 0.35                                  # Person B's chosen threshold

wf   <- readRDS(MODEL_PATH)
ref  <- readRDS("models/reference.rds")
test <- readRDS(TEST_PATH)

v <- validate_households(test[PREDICTORS])
s <- score_households(wf, v, ref, THRESHOLD)
direct <- round(predict(wf, new_data = test, type = "prob")[[POSITIVE_COL]], 3)

keep <- s$status != "not scored"
print(table(s$status))
cat("Test rows the app refuses:", sum(!keep), "of", nrow(test), "\n")
stopifnot(isTRUE(all.equal(s$probability[keep], direct[keep])))
cat("App and model agree on all", sum(keep), "scored test rows.\n")

# These two numbers become baselines in the monitoring plan.
cat("% of test rows not scored:", round(100 * mean(!keep), 1), "\n")
cat("% flagged higher risk:", round(100 * mean(s$probability[keep] >= THRESHOLD), 1), "\n")
