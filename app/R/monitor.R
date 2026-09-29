# monitor.R
# Drift checks for each uploaded batch. Only AGGREGATES are written to disk
# (counts, rates, PSI values), never household rows: that is how monitoring and the
# "no storage of inputs" privacy rule can both hold.

# Population Stability Index: sum((actual% - expected%) * ln(actual% / expected%))
# Rule of thumb: < 0.10 stable, 0.10-0.25 watch, > 0.25 significant shift.
psi <- function(expected, actual, breaks = NULL) {
  expected <- expected[!is.na(expected)]
  actual   <- actual[!is.na(actual)]
  if (is.null(breaks)) {                                  # categorical: one bin per code
    lv <- sort(unique(expected))
    e <- table(factor(expected, levels = lv)); a <- table(factor(actual, levels = lv))
  } else {                                                # numeric: fixed training bins
    e <- table(cut(expected, breaks, include.lowest = TRUE))
    a <- table(cut(actual,   breaks, include.lowest = TRUE))
  }
  e <- pmax(as.numeric(e) / sum(e), 1e-4)                 # floor avoids log(0)
  a <- pmax(as.numeric(a) / sum(a), 1e-4)
  sum((a - e) * log(a / e))
}

MIN_PSI_ROWS <- 200   # PSI on smaller batches is noise, so it is left blank

batch_summary <- function(scored, reference, threshold) {
  d <- scored
  enough <- nrow(d) >= MIN_PSI_ROWS
  train <- reference$train
  income_breaks <- unique(c(-Inf, quantile(train$TotalMonthlyHouseholdIncomeRaw,
                                           probs = seq(0.1, 0.9, 0.1), na.rm = TRUE), Inf))
  data.frame(
    date              = as.character(Sys.Date()),
    model_version     = reference$model_version,
    rows              = nrow(d),
    pct_not_scored    = round(100 * mean(d$status == "not scored"), 1),
    pct_income_missing = round(100 * mean(is.na(d$TotalMonthlyHouseholdIncomeRaw)), 1),
    psi_income        = if (!enough) NA else round(psi(train$TotalMonthlyHouseholdIncomeRaw,
                                  d$TotalMonthlyHouseholdIncomeRaw, income_breaks), 3),
    psi_geotype       = if (!enough) NA else round(psi(train$GeoTypeCode, d$GeoTypeCode), 3),
    psi_hhsize        = if (!enough) NA else round(psi(train$HouseholdSize, d$HouseholdSize,
                                  c(-Inf, 1, 2, 3, 4, 5, 7, Inf)), 3),
    pct_higher_risk   = round(100 * mean(d$probability >= threshold, na.rm = TRUE), 1)
  )
}

log_batch <- function(summary_row, path = "monitoring/batch_log.csv") {
  dir.create(dirname(path), showWarnings = FALSE, recursive = TRUE)
  write.table(summary_row, path, sep = ",", row.names = FALSE,
              col.names = !file.exists(path), append = file.exists(path))
}
