#!/usr/bin/env python3
"""Finish the group deck: Alexander's slides 1 to 7, plus Person C's slides 8 to 10.

Alexander built slides 1 to 7 in BIN381_M4_PersonA_Slides_1_4.pptx (title, approach, data,
modelling, performance, findings, dashboard demo). This appends the three that were missing,
following BIN381_M4_PersonC_Slides_8_to_10.md, in his own layout: the Title Only layout, the
same margins, a 24pt message line under the title, and a 10pt footnote at the bottom. His
slides are not touched, except that slides without speaker notes get a draft set.

Run from the repository root:  python report/M4/build_slides.py
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FIGURES = os.path.join(ROOT, "docs", "figures")
BASE = os.path.join(HERE, "BIN381_M4_PersonA_Slides_1_4.pptx")
OUT = os.path.join(HERE, "BIN381_M4_Slides_Group_P1.pptx")

# Alexander's deck: Century Gothic theme, Aptos on the runs, and a dark textured background
# from the template, so slide text is white. Tables and screenshots sit on light cards, the
# way his charts do.
FONT = "Aptos"
INK = RGBColor(0xFF, 0xFF, 0xFF)       # text on the dark slide
MUTED = RGBColor(0xD9, 0xD9, 0xD9)     # footnotes, still legible on the texture
WARN = RGBColor(0xE9, 0xA0, 0x39)      # accent5: the gaps we are honest about
CARD = RGBColor(0xFF, 0xFF, 0xFF)      # table body, like the white card behind his charts
CARD_INK = RGBColor(0x36, 0x3D, 0x46)  # dk2, text on that card
TINT = RGBColor(0xEB, 0xEB, 0xEB)      # lt2, table header fill

MARGIN = Inches(1.25)
BODY_W = Inches(10.83)
HEAD_Y = Inches(1.62)
BODY_Y = Inches(2.3)
FOOT_Y = Inches(6.40)

# Screenshots of the merged dashboard do not exist yet; fall back to what is in the repository
# and say so, and pick the new ones up automatically once they are exported.
SHOTS = {
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


prs = Presentation(BASE)
LAYOUT = next(l for l in prs.slide_layouts if l.name == "Title Only")


def tx(s, text, x, y, w, h, size=14, bold=False, color=INK, align=PP_ALIGN.LEFT,
       italic=False, space_after=6):
    """One text box. `text` is a string, or a list of (text, overrides) paragraphs."""
    box = s.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    for i, (body, over) in enumerate(text if isinstance(text, list) else [(text, {})]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = over.get("align", align)
        p.space_after = Pt(over.get("space_after", space_after))
        run = p.add_run()
        run.text = body
        f = run.font
        f.name = FONT
        f.size = Pt(over.get("size", size))
        f.bold = over.get("bold", bold)
        f.italic = over.get("italic", italic)
        f.color.rgb = over.get("color", color)
    return box


def slide(eyebrow, message, footnote=None):
    s = prs.slides.add_slide(LAYOUT)
    title = s.shapes.title
    title.text = eyebrow
    # The layout's title box is deeper than the one Alexander uses on his slides, and would
    # sit on top of the message line.
    title.left, title.top, title.width, title.height = \
        MARGIN, Inches(0.67), BODY_W, Inches(0.72)
    tx(s, message, MARGIN, HEAD_Y, BODY_W, Inches(0.5), size=24)
    if footnote:
        tx(s, footnote, MARGIN, FOOT_Y, BODY_W, Inches(0.45), size=10, color=MUTED)
    return s


def table(s, rows, x, y, w, col_w, size=11, row_h=Inches(0.42), emphasise=()):
    t = s.shapes.add_table(len(rows), len(rows[0]), x, y, w, row_h * len(rows)).table
    t.first_row = True
    for i, cw in enumerate(col_w):
        t.columns[i].width = cw
    for r, row in enumerate(rows):
        t.rows[r].height = row_h
        for c, val in enumerate(row):
            cell = t.cell(r, c)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.fill.solid()
            cell.fill.fore_color.rgb = TINT if r == 0 else CARD
            run = cell.text_frame.paragraphs[0].add_run()
            run.text = str(val)
            run.font.size = Pt(size)
            run.font.name = FONT
            run.font.bold = r == 0 or (r, c) in emphasise
            run.font.color.rgb = RGBColor(0xB8, 0x5A, 0x1E) if (r, c) in emphasise else CARD_INK
    return t


def picture(s, key, x, y, box_w, box_h):
    """Fit the screenshot inside the column box, centred. The three app pages have very
    different shapes, so sizing on height alone makes them overlap."""
    p = shot(key)
    if not p:
        ph = s.shapes.add_shape(1, x, y, box_w, box_h)
        ph.fill.solid()
        ph.fill.fore_color.rgb = TINT
        ph.line.color.rgb = MUTED
        ph.text_frame.text = "screenshot to be exported"
        return ph
    pic = s.shapes.add_picture(p, x, y)
    scale = min(box_w / pic.width, box_h / pic.height)
    pic.width, pic.height = Emu(int(pic.width * scale)), Emu(int(pic.height * scale))
    pic.left = Emu(int(x + (box_w - pic.width) / 2))
    return pic


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text.strip()


# ---------------------------------------------------------------------------
# 8. The Shiny app demo
# ---------------------------------------------------------------------------
s = slide("App demo", "An official can score one household in about ten seconds",
          "All 6,279 test households were pushed back through the app's own code path and "
          "compared with the saved predictions. Largest difference: zero.")
col_w, shot_h = Inches(3.45), Inches(3.0)
for i, (key, cap) in enumerate([("app_single", "One household, scored"),
                                ("app_batch", "A batch, with the issues it refused"),
                                ("app_limits", "What the tool cannot tell you")]):
    x = MARGIN + i * (col_w + Inches(0.24))
    picture(s, key, x, BODY_Y, col_w, shot_h)
    tx(s, cap, x, BODY_Y + shot_h + Inches(0.12), col_w, Inches(0.3), size=11, bold=True,
       align=PP_ALIGN.CENTER)
tx(s, [("Seven questions in. A probability, a recommendation and the three reasons out.",
        {"size": 16, "bold": True})], MARGIN, Inches(5.95), BODY_W, Inches(0.4))
notes(s, """
Live demo, in this order:

1. One household. Type the rural example: income fell sharply, no electricity, six people,
   R1,200 a month, two grant recipients, pit latrine. Score it. Point at the three factors the app
   gives back, and at the words it uses - "Higher risk: refer for review", never "food insecure".
2. The contrast. Change income to R30,000 and settlement to urban, re-score, and let the
   probability drop. That is the whole model in one gesture.
3. The batch. Upload tests/messy_households.csv - 13 deliberately broken rows. Scroll the issues
   table: sentinel codes recoded, an impossible household size rejected, a duplicate identifier
   flagged, rows with too much missing left unscored rather than guessed.
4. The limits page. Land here, not on a score. Read the two lines about which households the
   screen misses.

This is the part a field officer actually touches. Seven questions, short enough to ask at a door,
and the answer comes back with the three things that drove it - so the officer can say why a
household was referred, and a supervisor can disagree with it.

Likely question - what happens if someone uploads real household IDs? They stay in the file and
never leave the machine. Uploads are processed in memory and not written to disk, identifiers are
never returned in the download, and the monitoring log keeps totals only.
""")

# ---------------------------------------------------------------------------
# 9. Recommendations
# ---------------------------------------------------------------------------
s = slide("Recommendations", "Five actions, each with the caution attached")
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
table(s, rows, MARGIN, BODY_Y, BODY_W,
      [Inches(3.6), Inches(4.8), Inches(2.43)], row_h=Inches(0.64))
tx(s, [("A screening aid. An official reviews every referral, and a low score is never clearance.",
        {"size": 14, "bold": True, "color": WARN})], MARGIN, FOOT_Y, BODY_W, Inches(0.4))
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

The last one is there because of what we found about ourselves. The screen is weakest for
households that do not look poor on our seven inputs. We chose not to patch that with a different
threshold for richer households, because that means treating people differently by income on the
basis of a proxy. We publish the gap instead, and ask for a monthly audit. Keep self-referral open.
""")

# ---------------------------------------------------------------------------
# 10. Limits and next steps
# ---------------------------------------------------------------------------
s = slide("Limits and next steps", "What this cannot tell you, and what we would do next",
          "Survey data, not a census. A screening aid, not an eligibility test.")
tx(s, "The limits", MARGIN, BODY_Y, Inches(5.2), Inches(0.35), size=16, bold=True, color=WARN)
tx(s, [("Moderate discrimination: ROC-AUC 0.736", {"bold": True}),
       ("58.1% of referrals are not food insecure; 19.3% of at-risk households are missed", {}),
       ("A proxy target from eight self-reported items, on one cross-sectional wave - "
        "association, never cause", {}),
       ("No external validation, and recall is weakest where risk is least expected", {})],
   MARGIN, Inches(2.75), Inches(5.2), Inches(2.8), size=13, space_after=14)
tx(s, "What we would do next", Inches(6.88), BODY_Y, Inches(5.2), Inches(0.35),
   size=16, bold=True)
tx(s, [("Capture follow-up outcomes, so the next model trains on what was found", {"bold": True}),
       ("Add a second survey wave for within-household change", {}),
       ("Bring in per-person income, employment, debt and local food prices", {}),
       ("Re-validate on a new release before extending the threshold to it", {})],
   Inches(6.88), Inches(2.75), Inches(5.2), Inches(2.8), size=13, space_after=14)
tx(s, [("A cheap, interpretable, monitored triage aid that finds four in five at-risk households "
        "and knows which ones it misses.", {"size": 16, "bold": True})],
   MARGIN, Inches(5.7), BODY_W, Inches(0.6))
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

Until then, the honest summary is the line at the bottom. Thank you - we are happy to take
questions on any slide.
""")

# --- Draft notes for the slides that have none, so nobody presents from a blank page ------
DRAFT_NOTES = {
    1: "Our question was a targeting one: when the institute can only follow up a fraction of "
       "households, which ones should it visit first? 20,940 households in the survey, three in "
       "ten at risk. What we built is a screen that ranks them - not a test of who qualifies for "
       "anything. Alexander takes the problem, the data and the modelling; Rudi the results and "
       "the dashboard; Timothy the app, the recommendations and the limits.",
    2: "Three goals from Milestone 1: rank the indicators, build an interpretable model without "
       "leakage, and give decision-makers self-service exploration. We followed CRISP-DM in "
       "order and went back three times when the evidence demanded it - the key repair, the "
       "duplicate-ID finding, and the move to a binary target. The dashed arrows on the diagram "
       "are those three returns.",
    3: "Seven of the eleven files are household-level and were kept. D01 to D03 are person-level "
       "and D11 is a different survey with no shared household IDs, so both were left out with "
       "reasons. The joins are guarded one-to-one joins that stop rather than drop a household: "
       "15 placeholder keys in D05 were repaired, not discarded. Sixteen columns that define or "
       "proxy the target are excluded from the predictors, and the notebook fails if one appears.",
    4: "We tuned three model families with stratified five-fold cross-validation, with all "
       "preprocessing re-learned inside each fold. The three-tier target failed on the middle "
       "tier - no three-tier model recalls more than 3.2% of those households - and we had "
       "written the binary fallback down in advance rather than inventing it afterwards. Class "
       "weights were tested and rejected: they helped recall but wrecked the probabilities, and "
       "the app reports a probability.",
}
drafted = []
for i, s in enumerate(prs.slides, 1):
    if not (s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip()):
        if i in DRAFT_NOTES:
            notes(s, DRAFT_NOTES[i])
            drafted.append(i)

prs.save(OUT)

# --- Checks ----------------------------------------------------------------
out = Presentation(OUT)
assert len(out.slides) == 10, f"the brief allows ten slides; this deck has {len(out.slides)}"
for i, sl in enumerate(out.slides, 1):
    assert sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip(), \
        f"slide {i} has no speaker notes"
for i, sl in enumerate(out.slides, 1):
    if i < 8:
        continue                      # Alexander's slides are his, and already laid out
    for shp in sl.shapes:
        assert shp.left >= 0 and shp.top >= 0, f"slide {i}: {shp.name} off the top or left"
        assert shp.left + shp.width <= out.slide_width + Emu(1000), \
            f"slide {i}: {shp.name} runs off the right edge"
        assert shp.top + shp.height <= out.slide_height + Emu(1000), \
            f"slide {i}: {shp.name} runs off the bottom edge"
    # Nothing on these three slides is meant to sit on top of anything else: the pictures
    # have very different shapes, and sizing them on one dimension silently overlapped them.
    boxes = [(s.left, s.top, s.left + s.width, s.top + s.height, s.name) for s in sl.shapes]
    for a in range(len(boxes)):
        for b in range(a + 1, len(boxes)):
            x0, y0, x1, y1, na = boxes[a]
            u0, v0, u1, v1, nb = boxes[b]
            assert x0 >= u1 or u0 >= x1 or y0 >= v1 or v0 >= y1, \
                f"slide {i}: {na} and {nb} overlap"

print("wrote", OUT)
print(f"  slides     : {len(out.slides)} (1-7 Alexander's, 8-10 added here)")
print(f"  notes      : on every slide; drafted for slide(s) {drafted or 'none'}")
print(f"  pictures   : {sum(1 for s in out.slides for sh in s.shapes if sh.shape_type == 13)}")
for m in dict.fromkeys(missing_art):
    print("  TO REPLACE :", m)
