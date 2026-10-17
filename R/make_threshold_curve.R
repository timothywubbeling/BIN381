# scripts/make_threshold_curve.R  --  Milestone 4, Person C (Timothy Wubbeling)
#
# Builds data/powerbi/powerbi_threshold_curve.csv: the test-set screening metrics at
# every candidate referral threshold from 0.05 to 0.90. The dashboard uses it for the
# "Recall, precision and referral load at every threshold" line chart, which is the
# static companion to the interactive Threshold what-if slicer.
#
# Rudi documented this curve as prose in docs/powerbi_m4_person_b_pages.md; this script
# makes it a table so the dashboard can show it and so it is regenerated whenever the
# model is retrained.
#
# Run from the repository root:
#   Rscript scripts/make_threshold_curve.R
# or with explicit paths:
#   Rscript scripts/make_threshold_curve.R <households.csv> <out.csv>

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(tibble)
})

args <- commandArgs(trailingOnly = TRUE)
in_path  <- if (length(args) >= 1) args[1] else "data/powerbi/powerbi_households.csv"
out_path <- if (length(args) >= 2) args[2] else "data/powerbi/powerbi_threshold_curve.csv"

DEPLOYED <- 0.24

hh <- read_csv(in_path, show_col_types = FALSE) %>% filter(Split == "Test")

n_test    <- nrow(hh)
n_at_risk <- sum(hh$AtRisk)

stopifnot(n_test == 6279, n_at_risk == 1919)

grid <- round(seq(0.05, 0.90, by = 0.01), 2)

curve <- lapply(grid, function(t) {
  referred <- hh$ModelProbability >= t
  n_ref    <- sum(referred)
  tp       <- sum(referred & hh$AtRisk == 1)
  tibble(
    Threshold       = sprintf("%.2f", t),
    Referred        = n_ref,
    ReferredShare   = round(n_ref / n_test, 6),
    TruePositives   = tp,
    Recall          = round(tp / n_at_risk, 6),
    Precision       = if (n_ref > 0) round(tp / n_ref, 6) else NA_real_,
    ReferredPer1000 = round(1000 * n_ref / n_test),
    MissedAtRisk    = n_at_risk - tp,
    IsDeployed      = if (abs(t - DEPLOYED) < 1e-9) "Deployed threshold" else "Other"
  )
}) %>% bind_rows()

write_csv(curve, out_path, na = "")
message(sprintf("wrote %s (%d rows)", out_path, nrow(curve)))

# ---------------------------------------------------------------- reconciliation
# The deployed row must match data/powerbi/powerbi_model_summary.csv exactly.
deployed <- curve %>% filter(IsDeployed == "Deployed threshold")

message("\nDeployed threshold row, against the evaluation outputs:")
message(sprintf("  recall     %.3f   (model summary: 0.807)", deployed$Recall))
message(sprintf("  precision  %.3f   (model summary: 0.419)", deployed$Precision))
message(sprintf("  referred   %.3f   (model summary: 0.589)", deployed$ReferredShare))

stopifnot(
  abs(deployed$Recall        - 0.807191) < 5e-4,
  abs(deployed$Precision     - 0.418762) < 5e-4,
  abs(deployed$ReferredShare - 0.589107) < 5e-4
)

# Spot-checks against Rudi's documented what-if table.
expected <- tribble(
  ~t,     ~recall, ~precision, ~referred,
  "0.14",   0.959,      0.350,     0.838,
  "0.20",   0.875,      0.387,     0.692,
  "0.22",   0.846,      0.402,     0.643,
  "0.24",   0.807,      0.419,     0.589,
  "0.26",   0.764,      0.441,     0.530,
  "0.30",   0.678,      0.473,     0.438,
  "0.35",   0.582,      0.512,     0.347,
  "0.40",   0.474,      0.553,     0.262,
  "0.50",   0.311,      0.624,     0.152
)

check <- expected %>%
  inner_join(curve, by = c("t" = "Threshold")) %>%
  mutate(ok = abs(recall - Recall) < 1e-3 &
              abs(precision - Precision) < 1e-3 &
              abs(referred - ReferredShare) < 1e-3)

message(sprintf("\nwhat-if curve spot-checks: %d of %d rows match the hand-over table",
                sum(check$ok), nrow(check)))
if (!all(check$ok)) {
  print(check %>% filter(!ok))
  stop("threshold curve no longer reconciles with docs/powerbi_m4_person_b_pages.md")
}
message("threshold curve reconciled.")
