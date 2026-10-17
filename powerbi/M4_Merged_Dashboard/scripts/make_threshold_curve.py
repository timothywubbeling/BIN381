"""Person C: build the what-if threshold curve table from the household-level export.

Reproduces, for every candidate referral threshold, the test-set metrics the
dashboard quotes. Verified against data/powerbi/powerbi_model_summary.csv at 0.24.
"""
import csv, os, sys

src = sys.argv[1]
out = sys.argv[2]

rows = [r for r in csv.DictReader(open(src, encoding="utf-8")) if r["Split"] == "Test"]
n = len(rows)
probs = [(float(r["ModelProbability"]), int(r["AtRisk"])) for r in rows]
at_risk = sum(a for _, a in probs)

grid = [round(0.05 + 0.01 * i, 2) for i in range(0, 86)]   # 0.05 .. 0.90

with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
    w.writerow(["Threshold", "Referred", "ReferredShare", "TruePositives",
                "Recall", "Precision", "ReferredPer1000", "MissedAtRisk", "IsDeployed"])
    for t in grid:
        ref = [(p, a) for p, a in probs if p >= t]
        tp = sum(a for _, a in ref)
        w.writerow([
            f"{t:.2f}",
            len(ref),
            round(len(ref) / n, 6),
            tp,
            round(tp / at_risk, 6),
            round(tp / len(ref), 6) if ref else "",
            round(1000 * len(ref) / n),
            at_risk - tp,
            "Deployed threshold" if abs(t - 0.24) < 1e-9 else "Other",
        ])

# reconciliation printout
for t in (0.14, 0.20, 0.22, 0.24, 0.26, 0.30, 0.35, 0.40, 0.50):
    ref = [(p, a) for p, a in probs if p >= t]
    tp = sum(a for _, a in ref)
    print(f"  {t:.2f}  recall {100*tp/at_risk:5.1f}%   precision {100*tp/len(ref):5.1f}%   referred {100*len(ref)/n:5.1f}%")
print(f"\ntest households {n}  at risk {at_risk}")
