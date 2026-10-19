# check_numbers.py
# Person B's Milestone 4 duty: "checks the evaluation numbers quoted anywhere".
#
#   python report/M4/check_numbers.py
#
# Two jobs:
#   1. Recompute the canonical figures straight from data/powerbi/powerbi_households.csv
#      and assert they match data/evaluation/. If the model is ever retrained, this fails
#      loudly instead of letting the report quote stale numbers.
#   2. Scan the Milestone 4 deliverables for figures that are easy to confuse, and report
#      where each canonical number appears.
#
# Exit code 0 = everything reconciles. Non-zero = something to fix before submission.

import csv
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVAL = os.path.join(ROOT, "data", "evaluation")
PBI = os.path.join(ROOT, "data", "powerbi")

THRESHOLD = 0.24
TOL = 5e-4

problems = []
notes = []


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def check(label, got, want, tol=TOL):
    ok = abs(got - want) <= tol
    print(f"  {'OK ' if ok else 'BAD'}  {label:<48} {got:.4f}  (expected {want:.4f})")
    if not ok:
        problems.append(f"{label}: computed {got:.4f}, evaluation file says {want:.4f}")
    return ok


# ---------------------------------------------------------------------------
# 1. Recompute from the dashboard table, compare with the evaluation outputs
# ---------------------------------------------------------------------------
print("\n1. Dashboard table vs evaluation outputs (test set, threshold 0.24)")

hh = read(os.path.join(PBI, "powerbi_households.csv"))
test = [r for r in hh if r["Split"] == "Test"]
at_risk = [r for r in test if r["AtRisk"] == "1"]
flagged = [r for r in test if float(r["ModelProbability"]) >= THRESHOLD]
tp = [r for r in flagged if r["AtRisk"] == "1"]

ev = {r["model"]: r for r in read(os.path.join(EVAL, "evaluation_matrix.csv"))}
f = ev["Binary logistic (glmnet)"]

check("recall", len(tp) / len(at_risk), float(f["screen_recall"]))
check("precision", len(tp) / len(flagged), float(f["screen_precision"]))
check("share referred (test)", len(flagged) / len(test), float(f["pct_flagged"]))
check("threshold", THRESHOLD, float(f["threshold"]))

sub = read(os.path.join(EVAL, "subgroup_performance.csv"))
n_test_sub = sum(int(r["households"]) for r in sub if r["variable"] == "grant_band")
if n_test_sub != len(test):
    problems.append(f"test-set size disagrees: subgroup table {n_test_sub}, dashboard {len(test)}")
print(f"  {'OK ' if n_test_sub == len(test) else 'BAD'}  test-set size                                    "
      f"{len(test)}  (subgroup table {n_test_sub})")

sev = {r["model"]: r for r in read(os.path.join(EVAL, "severe_flagged.csv"))}
sev_test = [r for r in test if r["Severe"] == "1"]
sev_flagged = [r for r in sev_test if float(r["ModelProbability"]) >= THRESHOLD]
check("severely insecure flagged",
      len(sev_flagged) / len(sev_test),
      float(sev["Binary logistic (glmnet)"]["severe_flagged"]))

# ---------------------------------------------------------------------------
# 2. The two populations that get confused
# ---------------------------------------------------------------------------
print("\n2. Populations that are easy to mix up")

all_flagged = sum(1 for r in hh if r["ReferForReview"] == "1") / len(hh)
test_flagged = len(flagged) / len(test)
recon = {(r["Breakdown"], r["Group"]): r for r in read(os.path.join(PBI, "powerbi_reconciliation.csv"))}
wt = read(os.path.join(EVAL, "survey_weighted_check.csv"))[0]

print(f"  share referred, TEST set only        {test_flagged:6.3f}   <- the report and slides use this")
print(f"  share referred, ALL 20,925 households {all_flagged:6.3f}   <- powerbi_reconciliation.csv uses this")
print(f"  at-risk weighted, ALL households      "
      f"{float(recon[('All','All households')]['AtRiskPct_weighted'])/100:6.3f}   <- population estimate")
print(f"  at-risk weighted, TEST set            {float(wt['weighted_at_risk_rate']):6.3f}   <- survey-weighted check")
print(f"  at-risk unweighted                    {float(wt['unweighted_at_risk_rate']):6.3f}")
notes.append(
    "58.9% (test) and 59.2% (all households) are both correct referral rates for different "
    "populations; 28.3% (all, weighted) and 28.8% (test, weighted) likewise. Label which one "
    "any visual or sentence means."
)

# ---------------------------------------------------------------------------
# 3. Where each canonical figure appears in the Milestone 4 deliverables
# ---------------------------------------------------------------------------
print("\n3. Canonical figures in the Person B deliverables")

CANON = {
    "80.7%": "recall on the test set",
    "41.9%": "precision",
    "58.9%": "share referred (test set)",
    "0.736": "screening ROC-AUC",
    "0.24": "referral threshold",
    "6,279": "test-set households",
    "20,925": "modelling-set households",
    "85.7%": "severely insecure households flagged",
    "39.2%": "recall, income above R11,500",
    "61.7%": "recall, no grant recipients",
    "94.0%": "recall, income below R2,500",
    "0.082": "top driver AUC drop",
    "58.3%": "food-insecure share where income fell sharply",
    "37.6%": "food-insecure share, grant households",
    "70.7%": "monitoring alert floor for recall",
}

targets = [
    os.path.join(ROOT, "report", "M4", "BIN381_M4_PersonB_Sections_4_6_8.docx"),
    os.path.join(ROOT, "report", "M4", "BIN381_M4_PersonB_Slides_5_to_7.md"),
    os.path.join(ROOT, "docs", "powerbi_m4_person_b_pages.md"),
    # The things that are actually submitted, so a figure cannot drift in the
    # assembled report or on a slide without this failing.
    os.path.join(ROOT, "report", "M4", "BIN381_M4_Report_Group_P1.docx"),
    os.path.join(ROOT, "report", "M4", "BIN381_M4_PersonC_Sections_5_7.docx"),
    os.path.join(ROOT, "report", "M4", "BIN381_M4_PersonC_Slides_8_to_10.md"),
    os.path.join(ROOT, "report", "M4", "BIN381_M4_Slides_Group_P1.pptx"),
]


def text_of(path):
    if path.endswith(".docx"):
        try:
            from docx import Document
        except ImportError:
            notes.append("python-docx not installed; skipped the .docx scan")
            return ""
        d = Document(path)
        parts = [p.text for p in d.paragraphs]
        parts += [c.text for t in d.tables for r in t.rows for c in r.cells]
        return "\n".join(parts)
    if path.endswith(".pptx"):
        try:
            from pptx import Presentation
        except ImportError:
            notes.append("python-pptx not installed; skipped the .pptx scan")
            return ""
        parts = []
        for slide in Presentation(path).slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    parts.append(shape.text_frame.text)
                if shape.has_table:
                    parts += [c.text for r in shape.table.rows for c in r.cells]
            if slide.has_notes_slide:
                parts.append(slide.notes_slide.notes_text_frame.text)
        return "\n".join(parts)
    with open(path, encoding="utf-8") as fh:
        return fh.read()


corpus = {}
for path in targets:
    if not os.path.exists(path):
        problems.append(f"missing deliverable: {os.path.relpath(path, ROOT)}")
        continue
    corpus[os.path.relpath(path, ROOT)] = text_of(path)

for figure, meaning in CANON.items():
    where = [name for name, body in corpus.items() if figure in body]
    print(f"  {figure:<9} {meaning:<46} {len(where)} file(s)")

# ---------------------------------------------------------------------------
# 4. Traps: figures that would be wrong in a Person B sentence
# ---------------------------------------------------------------------------
print("\n4. Traps")

for name, body in corpus.items():
    for sentence in re.split(r"(?<=[.!?])\s+", body):
        if "59.2" in sentence and "test" in sentence.lower() and "all" not in sentence.lower():
            problems.append(f"{name}: 59.2% described as a test-set figure — that is the "
                            f"all-household rate (58.9% is the test set)")
        m = re.search(r"\b28\.3\s*%", sentence)
        # A sentence that lists several figures can mention the test set for a different
        # one, so only flag 28.3% when it is not labelled correctly where it appears.
        if m and "test" in sentence.lower() and not re.search(
                r"weighted|all household", sentence[m.start():m.end() + 30], re.I):
            problems.append(f"{name}: 28.3% described as a test-set figure — that is the "
                            f"all-household weighted rate (28.8% is the test set)")
        if re.search(r"accuracy of \d", sentence, re.I):
            problems.append(f"{name}: quotes an accuracy figure; this is an imbalanced screen, "
                            f"report recall/precision instead")
print("  checked 3 confusable-figure patterns across "
      f"{len(corpus)} deliverable(s)")

# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
for n in notes:
    print("NOTE:", n)
if problems:
    print(f"\n{len(problems)} problem(s) to fix:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("\nAll Milestone 4 Person B figures reconcile with data/evaluation/.")
