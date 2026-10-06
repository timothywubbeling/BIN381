# Power BI dashboard (Milestone 3, second iteration): build guide

The project outline lists an interactive Power BI dashboard among the Milestone 3 deliverables,
and the Milestone 1 plan promised its second iteration here. The data is ready in `data/powerbi/`
(made by `R/export_powerbi.R`); this guide builds the dashboard in Power BI Desktop in about
30–45 minutes. Save it as `powerbi/BIN381_M3_Dashboard.pbix` and commit it.

## 1. Load the data

**Home → Get data → Text/CSV**, and load these files from `data/powerbi/`:

| File | What it holds |
|---|---|
| `powerbi_households.csv` | 20,925 households: province, settlement type, income band, size band, grant band, electricity, income change, FI Score and tier, at-risk flag, survey weight, the deployed model's probability and referral flag, train/test split |
| `powerbi_subgroup_performance.csv` | Recall, precision and share referred by subgroup (test set), with the 10-point tolerance flag |
| `powerbi_permutation_importance.csv` | How much each predictor matters to the deployed model |
| `powerbi_odds_ratios.csv` | Odds ratios with 95% confidence intervals |
| `powerbi_model_summary.csv` | Threshold, recall, precision, share referred, ROC-AUC, PR-AUC, Brier score |
| `powerbi_reconciliation.csv` | The numbers the dashboard must reproduce (Section 5) |

The tables are independent; no relationships are needed. In Power Query, check that
`HouseholdWeight`, `ModelProbability`, `MonthlyIncome` and the 0/1 flags are numbers.

## 2. Measures (Modeling → New measure, on `powerbi_households`)

Population claims must use the survey weights (Milestone 1 ethics commitment).

```DAX
Households in sample = COUNTROWS(powerbi_households)

At-risk % (weighted) =
DIVIDE(SUMX(powerbi_households, powerbi_households[AtRisk] * powerbi_households[HouseholdWeight]),
       SUM(powerbi_households[HouseholdWeight]))

Severe % (weighted) =
DIVIDE(SUMX(powerbi_households, powerbi_households[Severe] * powerbi_households[HouseholdWeight]),
       SUM(powerbi_households[HouseholdWeight]))

Estimated SA households at risk =
SUMX(powerbi_households, powerbi_households[AtRisk] * powerbi_households[HouseholdWeight])

Referred % = AVERAGE(powerbi_households[ReferForReview])

Average model probability = AVERAGE(powerbi_households[ModelProbability])
```

Format the percentage measures as percentages with one decimal.

## 3. Pages

**Page 1 – Where food insecurity is (Business Objective 3)**
- Cards: *Households in sample*, *At-risk % (weighted)*, *Severe % (weighted)*, *Estimated SA households at risk*.
- Bar chart: `Province` on the axis, *At-risk % (weighted)* as the value, sorted descending.
- Clustered bar charts: *At-risk % (weighted)* by `Settlement`, by `IncomeBand` and by `GrantBand`.
- Slicers: `Province`, `Settlement`, `IncomeBand`, `GrantBand`, `Electricity`.

**Page 2 – What is associated with it (Task 3)**
- Bar chart: `Predictor` by `AUC_drop` (permutation importance), sorted descending.
- Column charts: *At-risk % (weighted)* by `IncomeChange` (shows the U-shape behind H1), by
  `Electricity` (H4), by `SizeBand` (H3) and by `GrantBand` (H5, reversed).
- Table: `powerbi_odds_ratios` (Term, OddsRatio, CI_low, CI_high, p_value).
- Text box: "Associations, not causes. Grant receipt marks targeted, poorer households."

**Page 3 – The screening model (Tasks 2 and 4)**
- Cards from `powerbi_model_summary` (filter each card on `Metric`): recall, precision,
  share of households referred, ROC-AUC.
- Bar chart: `group` by `recall` from `powerbi_subgroup_performance`, with a slicer on
  `variable`. Add constant lines at 0.707 and 0.907 (Analytics pane) for the 10-point tolerance,
  and colour bars by `within_tolerance`.
- Histogram (column chart of `ModelProbability` binned at 0.05, filtered to `Split = Test`) with a
  constant line at the 0.24 threshold.
- Text box: "Screening aid only. Every referral is reviewed by an official; 'Lower risk' is not clearance."

## 4. Title and notes
Add a title bar on each page ("Household food insecurity – GHS 2024 – Group P1") and a footnote:
"Source: Stats SA General Household Survey 2024; percentages weighted with HouseholdWeight."

## 5. Reconcile with R (Business Objective 3 success criterion)
Milestone 1 set the criterion that the dashboard must reconcile with the R summary tables.
Compare the dashboard with `powerbi_reconciliation.csv`, for example:

| Check | Expected |
|---|---|
| At-risk % (weighted), all households | 28.3% |
| Eastern Cape, at-risk % (weighted) | 43.0% |
| Limpopo, at-risk % (weighted) | 13.1% |
| Referred %, all households | see `ReferredPct` in the file |

If a value differs, check that the measure uses `HouseholdWeight` and that no slicer is active.
Take a screenshot of each page for the report.
