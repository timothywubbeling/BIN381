# 00_placeholder_model.R
# TEMPORARY model so the Shiny app can be built before Person A's hand-off.
# Same predictors, same input format and same output columns as the real model,
# so swapping it out on Thursday is a one-line change in app/app.R.
library(dplyr)
library(recipes)
library(parsnip)
library(workflows)

set.seed(381)
CLEAN_DIR <- "data/clean/"

d05 <- readRDS(file.path(CLEAN_DIR, "D05_clean.rds"))
d06 <- readRDS(file.path(CLEAN_DIR, "D06_clean.rds"))
d07 <- readRDS(file.path(CLEAN_DIR, "D07_clean.rds"))
d09 <- readRDS(file.path(CLEAN_DIR, "D09_clean.rds"))

fi_items <- c("WorriedFoodWouldRunOutCode", "UnableToEatHealthyFoodCode", "AteFewFoodsCode",
              "SkippedMealCode", "AteLessCode", "RanOutOfFoodCode",
              "HungryButDidNotEatCode", "WholeDayWithoutEatingCode")

hh <- d07 %>%
  select(HouseholdID, all_of(fi_items), HouseholdSize, TotalMonthlyHouseholdIncomeRaw, GeoTypeCode) %>%
  inner_join(select(d09, HouseholdID, ComparativeIncomeCode, SocialGrantRecipients), by = "HouseholdID") %>%
  inner_join(select(d06, HouseholdID, ElectricityAccessCode), by = "HouseholdID") %>%
  inner_join(select(d05, HouseholdID, MainToiletCode), by = "HouseholdID") %>%
  mutate(fi_score = rowSums(across(all_of(fi_items), ~ .x == 1)),
         food_insecure = factor(if_else(fi_score >= 1, "insecure", "secure"),
                                levels = c("insecure", "secure"))) %>%
  filter(!is.na(food_insecure)) %>%
  select(-all_of(fi_items), -fi_score, -HouseholdID)   # leakage rule: FI items never reach the model

# The workflow takes the RAW validated codes; every conversion happens inside the recipe.
rec <- recipe(food_insecure ~ ., data = hh) %>%
  step_mutate(TotalMonthlyHouseholdIncomeRaw = log1p(TotalMonthlyHouseholdIncomeRaw),
              GeoTypeCode           = factor(GeoTypeCode, levels = 1:3),
              ElectricityAccessCode = factor(ElectricityAccessCode, levels = 1:2),
              MainToiletCode        = factor(MainToiletCode, levels = 1:12)) %>%
  step_impute_median(all_numeric_predictors()) %>%
  step_impute_mode(all_nominal_predictors()) %>%
  step_dummy(all_nominal_predictors())

wf <- workflow() %>%
  add_recipe(rec) %>%
  add_model(logistic_reg() %>% set_engine("glm")) %>%
  fit(data = hh)

# Reference values: "typical household" for the contributing-factor explanation,
# and the training distribution that the drift (PSI) checks compare against.
source("R/make_reference.R")
reference <- make_reference(hh, model_version = "placeholder-glm-0.1")

dir.create("models", showWarnings = FALSE)
saveRDS(wf, "models/placeholder_workflow.rds")
saveRDS(reference, "models/reference.rds")
cat("Placeholder model saved. Rows used:", nrow(hh), "\n")
