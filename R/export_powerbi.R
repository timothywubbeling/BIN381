# export_powerbi.R  -  run from the repo root: source("R/export_powerbi.R")
# Builds the tables for the Milestone 3 Power BI dashboard (second iteration) in data/powerbi/.
# Every household is scored with the deployed model through the app's own conversion
# (to_model_input), so the dashboard shows the same probabilities as the app.
# Business Objective 3 requires the dashboard to reconcile with R summary tables:
# powerbi_reconciliation.csv holds the numbers each dashboard visual must match.
library(dplyr)
library(workflows)
source("app/R/score.R")   # PREDICTORS is defined in validate.R
source("app/R/validate.R")

OUT_DIR   <- "data/powerbi"
THRESHOLD <- read.csv("data/evaluation/monitoring_baseline.csv")$threshold
dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

wf    <- readRDS("models/final_workflow.rds")
train <- readRDS("data/integrated/M2_train.rds") %>% mutate(Split = "Train")
test  <- readRDS("data/integrated/M2_test.rds")  %>% mutate(Split = "Test")
hh    <- bind_rows(train, test)
stopifnot(nrow(hh) == 20925)

# GHS 2024 toilet codes 1-12 (variable san_toil); the same labels as the app (app/app.R)
toilet_labels <- c("Flush toilet: public sewerage", "Flush toilet: septic or conservancy tank",
                   "Pour/bucket-flush toilet: septic tank or seepage pit", "Chemical/portable toilet",
                   "Pit latrine with ventilation pipe (VIP)", "Pit latrine without ventilation pipe, with slab",
                   "Pit latrine without ventilation pipe, no slab or open pit", "Bucket toilet (collected by municipality)",
                   "Bucket toilet (emptied by household)", "Composting toilet", "Open defecation (no facility)",
                   "Other toilet facility")

province_names <- c("Western Cape", "Eastern Cape", "Northern Cape", "Free State", "KwaZulu-Natal",
                    "North West", "Gauteng", "Mpumalanga", "Limpopo")

households <- hh %>%
  mutate(
    ModelProbability = round(predict_risk(wf, hh[PREDICTORS]), 4),
    ReferForReview   = as.integer(ModelProbability >= THRESHOLD),
    Province         = province_names[ProvinceCode],
    Settlement       = c("Urban", "Traditional/tribal", "Farms")[GeoTypeCode],
    IncomeChange     = c("1 Much higher", "2", "3", "4", "5 Much lower")[ComparativeIncomeCode],
    Electricity      = c("Yes", "No")[ElectricityAccessCode],
    IncomeBand       = as.character(cut(TotalMonthlyHouseholdIncomeRaw, c(-Inf, 2500, 5000, 11500, Inf),
                                        labels = c("< R2,500", "R2,500-5,000", "R5,000-11,500", "> R11,500"))),
    SizeBand         = as.character(cut(HouseholdSize, c(0, 2, 4, 6, Inf), labels = c("1-2", "3-4", "5-6", "7+"))),
    GrantBand        = ifelse(SocialGrantRecipients > 0, "Receives grants", "No grants"),
    AtRisk           = as.integer(Food_Insecure_Binary == "Insecure"),
    Severe           = as.integer(Vulnerability_Tier == "Severely food insecure")
  ) %>%
  transmute(                                  # no HouseholdID: the dashboard does not need it
    HouseholdKey = row_number(), Split, Province, ProvinceCode, Settlement,
    HouseholdSize, SizeBand, MonthlyIncome = TotalMonthlyHouseholdIncomeRaw, IncomeBand, IncomeChange,
    Electricity, GrantRecipients = SocialGrantRecipients, GrantBand, ToiletCode = MainToiletCode,
    ToiletType = toilet_labels[MainToiletCode],
    FI_Score, Tier = as.character(Vulnerability_Tier), AtRisk, Severe,
    ModelProbability, ReferForReview, HouseholdWeight)
households$IncomeBand[is.na(households$IncomeBand)] <- "Unknown"
households$SizeBand[is.na(households$SizeBand)]     <- "Unknown"
write.csv(households, file.path(OUT_DIR, "powerbi_households.csv"), row.names = FALSE, na = "")

# Model results for the screening page (Person B's evaluation, test set)
b <- read.csv("data/evaluation/monitoring_baseline.csv")
sm <- read.csv("data/evaluation/evaluation_matrix.csv") %>% filter(model == b$model)
write.csv(data.frame(
  Metric = c("Threshold", "Recall (at-risk households found)", "Precision (referrals at risk)",
             "Share of households referred", "ROC-AUC", "PR-AUC", "Brier score", "Test households"),
  Value  = c(b$threshold, b$test_recall, b$test_precision, b$test_pct_flagged,
             b$test_roc_auc, sm$screen_pr_auc, b$test_brier, nrow(test))),
  file.path(OUT_DIR, "powerbi_model_summary.csv"), row.names = FALSE)

sub <- read.csv("data/evaluation/subgroup_performance.csv") %>%
  mutate(variable = recode(variable, GeoTypeCode = "Settlement type", income_band = "Monthly income",
                           size_band = "Household size", grant_band = "Grant receipt", province = "Province"),
         group = recode(group, Traditional_Tribal = "Traditional/tribal"),
         within_tolerance = ifelse(within_10_points, "Yes", "No"))
write.csv(sub, file.path(OUT_DIR, "powerbi_subgroup_performance.csv"), row.names = FALSE)

imp <- read.csv("data/evaluation/permutation_importance.csv") %>% filter(model == "binary") %>%
  transmute(Predictor = variable, AUC_drop = round(auc_drop, 4), Rank = rank)
write.csv(imp, file.path(OUT_DIR, "powerbi_permutation_importance.csv"), row.names = FALSE)
write.csv(read.csv("data/evaluation/odds_ratios.csv") %>%
            transmute(Term = term, OddsRatio = estimate, CI_low = conf.low, CI_high = conf.high, p_value = p.value),
          file.path(OUT_DIR, "powerbi_odds_ratios.csv"), row.names = FALSE)

# Reconciliation: the numbers the dashboard must reproduce (Business Objective 3)
recon <- function(d, by) {
  d %>% group_by(.data[[by]]) %>%
    summarise(Households = n(),
              AtRiskPct_unweighted = round(100 * mean(AtRisk), 1),
              AtRiskPct_weighted   = round(100 * weighted.mean(AtRisk, HouseholdWeight), 1),
              SeverePct_weighted   = round(100 * weighted.mean(Severe, HouseholdWeight), 1),
              ReferredPct          = round(100 * mean(ReferForReview), 1),
              .groups = "drop") %>%
    rename(Group = 1) %>% mutate(Breakdown = by, .before = 1)
}
all_hh <- households %>% mutate(All = "All households")
reconciliation <- bind_rows(recon(all_hh, "All"), recon(households, "Province"),
                            recon(households, "Settlement"), recon(households, "IncomeBand"))
write.csv(reconciliation, file.path(OUT_DIR, "powerbi_reconciliation.csv"), row.names = FALSE)

cat("Power BI tables written to", OUT_DIR, ":", paste(list.files(OUT_DIR), collapse = ", "), "\n")
print(reconciliation %>% filter(Breakdown %in% c("All", "Province")), n = 20)
