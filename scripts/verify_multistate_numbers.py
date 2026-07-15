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
print("=== Oregon clusters and corroboration (Phase A5) ===")
or_clusters = load_csv(os.path.join(BASE, "anonymized_data/oregon/OR_Operator_PhoneClusters_ANON.csv"))
check("OR distinct operator clusters", len(or_clusters), 49)

or_corrob = load_csv(os.path.join(BASE, "anonymized_data/oregon/A5_OR_Cluster_Corroboration_ANON.csv"))
check("OR corroboration rows", len(or_corrob), 49)
or_evidence_counts = {}
for r in or_corrob:
    k = r["evidence_class"]
    or_evidence_counts[k] = or_evidence_counts.get(k, 0) + 1
check("OR 'Same openly disclosed brand'", or_evidence_counts.get("Same openly disclosed brand", 0), 36)
check("OR 'Same officers/owners/managers'", or_evidence_counts.get("Same officers/owners/managers", 0), 8)
check("OR 'Same residential or business address'", or_evidence_counts.get("Same residential or business address", 0), 2)
check("OR 'No public connection found'", or_evidence_counts.get("No public connection found", 0), 1)
check("OR 'Same legal entity'", or_evidence_counts.get("Same legal entity", 0), 1)
check("OR 'Indeterminate'", or_evidence_counts.get("Indeterminate", 0), 1)

or_result_counts = {}
for r in or_corrob:
    k = r["corroboration_result"]
    or_result_counts[k] = or_result_counts.get(k, 0) + 1
check("OR clusters corroborated", or_result_counts.get("Corroborated", 0), 47)
check("OR clusters not corroborated", or_result_counts.get("Not corroborated", 0), 1)
check("OR clusters indeterminate", or_result_counts.get("Indeterminate", 0), 1)

print()
print("=== Cross-state cluster-corroboration summary (build_corroboration_analysis.py output) ===")
corrob_summary = load_csv(os.path.join(BASE, "anonymized_data/corroboration_analysis_summary.csv"))
wa_rate_row = next(r for r in corrob_summary if r["metric"] == "cluster corroboration rate" and r["state"] == "Washington")
or_rate_row = next(r for r in corrob_summary if r["metric"] == "cluster corroboration rate" and r["state"] == "Oregon")
check("WA cluster corroboration rate, total", int(wa_rate_row["n_total_clusters"]), 72)
check("WA clusters corroborated", int(wa_rate_row["n_corroborated"]), 70)
check("WA clusters not corroborated", int(wa_rate_row["n_not_corroborated"]), 2)
check("OR cluster corroboration rate, total", int(or_rate_row["n_total_clusters"]), 49)
check("OR clusters corroborated (summary file)", int(or_rate_row["n_corroborated"]), 47)

print()
print("=== Threshold-sensitivity sweep (build_sensitivity_analysis.py output) ===")
sens = load_csv(os.path.join(BASE, "anonymized_data/sensitivity_analysis_summary.csv"))


def sens_row(state, threshold, linkage_type="phone", facility_type=""):
    return next(
        r for r in sens
        if r.get("state") == state and r.get("threshold") == str(threshold)
        and r.get("linkage_type") == linkage_type and r.get("facility_type", "") == facility_type
    )


check("WA threshold=2 qualifying facilities", int(sens_row("Washington", 2)["n_qualifying_facilities"]), 164)
check("WA threshold=3 qualifying facilities", int(sens_row("Washington", 3)["n_qualifying_facilities"]), 50)
check("WA threshold=4 qualifying facilities", int(sens_row("Washington", 4)["n_qualifying_facilities"]), 20)
check("WA threshold=5 qualifying facilities", int(sens_row("Washington", 5)["n_qualifying_facilities"]), 0)
check("OR threshold=2 qualifying facilities (all types)", int(sens_row("Oregon", 2)["n_qualifying_facilities"]), 101)
check("OR threshold=3, RCF qualifying facilities", int(sens_row("Oregon", 3, facility_type="RCF")["n_qualifying_facilities"]), 5)
check("OR threshold=3, RCF stratum size", int(sens_row("Oregon", 3, facility_type="RCF")["n_total_facilities_in_stratum"]), 81)
check("OR threshold=3, AFH qualifying facilities", int(sens_row("Oregon", 3, facility_type="AFH")["n_qualifying_facilities"]), 0)
check("OR threshold=3, AFH stratum size", int(sens_row("Oregon", 3, facility_type="AFH")["n_total_facilities_in_stratum"]), 629)

print()
print("=== Public-record observability (build_observability_analysis.py output) ===")
obs = load_csv(os.path.join(BASE, "anonymized_data/observability_analysis_summary.csv"))


def obs_row(metric, state):
    return next(r for r in obs if r["metric"] == metric and r["state"] == state)


check(
    "WA no public record at all",
    int(obs_row("No public record at all (external analyst cannot observe this facility)", "Washington")["n_facilities"]),
    1287,
)
check(
    "OR no public record at all",
    int(obs_row("No public record at all (external analyst cannot observe this facility)", "Oregon")["n_facilities"]),
    118,
)
check("WA has enforcement record(s)", int(obs_row("Has enforcement record(s)", "Washington")["n_facilities"]), 165)
check("OR has enforcement record(s)", int(obs_row("Has enforcement record(s)", "Oregon")["n_facilities"]), 149)
check("WA has complaint/investigation record(s)", int(obs_row("Has complaint/investigation record(s)", "Washington")["n_facilities"]), 586)
check("OR has complaint/investigation record(s)", int(obs_row("Has complaint/investigation record(s)", "Oregon")["n_facilities"]), 221)

print()
print("=== Table 1 / Appendix G / Appendix B reconciliation (parsed directly from the manuscript files) ===")
with open(os.path.join(BASE, "Hussein_Multistate_Manuscript.md")) as f:
    manuscript_lines = f.readlines()

table1_start = next(i for i, l in enumerate(manuscript_lines) if l.startswith("**Table 1."))
table1_rows = [l for l in manuscript_lines[table1_start:table1_start + 15] if l.startswith("| ") and not l.startswith("| Category") and not l.startswith("|---")]
table1_categories = {l.split("|")[1].strip(): len([s for s in l.split("|")[2].split(";") if s.strip()]) for l in table1_rows}
check("Table 1 category count", len(table1_categories), 5)
check("Table 1 'Strong independent convergence' indicator count", table1_categories.get("Strong independent convergence"), 7)
check("Table 1 'Limited or related convergence' indicator count", table1_categories.get("Limited or related convergence"), 5)
check("Table 1 'Anchor-derived only' indicator count", table1_categories.get("Anchor-derived only"), 5)
check("Table 1 'Operational proxy' indicator count", table1_categories.get("Operational proxy"), 1)
check("Table 1 'Unsupported, redefined, or retired' indicator count", table1_categories.get("Unsupported, redefined, or retired"), 3)
check("Table 1 total indicators across categories", sum(table1_categories.values()), 21)

with open(os.path.join(BASE, "Hussein_Multistate_Manuscript_Supplementary.md")) as f:
    supp_lines = f.readlines()

appendix_starts = {l.split(":")[0].replace("## ", "").strip(): i for i, l in enumerate(supp_lines) if l.startswith("## Appendix")}
appendix_bounds = sorted(appendix_starts.items(), key=lambda kv: kv[1])


def appendix_span(name):
    idx = [i for i, (n, _) in enumerate(appendix_bounds) if n == name][0]
    start = appendix_bounds[idx][1]
    end = appendix_bounds[idx + 1][1] if idx + 1 < len(appendix_bounds) else len(supp_lines)
    return supp_lines[start:end]


appendix_b_rows = sum(1 for l in appendix_span("Appendix B") if l.startswith("| RF-"))
check("Appendix B RF rows", appendix_b_rows, 22)

appendix_g_lines = appendix_span("Appendix G")
table_g1_end = next(i for i, l in enumerate(appendix_g_lines) if l.startswith("### False-positive safeguards"))
appendix_g1_rows = sum(1 for l in appendix_g_lines[:table_g1_end] if l.startswith("| RF-"))
check("Appendix G Table G1 RF rows", appendix_g1_rows, 22)
check("Appendix B rows == Appendix G Table G1 rows", appendix_b_rows, appendix_g1_rows)

print()
print("=== Table G1 MN-derivation-anchor-status tally (parsed directly from Appendix G, not the manuscript's prose) ===")
table_g1_lines = appendix_g_lines[:table_g1_end]
table_g1_rows = [l for l in table_g1_lines if l.startswith("| RF-")]
check("Table G1 rows found for tally", len(table_g1_rows), 22)

anchor_buckets = {"directly_stated": 0, "abstraction_weak": 0, "not_derivable": 0, "contradicted": 0, "proxy": 0}
for row in table_g1_rows:
    cols = [c.strip() for c in row.split("|")]
    anchor_status_cell = cols[3]
    if anchor_status_cell.startswith("Directly stated"):
        anchor_buckets["directly_stated"] += 1
    elif anchor_status_cell.startswith("Reasonable abstraction") or anchor_status_cell.startswith("Weak/indirect"):
        anchor_buckets["abstraction_weak"] += 1
    elif anchor_status_cell.startswith("Not derivable"):
        anchor_buckets["not_derivable"] += 1
    elif anchor_status_cell.startswith("Contradicted"):
        anchor_buckets["contradicted"] += 1
    elif anchor_status_cell.startswith("Framed as"):
        anchor_buckets["proxy"] += 1

check("Directly stated (MN anchor)", anchor_buckets["directly_stated"], 12)
check("Reasonable abstraction / Weak-indirect (MN anchor)", anchor_buckets["abstraction_weak"], 4)
check("Not derivable (MN anchor)", anchor_buckets["not_derivable"], 4)
check("Contradicted (MN anchor, i.e. retired RF-02)", anchor_buckets["contradicted"], 1)
check("Proxy, unscored (MN anchor, i.e. RF-08)", anchor_buckets["proxy"], 1)
check(
    "Total (12+4+4 active-scored + 1 proxy + 1 retired = 22)",
    sum(anchor_buckets.values()),
    22,
)

print()
print("=== Exploratory cluster-enforcement comparison (build_cluster_enforcement_exploratory.py output) ===")
cluster_enf = load_csv(os.path.join(BASE, "anonymized_data/cluster_enforcement_exploratory_summary.csv"))


def cluster_enf_row(state, outcome, record_filter):
    return next(
        r for r in cluster_enf
        if r["state"] == state and r["outcome"] == outcome and r["record_filter"] == record_filter
    )


or_enf_all = cluster_enf_row("Oregon", "n_enforcement", "All facilities")
check("OR enforcement, crude RR (x1000, all facilities)", round(float(or_enf_all["crude_risk_ratio"]) * 1000), 2100)
check("OR enforcement, MH-adjusted RR (x1000, all facilities)", round(float(or_enf_all["mh_adjusted_risk_ratio"]) * 1000), 664)
check("OR enforcement, n clustered (all facilities)", int(or_enf_all["n_clustered"]), 101)
check("OR enforcement, n nonclustered (all facilities)", int(or_enf_all["n_nonclustered"]), 691)

print()
print("=== Figures present and non-trivial in size ===")
for fname in ("Fig1_Conceptual_Overview.png", "Fig2_Framework_Architecture.png", "Fig3_Population_Analytic_Flow.png"):
    fpath = os.path.join(BASE, "figures", fname)
    exists = os.path.isfile(fpath)
    size_ok = exists and os.path.getsize(fpath) > 10_000
    check(f"{fname} exists and is a non-trivial PNG", exists and size_ok, True)

print()
if FAILURES:
    raise SystemExit(f"FAILED: {len(FAILURES)} mismatch(es): {FAILURES}")
print("All multistate headline numbers verified against this repository's own anonymized_data/.")
print("Federal audit and congressional-letter facts are document citations, not facility-level")
print("computations; see SOURCE_MANIFEST.md for their sources and access dates.")
