# -*- coding: utf-8 -*-
"""Assemble the merged Milestone 4 Power BI project (PBIP) and validate it."""
import base64
import gzip
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pbir
from pbir import (PAGES_SCHEMA, REPORT_SCHEMA, VERSION_SCHEMA)
from model import MODEL
import pages as P

NAME = "BIN381_M4_Dashboard_Group_P1"
OUT = sys.argv[1]
THEME_SRC = sys.argv[2]        # extracted Main Dash.pbix
DATA_SRC = sys.argv[3]         # team repo data/powerbi
CURVE_SRC = sys.argv[4]        # generated threshold curve csv
FOUNDATION_SRC = sys.argv[5]   # generated inventory + data quality csvs
# Optional: point DataFolder at an existing data directory (the repository's
# data/powerbi/) instead of keeping a private copy of the CSVs inside the project.
# When given, this script does not create or clear that directory.
DATA_OVERRIDE = sys.argv[6] if len(sys.argv) > 6 else None

REPORT = os.path.join(OUT, NAME + ".Report")
SEMANTIC = os.path.join(OUT, NAME + ".SemanticModel")
DATA = DATA_OVERRIDE or os.path.join(OUT, "data", "powerbi")

CSVS = ["powerbi_households.csv", "powerbi_model_summary.csv",
        "powerbi_subgroup_performance.csv", "powerbi_permutation_importance.csv",
        "powerbi_odds_ratios.csv", "powerbi_reconciliation.csv"]


def write(path, obj, raw=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        if raw:
            fh.write(obj)
        else:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
            fh.write("\n")


# Only the generated folders are replaced. README.md, scripts/ and anything else a
# human put in the project directory is left alone - an earlier version of this script
# removed the whole of OUT and took the hand-over notes with it.
generated_dirs = [REPORT, SEMANTIC]
if not DATA_OVERRIDE:
    generated_dirs.append(DATA)
for generated in generated_dirs:
    if os.path.isdir(generated):
        shutil.rmtree(generated)

# ------------------------------------------------------------------- data
os.makedirs(DATA, exist_ok=True)
if not DATA_OVERRIDE:
    # Private copy of the six exported tables, so the project refreshes on its own.
    for c in CSVS:
        shutil.copy2(os.path.join(DATA_SRC, c), os.path.join(DATA, c))
# The three tables this project adds are written in either case.
shutil.copy2(CURVE_SRC, os.path.join(DATA, "powerbi_threshold_curve.csv"))
for c in ("powerbi_dataset_inventory.csv", "powerbi_data_quality.csv"):
    shutil.copy2(os.path.join(FOUNDATION_SRC, c), os.path.join(DATA, c))

# -------------------------------------------------------------- semantic model
# Each table's CSV is gzipped and base64-encoded straight into its partition, so the
# model carries its own data and needs no file path on any machine. A leading UTF-8
# BOM is stripped first so the first column name survives Table.PromoteHeaders.
bim = json.dumps(MODEL, indent=2, ensure_ascii=False)
embedded = {}
for token in sorted(set(re.findall(r"%%EMBED:([^%]+)%%", bim))):
    raw = open(os.path.join(DATA, token), "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    b64 = base64.b64encode(gzip.compress(raw, 9)).decode("ascii")
    # Plain concatenation, not %-formatting: "%%EMBED:%s%%" % token collapses each
    # %% to a single %, which leaves a stray % glued to the base64 and makes Power
    # Query fail every table with "[Expression.Error] Invalid binary encoding."
    bim = bim.replace("%%EMBED:" + token + "%%", b64)
    embedded[token] = (raw, b64)
    print("  embedded %-38s %9s bytes -> %9s base64"
          % (token, f"{len(raw):,}", f"{len(b64):,}"))

if "EMBED" in bim or "%%" in bim:
    sys.exit("unreplaced embed token left in model.bim")

# Read the payloads back out of the finished file and decode them, so a mangled
# literal fails the build instead of failing in Power BI.
check = json.loads(bim)
seen = 0
for t in check["model"]["tables"]:
    src = t["partitions"][0]["source"]
    if src.get("type") != "m":
        continue
    joined = "\n".join(src["expression"])
    found = re.search(r'Binary\.FromText\("([^"]+)"', joined)
    if not found:
        sys.exit("table %s has no embedded payload" % t["name"])
    payload = found.group(1)
    stray = sorted(set(c for c in payload if not (c.isalnum() or c in "+/=")))
    if stray:
        sys.exit("table %s: payload has non-base64 characters %r" % (t["name"], stray))
    match = [k for k, (_, b) in embedded.items() if b == payload]
    if not match:
        sys.exit("table %s: payload does not match any source file" % t["name"])
    original = embedded[match[0]][0]
    if gzip.decompress(base64.b64decode(payload)) != original:
        sys.exit("table %s: embedded payload does not round-trip" % t["name"])
    seen += 1
if seen != len(embedded):
    sys.exit("embedded %d payloads but only %d tables carry one" % (len(embedded), seen))

write(os.path.join(SEMANTIC, "model.bim"), bim + "\n", raw=True)
print("  %d tables embedded and round-tripped, model.bim is %.2f MB"
      % (seen, len(bim) / 1048576))
write(os.path.join(SEMANTIC, "definition.pbism"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/"
               "definitionProperties/1.0.0/schema.json",
    "version": "4.0",
    "settings": {},
})

# --------------------------------------------------------------------- report
write(os.path.join(REPORT, "definition.pbir"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/"
               "definitionProperties/2.0.0/schema.json",
    "version": "4.0",
    "datasetReference": {"byPath": {"path": "../" + NAME + ".SemanticModel"}},
})
write(os.path.join(REPORT, "definition", "version.json"),
      {"$schema": VERSION_SCHEMA, "version": "2.0.0"})

# Tim's exact theme pair: the Fluent2 base plus the Innovate dark custom theme.
for src, dst in [
    ("Report/StaticResources/SharedResources/BaseThemes/Fluent2-CY26SU08.json",
     "StaticResources/SharedResources/BaseThemes/Fluent2-CY26SU08.json"),
    ("Report/StaticResources/SharedResources/BuiltInThemes/Innovate.json",
     "StaticResources/SharedResources/BuiltInThemes/Innovate.json"),
]:
    d = os.path.join(REPORT, dst)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copy2(os.path.join(THEME_SRC, src), d)

write(os.path.join(REPORT, "definition", "report.json"), {
    "$schema": REPORT_SCHEMA,
    "themeCollection": {
        "baseTheme": {"name": "Fluent2-CY26SU08", "type": "SharedResources"},
        "customTheme": {"name": "Innovate", "type": "SharedResources"},
    },
    "objects": {
        "section": [{"properties": {"verticalAlignment": pbir.s("Top")}}],
        "outspacePane": [{"properties": {"expanded": pbir.boo(False)}}],
    },
    "resourcePackages": [{
        "name": "SharedResources", "type": "SharedResources",
        "items": [
            {"name": "Fluent2-CY26SU08", "path": "BaseThemes/Fluent2-CY26SU08.json",
             "type": "BaseTheme"},
            {"name": "Innovate", "path": "BuiltInThemes/Innovate.json", "type": "CustomTheme"},
        ],
    }],
    "settings": {
        "useStylableVisualContainerHeader": True,
        "exportDataMode": "AllowSummarized",
        "defaultDrillFilterOtherVisuals": True,
        "allowChangeFilterTypes": True,
        "useEnhancedTooltips": True,
        "useDefaultAggregateDisplayName": True,
    },
})

built = [fn() for fn in P.PAGES]
order = [p["page"]["name"] for p in built]
write(os.path.join(REPORT, "definition", "pages", "pages.json"),
      {"$schema": PAGES_SCHEMA, "pageOrder": order, "activePageName": order[0]})

for p in built:
    pid = p["page"]["name"]
    base = os.path.join(REPORT, "definition", "pages", pid)
    write(os.path.join(base, "page.json"), p["page"])
    for v in p["visuals"]:
        write(os.path.join(base, "visuals", v["name"], "visual.json"), v)

# -------------------------------------------------------------------- wrappers
write(os.path.join(OUT, NAME + ".pbip"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/"
               "1.0.0/schema.json",
    "version": "1.0",
    "artifacts": [{"report": {"path": NAME + ".Report"}}],
    "settings": {"enableAutoRecovery": True},
})
write(os.path.join(OUT, ".gitignore"),
      "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n", raw=True)

# ======================================================== validation
print("\nValidating against the semantic model ...")
cols, meas = {}, {}
for t in MODEL["model"]["tables"]:
    cols[t["name"]] = {c["name"] for c in t["columns"]}
    meas[t["name"]] = {m["name"] for m in t.get("measures", [])}

problems = []
seen_names = {}
nvis = 0


def check_fields(node, where):
    if isinstance(node, dict):
        for kind, bucket in (("Column", cols), ("Measure", meas)):
            e = node.get(kind)
            if isinstance(e, dict) and "Property" in e:
                ent = e.get("Expression", {}).get("SourceRef", {}).get("Entity")
                prop = e["Property"]
                if ent is None:
                    pass
                elif ent not in bucket:
                    problems.append("%s: unknown table %r" % (where, ent))
                elif prop not in bucket[ent]:
                    problems.append("%s: %s has no %s %r" % (where, ent, kind.lower(), prop))
        for v in node.values():
            check_fields(v, where)
    elif isinstance(node, list):
        for v in node:
            check_fields(v, where)


for p in built:
    pg = p["page"]
    assert re.fullmatch(r"[0-9a-f]{20}", pg["name"]), pg["name"]
    for v in p["visuals"]:
        nvis += 1
        assert re.fullmatch(r"[0-9a-f]{20}", v["name"]), v["name"]
        key = (pg["name"], v["name"])
        if key in seen_names:
            problems.append("duplicate visual id on %s: %s" % (pg["displayName"], v["name"]))
        seen_names[key] = True
        pos = v["position"]
        if pos["x"] < 0 or pos["y"] < 0:
            problems.append("%s/%s negative position" % (pg["displayName"], v["name"]))
        if pos["x"] + pos["width"] > pbir.W:
            problems.append("%s: %s overflows right edge (%d)"
                            % (pg["displayName"], v["visual"]["visualType"],
                               pos["x"] + pos["width"]))
        if pos["y"] + pos["height"] > pbir.H:
            problems.append("%s: %s overflows bottom edge (%d)"
                            % (pg["displayName"], v["visual"]["visualType"],
                               pos["y"] + pos["height"]))
        check_fields(v["visual"].get("query", {}),
                     "%s/%s" % (pg["displayName"], v["visual"]["visualType"]))
        check_fields(v.get("filterConfig", {}),
                     "%s/%s filter" % (pg["displayName"], v["visual"]["visualType"]))
        # every selector-based dataPoint colour must name a real column value
        for dp in v["visual"].get("objects", {}).get("dataPoint", []):
            sel = dp.get("selector", {})
            if "metadata" in sel:
                qrefs = set()

                def collect(n):
                    if isinstance(n, dict):
                        if "queryRef" in n:
                            qrefs.add(n["queryRef"])
                        for x in n.values():
                            collect(x)
                    elif isinstance(n, list):
                        for x in n:
                            collect(x)
                collect(v["visual"].get("query", {}))
                if sel["metadata"] not in qrefs:
                    problems.append("%s: dataPoint selector %r matches no projection"
                                    % (pg["displayName"], sel["metadata"]))

# check overlaps within a page (ignoring the full-width header/footer chrome)
for p in built:
    boxes = [(v["name"], v["visual"]["visualType"], v["position"]) for v in p["visuals"]]
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][2], boxes[j][2]
            ox = min(a["x"] + a["width"], b["x"] + b["width"]) - max(a["x"], b["x"])
            oy = min(a["y"] + a["height"], b["y"] + b["height"]) - max(a["y"], b["y"])
            if ox > 2 and oy > 2:
                problems.append("%s: %s overlaps %s by %dx%d"
                                % (p["page"]["displayName"], boxes[i][1], boxes[j][1], ox, oy))

print("  pages   %d" % len(built))
print("  visuals %d" % nvis)
for p in built:
    print("    %-28s %2d visuals" % (p["page"]["displayName"], len(p["visuals"])))
if problems:
    print("\n%d PROBLEM(S):" % len(problems))
    for x in sorted(set(problems)):
        print("  -", x)
    sys.exit(1)
print("\nAll field references, ids, bounds and overlaps OK.")
print("Data is embedded in model.bim; the project has no file dependency and no "
      "parameter to set.")
