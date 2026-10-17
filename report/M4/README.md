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

1. **Rudi's sign-off** on the AI log in `BIN381_M4_PersonB_Reflection_and_AI_Log.md` (AI-M4-7 records
   that the assistant built the dashboard pages).
2. **Alexander's two dashboard pages** ("Where the need is", "Who is affected"). Recommendation 4 in
   §6 promises a province drill-down "on the dashboard"; it only becomes true once those exist.
3. **The slide deck itself.** Slides 5–7 exist as notes only; screenshots for them are in
   `docs/figures/pbi_b*.png`.
4. **Hand to Timothy** for merging into the final report, with the cover page, contents,
   references and the 10-page check.

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
