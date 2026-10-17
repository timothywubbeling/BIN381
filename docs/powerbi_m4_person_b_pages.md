# Milestone 4 Power BI — Person B's pages: hand-over and build steps

**Open `powerbi/BIN381_M4_Dashboard.pbix`.** The data plumbing is already done in that file. This
document is the rest: six measures to paste, then three pages to build.

Person B owns the model-performance and subgroup pages, the drivers page, and the layout and
navigation across the whole report. Alexander owns the data and household pages; Timothy reconciles
every figure against R and saves the final file.

> **Do not build on `Main Dash.pbix`.** That is the Milestone 1/2 dashboard (Data Inventory, Data
> Quality, Distributions, Food Security, Relationships) and it reads the raw `D0x` tables.
> Milestone 4 asks for a decision-support dashboard on the *final analytical dataset*. Keep it as
> evidence of the first iteration — its Food Security page is a good model for Alexander's pages.

---

## 1. What is already in the file

| | |
|---|---|
| Tables loaded | `powerbi_households` (20,925 rows), `powerbi_model_summary`, `powerbi_odds_ratios`, `powerbi_permutation_importance`, `powerbi_subgroup_performance` |
| Relationships | **None, deliberately.** The tables are different grains (household, metric, predictor, subgroup). Do not create any — it will silently cross-filter the wrong things. |
| What-if parameter | `Threshold`, decimal, 0 to 1, step 0.01, default **0.24**, with its slicer sitting on Page 1 |
| Measures | `Test households` only — the other five are below |
| Import locale | Set to **English (United States)** |

### The one trap worth knowing

This machine's locale is English (South Africa), which uses a **comma** as the decimal separator.
On the first import every decimal column (`ModelProbability`, `recall`, `AUC_drop`, …) came in as
**text**, which silently breaks every chart. The fix is File → Options and settings → Options →
CURRENT FILE → Regional Settings → **Locale for import: English (United States)**, and it is
already applied to this file.

It is a *per-file* setting. If you ever start a new `.pbix` and import these CSVs again, set it
**before** the first import, or you will have to delete the tables and re-import. Values displaying
as `0,24` rather than `0.24` is only display formatting and is fine.

---

## 2. Housekeeping (1 minute)

In the Data pane, expand the **Threshold** table. Delete the stray field called **`Measure`**
(right-click → Delete from model) — it is an empty leftover. Keep `Threshold` and `Threshold Value`.

---

## 3. The five remaining measures

**Click `powerbi_households` in the Data pane first**, so each measure lands on that table. Then for
each one: **Home → New measure**, click into the formula bar, `Ctrl+A`, paste, `Enter`.

Each is a single line — paste it exactly as given.

```DAX
At-risk households (test) = CALCULATE(SUM(powerbi_households[AtRisk]), powerbi_households[Split] = "Test")
```

```DAX
Recall at threshold = VAR T = [Threshold Value] RETURN DIVIDE(CALCULATE(SUM(powerbi_households[AtRisk]), powerbi_households[Split] = "Test", FILTER(ALL(powerbi_households[ModelProbability]), powerbi_households[ModelProbability] >= T)), [At-risk households (test)])
```

```DAX
Referred at threshold = VAR T = [Threshold Value] RETURN DIVIDE(CALCULATE(COUNTROWS(powerbi_households), powerbi_households[Split] = "Test", FILTER(ALL(powerbi_households[ModelProbability]), powerbi_households[ModelProbability] >= T)), [Test households])
```

```DAX
Precision at threshold = VAR T = [Threshold Value] RETURN DIVIDE(CALCULATE(SUM(powerbi_households[AtRisk]), powerbi_households[Split] = "Test", FILTER(ALL(powerbi_households[ModelProbability]), powerbi_households[ModelProbability] >= T)), CALCULATE(COUNTROWS(powerbi_households), powerbi_households[Split] = "Test", FILTER(ALL(powerbi_households[ModelProbability]), powerbi_households[ModelProbability] >= T)))
```

```DAX
Households referred (per 1,000) = ROUND([Referred at threshold] * 1000, 0)
```

Then select `Recall at threshold`, `Referred at threshold` and `Precision at threshold` one at a
time and set **Measure tools → Format → Percentage, 1 decimal**.

**Why every one of them filters to `Split = "Test"`:** recall and precision are only meaningful on
the held-out test set. Drop that filter and the numbers quietly start including training households
the model has already seen, and they will no longer match the report.

### Two label columns

The exported tables carry modelling variable names. These make the dashboard read like a report.
Select the table, then **Table tools → New column**, and paste:

On `powerbi_permutation_importance`:

```DAX
Driver = SWITCH(powerbi_permutation_importance[Predictor], "ComparativeIncomeCode", "Income change vs a year ago", "Income_PerCapita", "Income per person", "SocialGrantRecipients", "Number of grant recipients", "Income_Log", "Household income", "ElectricityAccessCode", "Electricity access", "GeoTypeCode", "Settlement type", "MainToiletCode", "Toilet type", "HouseholdSize", "Household size", powerbi_permutation_importance[Predictor])
```

On `powerbi_odds_ratios`:

```DAX
Factor = SWITCH(powerbi_odds_ratios[Term], "ComparativeIncomeCode2", "Income a little higher than a year ago", "ComparativeIncomeCode3", "Income about the same", "ComparativeIncomeCode4", "Income a little lower", "ComparativeIncomeCode5", "Income much lower", "GeoTypeCodeTraditional_Tribal", "Traditional / tribal area", "GeoTypeCodeFarms", "Farm", "HouseholdSize", "Each extra household member", "Income_Log", "Higher household income", "ElectricityAccessCodeNo", "No electricity", "SocialGrantRecipients", "Each extra grant recipient", "MainToiletCode2", "Flush toilet, septic tank", "MainToiletCode5", "Pit latrine with ventilation pipe", "MainToiletCode6", "Pit latrine, no pipe, with slab", "MainToiletCode7", "Pit latrine, no pipe, no slab", "MainToiletCodeOther", "Other toilet type", powerbi_odds_ratios[Term])
```

```DAX
Direction = IF(powerbi_odds_ratios[CI_low] > 1, "Raises risk", IF(powerbi_odds_ratios[CI_high] < 1, "Lowers risk", "No clear effect"))
```

---

## 4. Decision questions

The brief is explicit: *"Avoid dashboards that merely display every variable. The dashboard should
answer defined decision questions."* Put these on the landing page as text, and title each page
with the question it answers. Person B owns 3, 4, 5 and 6.

| # | Decision question | Page | Owner |
|---|---|---|---|
| 1 | Where are food-insecure households concentrated? | Where the need is | A |
| 2 | Which kinds of household are most affected? | Who is affected | A |
| 3 | Can we trust the screening tool enough to act on it? | How well the screen works | **B** |
| 4 | Which households does the screen miss, and where? | Who the screen misses | **B** |
| 5 | What should we ask about to spot risk early? | What drives risk | **B** |
| 6 | How many households would a given threshold send for follow-up? | How well the screen works | **B** |

---

## 5. The three pages

### Page — "How well does the screening tool work?"

Rename Page 1 to this; the `Threshold` slicer is already on it.

- **Four cards** from `powerbi_model_summary`. Drag `Value` into a card, then in the Filters pane
  filter that card on `Metric` to a single value. Retitle each card in plain language:

  | Filter `Metric` to | Card title |
  |---|---|
  | Recall (at-risk households found) | At-risk households found |
  | Precision (referrals at risk) | Referrals that are genuinely at risk |
  | Share of households referred | Households sent for follow-up |
  | ROC-AUC | Ranking quality (0.5 = coin flip) |

- **What-if panel**: the `Threshold` slicer plus three cards — `Recall at threshold`,
  `Precision at threshold`, `Households referred (per 1,000)`. Moving the slicer must visibly move
  all three. This is the interactivity the rubric rewards.
- **Score distribution**: clustered column chart of `ModelProbability` (`powerbi_households`),
  filtered to `Split = "Test"`. Right-click the field → New group → Bin size **0.05**. Put `AtRisk`
  on the legend. Analytics pane → constant line at **0.24**, labelled "Referral threshold".
- **Text box**: *"Screening aid only. Every referral is reviewed by an official. 'Lower risk' is
  not clearance. Recall and precision are measured on the 6,279-household held-out test set."*

### Page — "Which households does the screen miss?"

- **Bar chart** from `powerbi_subgroup_performance`: `group` on the axis, `recall` as the value,
  sorted ascending so the worst group is on top. Colour by `within_tolerance`.
- **Slicer** on `variable` (Settlement type, Monthly income, Household size, Grant receipt,
  Province). One chart, five cuts — this is the drill-down.
- **Constant lines** at **0.707** and **0.907** (Analytics pane), labelled "10-point tolerance
  band". Overall recall is 0.807, so a bar outside the band is an agreed real gap.
- **Table**: `group`, `households`, `at_risk`, `recall`, `recall_95_low`, `recall_95_high`,
  `precision`. Keep the interval columns — they stop a reader over-reading a small group like Farms
  (197 test households).
- **Text box**: *"A wide confidence interval means the group is too small to judge. The screen is
  weakest for higher-income and no-grant households — exactly where food insecurity is least
  expected."*

### Page — "What should we ask about to spot risk early?"

- **Bar chart**: `Driver` by `AUC_drop` from `powerbi_permutation_importance`, sorted descending.
  Title it "How much the screen relies on each answer".
- **Table**: `Factor`, `OddsRatio`, `CI_low`, `CI_high`, `Direction` from `powerbi_odds_ratios`,
  sorted by `OddsRatio` descending. Data bars on `OddsRatio`.
- **Comparison columns** from `powerbi_households`: at-risk share by `IncomeChange` (the U-shape
  behind H1), by `Electricity` (H4) and by `GrantBand` (H5, reversed).
- **Text box**: *"Associations, not causes. Grant receipt marks households that were targeted
  because they are poor; it is not evidence that grants cause food insecurity."*

### Layout and navigation (Person B owns this across all pages)

- Title bar on every page: **"Household food insecurity — GHS 2024 — Group P1"**, with the page's
  own question as the subtitle.
- Page navigator (Insert → Buttons → Navigator → Page navigator) in the same position on every page.
- One colour per meaning throughout: one for at-risk/attention, one neutral, one for "below
  tolerance". Never reuse the at-risk colour for anything else.
- Every axis labelled; percentages to one decimal.
- Footnote on every page: *"Source: Stats SA General Household Survey 2024, 20,925 households.
  Population percentages are weighted with HouseholdWeight."*
- **No household identifiers anywhere.** `powerbi_households` ships a `HouseholdKey` row number
  instead of `HouseholdID` on purpose — do not add the real ID back.

---

## 6. Reconcile before saving

Check each of these with **no slicer active**. Every value was recomputed from
`powerbi_households.csv` and matches `data/evaluation/evaluation_matrix.csv` exactly.

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

Move the slicer and spot-check three of these rows.

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

### The 58.9% vs 59.2% trap

`powerbi_reconciliation.csv` reports **59.2%** referred, because it covers all 20,925 households
(train and test). The report and every card on your pages quote **58.9%**, the test-set figure.
Both are right; they are different populations. Keep the `Split = "Test"` filter on the
model-performance visuals, or the dashboard and the report will appear to disagree in front of a
marker. `report/M4/check_numbers.py` fails the build if the two get swapped.

---

## 7. Before handing to Timothy

- [ ] Screenshot each of the three pages at 1920×1080 into `docs/figures/` as
      `pbi_b1_performance.png`, `pbi_b2_subgroups.png`, `pbi_b3_drivers.png` — needed for report
      §5 and slides 5–7.
- [ ] Check every number in §6 with no slicer active.
- [ ] Set the `Threshold` slicer back to **0.24** before saving, so the file opens on the deployed
      threshold.
- [ ] Confirm no page shows a household identifier.
- [ ] Save and commit `powerbi/BIN381_M4_Dashboard.pbix`.
