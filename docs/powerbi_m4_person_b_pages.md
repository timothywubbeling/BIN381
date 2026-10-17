# Milestone 4 Power BI: Person B's pages (model performance, subgroups, drivers)

Person B leads the Milestone 4 dashboard and owns the model-performance and subgroup pages, the
drivers page, and the overall layout and navigation. Alexander owns the data and household pages;
Timothy reconciles every figure against R and saves the final `.pbix`.

**Start from a new file, not from `Main Dash.pbix`.** That file is the Milestone 1/2 dashboard
(Data Inventory, Data Quality, Distributions, Food Security, Relationships) and it is built on the
raw `D0x` tables. Milestone 4 asks for a decision-support dashboard built on the *final analytical
dataset*, which is `data/powerbi/`. Keep `Main Dash.pbix` for reference and as evidence of the
first iteration; its Food Security page is a good model for Alexander's household pages.

Save the new file as `powerbi/BIN381_M4_Dashboard.pbix` and commit it.

---

## 1. Decision questions

The brief is explicit: *"Avoid dashboards that merely display every variable. The dashboard should
answer defined decision questions."* Put these on the landing page as text, and give each page a
title that answers one of them. Person B owns questions 3, 4 and 5.

| # | Decision question | Page | Owner |
|---|---|---|---|
| 1 | Where are food-insecure households concentrated? | Where the need is | A |
| 2 | Which kinds of household are most affected? | Who is affected | A |
| 3 | Can we trust the screening tool enough to act on it? | How well the screen works | **B** |
| 4 | Which households does the screen miss, and where? | Who the screen misses | **B** |
| 5 | What should we ask about to spot risk early? | What drives risk | **B** |
| 6 | How many households would a given threshold send for follow-up? | How well the screen works (what-if) | **B** |

---

## 2. Load the data

**Home → Get data → Text/CSV**, from `data/powerbi/`. Person B's pages need four of the six tables:

| File | Used on |
|---|---|
| `powerbi_model_summary.csv` | How well the screen works (cards) |
| `powerbi_households.csv` | How well the screen works (what-if, score distribution) |
| `powerbi_subgroup_performance.csv` | Who the screen misses |
| `powerbi_permutation_importance.csv`, `powerbi_odds_ratios.csv` | What drives risk |

The tables are independent — **do not create relationships between them**. They are different grains
(household, subgroup, predictor) and relating them will silently cross-filter the wrong things.

In Power Query, confirm the types: `ModelProbability`, `HouseholdWeight`, `MonthlyIncome`,
`recall`, `precision`, `pct_flagged`, `AUC_drop`, `OddsRatio` must all be **Decimal Number**, and
the 0/1 flags (`AtRisk`, `Severe`, `ReferForReview`) **Whole Number**.

---

## 3. Measures

Create these on `powerbi_households` (Modeling → New measure). Format every percentage as a
percentage with one decimal.

```DAX
Test households = CALCULATE(COUNTROWS(powerbi_households), powerbi_households[Split] = "Test")

At-risk households (test) =
CALCULATE(SUM(powerbi_households[AtRisk]), powerbi_households[Split] = "Test")
```

### 3.1 The what-if threshold (decision question 6)

**Modeling → New parameter → Numeric range**: name `Threshold`, minimum `0`, maximum `1`,
increment `0.01`, default `0.24`. Tick "Add slicer to this page". Power BI creates a
`Threshold` table with a `Threshold Value` measure. Then add:

```DAX
Referred at threshold =
VAR T = [Threshold Value]
RETURN DIVIDE(
    CALCULATE(COUNTROWS(powerbi_households),
              powerbi_households[Split] = "Test",
              powerbi_households[ModelProbability] >= T),
    [Test households])

Recall at threshold =
VAR T = [Threshold Value]
RETURN DIVIDE(
    CALCULATE(SUM(powerbi_households[AtRisk]),
              powerbi_households[Split] = "Test",
              powerbi_households[ModelProbability] >= T),
    [At-risk households (test)])

Precision at threshold =
VAR T = [Threshold Value]
RETURN DIVIDE(
    CALCULATE(SUM(powerbi_households[AtRisk]),
              powerbi_households[Split] = "Test",
              powerbi_households[ModelProbability] >= T),
    CALCULATE(COUNTROWS(powerbi_households),
              powerbi_households[Split] = "Test",
              powerbi_households[ModelProbability] >= T))

Households referred (per 1,000) = ROUND([Referred at threshold] * 1000, 0)
```

`Households referred (per 1,000)` turns the percentage into something a programme manager can act
on: *"at this threshold you will visit this many households per thousand."*

**Every one of these measures is filtered to `Split = "Test"` on purpose.** Recall and precision
are only meaningful on the held-out test set. If you drop that filter the numbers will quietly
include training households the model has already seen, and they will not match the report.

### 3.2 Friendly labels

The exported tables use the modelling variable names. Add these calculated columns so the dashboard
reads like a report rather than a codebook.

On `powerbi_permutation_importance`:

```DAX
Driver =
SWITCH(powerbi_permutation_importance[Predictor],
    "ComparativeIncomeCode", "Income change vs a year ago",
    "Income_PerCapita",      "Income per person",
    "SocialGrantRecipients", "Number of grant recipients",
    "Income_Log",            "Household income",
    "ElectricityAccessCode", "Electricity access",
    "GeoTypeCode",           "Settlement type",
    "MainToiletCode",        "Toilet type",
    "HouseholdSize",         "Household size",
    powerbi_permutation_importance[Predictor])
```

On `powerbi_odds_ratios`:

```DAX
Factor =
SWITCH(powerbi_odds_ratios[Term],
    "ComparativeIncomeCode2", "Income a little higher than a year ago",
    "ComparativeIncomeCode3", "Income about the same",
    "ComparativeIncomeCode4", "Income a little lower",
    "ComparativeIncomeCode5", "Income much lower",
    "GeoTypeCodeTraditional_Tribal", "Traditional / tribal area",
    "GeoTypeCodeFarms",       "Farm",
    "HouseholdSize",          "Each extra household member",
    "Income_Log",             "Higher household income",
    "ElectricityAccessCodeNo","No electricity",
    "SocialGrantRecipients",  "Each extra grant recipient",
    "MainToiletCode2",        "Flush toilet, septic tank",
    "MainToiletCode5",        "Pit latrine with ventilation pipe",
    "MainToiletCode6",        "Pit latrine, no pipe, with slab",
    "MainToiletCode7",        "Pit latrine, no pipe, no slab",
    "MainToiletCodeOther",    "Other toilet type",
    powerbi_odds_ratios[Term])

Significant = IF(powerbi_odds_ratios[p_value] < 0.05, "Yes", "No")

Direction =
IF(powerbi_odds_ratios[CI_low] > 1, "Raises risk",
   IF(powerbi_odds_ratios[CI_high] < 1, "Lowers risk", "No clear effect"))
```

On `powerbi_subgroup_performance`:

```DAX
Recall gap (points) = ROUND(powerbi_subgroup_performance[gap_vs_overall] * 100, 1)
```

---

## 4. Page specifications

### Page 3 — "How well the screen works"

Answers decision questions 3 and 6. Title: **How well does the screening tool work?**

- **Four cards** across the top, from `powerbi_model_summary` (put `Metric` in the visual's filter
  pane and select one value per card): *Recall*, *Precision*, *Share of households referred*,
  *ROC-AUC*. Rename them in plain language on the card title:
  - Recall → "At-risk households found"
  - Precision → "Referrals that are genuinely at risk"
  - Share referred → "Households sent for follow-up"
  - ROC-AUC → "Ranking quality (0.5 = coin flip)"
- **What-if panel**: the `Threshold` slicer, plus three cards showing *Recall at threshold*,
  *Precision at threshold* and *Households referred (per 1,000)*. This is the interactivity the
  rubric asks for — moving the slicer must visibly move all three.
- **Score distribution**: clustered column chart of `ModelProbability` from `powerbi_households`,
  filtered to `Split = "Test"`, binned at 0.05 (right-click the field → New group → Bin size 0.05),
  with `AtRisk` on the legend so the two populations overlap. Add a constant line at **0.24** from
  the Analytics pane, labelled "Referral threshold".
- **Text box** (bottom): *"Screening aid only. Every referral is reviewed by an official.
  'Lower risk' is not clearance. Recall and precision are measured on the 6,279-household held-out
  test set."*

### Page 4 — "Who the screen misses"

Answers decision question 4. Title: **Which households does the screen miss?**

- **Bar chart**: `group` on the axis, `recall` as the value, from `powerbi_subgroup_performance`,
  sorted ascending so the worst group is at the top. Colour by `within_tolerance` (Yes = neutral,
  No = warning colour) with conditional formatting.
- **Slicer** on `variable` (Settlement type, Monthly income, Household size, Grant receipt,
  Province) — this is the drill-down: one chart, five different cuts.
- **Constant lines** on the bar chart at **0.707** and **0.907** (Analytics pane), labelled
  "10-point tolerance band". Overall recall is 0.807, so a bar outside this band is a group the
  team has agreed to treat as a real gap.
- **Table**: `group`, `households`, `at_risk`, `recall`, `recall_95_low`, `recall_95_high`,
  `precision`, `Recall gap (points)`. Keep the confidence interval columns — they are what stops a
  reader over-reading a small group such as Farms (197 test households).
- **Text box**: *"A wide confidence interval means the group is too small to judge. The screen is
  weakest for higher-income and no-grant households — exactly where food insecurity is least
  expected."*

### Page 5 — "What drives risk"

Answers decision question 5. Title: **What should we ask about to spot risk early?**

- **Bar chart**: `Driver` by `AUC_drop` from `powerbi_permutation_importance`, sorted descending.
  Title it "How much the screen relies on each answer".
- **Table**: `Factor`, `OddsRatio`, `CI_low`, `CI_high`, `Direction`, `Significant` from
  `powerbi_odds_ratios`, sorted by `OddsRatio` descending. Apply data bars to `OddsRatio` with the
  axis at 1.0 so "raises risk" and "lowers risk" point in opposite directions.
- **Comparison columns** (from `powerbi_households`, Alexander's weighted measure): at-risk share by
  `IncomeChange` (the U-shape behind H1), by `Electricity` (H4) and by `GrantBand` (H5, reversed).
- **Text box**: *"Associations, not causes. Grant receipt marks households that were targeted
  because they are poor; it is not evidence that grants cause food insecurity."*

### Layout and navigation (Person B owns this across all pages)

- A title bar at the top of every page: **"Household food insecurity — GHS 2024 — Group P1"**,
  then the page's own question as a subtitle.
- Page navigator (Insert → Buttons → Navigator → Page navigator) in the same position on every page.
- One colour per meaning, used everywhere: one colour for at-risk/attention, one neutral, one for
  "below tolerance". Do not re-use the at-risk colour for anything else.
- Every axis labelled, every percentage formatted to one decimal.
- A footnote on every page: *"Source: Stats SA General Household Survey 2024, 20,925 households.
  Population percentages are weighted with HouseholdWeight."*
- **No household identifiers anywhere.** `powerbi_households.csv` deliberately ships a
  `HouseholdKey` row number instead of `HouseholdID`; do not add the real ID back.

---

## 5. Reconciliation — the numbers these pages must show

Business Objective 3 requires the dashboard to reconcile with the R outputs. Check each of these
with **no slicer active** before saving. Every value below was recomputed from
`data/powerbi/powerbi_households.csv` and matches `data/evaluation/evaluation_matrix.csv` exactly.

| Visual | Expected |
|---|---|
| Recall card | 80.7% |
| Precision card | 41.9% |
| Share referred card | 58.9% |
| ROC-AUC card | 0.736 |
| Test households | 6,279 (1,919 at risk) |
| What-if at 0.24: recall / precision / referred | 80.7% / 41.9% / 58.9% |
| Worst subgroup recall (income > R11,500) | 39.2% |
| No-grant households recall | 61.7% |
| Best subgroup recall (7+ members) | 95.9% |
| Top driver (income change vs a year ago) | AUC drop 0.082 |

### What-if verification curve

If the what-if measures are written correctly, moving the slicer reproduces this curve on the test
set. Spot-check three rows after building it.

| Threshold | Recall | Precision | Referred (test) |
|---|---|---|---|
| 0.14 | 95.9% | 35.0% | 83.8% |
| 0.20 | 87.5% | 38.7% | 69.2% |
| 0.22 | 84.6% | 40.2% | 64.3% |
| **0.24** | **80.7%** | **41.9%** | **58.9%** |
| 0.26 | 76.4% | 44.1% | 53.0% |
| 0.30 | 67.8% | 47.3% | 43.8% |
| 0.35 | 58.2% | 51.2% | 34.7% |
| 0.40 | 47.4% | 55.3% | 26.2% |
| 0.50 | 31.1% | 62.4% | 15.2% |

### One trap to avoid

`powerbi_reconciliation.csv` reports **59.2%** referred, because it covers all 20,925 households
(train and test). The report and every card on Person B's pages quote **58.9%**, the test-set
figure. Both are right; they are different populations. Keep the `Split = "Test"` filter on the
model-performance visuals and label Alexander's all-household figure separately, or the dashboard
and the report will appear to disagree in front of a marker.

---

## 6. Before handing over to Timothy

- [ ] Screenshot each of the three pages at 1920×1080 for the report (Section 5) and slides 5–7.
      Save to `docs/figures/` as `pbi_b1_performance.png`, `pbi_b2_subgroups.png`,
      `pbi_b3_drivers.png`.
- [ ] Check every number in the reconciliation table above with no slicer active.
- [ ] Set the what-if slicer back to **0.24** before saving, so the file opens on the deployed
      threshold.
- [ ] Confirm no page shows a household identifier.
- [ ] Save as `powerbi/BIN381_M4_Dashboard.pbix` and commit.
