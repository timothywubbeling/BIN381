# review_monitoring.R  -  the monthly review of monitoring/batch_log.csv
# Applies the alert rules from the monitoring plan to every logged upload.

BASELINE_PCT_FLAGGED <- 30   # replace with the test-set % flagged higher risk (Thursday)

log <- read.csv("monitoring/batch_log.csv")

worst_psi <- suppressWarnings(pmax(log$psi_income, log$psi_geotype, log$psi_hhsize, na.rm = TRUE))
log$drift <- ifelse(is.na(worst_psi), "batch too small for PSI",
             ifelse(worst_psi > 0.25, "ACT: significant shift",
             ifelse(worst_psi > 0.10, "watch", "stable")))
log$data_quality <- ifelse(log$pct_income_missing > 5 | log$pct_not_scored > 5,
                           "ACT: check source data", "ok")
log$output_shift <- ifelse(abs(log$pct_higher_risk - BASELINE_PCT_FLAGGED) > 10,
                           "check threshold and drift", "ok")

print(log[, c("date", "model_version", "rows", "drift", "data_quality", "output_shift")])
