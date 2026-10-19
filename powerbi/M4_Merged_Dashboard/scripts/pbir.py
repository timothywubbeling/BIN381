# -*- coding: utf-8 -*-
"""Small helpers for writing Power BI enhanced report format (PBIR) JSON."""
import hashlib

VC_SCHEMA = ("https://developer.microsoft.com/json-schemas/fabric/item/report/"
             "definition/visualContainer/2.13.0/schema.json")
PAGE_SCHEMA = ("https://developer.microsoft.com/json-schemas/fabric/item/report/"
               "definition/page/2.1.0/schema.json")
PAGES_SCHEMA = ("https://developer.microsoft.com/json-schemas/fabric/item/report/"
                "definition/pagesMetadata/1.1.0/schema.json")
REPORT_SCHEMA = ("https://developer.microsoft.com/json-schemas/fabric/item/report/"
                 "definition/report/3.3.0/schema.json")
VERSION_SCHEMA = ("https://developer.microsoft.com/json-schemas/fabric/item/report/"
                  "definition/versionMetadata/1.0.0/schema.json")
# Power BI requires this on every entry in themeCollection and opens the project with an
# error about report.json without it. The values are the ones Power BI Desktop itself wrote
# into the Milestone 3 report, which opens clean.
THEME_IMPORT_VERSION = {"visual": "2.12.0", "report": "3.4.0", "page": "2.3.1"}

# -- Tim's "Innovate" dark palette -------------------------------------------
FONT = "IBM Plex Sans, Segoe UI, system-ui, sans-serif"
FG = "#FFFFFF"        # primary text
FG2 = "#D2D0CE"       # secondary text
FG3 = "#979593"       # tertiary / footnotes / neutral series
BORDER = "#605E5C"
PANEL = "#3B3A39"     # card and panel fill
BLUE = "#70B0E0"      # the main measure, everywhere
DEEP = "#2878BD"      # secondary measure
AMBER = "#FCB714"     # warning, R benchmark, outside tolerance
TEAL = "#0EB194"      # referral volume
RED = "#F15628"       # severe / at-risk outcome
GREY = "#979593"      # not at risk

# -- canvas grid (1280x720, 16px gutters, four 300px columns) ----------------
W, H = 1280, 720
C1, C2, C3, C4 = 16, 332, 648, 964
W1, W2, W3, W4 = 300, 616, 932, 1248
TITLE_Y, TITLE_H = 12, 34
SUB_Y, SUB_H = 48, 22
NAV_Y, NAV_H = 78, 34
FOOT_Y, FOOT_H = 696, 14
B1_Y, B1_H = 124, 78          # KPI / slicer band
B2_Y, B2_H = 218, 232         # main band
B3_Y, B3_H = 466, 224         # lower band
TALL_Y, TALL_H = 218, 472     # B2+B3 merged
FULL_Y, FULL_H = 124, 566     # everything under the navigator

FOOTNOTE = ("Source: Stats SA General Household Survey 2024 · 20,925 modelled households "
            "· population percentages weighted with HouseholdWeight · "
            "screening aid only, not an eligibility test · no household is identifiable.")

_seq = [0]


def vid(seed):
    """Deterministic 20-hex-character visual / page name."""
    return hashlib.md5(seed.encode()).hexdigest()[:20]


def nextz():
    _seq[0] += 1
    return _seq[0] * 10


# -- literal / expression helpers --------------------------------------------
def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def s(v):
    return lit("'%s'" % str(v).replace("'", "''"))


def num(v):
    return lit("%sD" % v)


def boo(v):
    return lit("true" if v else "false")


def solid(c):
    return {"solid": {"color": {"expr": {"Literal": {"Value": "'%s'" % c}}}}}


# -- field / projection helpers ----------------------------------------------
def fcol(entity, prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def fmeas(entity, prop):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def fagg(entity, prop, fn=0):
    return {"Aggregation": {"Expression": {"Column": {
        "Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}, "Function": fn}}


def pcol(entity, prop, display=None, active=None):
    p = {"field": fcol(entity, prop), "queryRef": "%s.%s" % (entity, prop),
         "nativeQueryRef": prop}
    if display:
        p["displayName"] = display
    if active is not None:
        p["active"] = active
    return p


def pmeas(entity, prop, display=None):
    p = {"field": fmeas(entity, prop), "queryRef": "%s.%s" % (entity, prop),
         "nativeQueryRef": prop}
    if display:
        p["displayName"] = display
    return p


def pagg(entity, prop, display=None):
    p = {"field": fagg(entity, prop), "queryRef": "Sum(%s.%s)" % (entity, prop),
         "nativeQueryRef": "Sum of %s" % prop}
    if display:
        p["displayName"] = display
    return p


def qref_of(p):
    return p["queryRef"]


# -- visual container ---------------------------------------------------------
def visual(seed, vtype, x, y, w, h, query=None, objects=None, vco=None, z=None):
    zz = nextz() if z is None else z
    v = {"visualType": vtype}
    if query:
        v["query"] = query
    if objects:
        v["objects"] = objects
    if vco:
        v["visualContainerObjects"] = vco
    v["drillFilterOtherVisuals"] = True
    return {
        "$schema": VC_SCHEMA,
        "name": vid(seed),
        "position": {"x": x, "y": y, "z": zz, "height": h, "width": w, "tabOrder": zz},
        "visual": v,
    }


def query(roles, sort=None):
    """roles: {'Category': [proj, ...], 'Y': [...]}; sort: [(proj, 'Ascending'), ...]"""
    q = {"queryState": {r: {"projections": ps} for r, ps in roles.items() if ps}}
    if sort:
        q["sortDefinition"] = {"sort": [{"field": p["field"], "direction": d} for p, d in sort]}
    return q


# -- common visual chrome -----------------------------------------------------
def chrome(title=None, subtitle=None, border=True, bg=None, size=11, color=FG):
    vco = {}
    if title:
        vco["title"] = [{"properties": {
            "show": boo(True), "text": s(title), "fontSize": num(size),
            "bold": boo(True), "fontColor": solid(color),
            "titleWrap": boo(True)}}]
    else:
        vco["title"] = [{"properties": {"show": boo(False)}}]
    if subtitle:
        vco["subTitle"] = [{"properties": {
            "show": boo(True), "text": s(subtitle), "fontSize": num(8),
            "fontColor": solid(FG3), "titleWrap": boo(True)}}]
    if border:
        vco["border"] = [{"properties": {
            "show": boo(True), "color": solid(BORDER), "radius": num(6)}}]
    if bg:
        vco["background"] = [{"properties": {
            "show": boo(True), "color": solid(bg), "transparency": num(0)}}]
    return vco


def axes(cat_title=None, val_title=None, val_start=None, val_end=None,
         cat_fontsize=9, val_fontsize=9):
    o = {}
    cat = {"fontSize": num(cat_fontsize), "labelColor": solid(FG2)}
    if cat_title:
        cat["titleText"] = s(cat_title)
        cat["showAxisTitle"] = boo(True)
        cat["titleFontColor"] = solid(FG3)
        cat["titleFontSize"] = num(8)
    else:
        cat["showAxisTitle"] = boo(False)
    o["categoryAxis"] = [{"properties": cat}]
    val = {"fontSize": num(val_fontsize), "labelColor": solid(FG2)}
    if val_title:
        val["titleText"] = s(val_title)
        val["showAxisTitle"] = boo(True)
        val["titleFontColor"] = solid(FG3)
        val["titleFontSize"] = num(8)
    else:
        val["showAxisTitle"] = boo(False)
    if val_start is not None:
        val["start"] = num(val_start)
    if val_end is not None:
        val["end"] = num(val_end)
    o["valueAxis"] = [{"properties": val}]
    return o


def legend(show=True, position="Top", title=None):
    p = {"show": boo(show)}
    if show:
        p["position"] = s(position)
        p["labelColor"] = solid(FG2)
        p["fontSize"] = num(9)
        if title:
            p["showTitle"] = boo(True)
            p["titleText"] = s(title)
        else:
            p["showTitle"] = boo(False)
    return {"legend": [{"properties": p}]}


def fill(color):
    return {"dataPoint": [{"properties": {"fill": solid(color)}}]}


def fill_by(entity, prop, mapping):
    """One fill per category value, e.g. {'At risk': RED, 'Not at risk': GREY}."""
    out = []
    for value, color in mapping.items():
        out.append({
            "properties": {"fill": solid(color)},
            "selector": {"data": [{"scopeId": {"Comparison": {
                "ComparisonKind": 0,
                "Left": fcol(entity, prop),
                "Right": {"Literal": {"Value": "'%s'" % value}}}}}]},
        })
    return {"dataPoint": out}


def fill_series(mapping):
    """One fill per measure series, keyed by queryRef."""
    return {"dataPoint": [
        {"properties": {"fill": solid(color)}, "selector": {"metadata": qr}}
        for qr, color in mapping.items()]}


def labels(show=True, size=8, color=FG2, position=None):
    p = {"show": boo(show)}
    if show:
        p["fontSize"] = num(size)
        p["color"] = solid(color)
        if position:
            p["labelPosition"] = s(position)
    return {"labels": [{"properties": p}]}


# -- text ---------------------------------------------------------------------
def run(value, size="10pt", color=FG, bold=False, italic=False):
    st = {"fontFamily": FONT, "fontSize": size, "color": color}
    if bold:
        st["fontWeight"] = "bold"
    if italic:
        st["fontStyle"] = "italic"
    return {"value": value, "textStyle": st}


def para(runs, align="left"):
    if isinstance(runs, dict):
        runs = [runs]
    return {"textRuns": runs, "horizontalTextAlignment": align}


def textbox(seed, x, y, w, h, paragraphs, bg=None, border=False, title=None, z=None):
    objects = {"general": [{"properties": {"paragraphs": paragraphs}}]}
    return visual(seed, "textbox", x, y, w, h, objects=objects,
                  vco=chrome(title=title, border=border, bg=bg), z=z)


# -- page chrome --------------------------------------------------------------
def page_header(pid, heading, question, badge=None):
    """Title, subtitle, page navigator and footnote - identical on every page."""
    out = [
        textbox(pid + "/h1", C1, TITLE_Y, 900, TITLE_H,
                [para(run(heading, "19pt", FG, bold=True))], z=9000),
        textbox(pid + "/h2", C1, SUB_Y, 900, SUB_H,
                [para(run(question, "11pt", FG2))], z=9001),
        visual(pid + "/nav", "pageNavigator", C1, NAV_Y, W4, NAV_H, z=9002),
        textbox(pid + "/foot", C1, FOOT_Y, W4, FOOT_H,
                [para(run(FOOTNOTE, "8pt", FG3, italic=True))], z=9003),
    ]
    if badge:
        out.append(textbox(pid + "/badge", 932, TITLE_Y, 332, 58,
                           [para(run(badge[0], "9pt", AMBER, bold=True), align="right"),
                            para(run(badge[1], "9pt", FG3), align="right")], z=9004))
    return out


def page(pid, display_name, visuals):
    return {
        "page": {"$schema": PAGE_SCHEMA, "name": vid(pid), "displayName": display_name,
                 "displayOption": "FitToPage", "height": H, "width": W},
        "visuals": visuals,
    }
