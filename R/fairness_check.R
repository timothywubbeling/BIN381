# fairness_check.R
# Subgroup performance for the fairness section (equal opportunity = similar recall
# for the food-insecure class in every group). Person B owns the official subgroup
# table; use this to check it, or to add a grouping B did not include.
#
# `preds` = one row per TEST household with: truth ("insecure"/"secure"),
# .pred_insecure (probability) and the predictor columns used for grouping.

subgroup_table <- function(preds, group_col, threshold, tolerance = 0.10) {
  preds <- preds[!is.na(preds[[group_col]]), ]
  preds$flag <- preds$.pred_insecure >= threshold
  preds$pos  <- preds$truth == "insecure"
  overall_recall <- sum(preds$flag & preds$pos) / sum(preds$pos)

  groups <- split(preds, as.character(preds[[group_col]]))
  out <- do.call(rbind, lapply(names(groups), function(g) {
    d  <- groups[[g]]
    tp <- sum(d$flag & d$pos); fn <- sum(!d$flag & d$pos); fp <- sum(d$flag & !d$pos)
    # 95% interval for recall (Wilson score). Wide intervals = too few households to judge.
    ci <- if (tp + fn > 0) suppressWarnings(prop.test(tp, tp + fn, correct = FALSE)$conf.int) else c(NA, NA)
    data.frame(variable = group_col, group = g,
               households = nrow(d), insecure = tp + fn,
               recall = round(tp / (tp + fn), 3),
               recall_95_low = round(ci[1], 3), recall_95_high = round(ci[2], 3),
               false_negative_rate = round(fn / (tp + fn), 3),
               precision = if (tp + fp > 0) round(tp / (tp + fp), 3) else NA,
               pct_flagged = round(100 * mean(d$flag), 1))
  }))
  out$gap_vs_overall   <- round(out$recall - overall_recall, 3)
  out$within_tolerance <- abs(out$gap_vs_overall) <= tolerance
  out
}

# Bands used in the work split (income, household size, grants). Agree the cut-points
# with Person B so both tables use the same groups. Income cut-points are close to the
# quartiles of the M2 data (R2,470 / R5,030 / R11,418).
add_bands <- function(preds) {
  preds$income_band <- cut(preds$TotalMonthlyHouseholdIncomeRaw, c(-Inf, 2500, 5000, 11500, Inf),
                           labels = c("< R2,500", "R2,500-5,000", "R5,000-11,500", "> R11,500"))
  preds$size_band   <- cut(preds$HouseholdSize, c(0, 2, 4, 6, Inf), labels = c("1-2", "3-4", "5-6", "7+"))
  preds$grant_band  <- ifelse(preds$SocialGrantRecipients > 0, "Receives grants", "No grants")
  preds
}

# Example (Thursday/Friday, once A and B have produced test-set predictions):
# preds <- add_bands(readRDS("<B's test predictions>.rds"))
# fairness <- do.call(rbind, lapply(c("GeoTypeCode", "income_band", "size_band", "grant_band"),
#                                   function(g) subgroup_table(preds, g, threshold = <B's threshold>)))
# write.csv(fairness, "outputs/fairness_subgroups.csv", row.names = FALSE)
