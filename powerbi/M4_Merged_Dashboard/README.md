# Milestone 4 dashboard — merged build (Group P1)

**Owner:** Timothy Wubbeling (Person C) · **Due:** Monday 19 October 2026, 23:59 on BC Connect

This is the single Milestone 4 dashboard. It merges the two first-iteration dashboards into one
decision-support report on the final analytical dataset:

| Source | What came across |
|---|---|
| `Main Dash.pbix` (Milestone 1) | The whole visual language — 1280×720 canvas, the four-column 16px grid, the dark **Innovate** theme, IBM Plex Sans. Plus the content of all five pages: *Food Security* → page 2, *Distributions* → page 3, *Relationships* (the H1–H6 hypotheses) → page 6, *Data Inventory* → page 7, *Data Quality* → page 8. |
| `powerbi/BIN381_M4_Dashboard.pbix` (Person B) | The decision-question framing and four pages: *Overview* → page 1, *performance* → page 4, *subgroups* → page 5, *drivers* → page 6. All six measures and the `Threshold` what-if parameter. |

`docs/powerbi_m4_person_b_pages.md` says *"do not build on Main Dash.pbix"*, and that is respected:
nothing here reads the raw `D0x` tables. The Milestone 1 pages were **rebuilt on tables that live in
this repository**, so the layout and palette carry over but every number is traceable.

It also closes the gap flagged in `report/M4/README.md`: Person A's two pages (*Where the need is*,
*Who is affected*) did not exist, so decision questions 1 and 2 had no page and Recommendation 4's
promised province drill-down was not actually in the file. Pages 2 and 3 are those pages.

---

## Open it and save the .pbix

Power BI Desktop 2.159.883.0 or later.

1. Open `BIN381_M4_Dashboard_Group_P1.pbip`.
2. **Home → Refresh.** The first open shows empty visuals until you do — a `.pbip` stores no data.
3. Check the `Threshold` slicer on page 4 reads **0.24**.
4. **File → Save as** → `powerbi/BIN381_M4_Dashboard_Group_P1.pbix`, beside Person B's file (keep
   that one as the record of the first iteration).

The `DataFolder` parameter points at this repository's `data/powerbi/`, as an absolute path:

```
C:\Tim\Varsity\3rd Year\BIN381\Project\BIN381\BIN381-P1\data\powerbi\
```

**On any other machine, change it first:** Transform data → Manage parameters → `DataFolder`, set it
to your own clone's `data\powerbi\`, keeping the trailing backslash. Power Query cannot take a
relative path, so this is the one value that is not portable.

> **Locale.** The model sets `culture: en-US` and every import step types its columns with the
> `en-US` locale, so the comma-decimal trap documented in `docs/powerbi_m4_person_b_pages.md`
> cannot bite this file. Do not retype the columns in the Power Query UI on an en-ZA machine.

---

## The nine pages

Pages 1–6 each answer one decision question. Pages 7–9 are the evidence behind them.

| # | Page | Decision question | From |
|---|---|---|---|
| 1 | Overview | The six questions, the four headline numbers, what the screen is and is not | B |
| 2 | Where the need is | **1** Where is food insecurity concentrated? | M1 *Food Security*, rebuilt |
| 3 | Who is affected | **2** Which kinds of household are most affected? | M1 *Distributions*, rebuilt |
| 4 | How well the screen works | **3** Can we trust it? **6** How many would a threshold refer? | B |
| 5 | Who the screen misses | **4** Which households does it miss, and where? | B |
| 6 | What drives risk | **5** What should we ask about to spot risk early? | B + M1 H1–H6 |
| 7 | Data foundation | What data is this built on? | M1 *Data Inventory*, rebuilt |
| 8 | Data quality | What was wrong with it, and what did we do? | M1 *Data Quality*, rebuilt |
| 9 | Reconciliation | Can we trust these numbers? | Person C |

**Interactivity the rubric asks for**

- *Slicers*: province, settlement type, income band and grant receipt, in the same four positions
  on pages 2 and 3.
- *Drill-down*: the province bar chart on page 2 drills into settlement type. The `variable` slicer
  on page 5 is a second drill — one chart, five cuts.
- *Comparison*: the `Threshold` what-if on page 4 moves recall, precision and referral volume
  together, against the static curve beside it; page 2 compares at-risk with severely food
  insecure; page 5 compares every subgroup against the overall 80.7%.

**Deliberately not here.** Household identifiers (the export ships `HouseholdKey`, a row number),
dwelling type and water source (profiled in M1 but dropped at variable selection, so showing them
would imply the model uses them), and the M1 shape map, which was bound to `usa.states.topo.json`
and could never have drawn South African provinces — page 2 uses a sorted province bar chart.

---

## The three tables this project adds

The six tables from `R/export_powerbi.R` are used unchanged. Three more are generated here, because
the Milestone 1 pages and the what-if curve need tables that the R export does not produce:

| Table | Built by | Holds |
|---|---|---|
| `powerbi_threshold_curve.csv` | `R/make_threshold_curve.R` | Test-set recall, precision and referral load at every threshold from 0.05 to 0.90 (86 rows). Person B documented this curve as prose; this makes it a table. |
| `powerbi_dataset_inventory.csv` | `scripts/make_data_foundation.py` | The ten GHS extracts: rows, columns, households, duplicate rows, grain and whether each was selected. Counted directly off `data/raw/`. |
| `powerbi_data_quality.csv` | `scripts/make_data_foundation.py` | The 115 entries of `data/clean/qa_log_personC.csv`, reshaped. |

Both generators assert their own results and fail rather than write a figure that has drifted.

> `Before` and `After` in the quality table are **text**. They mean different things per row — row
> counts for the de-duplication entries, value counts for the recodes — so they must never be
> summed. The column descriptions in the model say so.

> `make_threshold_curve.R` **has not been executed**: R was not installed on the machine where the
> shipped CSV was generated, and the Python equivalent in `scripts/make_threshold_curve.py`
> produced it. Both carry the same assertions, and the CSV reconciles exactly. Run the R version
> once and confirm it reproduces the same 86 rows before relying on it.

---

## What was verified, and how

The model was loaded in Power BI Desktop, refreshed, and queried over the local Analysis Services
XMLA endpoint. Every figure below was read out of the live model.

| Check | Expected | Model returned |
|---|---|---|
| Households | 20,925 | 20,925 |
| At-risk share, weighted / unweighted | 28.3% / 30.6% | 28.3% / 30.6% |
| Severe share, weighted | 18.6% | 18.6% |
| Referred, all households | 59.2% | 59.2% |
| Test households / at risk in test | 6,279 / 1,919 | 6,279 / 1,919 |
| Recall · precision · referred at 0.24 | 80.7% · 41.9% · 58.9% | identical |
| ROC-AUC · PR-AUC · Brier | 0.736 · 0.550 · 0.180 | identical |
| What-if at 0.24 vs the deployed cards | identical | gap 0.000 on all three |
| What-if at 0.35 | 58.2% recall | 58.2% |
| **Province reconciliation, dashboard − R** | **0.0 points, all 9** | **0.0, all 9, status Reconciled** |
| Settlement and income-band cuts | match `powerbi_reconciliation.csv` | match, all 8 rows |
| Threshold curve at 0.14 / 0.24 / 0.50 | 95.9% / 80.7% / 31.1% recall | identical |
| Subgroups outside tolerance | 4 of 22 | 4 (two below the band, two above) |
| Datasets profiled / selected / set aside | 10 / 7 / 3 | 10 / 7 / 3 |
| Rows in selection · households after de-dup | 146,626 · 20,940 | identical |
| Duplicate rows removed · columns profiled | 46 · 229 | identical |
| Cleaning-log entries · problem types · columns | 115 · 16 · 113 | identical |

Reproduce it while the file is open:

```bash
powershell -File scripts/refresh.ps1 -Port <port>
powershell -File scripts/query.ps1 -Port <port> -QueryFile scripts/checks.dax
powershell -File scripts/query.ps1 -Port <port> -QueryFile scripts/m1.dax
```

The port is in
`%USERPROFILE%\Microsoft\Power BI Desktop Store App\AnalysisServicesWorkspaces\AnalysisServicesWorkspace_*\Data\msmdsrv.port.txt`.

**Not verified by machine:** how the visuals *look*. The report definition parses and loads, and
every field reference was checked against the model before building, but the rendering of each of
the 118 visuals is a human check. Pages 1–6 have been walked; pages 7–9 have not.

---

## Rebuilding the report definition

The nine pages and 118 visuals are generated, not hand-placed, so the grid stays exact and a change
can be made in one place.

```bash
python scripts/build.py <out-dir> <extracted-Main-Dash.pbix> <repo>/data/powerbi \
    <threshold-curve.csv> <foundation-dir> [<repo>/data/powerbi]
```

- `scripts/pbir.py` — the grid, the Innovate palette, and PBIR JSON helpers.
- `scripts/pages.py` — the nine pages. Edit here.
- `scripts/model.py` — the semantic model: 10 tables, 43 measures, 10 calculated columns, and
  deliberately **zero relationships** (the tables are different grains; if you re-import a CSV,
  open Manage relationships and delete anything autodetect created).
- `scripts/build.py` — assembles the project, then validates every field reference against the
  model and checks visual ids, canvas bounds and overlaps. Exits non-zero on any problem. The sixth
  argument points `DataFolder` at an existing data directory instead of keeping a private copy.

It replaces the `.Report` and `.SemanticModel` folders only; this README and `scripts/` are left
alone. Once anyone starts editing in the Power BI UI the generator stops being the source of truth —
say so in the commit message when that happens.

### Known quirk

`Threshold[Threshold]` values drift. `GENERATESERIES(0, 1, 0.01)` accumulates, so the step shown as
0.24 is stored as `0.24000000000000007` and the table tops out at 0.99. Filter with a range
(`> 0.239 && < 0.241`), never `= 0.24`, which silently matches nothing. The slicer default already
uses the drifted literal, as Person B's file did.

---

## Maintenance

**After a retrain, in order:** `R/export_powerbi.R` → `R/make_threshold_curve.R` →
`python scripts/make_data_foundation.py <repo> <repo>/data/powerbi` →
`python report/M4/check_numbers.py` → open this project, Refresh, check page 9 reads 0.0 for all
nine provinces → re-save the `.pbix` → re-take the screenshots.

Monitoring thresholds, retraining and retirement triggers, model version and rollback are in
`report/M4/BIN381_M4_Handover_and_Maintenance.md`.

## Screenshots for the report and slides

Export each page at 1280×720 into `docs/figures/` as `pbi_m4_1_overview.png` …
`pbi_m4_9_reconciliation.png`. Report §5 refers to pages 1 and 4; slides 7–8 use pages 1, 4 and 5.
Person B's `pbi_b*.png` are from the pre-merge file and should be replaced.
