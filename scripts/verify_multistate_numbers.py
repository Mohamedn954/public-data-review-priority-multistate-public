"""Independently recomputes every headline number in Hussein_Multistate_Manuscript.md
from this repository's own anonymized_data/, using only Washington and Oregon
facility-level data already de-identified in the companion repositories. Fails
loudly on any mismatch. Does not touch federal audit or congressional-letter
citations, which are not facility-level data and are documented in
SOURCE_MANIFEST.md instead.
"""

import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAILURES = []


def check(label, actual, expected):
    status = "OK" if actual == expected else "MISMATCH"
    print(f"  {label}: {actual} (expect {expected}) [{status}]")
    if actual != expected:
        FAILURES.append(label)


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


print("=== Washington ===")
wa = load_csv(os.path.join(BASE, "anonymized_data/washington/WA_AFH_3County_Enriched_ANON.csv"))
check("facilities", len(wa), 3457)

n_enforcement = sum(1 for r in wa if int(r["n_enforcement"] or 0) >= 1)
check("facilities with >=1 enforcement action", n_enforcement, 165)
check(
    "enforcement prevalence pct (rounded)",
    round(100 * n_enforcement / len(wa), 1),
    4.8,
)

n_repeat_enforcement = sum(1 for r in wa if int(r["n_enforcement"] or 0) >= 2)
check("facilities with >=2 enforcement actions", n_repeat_enforcement, 60)

n_stop_placement = sum(1 for r in wa if int(r["n_stop_placement"] or 0) >= 1)
check("facilities with stop-placement orders", n_stop_placement, 18)

n_investigations = sum(1 for r in wa if int(r["n_investigations"] or 0) >= 1)
check("facilities with >=1 complaint investigation", n_investigations, 586)

clusters = load_csv(os.path.join(BASE, "anonymized_data/washington/WA_Operator_Clusters_ANON.csv"))
cluster_ids = {r.get("cluster_id") for r in clusters if r.get("cluster_id")}
check("distinct operator clusters (from clusters file)", len(cluster_ids), 72)

facilities_in_clusters = sum(1 for r in wa if r.get("cluster_id"))
check("facilities in shared-contact clusters", facilities_in_clusters, 164)

print()
print("=== Oregon ===")
orr = load_csv(os.path.join(BASE, "anonymized_data/oregon/OR_Providers_Enriched_ANON.csv"))
check("facilities", len(orr), 792)

clackamas = sum(1 for r in orr if r.get("County") == "Clackamas")
washington_co = sum(1 for r in orr if r.get("County") == "Washington")
check("Clackamas County facilities", clackamas, 324)
check("Washington County facilities", washington_co, 468)

rf03 = sum(1 for r in orr if float(r.get("phone_shared_count") or 0) >= 2)
rf08 = sum(1 for r in orr if float(r.get("phone_shared_count") or 0) >= 3)
check("RF-03 (phone_shared_count>=2)", rf03, 101)
check("RF-08 (phone_shared_count>=3)", rf08, 5)

print()
print("=== Combined evidentiary accounting ===")
combined = load_csv(os.path.join(BASE, "anonymized_data/combined_evidence_matrix.csv"))
check("indicators in combined matrix", len(combined), 20)
category_counts = {}
for r in combined:
    cat = r["Combined_Status"]
    category_counts[cat] = category_counts.get(cat, 0) + 1
internal_data_count = sum(v for k, v in category_counts.items() if k.startswith("Internal Data Required"))
check("Directly Operationalized", category_counts.get("Directly Operationalized", 0), 2)
check("System-Level Evidence", category_counts.get("System-Level Evidence", 0), 3)
check("Case-Level Evidence", category_counts.get("Case-Level Evidence", 0), 2)
check("Partially Operationalized", category_counts.get("Partially Operationalized", 0), 4)
check("Contextually Assessed", category_counts.get("Contextually Assessed", 0), 2)
check("Publicly Testable, Not Completed", category_counts.get("Publicly Testable, Not Completed", 0), 3)
check("Internal Data Required (incl. RF-15 compound label)", internal_data_count, 4)
check("indicators requiring internal data in both states", internal_data_count, 4)

print()
if FAILURES:
    raise SystemExit(f"FAILED: {len(FAILURES)} mismatch(es): {FAILURES}")
print("All multistate headline numbers verified against this repository's own anonymized_data/.")
print("Federal audit and congressional-letter facts are document citations, not facility-level")
print("computations; see SOURCE_MANIFEST.md for their sources and access dates.")
