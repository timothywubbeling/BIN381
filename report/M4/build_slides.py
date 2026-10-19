#!/usr/bin/env python3
"""Build the ten-slide executive deck from the team's speaker notes.

Slides 5 to 7 follow BIN381_M4_PersonB_Slides_5_to_7.md and slides 8 to 10 follow
BIN381_M4_PersonC_Slides_8_to_10.md. Slides 2 to 4 are drafted from sections 1 to 3 of the
report and are Alexander's to approve. Every figure on a slide is listed in FIGURES below
and is re-checked against data/evaluation/ by check_numbers.py.

Run from the repository root:  python report/M4/build_slides.py
"""
import csv
import os

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FIGURES = os.path.join(ROOT, "docs", "figures")
OUT = os.path.join(HERE, "BIN381_M4_Slides_Group_P1.pptx")
CURVE = os.path.join(ROOT, "data", "powerbi", "powerbi_threshold_curve.csv")


def curve_row(threshold):
    """Recall and referral share at a threshold, read from the curve rather than typed."""
    with open(CURVE, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if abs(float(r["Threshold"]) - threshold) < 1e-9:
                return f'{float(r["Recall"]):.1%}', f'{float(r["ReferredShare"]):.1%}'
    raise SystemExit(f"threshold {threshold} is not in {os.path.basename(CURVE)}")

# The dashboard's own palette, so a pasted screenshot does not clash with the slide.
INK = RGBColor(0x20, 0x1F, 0x1E)
DARK = RGBColor(0x20, 0x1F, 0x1E)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x60, 0x5E, 0x5C)
PALE = RGBColor(0xD2, 0xD0, 0xCE)
BLUE = RGBColor(0x28, 0x78, 0xBD)      # the main measure, as on the dashboard
LIGHTBLUE = RGBColor(0x70, 0xB0, 0xE0)
AMBER = RGBColor(0xFC, 0xB7, 0x14)     # caution
TEAL = RGBColor(0x0E, 0xB1, 0x94)      # referral volume
RED = RGBColor(0xF1, 0x56, 0x28)       # where the screen is weakest
TINT = RGBColor(0xF3, 0xF6, 0xFA)      # card fill on a light slide

HEAD, BODY = "Calibri", "Calibri"
MARGIN = Inches(0.6)
W, H = Inches(13.333), Inches(7.5)

# Screenshots of the merged dashboard do not exist yet; fall back to the pre-merge
# versions so the deck builds, and pick the new ones up automatically once exported.
SHOTS = {
    "dashboard": ["pbi_m4_4_performance.png", "pbi_b1_performance.png"],
    "app_single": ["app_1_single_household.png"],
    "app_batch": ["app_2_batch_upload.png"],
    "app_limits": ["app_3_about_and_limits.png"],
}
missing_art = []


def shot(key):
    for name in SHOTS[key]:
        p = os.path.join(FIGURES, name)
        if os.path.exists(p):
            if name != SHOTS[key][0]:
                missing_art.append(f"{SHOTS[key][0]} not exported yet; used {name}")
            return p
    missing_art.append(f"no image found for {key}: {SHOTS[key]}")
    return None


prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]


def slide(dark=False, number=None):
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = DARK if dark else WHITE
    if number:
        tx(s, f"{number}/10", W - Inches(1.1), H - Inches(0.5), Inches(0.6), Inches(0.3),
           size=10, color=PALE if dark else MUTED, align=PP_ALIGN.RIGHT)
    return s


def tx(s, text, x, y, w, h, size=15, bold=False, color=INK, align=PP_ALIGN.LEFT,
       font=BODY, italic=False, space_after=6, line=None):
    """One text box. `text` is a string, or a list of (text, overrides) paragraphs."""
    box = s.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    paras = text if isinstance(text, list) else [(text, {})]
    for i, (body, over) in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = over.get("align", align)
        p.space_after = Pt(over.get("space_after", space_after))
        if over.get("line", line):
            p.line_spacing = over.get("line", line)
        run = p.add_run()
        run.text = body
        f = run.font
        f.name = over.get("font", font)
        f.size = Pt(over.get("size", size))
        f.bold = over.get("bold", bold)
        f.italic = over.get("italic", italic)
        f.color.rgb = over.get("color", color)
    return box


def title(s, text, dark=False):
    return tx(s, text, MARGIN, Inches(0.45), W - 2 * MARGIN, Inches(1.15),
              size=32, bold=True, color=WHITE if dark else INK, font=HEAD)


def stat(s, value, label, x, y, w, color=BLUE, value_size=48, card=True):
    """A big number with a small label under it."""
    if card:
        box = s.shapes.add_shape(1, x, y, w, Inches(1.55))     # 1 = rectangle
        box.fill.solid()
        box.fill.fore_color.rgb = TINT
        box.line.fill.background()
        box.shadow.inherit = False
        box.text_frame.text = ""
    tx(s, value, x + Inches(0.2), y + Inches(0.12), w - Inches(0.4), Inches(0.75),
       size=value_size, bold=True, color=color, font=HEAD)
    tx(s, label, x + Inches(0.2), y + Inches(0.93), w - Inches(0.4), Inches(0.5),
       size=12, color=MUTED, space_after=0)


def footer(s, text, color=MUTED, dark=False, italic=True):
    tx(s, text, MARGIN, H - Inches(0.95), W - 2 * MARGIN - Inches(0.8), Inches(0.62),
       size=13, italic=italic, color=color)


def table(s, rows, x, y, w, col_w, header=True, size=12, row_h=Inches(0.42),
          emphasise=()):
    """A plain table: no banding, no borders to fight with, header in bold blue."""
    t = s.shapes.add_table(len(rows), len(rows[0]), x, y, w, row_h * len(rows)).table
    t.first_row = header
    for i, cw in enumerate(col_w):
        t.columns[i].width = cw
    for r, row in enumerate(rows):
        t.rows[r].height = row_h
        for c, val in enumerate(row):
            cell = t.cell(r, c)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            cell.fill.solid()
            cell.fill.fore_color.rgb = TINT if r == 0 and header else WHITE
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = str(val)
            run.font.size = Pt(size)
            run.font.name = BODY
            run.font.bold = (r == 0 and header) or (r, c) in emphasise
            run.font.color.rgb = (BLUE if r == 0 and header else
                                  RED if (r, c) in emphasise else INK)
    return t


def bar_chart(s, cats, vals, x, y, w, h, colour=BLUE, number_format='0.000'):
    data = CategoryChartData()
    data.categories = cats
    data.add_series("v", vals, number_format)
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, x, y, w, h, data)
    ch = gf.chart
    ch.has_title = False
    ch.has_legend = False
    plot = ch.plots[0]
    plot.gap_width = 60
    plot.vary_by_categories = False
    plot.has_data_labels = True
    labels = plot.data_labels
    labels.number_format, labels.number_format_is_linked = number_format, False
    labels.position = XL_LABEL_POSITION.OUTSIDE_END
    labels.font.size, labels.font.bold, labels.font.name = Pt(11), True, BODY
    labels.font.color.rgb = INK
    ser = plot.series[0]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = colour
    cat_ax, val_ax = ch.category_axis, ch.value_axis
    cat_ax.tick_labels.font.size, cat_ax.tick_labels.font.name = Pt(11), BODY
    cat_ax.tick_labels.font.color.rgb = INK
    cat_ax.has_major_gridlines = False
    val_ax.has_major_gridlines = False
    val_ax.visible = False
    return ch


def picture(s, key, x, y, w):
    p = shot(key)
    if p:
        return s.shapes.add_picture(p, x, y, width=w)
    ph = s.shapes.add_shape(1, x, y, w, Emu(int(w * 0.56)))
    ph.fill.solid()
    ph.fill.fore_color.rgb = TINT
    ph.line.color.rgb = PALE
    ph.text_frame.text = "screenshot to be exported"
    return ph


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text.strip()


DRAFTED = ("\n\nDrafted from sections 1 to 3 of the report, which are Alexander's. "
           "He presents this slide and should change any wording he would not say.")

# ---------------------------------------------------------------------------
# 1. Title
# ---------------------------------------------------------------------------
s = slide(dark=True)
tx(s, "Finding the households most at risk of food insecurity",
   MARGIN, Inches(2.1), Inches(10.6), Inches(2.0), size=40, bold=True, color=WHITE, font=HEAD)
tx(s, "A screening aid for targeting limited support, built on the Stats SA General "
      "Household Survey 2024", MARGIN, Inches(4.0), Inches(9.8), Inches(0.9),
   size=18, color=PALE)
tx(s, [("Group P1  ·  BIN381 Milestone 4", {"size": 14, "color": LIGHTBLUE, "bold": True}),
       ("Alexander Solomon  ·  Rudi Jan du Plessis  ·  Timothy Wubbeling",
        {"size": 14, "color": PALE})],
   MARGIN, Inches(5.6), Inches(9.0), Inches(1.0))
notes(s, """
Good morning. Our question was not what causes food insecurity, it was a targeting question: when a
policy institute can only follow up a fraction of households, which ones should it visit first?

We built a screening model on the General Household Survey 2024, a Power BI dashboard for the
programme manager who sets that capacity, and a Shiny tool for the official assessing a household at
the door. Alexander takes the problem, the data and the modelling; Rudi the results and the
dashboard; Timothy the app, the recommendations and the limits.
""")

# ---------------------------------------------------------------------------
# 2. The problem
# ---------------------------------------------------------------------------
s = slide(number=2)
title(s, "Three in ten households are food insecure, and support reaches a fraction of them")
tx(s, "The institute has to choose which households to follow up. We rank them by risk, so "
      "scarce field capacity goes where it is most likely to find a household that needs it. "
      "The tool advises an official; it never decides eligibility.",
   MARGIN, Inches(1.62), Inches(11.2), Inches(0.9), size=16)
for i, (v, l, c) in enumerate([
        ("20,940", "households surveyed, all nine provinces", BLUE),
        ("30.6%", "report running out of food, skipping meals or going hungry", RED),
        ("8", "survey questions behind the food-insecurity score", TEAL)]):
    stat(s, v, l, MARGIN + i * Inches(3.95), Inches(2.8), Inches(3.6), color=c,
         value_size=40)
tx(s, [("What we promised in Milestone 1", {"size": 16, "bold": True, "color": BLUE}),
       ("BO1  Rank the household indicators most associated with food insecurity, "
        "with an effect size.", {}),
       ("BO2  Build an interpretable model, without leakage, tested on held-out data.", {}),
       ("BO3  Give decision-makers self-service exploration by province and household type.", {})],
   MARGIN, Inches(4.75), Inches(11.5), Inches(1.6), size=15)
footer(s, "Six hypotheses about what puts a household at risk - income, settlement, size, "
          "electricity, grants, sanitation - are answered in sections 4 and 7 of the report.")
notes(s, """
The stakeholder is a policy institute of the Department of Social Development type. It cannot visit
everyone, so the useful question is who to visit first.

Our evidence is the General Household Survey 2024: 20,940 households, and eight questions about
running out of food, skipping meals and going hungry. Counting the yes answers gives a food
insecurity score, and three in ten households score at least one.

Note the wording of BO2: interpretable, and without leakage. We will come back to both - the eight
food questions that define the target can never be inputs to the model that predicts it.""" + DRAFTED)

# ---------------------------------------------------------------------------
# 3. Data strategy
# ---------------------------------------------------------------------------
s = slide(number=3)
title(s, "Seven of eleven survey files, joined without losing a single household")
rows = [["Decision", "Why", "What it changed"],
        ["Keep seven household-level files",
         "D01-D03 are person-level; D11 is a different survey with no shared IDs",
         "One row per household, key HouseholdID"],
        ["Read every ID as text",
         "18-digit IDs lose their last digits when read as numbers",
         "The 256-272 'duplicate households' per file disappeared"],
        ["Guarded one-to-one joins",
         "A plain join drops or duplicates rows silently",
         "15 placeholder keys in D05 repaired, not dropped"],
        ["Refused and 'unspecified' codes to missing",
         "9, 99, 9999999 are not real answers",
         "451 households have no usable income; imputed in-fold only"],
        ["Exclude the 8 food items and 8 related columns",
         "They define the target, so they cannot predict it",
         "Asserted in code; 8 predictors remain"]]
table(s, rows, MARGIN, Inches(1.62), W - 2 * MARGIN,
      [Inches(3.3), Inches(4.3), Inches(4.5)], size=12, row_h=Inches(0.52))
tx(s, [("20,940 households integrated  ->  15 cannot be scored  ->  "
        "20,925 modelled  ->  14,646 train / 6,279 test",
        {"size": 16, "bold": True, "color": BLUE})],
   MARGIN, Inches(5.45), W - 2 * MARGIN, Inches(0.5))
footer(s, "Every treatment is logged in data/clean/qa_log_personC.csv and every column's source "
          "and treatment in the Milestone 2 data dictionary. The test set was not used for any "
          "modelling decision.")
notes(s, """
Three files were left out on purpose, and we can defend each: D01 to D03 are about people, not
households, so using them would force an aggregation choice for every variable; D11 is a different
survey with no household IDs in common.

The second row is my favourite finding. Milestone 1 reported about 260 duplicate household IDs per
file. They were not duplicates - an 18-digit ID read as a number loses its last digits, so different
households collapsed onto the same value. Reading IDs as text made the problem vanish.

The last row is the leakage rule. The target counts eight food questions, so those eight and eight
related follow-ups are excluded from the predictors, and the notebook fails if any of them appears in
the modelling data.""" + DRAFTED)

# ---------------------------------------------------------------------------
# 4. Modelling
# ---------------------------------------------------------------------------
s = slide(number=4)
title(s, "Four candidates, cross-validated, and a deliberate switch to a yes-or-no screen")
rows = [["Model", "Three-tier CV ROC-AUC", "Screening CV ROC-AUC"],
        ["Multinomial logistic (glmnet)", "0.669", "0.734"],
        ["Decision tree (rpart)", "0.658", "0.721"],
        ["Random forest (ranger)", "0.673", "0.739"],
        ["Binary logistic (glmnet, lasso)", "not applicable", "0.733"]]
table(s, rows, MARGIN, Inches(1.62), Inches(7.1),
      [Inches(3.3), Inches(1.9), Inches(1.9)], size=12, row_h=Inches(0.46))
tx(s, [("Why the target changed", {"size": 16, "bold": True, "color": BLUE}),
       ("We began with three tiers because the brief asks for vulnerability levels, and wrote "
        "down in advance that we would fall back to a yes-or-no screen if the middle tier could "
        "not be separated.", {}),
       ("It could not: no three-tier model recalls more than 3.2% of mildly-to-moderately "
        "insecure households. The app also needs one probability per household.", {})],
   Inches(8.1), Inches(1.62), Inches(4.6), Inches(3.0), size=14)
tx(s, [("Stratified 5-fold cross-validation, seed 381, on the training set only. Preprocessing "
        "is re-learned inside every fold, so nothing leaks from the test set. Package versions "
        "are pinned with renv.", {"size": 13, "color": MUTED})],
   MARGIN, Inches(4.5), Inches(7.1), Inches(1.1))
footer(s, "Class weights were tested and rejected: they tripled severe-tier recall but halved "
          "recall on food-secure households and wrecked calibration. Imbalance is handled at the "
          "threshold instead.")
notes(s, """
Three model families, one more than the minimum, chosen to cover the trade-off between
interpretability and performance: a regularised logistic regression whose coefficients map onto our
hypotheses, a tree for readable rules, and a random forest as the performance benchmark.

The honest part of this slide is the right-hand side. The three-tier target failed. The middle tier -
about one household in ten - cannot be separated from its neighbours with these predictors, and we
had committed in advance to the fallback rather than inventing a reason afterwards. So we fitted a
fourth model on a single question: is this household at risk of any food insecurity?

Accuracy is never the selection metric here. Predicting food secure for everyone scores 69%.""" + DRAFTED)

# ---------------------------------------------------------------------------
# 5. Performance (Person B)
# ---------------------------------------------------------------------------
s = slide(number=5)
title(s, "The screen finds 4 in 5 at-risk households, and refers 3 in 5")
for i, (v, l, c) in enumerate([
        ("80.7%", "of at-risk households found", BLUE),
        ("41.9%", "of referrals are genuinely at risk", AMBER),
        ("58.9%", "of households sent for follow-up", TEAL),
        ("0.736", "ROC-AUC (0.5 would be a coin flip)", BLUE)]):
    stat(s, v, l, MARGIN + i * Inches(3.05), Inches(1.6), Inches(2.8), color=c, value_size=40)
rows = [["Threshold", "Recall", "Referred", "What it means"]] + [
    [label] + list(curve_row(t)) + [meaning] for t, label, meaning in [
        (0.14, "0.14 (F2-optimal)", "Rejected: refers five households in six"),
        (0.24, "0.24 (chosen)", "At least 80% recall, at the fewest referrals"),
        (0.30, "0.30", "150 fewer visits per 1,000, 1 in 8 at-risk newly missed"),
        (0.50, "0.50 (default)", "Rejected: misses 68.9% of at-risk households"),
    ]]
table(s, rows, MARGIN, Inches(3.5), W - 2 * MARGIN,
      [Inches(2.6), Inches(1.4), Inches(1.5), Inches(6.6)], size=12, row_h=Inches(0.46),
      emphasise={(2, 0), (2, 1), (2, 2)})
footer(s, "Measured once on a held-out test set of 6,279 households. Cross-validated AUC 0.733 "
          "against 0.736 on test, so there is no meaningful overfitting; Brier 0.180 and "
          "calibration error 0.012.")
notes(s, """
We chose the threshold before we looked at the test data, using a rule agreed with the problem in
mind: find at least 80% of at-risk households, at the fewest referrals. That lands on 0.24. On data
the model had never seen it finds 80.7% of at-risk households, and 85.7% of the severely food
insecure - the ones we least want to miss.

The cost is in the third column. Four in ten referrals are households that turn out to be food
secure, and we send three in five households for follow-up. That is a real operational load, and it
is a dial, not a fact: push the threshold up and you visit fewer households but miss more. The dial
is in the dashboard so programme managers can set it against the capacity they actually have.

One thing worth saying plainly: the random forest scored very slightly better, by about 0.009 AUC. We
did not take it. This tool has to justify every referral to an official, and a logistic regression
gives one interpretable number per factor. We traded a fraction of a point of accuracy for an
explanation.
""")

# ---------------------------------------------------------------------------
# 6. Drivers and weakness (Person B)
# ---------------------------------------------------------------------------
s = slide(number=6)
title(s, "A recent fall in income is the warning sign - but the screen is blind to the "
         "comfortable poor")
tx(s, "What drives risk", MARGIN, Inches(1.62), Inches(5.6), Inches(0.4),
   size=17, bold=True, color=BLUE)
tx(s, "Permutation importance: drop in ROC-AUC when the variable is shuffled",
   MARGIN, Inches(2.02), Inches(5.9), Inches(0.4), size=12, color=MUTED)
bar_chart(s, ["Household income (log)", "Grant recipients", "Income per person",
              "Income change vs a year ago"],
          [0.021, 0.029, 0.033, 0.082], MARGIN, Inches(2.45), Inches(6.2), Inches(2.75))
tx(s, "58.3% of households whose income fell sharply are food insecure, against 18-21% mid-scale.",
   MARGIN, Inches(5.3), Inches(6.2), Inches(0.6), size=13, italic=True, color=INK)
tx(s, "Where the screen is weakest", Inches(7.2), Inches(1.62), Inches(5.5), Inches(0.4),
   size=17, bold=True, color=RED)
tx(s, "Recall by subgroup, against the overall 80.7%",
   Inches(7.2), Inches(2.02), Inches(5.5), Inches(0.4), size=12, color=MUTED)
rows = [["Group", "Recall"],
        ["Earning under R2,500", "94.0%"],
        ["Earning over R11,500", "39.2%"],
        ["Receives grants", "88.0%"],
        ["No grants", "61.7%"]]
table(s, rows, Inches(7.2), Inches(2.45), Inches(5.5),
      [Inches(3.6), Inches(1.9)], size=13, row_h=Inches(0.52),
      emphasise={(2, 0), (2, 1), (4, 0), (4, 1)})
tx(s, "Grant households are more food insecure, not less - 37.6% against 20.6%. Grants are "
      "means-tested, so they mark households that were already poor. Targeting, not cause.",
   Inches(7.2), Inches(5.3), Inches(5.5), Inches(0.9), size=13, italic=True)
footer(s, "A low score is not clearance. It is the absence of a flag, which is why self-referral "
          "stays open.", color=INK)
notes(s, """
The strongest single signal is not income level - it is income change. Whether a household is worse
off than a year ago matters more than any other answer we collect, by a factor of about two and a
half. That is a cheap question, and it is actionable: it can be asked at intake, in one sentence,
before anything else.

Two findings surprised us. Grant-receiving households are more food insecure, not less: 37.6%
against 20.6%. That is not evidence that grants cause harm; grants are means-tested, so they mark
households that were already poor. We cannot separate targeting from effect in a single survey wave,
and we say so in the report rather than hiding it.

The second is the right-hand side, and it is the honest limitation of the tool. The screen finds 94%
of at-risk households at the bottom of the income scale and 39% at the top. It is weakest exactly
where food insecurity is least expected. So a lower-risk result is not clearance, and we keep
self-referral channels open because of it.
""")

# ---------------------------------------------------------------------------
# 7. Dashboard demo (Person B)
# ---------------------------------------------------------------------------
s = slide(number=7)
title(s, "Dashboard demo: setting the threshold against real capacity")
picture(s, "dashboard", MARGIN, Inches(1.62), Inches(7.6))
tx(s, [("Three questions, live", {"size": 17, "bold": True, "color": BLUE}),
       ("How well the screening tool works - and what a different threshold would cost", {}),
       ("Which households the screen misses", {}),
       ("What to ask about to spot risk early", {})],
   Inches(8.5), Inches(1.72), Inches(4.2), Inches(2.6), size=15, space_after=10)
tx(s, [("Nine pages. Pages 1 to 6 each answer one decision question; pages 7 to 9 are the "
        "evidence behind them, including a reconciliation page that compares every figure with R.",
        {"size": 13, "color": MUTED})],
   Inches(8.5), Inches(4.4), Inches(4.2), Inches(1.6))
footer(s, "If the live demo fails: the screenshots carry the same three numbers. Do not debug on "
          "stage.")
notes(s, """
Demo script, in this order, and do not improvise.

1. Open on the Overview page. Six decision questions; every page answers one of them - that was the
   design rule.
2. Go to "How well does the screening tool work?". Point at the four cards: these are the numbers
   from the previous slide, live from the final dataset.
3. Type 0.30 into the threshold box and press Enter - dragging is fiddly on a projector. Recall drops
   from 80.7% to 67.8%, referrals from 59% to 44%. That is 150 fewer households per thousand to
   visit, and about one in eight at-risk households newly missed. This is the conversation we want
   managers to have with us, and it is why the dial is in the tool rather than in a footnote.
4. Put it back to 0.24.
5. Go to "Which households does the screen miss?". Click through the breakdown slicer: income, then
   grant receipt, then province. Same chart, five cuts. The band is our agreed 10-point tolerance;
   income above R11,500 sits far outside it, and that is a documented limitation, not a surprise.
6. Go to "What should we ask about to spot risk early?". Income change at the top, and the odds-ratio
   table beside it with confidence intervals, because a direction without an interval is not
   evidence.
7. Hand to Timothy for the app.
""")

# ---------------------------------------------------------------------------
# 8. Shiny demo (Person C)
# ---------------------------------------------------------------------------
s = slide(number=8)
title(s, "An official can score one household in about ten seconds")
for i, key in enumerate(["app_single", "app_batch", "app_limits"]):
    picture(s, key, MARGIN + i * Inches(4.1), Inches(1.62), Inches(3.8))
for i, cap in enumerate(["One household, scored", "A batch, with the issues it refused",
                         "What the tool cannot tell you"]):
    tx(s, cap, MARGIN + i * Inches(4.1), Inches(4.3), Inches(3.8), Inches(0.4),
       size=13, bold=True, color=BLUE)
tx(s, [("Seven questions in. A probability, a recommendation and the three reasons out.",
        {"size": 18, "bold": True, "color": INK})],
   MARGIN, Inches(5.1), W - 2 * MARGIN, Inches(0.6))
tx(s, "The words are deliberate: \"Higher risk: refer for review\", never \"food insecure\". "
      "Rows with impossible values are left unscored rather than guessed - a screening tool that "
      "guesses when it does not know is worse than one that abstains.",
   MARGIN, Inches(5.75), Inches(11.4), Inches(0.9), size=14, color=MUTED)
footer(s, "All 6,279 test households were pushed back through the app's own code path and compared "
          "with the saved predictions. Largest difference: zero.", color=INK)
notes(s, """
Live demo, in this order:

1. One household. Type the rural example: income fell sharply, no electricity, six people, R1,200 a
   month, two grant recipients, pit latrine. Score it. Point at the three factors the app gives
   back, and at the words it uses - "Higher risk: refer for review", never "food insecure".
2. The contrast. Change income to R30,000 and settlement to urban, re-score, and let the probability
   drop. That is the whole model in one gesture.
3. The batch. Upload tests/messy_households.csv - 13 deliberately broken rows. Scroll the issues
   table: sentinel codes recoded, an impossible household size rejected, a duplicate identifier
   flagged, rows with too much missing left unscored rather than guessed.
4. The limits page. Land here, not on a score. Read the two lines about which households the screen
   misses.

This is the part a field officer actually touches. Seven questions, short enough to ask at a door,
and the answer comes back with the three things that drove it - so the officer can say why a
household was referred, and a supervisor can disagree with it.

Likely question - what happens if someone uploads real household IDs? They stay in the file and never
leave the machine. Uploads are processed in memory and not written to disk, identifiers are never
returned in the download, and the monitoring log keeps totals only.
""")

# ---------------------------------------------------------------------------
# 9. Recommendations (Person C)
# ---------------------------------------------------------------------------
s = slide(number=9)
title(s, "Five actions, each with the caution attached")
rows = [["Action", "The number behind it", "Who acts"],
        ["Use it for outreach triage, and resource the referral rate",
         "refers 58.9% of households; 41.9% of referrals are at risk", "Programme managers"],
        ["Ask about income change over the past year at intake",
         "strongest single predictor, AUC drop 0.082, about 2.5x the next", "Field staff"],
        ["Coordinate relief with the grant registers",
         "37.6% of grant-receiving households at risk against 20.6% without",
         "Social development"],
        ["Fund the four highest-risk provinces first",
         "Eastern Cape 43.0%, Northern Cape 40.5%, North West 37.1%, Mpumalanga 35.5%, "
         "against 28.3% nationally", "Provincial teams"],
        ["Audit \"lower risk\" households where the screen is weakest",
         "recall 39.2% above R11,500 and 61.7% with no grants", "Field officers, monthly"]]
table(s, rows, MARGIN, Inches(1.62), W - 2 * MARGIN,
      [Inches(4.3), Inches(5.6), Inches(2.2)], size=12, row_h=Inches(0.72))
tx(s, [("A screening aid. An official reviews every referral, and a low score is never clearance.",
        {"size": 16, "bold": True, "color": AMBER})],
   MARGIN, Inches(6.1), W - 2 * MARGIN, Inches(0.6))
notes(s, """
Each of these starts from a number on Rudi's slides, and each has a limit attached, because the
limits are what make them safe to act on.

The first is a budget decision disguised as a technical one. At our threshold the tool refers about
three households in five, and about four in ten of those referrals turn out to be food secure. That
is the cost of finding four in five of the households that are at risk. Managers should size
follow-up capacity against that rate before go-live - or move the threshold knowingly, which the
dashboard lets them do, and accept that they will miss more people.

The second is the cheapest thing on this list. One question about whether income has fallen carries
more signal than anything else we measured, and it can be asked without the model at all.

The third needs the caution said out loud. Grant-receiving households are at higher risk because
grants are targeted at poor households. That is a reason to use the registers to find people
quickly. It is not evidence that grants cause food insecurity.

The last one is there because of what we found about ourselves. The screen is weakest for households
that do not look poor on our seven inputs. We chose not to patch that with a different threshold for
richer households, because that means treating people differently by income on the basis of a proxy.
We publish the gap instead, and ask for a monthly audit. Keep self-referral open.
""")

# ---------------------------------------------------------------------------
# 10. Limits and next steps (Person C)
# ---------------------------------------------------------------------------
s = slide(dark=True, number=10)
title(s, "What this cannot tell you, and what we would do next", dark=True)
tx(s, "The limits", MARGIN, Inches(1.6), Inches(5.9), Inches(0.4),
   size=18, bold=True, color=AMBER)
tx(s, [("Moderate discrimination: ROC-AUC 0.736", {"bold": True}),
       ("58.1% of referrals are not food insecure; 19.3% of at-risk households are missed", {}),
       ("A proxy target from eight self-reported items, on one cross-sectional wave - "
        "association, never cause", {}),
       ("No external validation, and recall is weakest where risk is least expected", {})],
   MARGIN, Inches(2.2), Inches(5.9), Inches(3.6), size=15, color=PALE, space_after=14)
tx(s, "What we would do next", Inches(7.1), Inches(1.6), Inches(5.6), Inches(0.4),
   size=18, bold=True, color=LIGHTBLUE)
tx(s, [("Capture follow-up outcomes, so the next model trains on what was found", {"bold": True}),
       ("Add a second survey wave for within-household change", {}),
       ("Bring in per-person income, employment, debt and local food prices", {}),
       ("Re-validate on a new release before extending the threshold to it", {})],
   Inches(7.1), Inches(2.2), Inches(5.6), Inches(3.6), size=15, color=PALE, space_after=14)
tx(s, [("A cheap, interpretable, monitored triage aid that finds four in five at-risk households "
        "and knows which ones it misses.", {"size": 17, "bold": True, "color": WHITE})],
   MARGIN, Inches(5.9), Inches(11.3), Inches(0.8))
footer(s, "Survey data, not a census. A screening aid, not an eligibility test.", color=PALE)
notes(s, """
We would rather say these ourselves than have them found.

An AUC of 0.736 is moderate. It separates risk better than chance by a useful margin, and it is
nowhere near good enough to decide anything on its own - which is exactly why the design keeps a
person in the loop and why we talk about referrals rather than decisions.

The deeper limitation is the target. We never observed whether a household went without food. We
built a proxy out of eight survey answers and predicted it from seven other answers about the same
household at the same moment. That tells you who looks like the households that report hunger. It
does not tell you why, and it cannot tell you what would change if you intervened. The reversed
grant result is the clearest case: targeting and effect cannot be separated in one cross-section.

So the first thing on the right matters most. The moment officials record what they actually found
when they visited, we can retrain on real outcomes instead of a survey proxy, and measure precision
in the field rather than against our own label.

Until then, the honest summary is the line at the bottom. Thank you - we are happy to take questions
on any slide.
""")

prs.save(OUT)

# --- Checks ----------------------------------------------------------------
check = Presentation(OUT)
assert len(check.slides) == 10, f"the brief allows ten slides; this deck has {len(check.slides)}"
for i, sl in enumerate(check.slides, 1):
    assert sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip(), \
        f"slide {i} has no speaker notes"
    for shp in sl.shapes:
        assert shp.left >= 0 and shp.top >= 0, f"slide {i}: {shp.shape_type} off the top or left"
        assert shp.left + shp.width <= prs.slide_width + Emu(1000), \
            f"slide {i}: {shp.name} runs off the right edge"
        assert shp.top + shp.height <= prs.slide_height + Emu(1000), \
            f"slide {i}: {shp.name} runs off the bottom edge"

print("wrote", OUT)
print(f"  slides     : {len(check.slides)}, every one with speaker notes")
print(f"  pictures   : {sum(1 for s in check.slides for sh in s.shapes if sh.shape_type == 13)}")
for m in dict.fromkeys(missing_art):
    print("  TO REPLACE :", m)
