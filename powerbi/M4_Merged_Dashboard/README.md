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
2. **Home → Refresh.** A `.pbip` stores no cached data, so the visuals are empty until you do this
   once. The refresh reads the snapshot embedded in the file — it touches no folder and cannot fail
   on a missing path.
3. Check the `Threshold` slicer on the "How well the screen works" page reads **0.24**.
4. **File → Save as** → `powerbi/BIN381_M4_Dashboard_Group_P1.pbix`, beside Person B's file (keep
   that one as the record of the first iteration).

**Hand the `.pbix` to the markers, not the `.pbip`.** A `.pbix` has the data compiled in and opens
with everything on screen, no refresh needed. The `.pbip` is the version-controlled source.

**There is nothing to configure.** Every table carries its own data: each CSV is gzipped,
base64-encoded and inlined into its partition in `model.bim`. The model reads no files, so there is
no parameter to repoint and no path that can be wrong. It opens and refreshes on any machine.

That was not true of the first version, which read the CSVs through a `DataFolder` parameter holding
an absolute path. It worked only on the machine that built it; anywhere else all nine tables failed
at once, which looks exactly like the data being missing from the repository. Embedding costs about
0.5 MB in `model.bim` and removes the whole class of problem.

> **The one thing that can still break it: path length.** A PBIP nests
> `…/<name>.Report/definition/pages/<20 chars>/visuals/<20 chars>/visual.json`, about 115 characters
> below the project folder. Windows refuses paths over 260 characters unless long-path support is
> on (it is off by default), and Power BI then opens a blank *Untitled* document instead of the
> project, with no error that explains why. Inside this repository the longest path is 198
> characters, so there is ~60 to spare. **Clone somewhere short** — `C:\BIN381\` is ideal, a deep
> `OneDrive - …\Documents\…` path is not. To check: the longest file path under
> `powerbi/M4_Merged_Dashboard/` must stay under 260.

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
| **Opens and refreshes with no data folder present** | **all 9 tables load** | **copied to `C:\PBITest\`, nothing else nearby: 20,925 households and every figure above identical** |

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
- `scripts/build.py` — assembles the project, embeds the nine CSVs, then validates: it decodes
  every embedded payload back out of the finished `model.bim` and compares it with the source file,
  and checks every field reference against the model plus visual ids, canvas bounds and overlaps.
  Exits non-zero on any problem. The sixth argument is the data directory to embed from.

**Because the data is embedded, a refresh in Power BI re-reads the snapshot inside the file, not
`data/powerbi/`.** New data therefore needs `build.py` re-run to re-embed it; the retrain sequence
below says so. The build fails rather than embed a payload that does not round-trip.

It replaces the `.Report` and `.SemanticModel` folders only; this README and `scripts/` are left
alone. Once anyone starts editing in the Power BI UI the generator stops being the source of truth —
say so in the commit message when that happens.

### Fixed: the what-if threshold is exact

`GENERATESERIES(0, 1, 0.01)` accumulates 0.01 at a time, so the step shown as 0.24 was stored as
`0.24000000000000007`. That is slightly more than 0.24, so the 26 test households scoring exactly
0.2400 — seven of them at risk — fell outside `ModelProbability >= T`: the what-if cards read
80.4% / 42.0% / 585 while the fixed cards above them read 80.7% / 41.9% / 589. A typed 0.30 matched
no row at all, `SELECTEDVALUE` fell back to its default, and the cards appeared not to move. The
slicer's saved `numericStart` held the same drifted value, which made 0.24 the bottom of its range.

The table is now built from whole numbers,
`SELECTCOLUMNS(GENERATESERIES(0, 100, 1), "Threshold", [Value] / 100)`, so each value is exactly
the number Power BI produces when it is typed; `Threshold Value` rounds to two decimals as a safety
net; and `numericStart` is gone, so the slider runs from 0 again.

**Check after opening:** at 0.24 both rows of cards read 80.7% / 41.9% / 58.9% (589 per 1,000).
Then type 0.14, 0.30 and 0.50 into the slicer box:

| Threshold | Recall | Precision | Referred | Per 1,000 |
|---|---|---|---|---|
| 0.14 | 95.9% | 35.0% | 83.8% | 838 |
| 0.24 | 80.7% | 41.9% | 58.9% | 589 |
| 0.30 | 67.8% | 47.3% | 43.8% | 438 |
| 0.50 | 31.1% | 62.4% | 15.2% | 152 |

Cards are set to display units "None" as well, so the Overview household count reads 20,925 and
not 21K.

---

## Maintenance

**After a retrain, in order:** `R/export_powerbi.R` → `R/make_threshold_curve.R` →
`python scripts/make_data_foundation.py <repo> <repo>/data/powerbi` →
**`python scripts/build.py` to re-embed the new data** → `python report/M4/check_numbers.py` →
open this project, Refresh, check the Reconciliation page reads 0.0 for all nine provinces →
re-save the `.pbix` → re-take the screenshots.

Skipping the `build.py` step leaves the dashboard showing the previous snapshot while the CSVs and
the report say something else — the Reconciliation page is what catches that.

Monitoring thresholds, retraining and retirement triggers, model version and rollback are in
`report/M4/BIN381_M4_Handover_and_Maintenance.md`.

## Screenshots for the report and slides

Export each page at 1280×720 into `docs/figures/` as `pbi_m4_1_overview.png` …
`pbi_m4_9_reconciliation.png`. Report §5 refers to pages 1 and 4; slides 7–8 use pages 1, 4 and 5.
Person B's `pbi_b*.png` are from the pre-merge file and should be replaced.
