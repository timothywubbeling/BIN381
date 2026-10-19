# -*- coding: utf-8 -*-
"""The seven pages of the merged Milestone 4 dashboard.

Content comes from both first-iteration dashboards:
  * Tim's Main Dash.pbix (M1): Food Security -> page 2, Distributions -> page 3,
    Data Inventory + Data Quality -> page 7, Relationships hypotheses -> page 6.
  * Rudi's BIN381_M4_Dashboard.pbix (M4): Overview -> page 1, performance -> page 4,
    subgroups -> page 5, drivers -> page 6.
Layout, palette and typography follow Tim's 1280x720 Innovate grid throughout.
"""
from pbir import *

HH = "powerbi_households"
MS = "powerbi_model_summary"
SG = "powerbi_subgroup_performance"
PI = "powerbi_permutation_importance"
OR = "powerbi_odds_ratios"
RC = "powerbi_reconciliation"
TC = "powerbi_threshold_curve"
DI = "powerbi_dataset_inventory"
DQ = "powerbi_data_quality"
TH = "Threshold"


# --------------------------------------------------------------- components
def card(seed, x, y, w, h, entity, name, title, subtitle=None, size=22):
    objects = {
        "label": [{"properties": {"show": boo(False)}, "selector": {"id": "default"}}],
        # displayUnits 1 = None. Auto abbreviates 20,925 to "21K" on the overview card.
        "value": [{"properties": {"fontSize": num(size), "bold": boo(True),
                                  "fontColor": solid(FG), "displayUnits": num(1)},
                   "selector": {"id": "default"}}],
    }
    return visual(seed, "cardVisual", x, y, w, h,
                  query=query({"Data": [pmeas(entity, name)]}),
                  objects=objects,
                  vco=chrome(title=title, subtitle=subtitle, bg=PANEL, size=9, color=FG2))


def filter_slicer(seed, x, y, w, h, entity, prop, title):
    objects = {
        "data": [{"properties": {"mode": s("Dropdown")}}],
        "header": [{"properties": {"show": boo(False)}}],
        "items": [{"properties": {"fontColor": solid(FG2), "background": solid(PANEL),
                                  "fontSize": num(9)}}],
    }
    return visual(seed, "slicer", x, y, w, h,
                  query=query({"Values": [pcol(entity, prop, active=True)]}),
                  objects=objects,
                  vco=chrome(title=title, bg=PANEL, size=9, color=FG2))


def list_slicer(seed, x, y, w, h, entity, prop, title):
    objects = {
        "data": [{"properties": {"mode": s("Basic")}}],
        "header": [{"properties": {"show": boo(False)}}],
        "items": [{"properties": {"fontColor": solid(FG2), "background": solid(PANEL),
                                  "fontSize": num(9)}}],
    }
    return visual(seed, "slicer", x, y, w, h,
                  query=query({"Values": [pcol(entity, prop, active=True)]}),
                  objects=objects,
                  vco=chrome(title=title, bg=PANEL, size=9, color=FG2))


def threshold_slicer(seed, x, y, w, h):
    """Numeric what-if slider, defaulted to the deployed 0.24 (as in Rudi's file)."""
    # Exact, and no numericStart: that was saved as the drifted 0.24 and became the
    # start of the slider's range, so it could not be dragged below the deployed value.
    default = "0.24D"
    objects = {
        "data": [{"properties": {"mode": s("Single")}}],
        "general": [{"properties": {"filter": {"filter": {
            "Version": 2,
            "From": [{"Name": "t", "Entity": TH, "Type": 0}],
            "Where": [{"Condition": {"Comparison": {
                "ComparisonKind": 0,
                "Left": {"Column": {"Expression": {"SourceRef": {"Source": "t"}},
                                    "Property": "Threshold"}},
                "Right": {"Literal": {"Value": default}}}}}]}}}}],
        "header": [{"properties": {"show": boo(False)}}],
    }
    return visual(seed, "slicer", x, y, w, h,
                  query=query({"Values": [pcol(TH, "Threshold", active=True)]}),
                  objects=objects,
                  vco=chrome(title="Referral threshold - drag to test a different cut-off",
                             subtitle="Deployed value 0.24", bg=PANEL, size=10, color=FG))


def table(seed, x, y, w, h, projections, title, subtitle=None, sort=None, text=8):
    objects = {
        "grid": [{"properties": {
            "gridVertical": boo(True), "gridVerticalColor": solid(BORDER),
            "gridHorizontal": boo(True), "gridHorizontalColor": solid(BORDER),
            "outlineColor": solid(BORDER), "textSize": num(text)}}],
        "columnHeaders": [{"properties": {
            "fontColor": solid(FG), "backColor": solid(PANEL), "bold": boo(True),
            "fontSize": num(text), "wordWrap": boo(True)}}],
        "values": [{"properties": {
            "fontColor": solid(FG2), "backColor": solid("#3a3a3a"), "fontSize": num(text)}}],
        "total": [{"properties": {"totals": boo(False)}}],
    }
    return visual(seed, "tableEx", x, y, w, h, query=query({"Values": projections}, sort=sort),
                  objects=objects, vco=chrome(title=title, subtitle=subtitle, bg=PANEL))


def chart(seed, vtype, x, y, w, h, roles, title, subtitle=None, sort=None, objects=None,
          filters=None):
    o = dict(objects or {})
    v = visual(seed, vtype, x, y, w, h, query=query(roles, sort), objects=o,
               vco=chrome(title=title, subtitle=subtitle, bg=PANEL))
    if filters:
        v["filterConfig"] = filters
    return v


def test_only_filter(seed):
    """Restrict a visual to the held-out test split."""
    return {"filters": [{
        "name": vid(seed + "/testfilter"),
        "field": fcol(HH, "Split"),
        "type": "Categorical",
        "filter": {
            "Version": 2,
            "From": [{"Name": "h", "Entity": HH, "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {
                    "Expression": {"SourceRef": {"Source": "h"}},
                    "Property": "Split"}}],
                "Values": [[{"Literal": {"Value": "'Test'"}}]]}}}]},
    }]}


def merge(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out


def four_filters(pid):
    """The same four slicers, in the same place, on every household page."""
    return [
        filter_slicer(pid + "/sl1", C1, B1_Y, W1, B1_H, HH, "Province", "Province"),
        filter_slicer(pid + "/sl2", C2, B1_Y, W1, B1_H, HH, "Settlement", "Settlement type"),
        filter_slicer(pid + "/sl3", C3, B1_Y, W1, B1_H, HH, "IncomeBand", "Monthly income band"),
        filter_slicer(pid + "/sl4", C4, B1_Y, W1, B1_H, HH, "GrantBand", "Social grant receipt"),
    ]


def panel(seed, x, y, w, h, title, lines):
    """A titled text panel. lines: list of (text, size, colour, bold) tuples."""
    paras = [para(run(title, "12pt", FG, bold=True))]
    for text, size, colour, bold in lines:
        paras.append(para(run(text, size, colour, bold=bold)))
    return textbox(seed, x, y, w, h, paras, bg=PANEL, border=True)


BLANK = ("", "6pt", FG3, False)


# =============================================================== 1. Overview
def p1():
    pid = "p1"
    v = page_header(
        pid,
        "Household food insecurity in South Africa",
        "A screening-support dashboard on the General Household Survey 2024 "
        "· Group P1 · Milestone 4",
        badge=("SCREENING AID",
               "Not an eligibility test. Every referral is reviewed by an official."))
    v += [
        card(pid + "/c1", C1, B1_Y, W1, B1_H, HH, "Households in sample",
             "Households in the survey sample"),
        card(pid + "/c2", C2, B1_Y, W1, B1_H, HH, "At-risk share (weighted)",
             "At risk of food insecurity", "Population estimate"),
        card(pid + "/c3", C3, B1_Y, W1, B1_H, MS, "Deployed recall",
             "At-risk households the screen finds", "Held-out test set"),
        card(pid + "/c4", C4, B1_Y, W1, B1_H, MS, "Deployed share referred",
             "Households sent for follow-up", "Held-out test set"),

        panel(pid + "/dq", C1, TALL_Y, W2, TALL_H,
              "The six decision questions this dashboard answers", [
                  BLANK,
                  ("1   Where are food-insecure households concentrated?", "11pt", FG, True),
                  ("      Page: Where the need is", "9pt", FG3, False),
                  ("2   Which kinds of household are most affected?", "11pt", FG, True),
                  ("      Page: Who is affected", "9pt", FG3, False),
                  ("3   Can we trust the screening tool enough to act on it?", "11pt", FG, True),
                  ("      Page: How well the screen works", "9pt", FG3, False),
                  ("4   Which households does the screen miss, and where?", "11pt", FG, True),
                  ("      Page: Who the screen misses", "9pt", FG3, False),
                  ("5   What should we ask about to spot risk early?", "11pt", FG, True),
                  ("      Page: What drives risk", "9pt", FG3, False),
                  ("6   How many households would a given threshold refer?", "11pt", FG, True),
                  ("      Page: How well the screen works", "9pt", FG3, False),
                  BLANK,
                  ("Each page is titled with the question it answers. Nothing on these pages "
                   "is here only because the data allowed it.", "9pt", FG2, False),
              ]),

        panel(pid + "/use", C3, B2_Y, W2, B2_H, "How to use it", [
            BLANK,
            ("Use the navigator above to move between pages. The four slicers on the household "
             "pages - province, settlement type, income band and grant receipt - filter every "
             "visual on that page.", "10pt", FG2, False),
            ("On the bar chart of provinces you can drill down into settlement type. On the "
             "performance page you can drag the referral threshold and watch recall, precision "
             "and referral volume move together.", "10pt", FG2, False),
            ("Percentages of the population are weighted with HouseholdWeight. Model "
             "performance is always measured on the 6,279 held-out test households.",
             "10pt", FG2, False),
        ]),

        panel(pid + "/about", C3, B3_Y, W2, B3_H, "About the screen", [
            BLANK,
            ("A lasso logistic regression scores each household from eight survey answers about "
             "income, grants, electricity, sanitation and household size. Households scoring "
             "0.24 or more are referred for follow-up.", "10pt", FG2, False),
            ("The threshold was chosen to find about 80% of at-risk households. That costs "
             "precision: 41.9% of referrals turn out to be at risk, and 58.9% of households "
             "are referred.", "10pt", FG2, False),
            ("This is a screening aid, not an eligibility test. A 'lower risk' score is not "
             "clearance, and no household is identifiable from this dashboard.",
             "10pt", AMBER, True),
        ]),
    ]
    return page(pid, "Overview", v)


# ======================================================== 2. Where the need is
def p2():
    pid = "p2"
    v = page_header(
        pid,
        "Where is food insecurity concentrated?",
        "Decision question 1 · which provinces and settlement types should be "
        "resourced first?",
        badge=("DRILL DOWN", "Use the drill controls on the province chart"))
    v += four_filters(pid)
    v += [
        chart(pid + "/prov", "barChart", C1, B2_Y, W2, B2_H,
              {"Category": [pcol(HH, "Province", "Province", active=True),
                            pcol(HH, "Settlement", "Settlement type")],
               "Y": [pmeas(HH, "At-risk share (weighted)", "At risk (weighted)")]},
              "Where food insecurity is concentrated",
              "Province, with drill-down to settlement type · national figure 28.3%",
              sort=[(pmeas(HH, "At-risk share (weighted)"), "Descending")],
              objects=merge(fill(BLUE),
                            axes(val_title="Share of households at risk (weighted)",
                                 val_start=0),
                            labels(True), legend(False))),

        chart(pid + "/inc", "clusteredColumnChart", C3, B2_Y, W2, B2_H,
              {"Category": [pcol(HH, "IncomeBand", "Monthly income", active=True)],
               "Y": [pmeas(HH, "At-risk share (weighted)", "At risk"),
                     pmeas(HH, "Severe share (weighted)", "Severely food insecure")]},
              "Food insecurity by income band",
              "At risk compared with severely food insecure · both weighted",
              objects=merge(fill_series({"%s.At-risk share (weighted)" % HH: BLUE,
                                         "%s.Severe share (weighted)" % HH: RED}),
                            axes(cat_title="Reported monthly household income",
                                 val_title="Share of households (weighted)", val_start=0),
                            labels(True), legend(True, "Top"))),

        chart(pid + "/settle", "barChart", C1, B3_Y, W1, B3_H,
              {"Category": [pcol(HH, "Settlement", "Settlement type", active=True)],
               "Y": [pmeas(HH, "At-risk share (weighted)", "At risk")]},
              "By settlement type",
              sort=[(pmeas(HH, "At-risk share (weighted)"), "Descending")],
              objects=merge(fill(BLUE), axes(val_title="At risk (weighted)", val_start=0),
                            labels(True), legend(False))),

        chart(pid + "/refer", "clusteredColumnChart", C2, B3_Y, W1, B3_H,
              {"Category": [pcol(HH, "Settlement", "Settlement type", active=True)],
               "Y": [pmeas(HH, "Referred share", "Referred")]},
              "Referred for follow-up",
              "Share of all 20,925 households the screen refers",
              objects=merge(fill(TEAL), axes(val_title="Referred", val_start=0),
                            labels(True), legend(False))),

        table(pid + "/tbl", C3, B3_Y, W2, B3_H,
              [pcol(HH, "Province", "Province"),
               pmeas(HH, "Households in sample", "Households"),
               pmeas(HH, "At-risk share (weighted)", "At risk"),
               pmeas(HH, "Severe share (weighted)", "Severe"),
               pmeas(HH, "Referred share", "Referred")],
              "Province detail",
              "Weighted prevalence and referral load, worst first",
              sort=[(pmeas(HH, "At-risk share (weighted)"), "Descending")]),
    ]
    return page(pid, "Where the need is", v)


# ========================================================== 3. Who is affected
def p3():
    pid = "p3"
    v = page_header(
        pid,
        "Which kinds of household are most affected?",
        "Decision question 2 · which household characteristics mark out the greatest need?")
    v += four_filters(pid)

    def cut(seed, x, prop, title, subtitle=None, colour=BLUE):
        return chart(pid + seed, "clusteredColumnChart", x, B2_Y, W1, B2_H,
                     {"Category": [pcol(HH, prop, active=True)],
                      "Y": [pmeas(HH, "At-risk share (weighted)", "At risk")]},
                     title, subtitle,
                     objects=merge(fill(colour),
                                   axes(val_title="At risk (weighted)", val_start=0),
                                   labels(True), legend(False)))

    v += [
        cut("/size", C1, "SizeBand", "Household size",
            "Larger households carry more risk"),
        cut("/chg", C2, "Income vs a year ago", "Income compared with a year ago",
            "Hypothesis H1 · the shape is a U, not a line"),
        cut("/grant", C3, "GrantBand", "Social grant receipt",
            "Hypothesis H5 · grants mark poverty, they do not cause it"),
        cut("/elec", C4, "Electricity", "Electricity access",
            "Hypothesis H4 · no electricity doubles the odds"),

        chart(pid + "/toilet", "barChart", C1, B3_Y, W2, B3_H,
              {"Category": [pcol(HH, "ToiletType", "Main toilet type", active=True)],
               "Y": [pmeas(HH, "At-risk share (weighted)", "At risk")]},
              "Sanitation: at-risk share by main toilet facility",
              sort=[(pmeas(HH, "At-risk share (weighted)"), "Descending")],
              objects=merge(fill(BLUE), axes(val_title="At risk (weighted)", val_start=0),
                            labels(True), legend(False))),

        chart(pid + "/fi", "clusteredColumnChart", C3, B3_Y, W1, B3_H,
              {"Category": [pcol(HH, "FI_Score", "Items reported", active=True)],
               "Y": [pmeas(HH, "Households in sample", "Households")]},
              "Food-insecurity items reported",
              "0 = food secure · 8 = every item reported",
              objects=merge(fill(AMBER),
                            axes(cat_title="Number of the eight items reported",
                                 val_title="Households"),
                            labels(False), legend(False))),

        panel(pid + "/read", C4, B3_Y, W1, B3_H, "How to read this page", [
            BLANK,
            ("Every bar is the weighted share of households in that group that are at risk. "
             "The national figure is 28.3%.", "9pt", FG2, False),
            ("The four slicers above apply to all seven charts, so a province can be compared "
             "with the country on the same cut.", "9pt", FG2, False),
            ("These are associations in survey data, not causes, and the target is a "
             "proxy built from eight survey items rather than a measured outcome.",
             "9pt", AMBER, False),
        ]),
    ]
    return page(pid, "Who is affected", v)


# ================================================ 4. How well the screen works
def p4():
    pid = "p4"
    v = page_header(
        pid,
        "How well does the screening tool work?",
        "Decision questions 3 and 6 · can we act on it, and how many households "
        "would a given threshold refer?",
        badge=("TEST SET ONLY", "6,279 held-out households, 1,919 at risk"))
    v += [
        card(pid + "/c1", C1, B1_Y, W1, B1_H, MS, "Deployed recall",
             "At-risk households found", "Recall at 0.24"),
        card(pid + "/c2", C2, B1_Y, W1, B1_H, MS, "Deployed precision",
             "Referrals that are genuinely at risk", "Precision at 0.24"),
        card(pid + "/c3", C3, B1_Y, W1, B1_H, MS, "Deployed share referred",
             "Households sent for follow-up", "Test-set referral rate"),
        card(pid + "/c4", C4, B1_Y, W1, B1_H, MS, "Deployed ROC-AUC",
             "Ranking quality", "0.5 would be a coin flip"),

        threshold_slicer(pid + "/th", C1, B2_Y, W2, 78),
        card(pid + "/w1", C1, 312, 194, 138, HH, "Recall at threshold",
             "At-risk households found", None, 20),
        card(pid + "/w2", 226, 312, 194, 138, HH, "Precision at threshold",
             "Referrals genuinely at risk", None, 20),
        card(pid + "/w3", 436, 312, 196, 138, HH, "Households referred (per 1,000)",
             "Referred per 1,000 households", None, 20),

        chart(pid + "/curve", "lineChart", C3, B2_Y, W2, B2_H,
              {"Category": [pcol(TC, "Threshold", "Referral threshold", active=True)],
               "Y": [pagg(TC, "Recall", "Recall"),
                     pagg(TC, "Precision", "Precision"),
                     pagg(TC, "ReferredShare", "Share referred")]},
              "Recall, precision and referral load at every threshold",
              "At the deployed 0.24: recall 80.7%, precision 41.9%, 58.9% of test "
              "households referred",
              objects=merge(fill_series({"Sum(%s.Recall)" % TC: BLUE,
                                         "Sum(%s.Precision)" % TC: AMBER,
                                         "Sum(%s.ReferredShare)" % TC: TEAL}),
                            axes(cat_title="Referral threshold",
                                 val_title="Share of test households",
                                 val_start=0, val_end=1),
                            legend(True, "Top"))),

        chart(pid + "/score", "columnChart", C1, B3_Y, W2, B3_H,
              {"Category": [pcol(HH, "Score band", "Model score band", active=True)],
               "Y": [pmeas(HH, "Households", "Test households")],
               "Series": [pcol(HH, "Outcome", "Outcome")]},
              "How the test households score",
              "Bands of 0.05 · everything from 0.24 upwards is referred",
              objects=merge(fill_by(HH, "Outcome", {"At risk": RED, "Not at risk": GREY}),
                            axes(cat_title="Model score band", val_title="Test households"),
                            legend(True, "Top")),
              filters=test_only_filter(pid + "/score")),

        panel(pid + "/note", C3, B3_Y, W2, B3_H, "What the threshold decides", [
            BLANK,
            ("Lower the threshold and the screen finds more at-risk households but sends more "
             "for follow-up. Raise it and fewer visits are wasted, but more people at risk are "
             "missed. At 0.14 recall reaches 95.9% and 83.8% of households are referred; at "
             "0.40 recall falls to 47.4% for 26.2% referred.", "10pt", FG2, False),
            ("Recall and precision are measured only on the 6,279 held-out test households. "
             "The 59.2% referral rate quoted on the household pages covers all 20,925 "
             "households, train and test - both figures are right, for different populations.",
             "9pt", FG3, False),
            ("Screening aid only. A referral is a request for a human visit, and a lower score "
             "is not clearance.", "10pt", AMBER, True),
        ]),
    ]
    return page(pid, "How well the screen works", v)


# ================================================= 5. Who the screen misses
def p5():
    pid = "p5"
    v = page_header(
        pid,
        "Which households does the screen miss?",
        "Decision question 4 · where are the recall gaps, and which groups are too "
        "small to judge?",
        badge=("FAIRNESS CHECK", "Amber bars fall outside the tolerance band"))
    v += [
        list_slicer(pid + "/sl", C1, B1_Y, W2, B1_H, SG, "variable",
                    "Break the screen down by"),
        card(pid + "/c1", C3, B1_Y, W1, B1_H, SG, "Overall recall (reference)",
             "Overall recall", "Centre of the tolerance band"),
        card(pid + "/c2", C4, B1_Y, W1, B1_H, SG, "Groups outside tolerance",
             "Groups outside tolerance", "Of 22 measured: two below the band, two above"),

        chart(pid + "/bars", "barChart", C1, TALL_Y, W2, TALL_H,
              {"Category": [pcol(SG, "group", "Group", active=True)],
               "Y": [pagg(SG, "recall", "Recall")],
               "Series": [pcol(SG, "within_tolerance", "Within tolerance")]},
              "Recall by group, worst first",
              "Overall recall is 80.7% · amber bars fall outside the "
              "70.7% to 90.7% tolerance band",
              sort=[(pagg(SG, "recall"), "Ascending")],
              objects=merge(fill_by(SG, "within_tolerance", {"Yes": BLUE, "No": AMBER}),
                            axes(val_title="Recall - share of at-risk households referred",
                                 val_start=0, val_end=1),
                            labels(True), legend(True, "Inside the 10-point tolerance band?"))),

        table(pid + "/tbl", C3, B2_Y, W2, B2_H,
              [pcol(SG, "group", "Group"),
               pagg(SG, "households", "Test households"),
               pagg(SG, "at_risk", "At risk"),
               pagg(SG, "recall", "Recall"),
               pagg(SG, "recall_95_low", "95% CI low"),
               pagg(SG, "recall_95_high", "95% CI high"),
               pagg(SG, "precision", "Precision")],
              "The numbers behind the bars",
              "Wilson 95% intervals · a wide interval means a small group",
              sort=[(pagg(SG, "recall"), "Ascending")]),

        panel(pid + "/note", C3, B3_Y, W2, B3_H, "What it means", [
            BLANK,
            ("The screen is weakest exactly where food insecurity is least expected: "
             "households with income above R11,500 (39.2% recall) and households receiving no "
             "grants (61.7%). It is strongest for households of seven or more (95.9%).",
             "10pt", FG2, False),
            ("A wide confidence interval means the group is too small to judge - Farms has only "
             "197 test households, so its 75.8% could sit anywhere between 63.8% and 84.8%.",
             "10pt", FG2, False),
            ("Officials should not treat a lower-risk score as clearance for a higher-income or "
             "no-grant household. These two groups need a second route into assessment that "
             "does not depend on the screen.", "10pt", AMBER, True),
        ]),
    ]
    return page(pid, "Who the screen misses", v)


# ========================================================= 6. What drives risk
def p6():
    pid = "p6"
    A_Y, A_H = 124, 250
    B_Y, B_H = 390, 150
    C_Y, C_H = 556, 134
    v = page_header(
        pid,
        "What should we ask about to spot risk early?",
        "Decision question 5 · which few answers carry most of the signal, and what "
        "did the six hypotheses show?")
    v += [
        chart(pid + "/imp", "clusteredBarChart", C1, A_Y, W2, A_H,
              {"Category": [pcol(PI, "Driver", "Driver", active=True)],
               "Y": [pagg(PI, "AUC_drop", "Drop in ROC-AUC")]},
              "How much the screen relies on each answer",
              "Fall in test ROC-AUC when that answer is scrambled",
              sort=[(pagg(PI, "AUC_drop"), "Descending")],
              objects=merge(fill(BLUE), axes(val_title="Drop in ROC-AUC", val_start=0),
                            labels(True), legend(False))),

        table(pid + "/odds", C3, A_Y, W2, A_H,
              [pcol(OR, "Factor", "Factor"),
               pagg(OR, "OddsRatio", "Odds ratio"),
               pagg(OR, "CI_low", "95% low"),
               pagg(OR, "CI_high", "95% high"),
               pcol(OR, "Direction", "Direction")],
              "Which answers raise or lower the odds of being at risk",
              "Adjusted odds ratios · above 1 raises risk, below 1 lowers it",
              sort=[(pagg(OR, "OddsRatio"), "Descending")]),
    ]

    def small(seed, x, prop, title, subtitle, colour=BLUE):
        return chart(pid + seed, "clusteredColumnChart", x, B_Y, W1, B_H,
                     {"Category": [pcol(HH, prop, active=True)],
                      "Y": [pmeas(HH, "At-risk share (weighted)", "At risk")]},
                     title, subtitle,
                     objects=merge(fill(colour), axes(val_start=0), labels(True),
                                   legend(False)))

    v += [
        small("/hyp1", C1, "Income vs a year ago", "H1  Income change",
              "Supported, as a U-shape"),
        small("/hyp4", C2, "Electricity", "H4  Electricity access", "Supported"),
        small("/hyp5", C3, "GrantBand", "H5  Social grants", "Supported, but reversed"),
        small("/hyp2", C4, "Settlement", "H2  Settlement type", "Partly supported"),

        panel(pid + "/hyp", C1, C_Y, W4, C_H, "What the six hypotheses showed", [
            ("H1  Lower income raises risk - supported, but as a U: households reporting income "
             "much lower than a year ago are at 2.05 times the odds, while a little higher or "
             "about the same both sit below 1.    "
             "H2  Farm and traditional areas - partly supported: traditional/tribal areas have "
             "the highest raw prevalence (35.1%) yet lower adjusted odds (0.76) once income is "
             "held constant.    "
             "H3  Larger households - supported and small: 1.04 per extra member.",
             "9pt", FG2, False),
            ("H4  No electricity - supported and strong: 2.07 times the odds.    "
             "H5  Social grants - supported but reversed in meaning: each extra recipient raises "
             "the odds 1.20, because grants mark households already identified as poor.    "
             "H6  Sanitation - mixed: a ventilated pit latrine raises the odds (1.31) while a "
             "septic flush toilet lowers them (0.72).", "9pt", FG2, False),
            ("Associations, not causes. Grant receipt marks households that were targeted "
             "because they are poor; it is not evidence that grants cause food insecurity, and "
             "nothing here should be read as a reason to withdraw a grant.", "9pt", AMBER, True),
        ]),
    ]
    return page(pid, "What drives risk", v)


# ======================================================== 7. Data foundation
def p7():
    """Timothy's Milestone 1 Data Inventory page, rebuilt on counts off data/raw/."""
    pid = "p7"
    v = page_header(
        pid,
        "What data is this built on?",
        "Ten GHS 2024 extracts profiled, seven selected, one modelling dataset",
        badge=("DATA LINEAGE", "Counted off data/raw/, not asserted"))
    v += [
        card(pid + "/c1", C1, B1_Y, W1, B1_H, DI, "Datasets provided",
             "Datasets profiled", "The ten GHS 2024 extracts"),
        card(pid + "/c2", C2, B1_Y, W1, B1_H, DI, "Datasets selected",
             "Datasets selected", "Household-level files only"),
        card(pid + "/c3", C3, B1_Y, W1, B1_H, DI, "Households after de-duplication",
             "Households after the join", "Before cleaning"),
        card(pid + "/c4", C4, B1_Y, W1, B1_H, HH, "Households in sample",
             "Households modelled", "After cleaning"),

        chart(pid + "/rows", "clusteredBarChart", C1, B2_Y, W2, B2_H,
              {"Category": [pcol(DI, "Domain", "Dataset", active=True)],
               "Y": [pagg(DI, "Rows", "Rows")],
               "Series": [pcol(DI, "Selected", "Selected")]},
              "What was provided, and what was used",
              "The three person-level files carry about 3.4 rows per household",
              sort=[(pagg(DI, "Rows"), "Descending")],
              objects=merge(fill_by(DI, "Selected", {"Yes": BLUE, "No": GREY}),
                            axes(val_title="Rows in the extract"),
                            legend(True, "Selected for modelling?"))),

        chart(pid + "/grain", "donutChart", C3, B2_Y, W1, B2_H,
              {"Category": [pcol(DI, "Grain", "Grain", active=True)],
               "Y": [pmeas(DI, "Datasets provided", "Datasets")]},
              "Grain of the ten files",
              "Only household-level files can join one-to-one",
              objects=merge(fill_by(DI, "Grain", {"Household": BLUE, "Person": GREY}),
                            legend(True, "Top"), labels(True, 9))),

        panel(pid + "/lineage", C4, B2_Y, W1, B2_H, "From ten files to one dataset", [
            BLANK,
            ("Ten extracts were profiled in Milestone 1. The three person-level files could not "
             "join one-to-one on the household key and were set aside.", "9pt", FG2, False),
            ("The seven household-level files joined on HouseholdID to give 20,940 households, "
             "after 46 exact duplicate rows were removed.", "9pt", FG2, False),
            ("Cleaning dropped a further 15, leaving the 20,925 households modelled. The eight "
             "food-insecurity items build the target and were held out of the predictors.",
             "9pt", FG2, False),
        ]),

        table(pid + "/tbl", C1, B3_Y, W4, B3_H,
              [pcol(DI, "Dataset", "File"),
               pcol(DI, "Domain", "Domain"),
               pcol(DI, "Grain", "Grain"),
               pagg(DI, "Rows", "Rows"),
               pagg(DI, "Columns", "Columns"),
               pagg(DI, "Households", "Households"),
               pagg(DI, "DuplicateRows", "Duplicate rows"),
               pcol(DI, "Selected", "Selected"),
               pcol(DI, "Reason", "Reason")],
              "The ten extracts, and why each was kept or set aside",
              "Row, column and household counts measured directly off data/raw/"),
    ]
    return page(pid, "Data foundation", v)


# ============================================================ 8. Data quality
def p8():
    """Timothy's Milestone 1 Data Quality page, rebuilt on the Milestone 2 cleaning log."""
    pid = "p8"
    v = page_header(
        pid,
        "What was wrong with it, and what did we do?",
        "Every data-quality problem found during cleaning, and how each was treated",
        badge=("CLEANING LOG", "qa_log_personC.csv, 115 entries"))
    v += [
        card(pid + "/c1", C1, B1_Y, W1, B1_H, DQ, "Issues logged",
             "Problems found and fixed", "Milestone 2 cleaning log"),
        card(pid + "/c2", C2, B1_Y, W1, B1_H, DQ, "Issue types",
             "Distinct kinds of problem", None),
        card(pid + "/c3", C3, B1_Y, W1, B1_H, DQ, "Datasets repaired",
             "Datasets affected", "Of the seven selected"),
        card(pid + "/c4", C4, B1_Y, W1, B1_H, DQ, "Columns repaired",
             "Columns repaired", "Counted per dataset"),

        chart(pid + "/types", "clusteredBarChart", C1, B2_Y, W3, B2_H,
              {"Category": [pcol(DQ, "Problem", "Problem", active=True)],
               "Y": [pmeas(DQ, "Issues logged", "Columns affected")]},
              "Data-quality problems by type",
              "Sentinel codes dominate: 99, 9 and 8 used for unspecified and do-not-know",
              sort=[(pmeas(DQ, "Issues logged"), "Descending")],
              objects=merge(fill(AMBER), axes(val_title="Columns affected"),
                            labels(True), legend(False))),

        panel(pid + "/how", C4, B2_Y, W1, B2_H, "How these were treated", [
            BLANK,
            ("Sentinel codes and text tokens were recoded to missing rather than imputed, so a "
             "do-not-know answer never becomes a number the model trusts.", "9pt", FG2, False),
            ("Duplicate household rows were removed, provinces rebuilt from the clean numeric "
             "code, and out-of-range values restricted to their valid set.", "9pt", FG2, False),
            ("The same rules run in the deployed application, so a household scored in "
             "production is cleaned exactly as the training data was.", "9pt", FG2, False),
            ("Before and After mean different things per row and are never summed.",
             "9pt", AMBER, False),
        ]),

        chart(pid + "/byfile", "clusteredColumnChart", C1, B3_Y, W2, B3_H,
              {"Category": [pcol(DQ, "Domain", "Dataset", active=True)],
               "Y": [pmeas(DQ, "Issues logged", "Issues")]},
              "Issues by dataset",
              "All seven selected files needed repair",
              sort=[(pmeas(DQ, "Issues logged"), "Descending")],
              objects=merge(fill(AMBER), axes(val_title="Issues logged"), labels(True),
                            legend(False))),

        table(pid + "/log", C3, B3_Y, W2, B3_H,
              [pcol(DQ, "Dataset", "File"),
               pcol(DQ, "Column", "Column"),
               pcol(DQ, "Problem", "Problem"),
               pcol(DQ, "Treatment", "Treatment")],
              "The repair log",
              "One row per column repaired, as written during Milestone 2 cleaning"),
    ]
    return page(pid, "Data quality", v)


# ============================================================= 9. Reconciliation
def p9():
    pid = "p9"
    v = page_header(
        pid,
        "Can we trust these numbers?",
        "Every dashboard figure checked against the R pipeline",
        badge=("RECONCILIATION", "Dashboard minus R must read 0.0"))
    v += [
        card(pid + "/c1", C1, B1_Y, W1, B1_H, HH, "Households in sample",
             "Households modelled", "Expected 20,925"),
        card(pid + "/c2", C2, B1_Y, W1, B1_H, HH, "At-risk share (weighted)",
             "At risk - this dashboard", "Weighted"),
        card(pid + "/c3", C3, B1_Y, W1, B1_H, HH, "R at-risk share (weighted)",
             "At risk - recomputed in R", "From powerbi_reconciliation.csv"),
        card(pid + "/c4", C4, B1_Y, W1, B1_H, HH, "Difference at-risk (points)",
             "Difference", "Percentage points - must read 0.0"),

        table(pid + "/recon", C1, B2_Y, W3, B2_H,
              [pcol(HH, "Province", "Province"),
               pmeas(HH, "Households in sample", "Households"),
               pmeas(HH, "At-risk share (weighted)", "At risk - dashboard"),
               pmeas(HH, "R at-risk share (weighted)", "At risk - R"),
               pmeas(HH, "Difference at-risk (points)", "Diff (pts)"),
               pmeas(HH, "Referred share", "Referred - dashboard"),
               pmeas(HH, "R referred share", "Referred - R"),
               pmeas(HH, "Difference referred (points)", "Diff (pts)"),
               pmeas(HH, "Reconciliation status", "Status")],
              "Dashboard against R, province by province",
              "Every difference column must read 0.0 and every status Reconciled"),

        panel(pid + "/how", C4, B2_Y, W1, B2_H, "How this check works", [
            BLANK,
            ("The dashboard measures recompute each percentage from the 20,925 household rows. "
             "The R columns are looked up from powerbi_reconciliation.csv, written straight out "
             "of the evaluation notebook.", "9pt", FG2, False),
            ("Because the two are computed independently, any difference other than 0.0 means "
             "the export, the model or a measure has moved.", "9pt", FG2, False),
            ("The same check runs headlessly in report/M4/check_numbers.py, which fails the "
             "build if the figures drift.", "9pt", FG3, False),
        ]),

        table(pid + "/bench", C1, B3_Y, W2, B3_H,
              [pcol(RC, "Breakdown", "Breakdown"),
               pcol(RC, "Group", "Group"),
               pagg(RC, "Households", "Households"),
               pagg(RC, "AtRiskPct_weighted", "At risk %"),
               pagg(RC, "SeverePct_weighted", "Severe %"),
               pagg(RC, "ReferredPct", "Referred %")],
              "The R benchmark table in full",
              "18 rows: all households, then by province, settlement type and income band"),

        panel(pid + "/lineage", C3, B3_Y, W2, B3_H, "Known limits", [
            ("Where the data comes from, and what was repaired to get it here, is on the Data "
             "foundation and Data quality pages.", "9pt", FG3, False),
            ("Income is self-reported and 448 households report it as unknown. The dwelling and "
             "water-source variables profiled in Milestone 1 did not survive variable selection "
             "and are deliberately not shown, because putting them beside the model's outputs "
             "would imply the screen uses them.", "9pt", FG2, False),
            ("The target is a proxy built from eight survey answers rather than a measured "
             "outcome, so every finding here is an association.", "9pt", FG2, False),
            ("Survey data, not a census. Percentages are weighted estimates carrying sampling "
             "error, and there is no external validation set.", "9pt", AMBER, True),
        ]),
    ]
    return page(pid, "Reconciliation", v)


PAGES = [p1, p2, p3, p4, p5, p6, p7, p8, p9]
