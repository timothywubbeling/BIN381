# -*- coding: utf-8 -*-
"""Build the two data-foundation tables the Milestone 1 dashboard used.

The Milestone 1 dashboard had a Data Inventory page and a Data Quality page driven by
tables (DatasetInventory, QualityFindings) that only existed inside that .pbix. This
rebuilds both from sources that are in the repository, so the figures are checkable:

  powerbi_dataset_inventory.csv  counted directly off data/raw/
  powerbi_data_quality.csv       reshaped from data/clean/qa_log_personC.csv

Every column is measured, not asserted. "Grain" is decided by comparing the number of
rows with the number of distinct HouseholdID values, which is also the reason the three
person-level files were not selected.

  python scripts/make_data_foundation.py <repo root> <out dir>
"""
import csv
import os
import sys

ROOT = sys.argv[1]
OUT = sys.argv[2]

RAW = os.path.join(ROOT, "data", "raw")
QA = os.path.join(ROOT, "data", "clean", "qa_log_personC.csv")

DOMAIN = {
    "D01": "Population profile",
    "D02": "Learning profile",
    "D03": "Economic participation",
    "D04": "Dwelling conditions",
    "D05": "Basic services",
    "D06": "Household energy",
    "D07": "Household wellbeing",
    "D08": "Connectivity and access",
    "D09": "Household resources",
    "D10": "Mobility and access",
}

# ------------------------------------------------------------------ inventory
inventory = []
for fn in sorted(os.listdir(RAW)):
    if not fn.lower().endswith(".csv"):
        continue
    code = fn.split("_")[0]
    with open(os.path.join(RAW, fn), encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = rd.fieldnames
        rows = list(rd)
    key = next((c for c in cols if c.lower() in ("householdid", "household_id")), None)
    households = len({r[key] for r in rows}) if key else 0
    per_hh = len(rows) / households if households else 0

    if per_hh > 1.5:
        grain = "Person"
        selected = "No"
        reason = (f"Person-level: about {per_hh:.1f} rows per household, so it cannot join "
                  f"one-to-one on {key}")
        dupes = 0
    else:
        grain = "Household"
        selected = "Yes"
        dupes = len(rows) - households
        reason = (f"Household-level: joined on {key}"
                  + (f"; {dupes} exact duplicate rows removed" if dupes else
                     "; no duplicate rows"))

    inventory.append({
        "Dataset": code,
        "Domain": DOMAIN.get(code, code),
        "Grain": grain,
        "Rows": len(rows),
        "Columns": len(cols),
        "Households": households,
        "DuplicateRows": dupes,
        "Selected": selected,
        "Reason": reason,
    })

inv_path = os.path.join(OUT, "powerbi_dataset_inventory.csv")
with open(inv_path, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(inventory[0].keys()))
    w.writeheader()
    w.writerows(inventory)

sel = [r for r in inventory if r["Selected"] == "Yes"]
print(f"wrote {inv_path}")
print(f"  datasets provided {len(inventory)} | selected {len(sel)} | "
      f"rows in selection {sum(r['Rows'] for r in sel):,}")
print(f"  households after de-duplication {max(r['Households'] for r in sel):,} | "
      f"duplicate rows removed {sum(r['DuplicateRows'] for r in sel)}")

# --------------------------------------------------------------- data quality
# before/after mean different things per row (row counts for the de-duplication rows,
# value counts for the recodes), so they are carried as text and never aggregated.
quality = []
with open(QA, encoding="utf-8-sig", newline="") as fh:
    for r in csv.DictReader(fh):
        quality.append({
            "Dataset": r["file"],
            "Domain": DOMAIN.get(r["file"], r["file"]),
            "Column": r["column"],
            "Problem": r["problem"],
            "Treatment": r["treatment"],
            "Before": r["before"],
            "After": r["after"],
        })

q_path = os.path.join(OUT, "powerbi_data_quality.csv")
with open(q_path, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(quality[0].keys()))
    w.writeheader()
    w.writerows(quality)

print(f"wrote {q_path}")
print(f"  issues logged {len(quality)} | datasets {len({r['Dataset'] for r in quality})} | "
      f"columns {len({(r['Dataset'], r['Column']) for r in quality})} | "
      f"issue types {len({r['Problem'] for r in quality})}")

# ------------------------------------------------------------- reconciliation
assert len(inventory) == 10, "expected ten GHS extracts in data/raw/"
assert len(sel) == 7, "expected seven household-level files to be selected"
assert max(r["Households"] for r in sel) == 20940, \
    "expected 20,940 households after de-duplication"
assert {r["Dataset"] for r in quality} == {r["Dataset"] for r in sel}, \
    "the QA log and the selected files disagree"
print("\ninventory and quality tables reconcile with the integration log.")
