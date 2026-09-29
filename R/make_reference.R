# make_reference.R
# Builds models/reference.rds from the TRAINING data only. The app uses it for:
#   - typical values: the baseline for the "main contributing factors" explanation
#   - the training distribution: what the drift (PSI) checks compare new uploads against
# Run it again whenever the model is retrained, with the new training set.

make_reference <- function(train, model_version) {
  preds <- c("ComparativeIncomeCode", "GeoTypeCode", "HouseholdSize",
             "TotalMonthlyHouseholdIncomeRaw", "ElectricityAccessCode",
             "SocialGrantRecipients", "MainToiletCode")
  missing_cols <- setdiff(preds, names(train))
  if (length(missing_cols) > 0) stop("Training data is missing: ", paste(missing_cols, collapse = ", "))

  # Codes are compared as numbers, so factors are turned back into their codes first.
  train <- as.data.frame(lapply(train[preds], function(x) as.numeric(as.character(x))))
  mode_of <- function(x) as.numeric(names(which.max(table(x))))

  list(
    typical = list(ComparativeIncomeCode          = mode_of(train$ComparativeIncomeCode),
                   GeoTypeCode                    = mode_of(train$GeoTypeCode),
                   HouseholdSize                  = median(train$HouseholdSize, na.rm = TRUE),
                   TotalMonthlyHouseholdIncomeRaw = median(train$TotalMonthlyHouseholdIncomeRaw, na.rm = TRUE),
                   ElectricityAccessCode          = mode_of(train$ElectricityAccessCode),
                   SocialGrantRecipients          = median(train$SocialGrantRecipients, na.rm = TRUE),
                   MainToiletCode                 = mode_of(train$MainToiletCode)),
    train         = train,
    model_version = model_version,
    trained_on    = Sys.Date()
  )
}
