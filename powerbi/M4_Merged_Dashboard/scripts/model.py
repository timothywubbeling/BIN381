# -*- coding: utf-8 -*-
"""Semantic model for the merged Milestone 4 dashboard (Group P1)."""
import hashlib

def lt(seed):
    h = hashlib.md5(('lineage/' + seed).encode()).hexdigest()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

ANN = [{"name": "SummarizationSetBy", "value": "Automatic"}]

def col(table, name, dtype, summarize="none", fmt=None, sort=None, hidden=False):
    c = {"name": name, "dataType": dtype, "sourceColumn": name,
         "summarizeBy": summarize, "lineageTag": lt(table + "/" + name),
         "annotations": list(ANN)}
    if fmt:
        c["formatString"] = fmt
    if sort:
        c["sortByColumn"] = sort
    if hidden:
        c["isHidden"] = True
    return c

def calc_col(table, name, expr, dtype=None, summarize="none", fmt=None, sort=None):
    c = {"name": name, "type": "calculated", "expression": expr,
         "isDataTypeInferred": True, "summarizeBy": summarize,
         "lineageTag": lt(table + "/" + name), "annotations": list(ANN)}
    if dtype:
        c["dataType"] = dtype
    if fmt:
        c["formatString"] = fmt
    if sort:
        c["sortByColumn"] = sort
    return c

def measure(table, name, expr, fmt=None, desc=None, folder=None):
    m = {"name": name, "expression": expr, "lineageTag": lt(table + "/m/" + name)}
    if fmt:
        m["formatString"] = fmt
    if desc:
        m["description"] = desc
    if folder:
        m["displayFolder"] = folder
    return m

def csv_partition(table, filename, types):
    typed = ", ".join('{{"{}", {}}}'.format(n, t) for n, t in types)
    expr = [
        "let",
        '    Source = Csv.Document(File.Contents(DataFolder & "%s"), '
        '[Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),' % filename,
        "    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),",
        '    Typed = Table.TransformColumnTypes(Promoted, {%s}, "en-US")' % typed,
        "in",
        "    Typed",
    ]
    return [{"name": table, "mode": "import",
             "source": {"type": "m", "expression": expr}}]

def calc_partition(table, expr):
    return [{"name": table, "mode": "import",
             "source": {"type": "calculated", "expression": expr}}]


# ------------------------------------------------------------------ households
HH = "powerbi_households"
HH_TYPES = [
    ("HouseholdKey", "Int64.Type"), ("Split", "type text"), ("Province", "type text"),
    ("ProvinceCode", "Int64.Type"), ("Settlement", "type text"), ("HouseholdSize", "Int64.Type"),
    ("SizeBand", "type text"), ("MonthlyIncome", "type number"), ("IncomeBand", "type text"),
    ("IncomeChange", "type text"), ("Electricity", "type text"), ("GrantRecipients", "Int64.Type"),
    ("GrantBand", "type text"), ("ToiletCode", "Int64.Type"), ("ToiletType", "type text"),
    ("FI_Score", "Int64.Type"), ("Tier", "type text"), ("AtRisk", "Int64.Type"),
    ("Severe", "Int64.Type"), ("ModelProbability", "type number"),
    ("ReferForReview", "Int64.Type"), ("HouseholdWeight", "type number"),
]

households = {
    "name": HH,
    "description": ("One row per modelled household (20,925). HouseholdKey is a row number, "
                    "not the survey HouseholdID - no household is identifiable from this table."),
    "lineageTag": lt("t/" + HH),
    "columns": [
        col(HH, "HouseholdKey", "int64", hidden=True),
        col(HH, "Split", "string"),
        col(HH, "Province", "string"),
        col(HH, "ProvinceCode", "int64", hidden=True),
        col(HH, "Settlement", "string"),
        col(HH, "HouseholdSize", "int64", "sum", "0"),
        col(HH, "SizeBand", "string"),
        col(HH, "MonthlyIncome", "double", "sum", "#,0"),
        col(HH, "IncomeBand", "string"),
        col(HH, "IncomeChange", "string", hidden=True),
        col(HH, "Electricity", "string"),
        col(HH, "GrantRecipients", "int64", "sum", "0"),
        col(HH, "GrantBand", "string"),
        col(HH, "ToiletCode", "int64", hidden=True),
        col(HH, "ToiletType", "string"),
        col(HH, "FI_Score", "int64", "none", "0"),
        col(HH, "Tier", "string"),
        col(HH, "AtRisk", "int64", "sum", "0"),
        col(HH, "Severe", "int64", "sum", "0"),
        col(HH, "ModelProbability", "double", "none", "0.000"),
        col(HH, "ReferForReview", "int64", "sum", "0"),
        col(HH, "HouseholdWeight", "double", "sum", "#,0.00"),
        calc_col(HH, "Outcome",
                 'IF(%s[AtRisk] = 1, "At risk", "Not at risk")' % HH, "string"),
        calc_col(HH, "Referral",
                 'IF(%s[ReferForReview] = 1, "Referred for follow-up", "Not referred")' % HH,
                 "string"),
        calc_col(HH, "Score band sort",
                 "FLOOR(%s[ModelProbability] * 20, 1)" % HH),
        calc_col(HH, "Score band",
                 'VAR b = FLOOR(%s[ModelProbability] * 20, 1) / 20 '
                 'RETURN FORMAT(b, "0.00") & " to " & FORMAT(b + 0.05, "0.00")' % HH,
                 "string", sort="Score band sort"),
        calc_col(HH, "Income vs a year ago sort",
                 'IFERROR(VALUE(LEFT(%s[IncomeChange], 1)), 9)' % HH),
        calc_col(HH, "Income vs a year ago",
                 'SWITCH(LEFT(%s[IncomeChange], 1), '
                 '"1", "Much higher", "2", "A little higher", "3", "About the same", '
                 '"4", "A little lower", "5", "Much lower", "Not stated")' % HH,
                 "string", sort="Income vs a year ago sort"),
    ],
    "partitions": csv_partition(HH, "powerbi_households.csv", HH_TYPES),
    "measures": [
        measure(HH, "Households in sample", "COUNTROWS(%s)" % HH, "#,0",
                "Households in the current selection.", "1 Counts"),
        measure(HH, "Households", "COUNTROWS(%s)" % HH, "#,0", None, "1 Counts"),
        measure(HH, "Test households",
                'CALCULATE(COUNTROWS(%s), %s[Split] = "Test")' % (HH, HH), "#,0", None,
                "1 Counts"),
        measure(HH, "Estimated households at risk",
                "SUMX(%s, %s[AtRisk] * %s[HouseholdWeight])" % (HH, HH, HH), "#,0",
                "Survey-weighted population estimate.", "1 Counts"),

        measure(HH, "At-risk share (weighted)",
                "DIVIDE(SUMX(%s, %s[AtRisk] * %s[HouseholdWeight]), SUM(%s[HouseholdWeight]))"
                % (HH, HH, HH, HH), "0.0%",
                "Share of households at risk, weighted by HouseholdWeight.", "2 Prevalence"),
        measure(HH, "At-risk share (unweighted)",
                "DIVIDE(SUM(%s[AtRisk]), COUNTROWS(%s))" % (HH, HH), "0.0%", None,
                "2 Prevalence"),
        measure(HH, "Severe share (weighted)",
                "DIVIDE(SUMX(%s, %s[Severe] * %s[HouseholdWeight]), SUM(%s[HouseholdWeight]))"
                % (HH, HH, HH, HH), "0.0%", None, "2 Prevalence"),
        measure(HH, "Referred share",
                "DIVIDE(SUM(%s[ReferForReview]), COUNTROWS(%s))" % (HH, HH), "0.0%",
                "Share referred across all 20,925 households (59.2%) - not the test-set figure.",
                "2 Prevalence"),

        measure(HH, "At-risk households (test)",
                'CALCULATE(SUM(%s[AtRisk]), %s[Split] = "Test")' % (HH, HH), "#,0", None,
                "3 What-if"),
        measure(HH, "Recall at threshold",
                'VAR T = [Threshold Value] RETURN DIVIDE(CALCULATE(SUM(%s[AtRisk]), '
                '%s[Split] = "Test", FILTER(ALL(%s[ModelProbability]), '
                '%s[ModelProbability] >= T)), [At-risk households (test)])' % (HH, HH, HH, HH),
                "0.0%", "At-risk test households referred at the selected threshold.",
                "3 What-if"),
        measure(HH, "Referred at threshold",
                'VAR T = [Threshold Value] RETURN DIVIDE(CALCULATE(COUNTROWS(%s), '
                '%s[Split] = "Test", FILTER(ALL(%s[ModelProbability]), '
                '%s[ModelProbability] >= T)), [Test households])' % (HH, HH, HH, HH),
                "0.0%", None, "3 What-if"),
        measure(HH, "Precision at threshold",
                'VAR T = [Threshold Value] RETURN DIVIDE(CALCULATE(SUM(%s[AtRisk]), '
                '%s[Split] = "Test", FILTER(ALL(%s[ModelProbability]), '
                '%s[ModelProbability] >= T)), CALCULATE(COUNTROWS(%s), %s[Split] = "Test", '
                'FILTER(ALL(%s[ModelProbability]), %s[ModelProbability] >= T)))'
                % (HH, HH, HH, HH, HH, HH, HH, HH), "0.0%", None, "3 What-if"),
        measure(HH, "Households referred (per 1,000)",
                "ROUND([Referred at threshold] * 1000, 0)", "#,0", None, "3 What-if"),

        measure(HH, "R at-risk share (weighted)",
                'VAR p = SELECTEDVALUE(%s[Province])\n'
                'VAR v = IF(ISBLANK(p),\n'
                '    LOOKUPVALUE(powerbi_reconciliation[AtRiskPct_weighted], '
                'powerbi_reconciliation[Breakdown], "All", '
                'powerbi_reconciliation[Group], "All households"),\n'
                '    LOOKUPVALUE(powerbi_reconciliation[AtRiskPct_weighted], '
                'powerbi_reconciliation[Breakdown], "Province", '
                'powerbi_reconciliation[Group], p))\n'
                'RETURN DIVIDE(v, 100)' % HH, "0.0%",
                "The same figure as computed in R, looked up from powerbi_reconciliation.csv.",
                "4 Reconciliation"),
        measure(HH, "R severe share (weighted)",
                'VAR p = SELECTEDVALUE(%s[Province])\n'
                'VAR v = IF(ISBLANK(p),\n'
                '    LOOKUPVALUE(powerbi_reconciliation[SeverePct_weighted], '
                'powerbi_reconciliation[Breakdown], "All", '
                'powerbi_reconciliation[Group], "All households"),\n'
                '    LOOKUPVALUE(powerbi_reconciliation[SeverePct_weighted], '
                'powerbi_reconciliation[Breakdown], "Province", '
                'powerbi_reconciliation[Group], p))\n'
                'RETURN DIVIDE(v, 100)' % HH, "0.0%", None, "4 Reconciliation"),
        measure(HH, "R referred share",
                'VAR p = SELECTEDVALUE(%s[Province])\n'
                'VAR v = IF(ISBLANK(p),\n'
                '    LOOKUPVALUE(powerbi_reconciliation[ReferredPct], '
                'powerbi_reconciliation[Breakdown], "All", '
                'powerbi_reconciliation[Group], "All households"),\n'
                '    LOOKUPVALUE(powerbi_reconciliation[ReferredPct], '
                'powerbi_reconciliation[Breakdown], "Province", '
                'powerbi_reconciliation[Group], p))\n'
                'RETURN DIVIDE(v, 100)' % HH, "0.0%", None, "4 Reconciliation"),
        measure(HH, "Difference at-risk (points)",
                "ROUND(([At-risk share (weighted)] - [R at-risk share (weighted)]) * 100, 1)",
                "0.0",
                "Dashboard minus R, in percentage points. Must read 0.0 for every province.",
                "4 Reconciliation"),
        measure(HH, "Difference referred (points)",
                "ROUND(([Referred share] - [R referred share]) * 100, 1)", "0.0", None,
                "4 Reconciliation"),
        measure(HH, "Reconciliation status",
                'VAR d = ABS([Difference at-risk (points)]) + '
                'ABS([Difference referred (points)])\n'
                'RETURN IF(d <= 0.1, "Reconciled", "CHECK")', None,
                "Reconciled when the dashboard and R agree to within 0.1 of a percentage point.",
                "4 Reconciliation"),
    ],
}

# --------------------------------------------------------------- model summary
MS = "powerbi_model_summary"

def deployed(name, metric, fmt):
    return measure(MS, name,
                   'CALCULATE(SUM(%s[Value]), %s[Metric] = "%s")' % (MS, MS, metric), fmt)

model_summary = {
    "name": MS,
    "description": ("Headline test-set metrics for the deployed screen, as written by the "
                    "R evaluation notebook."),
    "lineageTag": lt("t/" + MS),
    "columns": [col(MS, "Metric", "string"), col(MS, "Value", "double", "sum", "0.000")],
    "partitions": csv_partition(MS, "powerbi_model_summary.csv",
                                [("Metric", "type text"), ("Value", "type number")]),
    "measures": [
        deployed("Deployed recall", "Recall (at-risk households found)", "0.0%"),
        deployed("Deployed precision", "Precision (referrals at risk)", "0.0%"),
        deployed("Deployed share referred", "Share of households referred", "0.0%"),
        deployed("Deployed ROC-AUC", "ROC-AUC", "0.000"),
        deployed("Deployed PR-AUC", "PR-AUC", "0.000"),
        deployed("Deployed Brier score", "Brier score", "0.000"),
        deployed("Deployed test households", "Test households", "#,0"),
        deployed("Deployed threshold", "Threshold", "0.00"),
    ],
}

# -------------------------------------------------------- subgroup performance
SG = "powerbi_subgroup_performance"
SG_TYPES = [
    ("variable", "type text"), ("group", "type text"), ("households", "Int64.Type"),
    ("at_risk", "Int64.Type"), ("recall", "type number"), ("recall_95_low", "type number"),
    ("recall_95_high", "type number"), ("false_negative_rate", "type number"),
    ("precision", "type number"), ("pct_flagged", "type number"),
    ("gap_vs_overall", "type number"), ("within_10_points", "type text"),
    ("within_tolerance", "type text"),
]
subgroup = {
    "name": SG,
    "description": "Test-set recall and precision by subgroup, with Wilson 95% intervals.",
    "lineageTag": lt("t/" + SG),
    "columns": [
        col(SG, "variable", "string"),
        col(SG, "group", "string"),
        col(SG, "households", "int64", "sum", "#,0"),
        col(SG, "at_risk", "int64", "sum", "#,0"),
        col(SG, "recall", "double", "sum", "0.0%"),
        col(SG, "recall_95_low", "double", "sum", "0.0%"),
        col(SG, "recall_95_high", "double", "sum", "0.0%"),
        col(SG, "false_negative_rate", "double", "sum", "0.0%"),
        col(SG, "precision", "double", "sum", "0.0%"),
        col(SG, "pct_flagged", "double", "sum", "0.0%"),
        col(SG, "gap_vs_overall", "double", "sum", "0.0"),
        col(SG, "within_10_points", "string", hidden=True),
        col(SG, "within_tolerance", "string"),
        calc_col(SG, "CI width", "%s[recall_95_high] - %s[recall_95_low]" % (SG, SG),
                 summarize="sum", fmt="0.0%"),
    ],
    "partitions": csv_partition(SG, "powerbi_subgroup_performance.csv", SG_TYPES),
    "measures": [
        measure(SG, "Overall recall (reference)", "0.807191245440333", "0.0%",
                "Overall test-set recall, the centre of the 10-point tolerance band."),
        measure(SG, "Tolerance band low", "0.707191245440333", "0.0%"),
        measure(SG, "Tolerance band high", "0.907191245440333", "0.0%"),
        measure(SG, "Groups outside tolerance",
                'COUNTROWS(FILTER(%s, %s[within_tolerance] = "No"))' % (SG, SG), "#,0"),
    ],
}

# ----------------------------------------------------- permutation importance
PI = "powerbi_permutation_importance"
importance = {
    "name": PI,
    "description": "Drop in test ROC-AUC when each predictor is randomly permuted.",
    "lineageTag": lt("t/" + PI),
    "columns": [
        col(PI, "Predictor", "string", hidden=True),
        col(PI, "AUC_drop", "double", "sum", "0.0000"),
        col(PI, "Rank", "int64", "none", "0"),
        calc_col(PI, "Driver",
                 'SWITCH(%s[Predictor], '
                 '"ComparativeIncomeCode", "Income change vs a year ago", '
                 '"Income_PerCapita", "Income per person", '
                 '"SocialGrantRecipients", "Number of grant recipients", '
                 '"Income_Log", "Household income", '
                 '"ElectricityAccessCode", "Electricity access", '
                 '"GeoTypeCode", "Settlement type", '
                 '"MainToiletCode", "Toilet type", '
                 '"HouseholdSize", "Household size", %s[Predictor])' % (PI, PI),
                 "string", sort="Rank"),
    ],
    "partitions": csv_partition(PI, "powerbi_permutation_importance.csv",
                                [("Predictor", "type text"), ("AUC_drop", "type number"),
                                 ("Rank", "Int64.Type")]),
}

# ----------------------------------------------------------------- odds ratios
OR = "powerbi_odds_ratios"
odds = {
    "name": OR,
    "description": ("Adjusted odds ratios from the final lasso logistic model, "
                    "with 95% intervals."),
    "lineageTag": lt("t/" + OR),
    "columns": [
        col(OR, "Term", "string", hidden=True),
        col(OR, "OddsRatio", "double", "sum", "0.000"),
        col(OR, "CI_low", "double", "sum", "0.000"),
        col(OR, "CI_high", "double", "sum", "0.000"),
        col(OR, "p_value", "double", "sum", "0.00E+00"),
        calc_col(OR, "Factor",
                 'SWITCH(%s[Term], '
                 '"ComparativeIncomeCode2", "Income a little higher than a year ago", '
                 '"ComparativeIncomeCode3", "Income about the same", '
                 '"ComparativeIncomeCode4", "Income a little lower", '
                 '"ComparativeIncomeCode5", "Income much lower", '
                 '"GeoTypeCodeTraditional_Tribal", "Traditional / tribal area", '
                 '"GeoTypeCodeFarms", "Farm", '
                 '"HouseholdSize", "Each extra household member", '
                 '"Income_Log", "Higher household income", '
                 '"ElectricityAccessCodeNo", "No electricity", '
                 '"SocialGrantRecipients", "Each extra grant recipient", '
                 '"MainToiletCode2", "Flush toilet, septic tank", '
                 '"MainToiletCode5", "Pit latrine with ventilation pipe", '
                 '"MainToiletCode6", "Pit latrine, no pipe, with slab", '
                 '"MainToiletCode7", "Pit latrine, no pipe, no slab", '
                 '"MainToiletCodeOther", "Other toilet type", %s[Term])' % (OR, OR), "string"),
        calc_col(OR, "Direction",
                 'IF(%s[CI_low] > 1, "Raises risk", '
                 'IF(%s[CI_high] < 1, "Lowers risk", "No clear effect"))' % (OR, OR), "string"),
    ],
    "partitions": csv_partition(OR, "powerbi_odds_ratios.csv",
                                [("Term", "type text"), ("OddsRatio", "type number"),
                                 ("CI_low", "type number"), ("CI_high", "type number"),
                                 ("p_value", "type number")]),
}

# --------------------------------------------------------------- reconciliation
RC = "powerbi_reconciliation"
recon = {
    "name": RC,
    "description": ("Benchmark percentages computed in R, by province, settlement type and "
                    "income band. Person C's reconciliation source: every dashboard figure "
                    "must match this file."),
    "lineageTag": lt("t/" + RC),
    "columns": [
        col(RC, "Breakdown", "string"),
        col(RC, "Group", "string"),
        col(RC, "Households", "int64", "sum", "#,0"),
        col(RC, "AtRiskPct_unweighted", "double", "sum", "0.0"),
        col(RC, "AtRiskPct_weighted", "double", "sum", "0.0"),
        col(RC, "SeverePct_weighted", "double", "sum", "0.0"),
        col(RC, "ReferredPct", "double", "sum", "0.0"),
    ],
    "partitions": csv_partition(RC, "powerbi_reconciliation.csv",
                                [("Breakdown", "type text"), ("Group", "type text"),
                                 ("Households", "Int64.Type"),
                                 ("AtRiskPct_unweighted", "type number"),
                                 ("AtRiskPct_weighted", "type number"),
                                 ("SeverePct_weighted", "type number"),
                                 ("ReferredPct", "type number")]),
}

# ------------------------------------------------------------- threshold curve
TC = "powerbi_threshold_curve"
curve = {
    "name": TC,
    "description": ("Test-set metrics at every candidate referral threshold from 0.05 to 0.90. "
                    "Built by scripts/make_threshold_curve.R from powerbi_households.csv."),
    "lineageTag": lt("t/" + TC),
    "columns": [
        col(TC, "Threshold", "double", "none", "0.00"),
        col(TC, "Referred", "int64", "sum", "#,0"),
        col(TC, "ReferredShare", "double", "sum", "0.0%"),
        col(TC, "TruePositives", "int64", "sum", "#,0"),
        col(TC, "Recall", "double", "sum", "0.0%"),
        col(TC, "Precision", "double", "sum", "0.0%"),
        col(TC, "ReferredPer1000", "int64", "sum", "#,0"),
        col(TC, "MissedAtRisk", "int64", "sum", "#,0"),
        col(TC, "IsDeployed", "string"),
    ],
    "partitions": csv_partition(TC, "powerbi_threshold_curve.csv",
                                [("Threshold", "type number"), ("Referred", "Int64.Type"),
                                 ("ReferredShare", "type number"),
                                 ("TruePositives", "Int64.Type"), ("Recall", "type number"),
                                 ("Precision", "type number"),
                                 ("ReferredPer1000", "Int64.Type"),
                                 ("MissedAtRisk", "Int64.Type"), ("IsDeployed", "type text")]),
}

# ------------------------------------------- dataset inventory (Milestone 1)
DI = "powerbi_dataset_inventory"
inventory = {
    "name": DI,
    "description": ("The ten GHS 2024 extracts as profiled in Milestone 1: row and column "
                    "counts, grain, and whether each was selected. Counted directly off "
                    "data/raw/ by scripts/make_data_foundation.py."),
    "lineageTag": lt("t/" + DI),
    "columns": [
        col(DI, "Dataset", "string"),
        col(DI, "Domain", "string"),
        col(DI, "Grain", "string"),
        col(DI, "Rows", "int64", "sum", "#,0"),
        col(DI, "Columns", "int64", "sum", "#,0"),
        col(DI, "Households", "int64", "sum", "#,0"),
        col(DI, "DuplicateRows", "int64", "sum", "#,0"),
        col(DI, "Selected", "string"),
        col(DI, "Reason", "string"),
    ],
    "partitions": csv_partition(DI, "powerbi_dataset_inventory.csv",
                                [("Dataset", "type text"), ("Domain", "type text"),
                                 ("Grain", "type text"), ("Rows", "Int64.Type"),
                                 ("Columns", "Int64.Type"), ("Households", "Int64.Type"),
                                 ("DuplicateRows", "Int64.Type"), ("Selected", "type text"),
                                 ("Reason", "type text")]),
    "measures": [
        measure(DI, "Datasets provided", "COUNTROWS(%s)" % DI, "#,0",
                "The ten extracts profiled in Milestone 1.", "1 Inventory"),
        measure(DI, "Datasets selected",
                'CALCULATE(COUNTROWS(%s), %s[Selected] = "Yes")' % (DI, DI), "#,0",
                "The seven household-level files that survived selection.", "1 Inventory"),
        measure(DI, "Datasets set aside",
                "[Datasets provided] - [Datasets selected]", "#,0", None, "1 Inventory"),
        measure(DI, "Rows in selection",
                'CALCULATE(SUM(%s[Rows]), %s[Selected] = "Yes")' % (DI, DI), "#,0", None,
                "1 Inventory"),
        measure(DI, "Columns profiled", "SUM(%s[Columns])" % DI, "#,0", None, "1 Inventory"),
        measure(DI, "Households after de-duplication",
                'CALCULATE(MAX(%s[Households]), %s[Selected] = "Yes")' % (DI, DI), "#,0",
                "20,940 households, before the 15 dropped at cleaning.", "1 Inventory"),
        measure(DI, "Duplicate rows removed",
                'CALCULATE(SUM(%s[DuplicateRows]), %s[Selected] = "Yes")' % (DI, DI), "#,0",
                None, "1 Inventory"),
    ],
}

# ---------------------------------------------- data quality (Milestone 1/2)
DQ = "powerbi_data_quality"
quality = {
    "name": DQ,
    "description": ("The Milestone 2 cleaning log: every data-quality problem found, the "
                    "column it was in and how it was treated. Before and After are text "
                    "because they mean different things per row (row counts for the "
                    "de-duplication entries, value counts for the recodes) and must never "
                    "be summed."),
    "lineageTag": lt("t/" + DQ),
    "columns": [
        col(DQ, "Dataset", "string"),
        col(DQ, "Domain", "string"),
        col(DQ, "Column", "string"),
        col(DQ, "Problem", "string"),
        col(DQ, "Treatment", "string"),
        col(DQ, "Before", "string"),
        col(DQ, "After", "string"),
        calc_col(DQ, "Dataset and column",
                 '%s[Dataset] & "." & %s[Column]' % (DQ, DQ), "string"),
    ],
    "partitions": csv_partition(DQ, "powerbi_data_quality.csv",
                                [("Dataset", "type text"), ("Domain", "type text"),
                                 ("Column", "type text"), ("Problem", "type text"),
                                 ("Treatment", "type text"), ("Before", "type text"),
                                 ("After", "type text")]),
    "measures": [
        measure(DQ, "Issues logged", "COUNTROWS(%s)" % DQ, "#,0",
                "Rows in the Milestone 2 cleaning log.", "2 Quality"),
        measure(DQ, "Issue types", "DISTINCTCOUNT(%s[Problem])" % DQ, "#,0", None, "2 Quality"),
        measure(DQ, "Datasets repaired", "DISTINCTCOUNT(%s[Dataset])" % DQ, "#,0", None,
                "2 Quality"),
        measure(DQ, "Columns repaired", "DISTINCTCOUNT(%s[Dataset and column])" % DQ, "#,0",
                "Counted per dataset, so the same column name in two files counts twice.",
                "2 Quality"),
    ],
}

# -------------------------------------------------------- Threshold what-if
TH = "Threshold"
threshold = {
    "name": TH,
    "description": ("What-if parameter: the referral threshold a decision-maker can try on the "
                    "'How well does the screening tool work?' page. Deployed value 0.24."),
    "lineageTag": lt("t/" + TH),
    "columns": [
        # isNameInferred must stay false: GENERATESERIES names its column [Value],
        # and the what-if measures and the slicer both reference Threshold[Threshold].
        {"name": "Threshold", "dataType": "double", "type": "calculatedTableColumn",
         "sourceColumn": "[Value]", "isNameInferred": False, "isDataTypeInferred": True,
         "summarizeBy": "none", "formatString": "0.00",
         "description": "GENERATESERIES accumulates 0.01 at a time, so the stored values "
                        "drift: the step shown as 0.24 is really 0.24000000000000007. Filter "
                        "or compare with a range (> 0.239 && < 0.241), never = 0.24, which "
                        "silently matches no rows. The slicer default literal on the "
                        "performance page already uses the drifted value.",
         "lineageTag": lt(TH + "/Threshold"), "annotations": list(ANN)},
    ],
    "partitions": calc_partition(TH, "GENERATESERIES(0, 1, 0.01)"),
    "measures": [
        measure(TH, "Threshold Value", "SELECTEDVALUE(%s[Threshold], 0.24)" % TH, "0.00",
                "The threshold currently chosen on the slicer; 0.24 when nothing is selected."),
    ],
}

MODEL = {
    "name": "SemanticModel",
    "compatibilityLevel": 1600,
    "model": {
        "culture": "en-US",
        "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "discourageImplicitMeasures": False,
        "sourceQueryCulture": "en-US",
        "tables": [households, model_summary, subgroup, importance, odds, recon, curve,
                   inventory, quality, threshold],
        "relationships": [],
        "expressions": [
            {"name": "DataFolder",
             "kind": "m",
             "expression": '"%%DATAFOLDER%%" meta [IsParameterQuery = true, Type = "Text", '
                           'IsParameterQueryRequired = true]',
             "lineageTag": lt("expr/DataFolder"),
             "annotations": [{"name": "PBI_NavigationStepName", "value": "Navigation"},
                             {"name": "PBI_ResultType", "value": "Text"}]},
        ],
        "annotations": [
            {"name": "PBI_QueryOrder",
             "value": '["DataFolder","powerbi_households","powerbi_model_summary",'
                      '"powerbi_subgroup_performance","powerbi_permutation_importance",'
                      '"powerbi_odds_ratios","powerbi_reconciliation",'
                      '"powerbi_threshold_curve","powerbi_dataset_inventory",'
                      '"powerbi_data_quality"]'},
            {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
        ],
    },
}
