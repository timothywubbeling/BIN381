# Milestone 4 — Person B (Rudi Jan du Plessis)

Due **Monday 19 October 2026, 23:59** on BC Connect. Late is an automatic 0, and nothing counts
unless it is uploaded there.

Person B's share of Milestone 4, per the team guideline and the official brief:

| Deliverable | Status | File |
|---|---|---|
| Report §4 Evaluation and key findings | Draft ready | `BIN381_M4_PersonB_Sections_4_6_8.docx` |
| Report §6 Recommendations | Draft ready | same |
| Report §8 Limitations and future work | Draft ready | same |
| Power BI: Overview + model-performance, subgroup and drivers pages | Built and reconciled (17 Oct) | `../../powerbi/BIN381_M4_Dashboard.pbix`, guide in `../../docs/powerbi_m4_person_b_pages.md` |
| Slides 5–7 + dashboard demo | Draft ready | `BIN381_M4_PersonB_Slides_5_to_7.md` |
| Reflection, ethics entries, AI log (now includes AI-M4-7, the dashboard build) | Draft ready — **needs Rudi's sign-off** | `BIN381_M4_PersonB_Reflection_and_AI_Log.md` |
| Check the evaluation numbers quoted anywhere | Passing | `check_numbers.py` |

## Rebuilding

Run both from the repository root:

```bash
python report/M4/build_personB_sections.py
python report/M4/check_numbers.py
```

`build_personB_sections.py` reads every figure from `data/evaluation/` and `data/powerbi/` at build
time, so the report cannot drift from the notebook. If the model is ever retrained, re-run both —
`check_numbers.py` exits non-zero if anything stops reconciling.

## What is still outstanding

Updated 19 October, after the merge. Items 2 to 4 below are done; what is left needs Power BI
Desktop, Word or a person.

1. **Rudi's sign-off** on the AI log in `BIN381_M4_PersonB_Reflection_and_AI_Log.md` (AI-M4-7 records
   that the assistant built the dashboard pages). Appendix A of the report carries these entries.
2. ~~Alexander's two dashboard pages~~ — done. The merged dashboard has "Where the need is" and
   "Who is affected" as pages 2 and 3, so recommendation 4's province drill-down exists.
3. ~~The slide deck~~ — built: `BIN381_M4_Slides_Group_P1.pptx`, ten slides with speaker notes,
   from these notes and Timothy's. Slides 1–4 are drafted from the report and are **Alexander's to
   approve**.
4. ~~Hand to Timothy~~ — merged: `BIN381_M4_Report_Group_P1.docx`, sections 1 to 8 in order with
   both appendices (`merge_final_report.py`).
5. **Still to do, and only on a machine with the applications** (see the repository `README.md`,
   *Milestone 4 deliverables*): save the dashboard as a `.pbix`, export the nine page screenshots
   over `docs/figures/pbi_m4_*.png`, check the 10-page limit in Word and export the report PDF,
   and fill the `TO CONFIRM` rows in the ethics log — Alexander's and Rudi's entries and
   reflections.

## Numbers that matter

Final model: lasso binary logistic (glmnet) at threshold **0.24**, on a held-out test set of
**6,279** households out of **20,925** modelled.

| | |
|---|---|
| Recall | 80.7% |
| Precision | 41.9% |
| Share referred (test set) | 58.9% |
| ROC-AUC | 0.736 |
| Severely insecure households flagged | 85.7% |
| Weakest subgroup (income > R11,500) | 39.2% recall |

**Watch this one:** 58.9% is the test-set referral rate and 59.2% is the rate across all 20,925
households (`powerbi_reconciliation.csv`). Both are right. Every Person B performance claim uses
the test-set figure, and `check_numbers.py` fails if the two get swapped.
