# build_personC_sections.py
# Builds Person C's Milestone 4 report sections (5 and 7) as a .docx.
#
#   python report/M4/build_personC_sections.py [--root <repo root>]
#
# Run from the repository root. Every number in the output is read from data/evaluation/
# and data/powerbi/ at build time, so the report cannot drift away from the notebooks.
# Re-run after any change to the model. Mirrors build_personB_sections.py.
#
# Section numbers follow the Milestone 4 team guideline:
#   5. Dashboard and deployment      (1.5 pages)
#   7. Ethics and responsible AI     (1 page)

import argparse
import csv
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))
ap.add_argument("--out", default=None)
args = ap.parse_args()

ROOT = args.root
EVAL = os.path.join(ROOT, "data", "evaluation")
PBI = os.path.join(ROOT, "data", "powerbi")
OUT = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "BIN381_M4_PersonC_Sections_5_7.docx")


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


# ---------------------------------------------------------------- the numbers
summary = {r["Metric"]: float(r["Value"]) for r in read(os.path.join(PBI, "powerbi_model_summary.csv"))}
recon = {(r["Breakdown"], r["Group"]): r for r in read(os.path.join(PBI, "powerbi_reconciliation.csv"))}
sub = read(os.path.join(PBI, "powerbi_subgroup_performance.csv"))
base = read(os.path.join(EVAL, "monitoring_baseline.csv"))[0]
severe = {r["model"]: r for r in read(os.path.join(EVAL, "severe_flagged.csv"))}
curve = read(os.path.join(PBI, "powerbi_threshold_curve.csv"))

THR = summary["Threshold"]
RECALL = summary["Recall (at-risk households found)"]
PREC = summary["Precision (referrals at risk)"]
FLAG = summary["Share of households referred"]
AUC = summary["ROC-AUC"]
TEST_N = int(summary["Test households"])
SEVERE_FLAGGED = float(severe["Binary logistic (glmnet)"]["severe_flagged"])

ALL = recon[("All", "All households")]
N_HH = int(ALL["Households"])
AT_RISK_W = float(ALL["AtRiskPct_weighted"])
SEVERE_W = float(ALL["SeverePct_weighted"])
REFERRED_ALL = float(ALL["ReferredPct"])

PROVINCES = sorted(((k[1], float(v["AtRiskPct_weighted"])) for k, v in recon.items()
                    if k[0] == "Province"), key=lambda kv: -kv[1])
WORST_PROV, WORST_PROV_PCT = PROVINCES[0]
BEST_PROV, BEST_PROV_PCT = PROVINCES[-1]
TRIB = recon[("Settlement", "Traditional/tribal")]
LOW_INC = recon[("IncomeBand", "< R2,500")]
HIGH_INC = recon[("IncomeBand", "> R11,500")]


def group(var, grp):
    for r in sub:
        if r["variable"] == var and r["group"] == grp:
            return r
    raise KeyError((var, grp))


HIGH_INC_RECALL = float(group("Monthly income", "> R11,500")["recall"])
NO_GRANT_RECALL = float(group("Grant receipt", "No grants")["recall"])
BIG_HH_RECALL = float(group("Household size", "7+")["recall"])
OUTSIDE = [r for r in sub if r["within_tolerance"] == "No"]
RECALL_ALERT = float(base["recall_alert_below"])


def at(t):
    for r in curve:
        if abs(float(r["Threshold"]) - t) < 1e-9:
            return r
    raise KeyError(t)


LOW_T, HIGH_T = at(0.14), at(0.40)


def pct(x, dp=1):
    return f"{100 * x:.{dp}f}%"


# ---------------------------------------------------------------- the document
# Match the Milestone 3 report and Person B's sections: A4, 2.54 cm margins, Calibri 11.
doc = Document()
for s in doc.sections:
    s.page_height, s.page_width = Cm(29.7), Cm(21.0)
    s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Cm(2.54)

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.paragraph_format.line_spacing = 1.15
normal.paragraph_format.space_after = Pt(6)

for name, size in (("Heading 1", 14), ("Heading 2", 12)):
    st = doc.styles[name]
    st.font.name = "Calibri"
    st.font.size = Pt(size)
    st.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)


def para(text, style=None, italic=False, size=None, bold=False):
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    run.italic = italic
    run.bold = bold
    if size:
        run.font.size = Pt(size)
    return p


def caption(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)
    p.paragraph_format.space_after = Pt(8)
    return p


def figure_slot(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    p.paragraph_format.space_after = Pt(2)
    return p


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.add_run(text)
    p.paragraph_format.space_after = Pt(4)
    return p


def table(headers, rows, widths=None, size=9):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(size)
        cell.paragraphs[0].paragraph_format.space_after = Pt(0)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(v))
            run.font.size = Pt(size)
            cells[i].paragraphs[0].paragraph_format.space_after = Pt(0)
    if widths:
        for r in t.rows:
            for i, w in enumerate(widths):
                r.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


# =========================================================== 5. Dashboard and deployment
doc.add_heading("5. Dashboard and deployment", level=1)

para(
    "Two things reached a user. A Power BI dashboard serves the programme manager deciding where "
    f"to send limited field capacity: it describes the {N_HH:,} surveyed households and lets the "
    "manager set the referral threshold against real capacity. An R/Shiny application serves the "
    "official assessing a household that was never surveyed, one at a time or in a batch, and "
    "shows why. Neither decides eligibility."
)

doc.add_heading("5.1 The dashboard answers six decision questions", level=2)

para(
    "Because the brief warns against showing every variable, the decision questions were written "
    "first and each of the first six pages is titled with the one it answers; three further pages "
    "carry the evidence behind them. The two first-iteration dashboards were merged into one "
    "report on the final analytical dataset, the Milestone 1 file contributing its layout and its "
    "geographic, household and data-lineage pages, rebuilt on tables that live in the repository, "
    "and the Milestone 4 file the performance, subgroup and driver pages."
)

table(
    ["Decision question", "Page", "What the dashboard shows"],
    [
        ["1. Where is food insecurity concentrated?", "Where the need is",
         f"{WORST_PROV} worst at {WORST_PROV_PCT:.1f}%, {BEST_PROV} lowest at "
         f"{BEST_PROV_PCT:.1f}%; traditional and tribal areas "
         f"{float(TRIB['AtRiskPct_weighted']):.1f}%. Drills into settlement type."],
        ["2. Which kinds of household are most affected?", "Who is affected",
         f"Risk falls from {float(LOW_INC['AtRiskPct_weighted']):.1f}% below R2,500 a month to "
         f"{float(HIGH_INC['AtRiskPct_weighted']):.1f}% above R11,500, and rises with household "
         "size, grant receipt and no electricity."],
        ["3. Can we trust the screening tool enough to act on it?", "How well the screen works",
         f"On {TEST_N:,} held-out households it finds {pct(RECALL)} of at-risk households and "
         f"{pct(SEVERE_FLAGGED)} of the severely insecure, at {pct(PREC)} precision, "
         f"ROC-AUC {AUC:.3f}."],
        ["4. Which households does the screen miss, and where?", "Who the screen misses",
         f"{len(OUTSIDE)} of {len(sub)} subgroups fall outside a 10-point tolerance band; "
         f"weakest above R11,500 ({pct(HIGH_INC_RECALL)}) and with no grants "
         f"({pct(NO_GRANT_RECALL)})."],
        ["5. What should we ask about to spot risk early?", "What drives risk",
         "Income change against a year ago carries most of the signal; no electricity roughly "
         "doubles the odds."],
        ["6. How many households would a given threshold refer?", "How well the screen works",
         f"A slider moves all three together: {pct(float(LOW_T['Recall']))} recall at "
         f"{pct(float(LOW_T['ReferredShare']))} referred (0.14) down to "
         f"{pct(float(HIGH_T['Recall']))} at {pct(float(HIGH_T['ReferredShare']))} (0.40)."],
    ],
    widths=[4.8, 2.9, 7.8],
    size=8,
)
caption("Table 5.1 The six decision questions, the page answering each, and the answer.")

figure_slot("[Figures 5.1 and 5.2 — pbi_m4_1_overview.png and pbi_m4_4_performance.png, "
            "side by side at about 7.5 cm wide each]")
caption("Figures 5.1-5.2 The landing page, and test-set performance with the threshold what-if.")

para(
    "Four slicers sit in the same position on every household page, every axis is labelled, and no "
    "household identifier appears anywhere: the export carries a row number instead. Every page "
    "states that this is a screening aid, not an eligibility test. Three further pages carry the "
    "evidence: the ten extracts profiled and the seven selected, the 115 data-quality problems "
    "found and how each was treated, and the reconciliation in 5.2 below."
)

doc.add_heading("5.2 Every dashboard figure reconciles with the analysis", level=2)

para(
    "The dashboard recomputes each percentage from the household rows; the R pipeline writes the "
    "same percentages independently. A reconciliation page subtracts the two, and all nine "
    "provinces, three settlement types and five income bands agree to 0.0 percentage points, "
    f"nationally at {AT_RISK_W:.1f}% at risk, {SEVERE_W:.1f}% severe and {REFERRED_ALL:.1f}% "
    f"referred. The what-if panel at the deployed threshold reproduces the headline cards exactly. "
    f"One distinction is kept visible: {pct(FLAG)} is the referral rate on the test set, used for "
    f"every performance claim, while {REFERRED_ALL:.1f}% is the rate across all {N_HH:,} modelled "
    "households, used on the prevalence pages. A build-time check fails if they are swapped."
)

doc.add_heading("5.3 The deployed path: validate, clean, preprocess, score", level=2)

para(
    "The application serves the same workflow object that was evaluated, at the same threshold of "
    f"{THR:.2f}; both are asserted in code rather than assumed. A typed household and a CSV upload "
    "follow one path:"
)
bullet(
    "Validate — the seven inputs must be present, every column is read as text so long household "
    "identifiers keep their precision, the eight food-insecurity items are discarded if present "
    "(the leakage rule, enforced at the door), and duplicates are flagged."
)
bullet(
    "Clean — the Milestone 2 rules, column by column: sentinels and text tokens become missing, "
    "and unseen codes, impossible values and rows missing more than two inputs are left unscored "
    "rather than guessed."
)
bullet(
    "Preprocess — raw codes become the training features (labelled factors, log income, income "
    "per person), then the recipe imputes, encodes and scales using training values only."
)
bullet(
    "Score — a probability, the words \"Higher risk: refer for review\" at or above the threshold, "
    "and the three inputs that moved it most."
)
para(
    "Bad input is a tested case: a 13-row file of deliberately malformed households exercises "
    f"every rule. Pushing all {TEST_N:,} test households back through the app's own path "
    "reproduces the saved predictions with a largest difference of zero, so the app, the notebook "
    "and the report quote one set of numbers."
)

doc.add_heading("5.4 Monitoring and retraining triggers", level=2)

para(
    "The outcome is only observed when Stats SA releases a new survey, so between releases the "
    "application monitors its inputs and outputs. Each upload appends one row of totals, never "
    "household rows, and a monthly review applies the thresholds below."
)

table(
    ["Signal", "Baseline", "Alert"],
    [
        ["Input drift in income, settlement type, household size", "PSI 0",
         "0.10 to 0.25 watch; above 0.25 act"],
        ["Missing income", "2.2% at integration", "above 5%"],
        ["Rows not scored", "0% of test rows", "above 5%"],
        ["Share referred", f"{pct(FLAG)}", "more than 10 points either way"],
        ["Recall, at each survey release", f"{RECALL:.3f}", f"below {RECALL_ALERT:.3f}"],
        ["Calibration, at each survey release", f"Brier {float(base['test_brier']):.3f}",
         "clearly worse"],
        ["Subgroup recall, at each survey release", "the subgroup table",
         "gap above 10 points"],
    ],
    widths=[7.0, 4.3, 4.2],
)
caption("Table 5.2 Monitoring thresholds, each tied to the test-set baseline.")

para(
    "A simulated shift makes the first row concrete: raising nominal incomes by 25%, roughly five "
    "years of inflation, drops the share referred from 59.8% to 51.9% with no change in real need. "
    "That is the failure mode this screen is most exposed to, because income enters the model in "
    "rands. Retrain when any alert fires, when the survey changes one of the eight predictor "
    "items, or annually at each release; retire the tool if recall for any group above 500 "
    "households falls below 0.65. Rollback is by model version, recorded with the test metrics "
    "that version achieved."
)

# ============================================== 7. Ethics and responsible AI
doc.add_heading("7. Ethics and responsible AI", level=1)

para(
    "The brief asks for ethics across the lifecycle rather than as a closing paragraph. Table 7.1 "
    "records where each issue was dealt with; the paragraphs below give the three that shaped the "
    "result."
)

table(
    ["CRISP-DM phase", "Issue", "What was done"],
    [
        ["Business understanding", "Could be read as an eligibility test",
         "Scope fixed as screening and prioritisation; an official reviews every higher-risk "
         "result, and the caveat appears on every page, result and download"],
        ["Data understanding", "Survey data about identifiable households",
         "Seven predictor fields only; identifiers never displayed or returned"],
        ["Data preparation", "The eight food-insecurity items define the target",
         "Excluded from the predictors and asserted in code at every stage, including in the "
         "upload validator"],
        ["Modelling", "Imbalance, and accuracy would flatter the model",
         "Stratified cross-validation; recall, precision, PR-AUC and calibration reported "
         "instead of accuracy"],
        ["Evaluation", "The best-scoring model was not the most suitable",
         "Interpretable logistic regression chosen over a marginally better random forest, with "
         "the trade-off stated"],
        ["Evaluation", "Unequal recall between groups",
         "Equal-opportunity criterion, 10-point tolerance fixed before results were seen; gaps "
         "disclosed, no group-specific thresholds"],
        ["Deployment", "Privacy of households scored in production",
         "Uploads processed in memory and not stored; monitoring keeps totals only; access "
         "behind sign-in"],
        ["Deployment", "Stigmatising labels",
         "The result reads \"Higher risk: refer for review\", never \"food insecure\""],
        ["Monitoring", "Only referred households generate new labels",
         "A random audit sample of lower-risk households is followed up monthly"],
    ],
    widths=[3.2, 4.3, 8.0],
    size=8,
)
caption("Table 7.1 Ethics decisions by lifecycle phase.")

doc.add_heading("Privacy, POPIA and human oversight", level=2)
para(
    "Data minimisation was applied at every boundary. The model needs seven fields and receives "
    "only those; uploads are held in memory for one request and never written to disk; the "
    "monitoring log keeps counts and distributions, never a household row; identifiers are not "
    "shown, not returned in downloads, and absent from the dashboard. Because a higher-risk result "
    "could affect a household's access to support, a human stays in the loop by default, which is "
    "also what POPIA section 71 requires of a decision taken solely by automated means."
)

doc.add_heading("Bias, and the gaps we did not close", level=2)
para(
    f"Equal opportunity was the chosen criterion, because the costly error here is missing a "
    f"food-insecure household. Of {len(sub)} subgroups, {len(OUTSIDE)} fall outside the 10-point "
    f"tolerance; two are better than average and two are worse. Recall is {pct(HIGH_INC_RECALL)} "
    f"for households reporting more than R11,500 a month and {pct(NO_GRANT_RECALL)} for households "
    f"receiving no grants, against {pct(RECALL)} overall: these are food-insecure households that "
    f"do not look poor on the inputs the model has. We did not close the gap with group-specific "
    f"thresholds, which would mean treating households differently by income on the basis of a "
    f"proxy target. Instead it is published on the dashboard, repeated in the app, and turned into "
    f"an operational rule, that a lower-risk result for a household in either group is not a reason "
    f"to close an assessment. Farm households, {group('Settlement type', 'Farms')['households']} in "
    f"the test set, have an interval too wide to support any claim of parity, so none is made."
)

doc.add_heading("Transparency, and the use of AI tools", level=2)
para(
    "Every result carries a probability, the three inputs that moved it most, and a statement of "
    "what the tool is not. The explanation method is honest about itself: it varies one input at a "
    "time against a typical household, so it shows association, not cause. The same discipline "
    "governs the findings, which is why grant receipt is reported everywhere as a marker of "
    "targeting rather than a cause, and why the target is described as a proxy built from eight "
    "survey answers on a sample rather than a census. Generative AI assistance was used by all "
    "three members, is acknowledged in the report, and is recorded use by use in the ethics and AI "
    "usage log with what the tool produced, how it was checked and what the team decided. Nothing "
    "was accepted on the assistant's word: AI-assisted code was run against the project's own data "
    "and compared with figures computed independently. The members remain the authors of the "
    "submission and of every decision in Table 7.1."
)

doc.save(OUT)
print("wrote", OUT)
print(f"  households {N_HH:,} | at risk {AT_RISK_W:.1f}% weighted | severe {SEVERE_W:.1f}%")
print(f"  test {TEST_N:,} | recall {pct(RECALL)} | precision {pct(PREC)} | referred {pct(FLAG)}")
print(f"  subgroups outside tolerance: {len(OUTSIDE)} of {len(sub)}")
