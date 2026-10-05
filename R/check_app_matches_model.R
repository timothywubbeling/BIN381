# check_app_matches_model.R  -  run from the repo root: source("R/check_app_matches_model.R")
# Proves the app's path (validate -> clean -> preprocess -> score) gives the same
# probabilities as Person B's evaluation of the final model, so the notebook, the
# report and the app agree (same test set, same model, same threshold).
library(workflows)
source("app/R/validate.R")
source("app/R/score.R")

MODEL_PATH <- "models/final_workflow.rds"
TEST_PATH  <- "data/integrated/M2_test.rds"                      # raw codes, from Milestone 2
B_PREDS    <- "data/evaluation/final_model_test_predictions.csv"  # Person B, same row order
THRESHOLD  <- 0.24                                                # Person B's chosen threshold

wf   <- readRDS(MODEL_PATH)
ref  <- readRDS("models/reference.rds")
test <- readRDS(TEST_PATH)
b    <- read.csv(B_PREDS)
stopifnot(nrow(b) == nrow(test),
          # same households in the same order: the columns both files share must agree
          isTRUE(all.equal(b$HouseholdSize, test$HouseholdSize)),
          isTRUE(all.equal(b$SocialGrantRecipients, test$SocialGrantRecipients)),
          isTRUE(all.equal(b$TotalMonthlyHouseholdIncomeRaw, test$TotalMonthlyHouseholdIncomeRaw)))

v <- validate_households(test[PREDICTORS])
s <- score_households(wf, v, ref, THRESHOLD)

keep <- s$status != "not scored"
print(table(s$status))
cat("Test rows the app refuses:", sum(!keep), "of", nrow(test), "\n")
diff <- abs(s$probability[keep] - round(b$.pred_insecure[keep], 3))
cat("Largest difference from Person B's probabilities:", max(diff), "\n")
stopifnot(max(diff) < 1e-9)
cat("App and model agree on all", sum(keep), "scored test rows.\n")

# Same flags at the threshold, so the recall in the report is the recall of the app.
at_risk <- b$truth[keep] == "insecure"
flag    <- s$predicted[keep] == "Higher risk: refer for review"   # the app's decision (unrounded probability)
cat("App recall on scored test rows:", round(sum(flag & at_risk) / sum(at_risk), 3), "\n")

# These numbers become baselines in the monitoring plan.
cat("% of test rows not scored:", round(100 * mean(!keep), 1), "\n")
cat("% flagged higher risk:", round(100 * mean(flag), 1), "\n")
