# test_validation.R  -  run from the repo root: source("tests/test_validation.R")
# Automated proof that the validation path handles messy input the way the report says.
source("app/R/validate.R")

raw <- read_upload("tests/messy_households.csv")
v   <- validate_households(raw)
st  <- setNames(v$data$status, v$data$row)
has <- function(row, text) any(v$issues$row == row & grepl(text, v$issues$problem, fixed = TRUE))

stopifnot(
  all(nchar(raw$HouseholdID) == 18),                     # 18-digit IDs kept exact (DQ-05)
  st[["1"]] == "ok",                                     # clean row
  st[["3"]] == "ok",                                     # household size 8 is VALID (M2 finding)
  has(4, "Household size 0"),  is.na(v$data$HouseholdSize[4]),
  has(5, "Income refused"),    is.na(v$data$TotalMonthlyHouseholdIncomeRaw[5]),
  st[["6"]] == "not scored",                             # GeoTypeCode 4 was never seen in training
  has(7, "Text where a number"),                         # 'Unknown' token (DQ-06)
  st[["8"]] == "ok",                                     # zero income is valid
  has(9, "More grant recipients"),                       # M2 cross-field check
  has(10, "Duplicate household"),
  st[["11"]] == "not scored",                            # 4 predictors missing after sentinels
  has(12, "Above the training range"), st[["12"]] == "scored with warning",
  st[["13"]] == "not scored",                            # negative household size
  has(0, "Food-insecurity items")                        # leakage columns ignored
)

# Error paths: an empty file and a missing column must stop with a clear message.
stopifnot(
  grepl("no rows", tryCatch(validate_households(raw[0, ]), error = conditionMessage)),
  grepl("GeoTypeCode", tryCatch(validate_households(raw[, names(raw) != "GeoTypeCode"]),
                                error = conditionMessage))
)
cat("All validation tests passed:", nrow(raw), "rows checked,", nrow(v$issues), "issues logged.\n")
