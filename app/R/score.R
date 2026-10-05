# score.R
# Steps 3-4 of the path: the fitted workflow does its own preprocessing (recipe),
# then scores. Contributions use a model-agnostic "swap to typical" check, so this
# works whether Person A's final model is logistic regression, a tree or a forest.

POSITIVE_COL <- ".pred_insecure"   # Person A's binary workflow: outcome levels secure / insecure

# Person A's final workflow was trained on the Milestone 2 features, not on raw codes:
# labelled factors plus two income features derived in M2 (Income_Log = log1p(income),
# Income_PerCapita = income / household size). This turns the validated raw codes into
# exactly that format, matching prep_df() in Person A's notebook. Missing values stay
# NA so the workflow's own imputation steps fill them, as they did in training.
to_model_input <- function(x) {
  income <- x$TotalMonthlyHouseholdIncomeRaw
  data.frame(
    ComparativeIncomeCode = factor(x$ComparativeIncomeCode, levels = 1:5, ordered = TRUE),
    GeoTypeCode           = factor(x$GeoTypeCode, levels = 1:3,
                                   labels = c("Urban", "Traditional_Tribal", "Farms")),
    HouseholdSize         = as.integer(x$HouseholdSize),
    Income_Log            = log1p(income),
    Income_PerCapita      = income / x$HouseholdSize,
    ElectricityAccessCode = factor(x$ElectricityAccessCode, levels = 1:2, labels = c("Yes", "No")),
    SocialGrantRecipients = as.integer(x$SocialGrantRecipients),
    MainToiletCode        = factor(x$MainToiletCode, levels = 1:12)
  )
}

predict_risk <- function(wf, x) {
  predict(wf, new_data = to_model_input(x), type = "prob")[[POSITIVE_COL]]
}

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
  p <- predict_risk(wf, x)

  # For each predictor: how much does the probability move if this household had
  # the typical training value instead? Positive = this factor raises the risk.
  # Swapping happens on the raw inputs, so swapping income (or household size) also
  # updates the derived income features, keeping explanations in the user's terms.
  contrib <- sapply(PREDICTORS, function(col) {
    x_swap <- x
    x_swap[[col]] <- reference$typical[[col]]
    p - predict_risk(wf, x_swap)
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
