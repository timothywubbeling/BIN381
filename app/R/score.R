# score.R
# Steps 3-4 of the path: the fitted workflow does its own preprocessing (recipe),
# then scores. Contributions use a model-agnostic "swap to typical" check, so this
# works whether Person A's final model is logistic regression, a tree or a forest.

POSITIVE_COL <- ".pred_insecure"   # agree this name with Person A at kickoff

LABELS <- c(ComparativeIncomeCode = "Income compared with a year ago",
            GeoTypeCode = "Settlement type",
            HouseholdSize = "Household size",
            TotalMonthlyHouseholdIncomeRaw = "Monthly household income",
            ElectricityAccessCode = "Electricity access",
            SocialGrantRecipients = "Social-grant recipients",
            MainToiletCode = "Toilet facility type")

score_households <- function(wf, validated, reference, threshold) {
  d <- validated$data
  ok <- d$status != "not scored"
  d$probability <- NA_real_
  d$predicted   <- NA_character_
  d$main_factors <- NA_character_
  if (!any(ok)) return(d)

  x <- d[ok, PREDICTORS, drop = FALSE]
  p <- predict(wf, new_data = x, type = "prob")[[POSITIVE_COL]]

  # For each predictor: how much does the probability move if this household had
  # the typical training value instead? Positive = this factor raises the risk.
  contrib <- sapply(PREDICTORS, function(col) {
    x_swap <- x
    x_swap[[col]] <- reference$typical[[col]]
    p - predict(wf, new_data = x_swap, type = "prob")[[POSITIVE_COL]]
  })
  contrib <- matrix(contrib, nrow = nrow(x), dimnames = list(NULL, PREDICTORS))

  top3 <- apply(contrib, 1, function(cv) {
    top <- head(cv[order(-abs(cv))], 3)
    top <- top[abs(top) >= 0.01]                      # ignore effects under 1 point
    if (length(top) == 0) return("No single factor stands out")
    paste0(LABELS[names(top)], ifelse(top > 0, " raises risk (+", " lowers risk ("),
           sprintf("%.0f", 100 * top), " pts)", collapse = "; ")
  })

  d$probability[ok]  <- round(p, 3)
  d$predicted[ok]    <- ifelse(p >= threshold, "Higher risk: refer for review", "Lower risk")
  d$main_factors[ok] <- top3
  d
}
