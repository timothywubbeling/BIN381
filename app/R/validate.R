# validate.R
# Step 1 of the path for new data: validate -> clean -> preprocess -> score.
# The rules are the Milestone 2 cleaning rules (Milestone2_PersonC_Cleaning.Rmd)
# applied to one new household or an uploaded CSV.

PREDICTORS <- c("ComparativeIncomeCode", "GeoTypeCode", "HouseholdSize",
                "TotalMonthlyHouseholdIncomeRaw", "ElectricityAccessCode",
                "SocialGrantRecipients", "MainToiletCode")

# The 8 items that build the FI Score, plus the two older GHS hunger items.
# If an upload contains any of them they are dropped: they define the target
# and must never reach the model (leakage rule).
LEAKAGE_COLS <- c("WorriedFoodWouldRunOutCode", "UnableToEatHealthyFoodCode",
                  "AteFewFoodsCode", "SkippedMealCode", "AteLessCode",
                  "RanOutOfFoodCode", "HungryButDidNotEatCode",
                  "WholeDayWithoutEatingCode", "AdultHungerCode", "ChildHungerCode")

# Per-column rules, taken from the Milestone 2 sentinel map and Data_Dictionary.pdf.
# levels = allowed codes (anything else is an unseen level -> reject).
# min/max = valid range; above max = outside the training data -> score but flag.
RULES <- list(
  ComparativeIncomeCode = list(sentinels = 9, levels = 1:5,
                               note = "Code 9 = unspecified"),
  GeoTypeCode           = list(sentinels = numeric(0), levels = 1:3, note = ""),
  HouseholdSize         = list(sentinels = 0, min = 1, max = 25, whole = TRUE,
                               note = "Household size 0 is impossible"),   # 8 and 9 are REAL sizes (M2)
  TotalMonthlyHouseholdIncomeRaw = list(sentinels = c(9999999, 99999999, 999999999, 9999999999),
                               min = 0, max = 1460000,
                               note = "Income refused / not recorded code"),  # 0 income is valid
  ElectricityAccessCode = list(sentinels = 9, levels = 1:2,
                               note = "Code 9 = unspecified"),
  SocialGrantRecipients = list(sentinels = 99, min = 0, max = 16, whole = TRUE,
                               note = "Code 99 = unspecified"),
  MainToiletCode        = list(sentinels = 99, levels = 1:12,
                               note = "Code 99 = unspecified")
)

MAX_MISSING <- 2   # more missing predictors than this and the row is not scored

# Read an uploaded CSV with EVERY column as text. This keeps 18-digit HouseholdIDs
# exact (the DQ-05 float bug) and lets text tokens be caught instead of crashing.
read_upload <- function(path) {
  read.csv(path, colClasses = "character", na.strings = c("", "NA"),
           check.names = FALSE, strip.white = TRUE)
}

validate_households <- function(raw) {
  raw <- as.data.frame(raw, stringsAsFactors = FALSE)
  if (nrow(raw) == 0) stop("The file has no rows.")
  missing_cols <- setdiff(PREDICTORS, names(raw))
  if (length(missing_cols) > 0)
    stop("Missing required column(s): ", paste(missing_cols, collapse = ", "))

  n <- nrow(raw)
  reject <- logical(n)
  flag   <- logical(n)
  issues <- list()
  log_issue <- function(rows, column, value, problem, action) {
    if (length(rows) > 0)
      issues[[length(issues) + 1]] <<- data.frame(
        row = rows, column = column,
        value = if (is.numeric(value)) format(value, scientific = FALSE, trim = TRUE) else as.character(value),
        problem = problem, action = action, stringsAsFactors = FALSE)
  }

  leaked <- intersect(LEAKAGE_COLS, names(raw))
  if (length(leaked) > 0)
    log_issue(0, paste(leaked, collapse = ", "), "",
              "Food-insecurity items found in the upload", "Columns ignored (leakage rule)")

  # Duplicate IDs are only detectable because the ID was read as text.
  if ("HouseholdID" %in% names(raw)) {
    dup <- which(!is.na(raw$HouseholdID) & duplicated(raw$HouseholdID))
    log_issue(dup, "HouseholdID", "(hidden)", "Duplicate household", "Scored, but check the source file")
    flag[dup] <- TRUE
  }

  clean <- data.frame(row = seq_len(n))
  for (col in PREDICTORS) {
    r   <- RULES[[col]]
    txt <- trimws(as.character(raw[[col]]))
    num <- suppressWarnings(as.numeric(txt))

    is_blank <- is.na(txt) | txt == ""
    log_issue(which(is_blank), col, "", "Missing value", "Imputed by the model if the row is scored")

    is_text <- !is.na(txt) & is.na(num)                        # DQ-06 text tokens
    log_issue(which(is_text), col, txt[is_text], "Text where a number is expected", "Treated as missing")

    is_sent <- !is.na(num) & num %in% r$sentinels              # DQ-01 sentinels
    log_issue(which(is_sent), col, num[is_sent], r$note, "Recoded to missing")
    num[is_sent] <- NA

    if (!is.null(r$levels)) {
      bad <- !is.na(num) & !(num %in% r$levels)                # unseen factor level
      log_issue(which(bad), col, num[bad],
                paste0("Code not in the training data (allowed ", min(r$levels), "-", max(r$levels), ")"),
                "Row not scored")
      reject[bad] <- TRUE
    } else {
      bad <- !is.na(num) & (num < r$min | (isTRUE(r$whole) & num != round(num)))
      log_issue(which(bad), col, num[bad], paste0("Invalid value (must be a whole number >= ", r$min, ")"),
                "Row not scored")
      reject[bad] <- TRUE
      high <- !is.na(num) & !bad & num > r$max
      log_issue(which(high), col, num[high], paste0("Above the training range (max ", r$max, ")"),
                "Scored, but less reliable")
      flag[high] <- TRUE
    }
    clean[[col]] <- num
  }

  # Cross-field check from M2: more grant recipients than people is impossible.
  cross <- which(!reject & clean$SocialGrantRecipients > clean$HouseholdSize)
  log_issue(cross, "SocialGrantRecipients", clean$SocialGrantRecipients[cross],
            "More grant recipients than household members", "Scored, but check the source")
  flag[cross] <- TRUE

  n_missing <- rowSums(is.na(clean[PREDICTORS]))
  too_sparse <- which(n_missing > MAX_MISSING)
  log_issue(too_sparse, "(row)", n_missing[too_sparse],
            paste0("More than ", MAX_MISSING, " predictors missing"), "Row not scored")
  reject[too_sparse] <- TRUE
  flag[n_missing > 0] <- TRUE   # remaining gaps are filled by the model's own imputation step

  clean$status <- ifelse(reject, "not scored", ifelse(flag, "scored with warning", "ok"))
  issues <- if (length(issues) > 0) do.call(rbind, issues) else
    data.frame(row = integer(), column = character(), value = character(),
               problem = character(), action = character())
  list(data = clean, issues = issues[order(issues$row), ])
}
