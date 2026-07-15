"""Cross-state cluster-corroboration analysis (RF-08).

Integrates Washington's existing cluster-corroboration data with Oregon's
newly completed A5 business-registry corroboration research (49/49 clusters
reviewed; see PRIVATE-public-data-review-priority-oregon/private/A5_*).

Washington's corroboration work (companion repo) recorded a linkage METHOD
(DSHS Primary Contact / CCFS Registered Agent or Principal-Office Address /
CCFS Governor (Owner/Member) / DSHS Off-Site Mailing Address / None found)
but did not separately flag whether a cluster's relationship was already
openly disclosed in facility branding versus discovered only through
registry research - that distinction was not part of the original WA
corroboration protocol. Oregon's A5 protocol was designed after seeing this
gap and does make that distinction explicitly. This script maps WA's methods
onto the closest shared evidence category for cross-state comparison and
states plainly, in its output, where WA's data cannot support the
finer openly-affiliated vs. registry-corroborated distinction Oregon's can.

Outputs:
  anonymized_data/corroboration_analysis_detailed.csv   (appendix-ready, both states, all clusters)
  anonymized_data/corroboration_analysis_summary.csv    (manuscript-facing, decisive findings only)
"""

import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# WA linkage method -> shared evidence category. WA's own research did not
# assess brand-openness, so nothing maps to "Same openly disclosed brand" here;
# that gap is stated explicitly in the summary output, not silently omitted.
WA_METHOD_TO_EVIDENCE_CLASS = {
    "CCFS Governor (Owner/Member)": "Same officers/owners/managers",
    "CCFS Registered Agent or Principal-Office Address": "Same residential or business address (WA data does not distinguish individual vs. commercial registered agent)",
    "DSHS Off-Site Mailing Address": "Same residential or business address",
    "DSHS Primary Contact": "Same contact/administrative link (WA-specific category; underlying research did not further specify officer vs. address)",
    "None found": "No public connection found",
}


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main():
    wa_clusters = load_csv(os.path.join(BASE, "anonymized_data/washington/WA_Operator_Clusters_ANON.csv"))
    wa_corrob = load_csv(os.path.join(BASE, "anonymized_data/washington/WA_Operator_Clusters_Corroboration_ANON.csv"))
    wa_corrob_by_id = {r["cluster_id"]: r for r in wa_corrob}

    or_corrob = load_csv(os.path.join(BASE, "anonymized_data/oregon/A5_OR_Cluster_Corroboration_ANON.csv"))

    detailed = []

    for r in wa_clusters:
        cid = r["cluster_id"]
        c = wa_corrob_by_id.get(cid, {})
        method = c.get("corroboration_linkage_method", "")
        status = c.get("corroboration_status", "")
        detailed.append(
            {
                "state": "Washington",
                "cluster_id": cid,
                "n_facilities": r["n_licenses"],
                "corroboration_result": status,
                "evidence_class": WA_METHOD_TO_EVIDENCE_CLASS.get(method, method),
                "total_enforcement": r.get("total_enforcement", ""),
                "total_investigations": r.get("total_investigations", ""),
                "total_civil_fines": r.get("total_civil_fines", ""),
            }
        )

    for r in or_corrob:
        detailed.append(
            {
                "state": "Oregon",
                "cluster_id": r["cluster_id"],
                "n_facilities": r["n_facilities"],
                "corroboration_result": r["corroboration_result"],
                "evidence_class": r["evidence_class"],
                "total_enforcement": "",
                "total_investigations": "",
                "total_civil_fines": "",
            }
        )

    detailed_path = os.path.join(BASE, "anonymized_data/corroboration_analysis_detailed.csv")
    with open(detailed_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "state",
                "cluster_id",
                "n_facilities",
                "corroboration_result",
                "evidence_class",
                "total_enforcement",
                "total_investigations",
                "total_civil_fines",
            ],
        )
        writer.writeheader()
        writer.writerows(detailed)
    print(f"Wrote {len(detailed)} rows to {detailed_path}")

    # Manuscript-facing summary: per-state corroboration rate, evidence-class
    # breakdown, and enforcement/investigation prevalence in vs. out of
    # corroborated clusters (Washington only - Oregon's A5 data does not carry
    # per-cluster enforcement counts in the same structure).
    def pct(n, total):
        return round(100 * n / total, 1) if total else 0.0

    summary_rows = []
    for state in ["Washington", "Oregon"]:
        rows = [r for r in detailed if r["state"] == state]
        total = len(rows)
        corroborated = sum(1 for r in rows if r["corroboration_result"] == "Corroborated")
        not_corroborated = sum(1 for r in rows if r["corroboration_result"] in ("Uncorroborated", "Not corroborated"))
        indeterminate = sum(1 for r in rows if r["corroboration_result"] == "Indeterminate")
        summary_rows.append(
            {
                "metric": "cluster corroboration rate",
                "state": state,
                "n_total_clusters": total,
                "n_corroborated": corroborated,
                "n_not_corroborated": not_corroborated,
                "n_indeterminate": indeterminate,
                "pct_corroborated": pct(corroborated, total),
            }
        )

    # Oregon evidence-class breakdown (the finer distinction WA's data can't make)
    or_rows = [r for r in detailed if r["state"] == "Oregon"]
    for ec in sorted({r["evidence_class"] for r in or_rows}):
        n = sum(1 for r in or_rows if r["evidence_class"] == ec)
        summary_rows.append(
            {
                "metric": "Oregon evidence-class breakdown",
                "state": "Oregon",
                "evidence_class": ec,
                "n_clusters": n,
                "pct_of_all_clusters": pct(n, len(or_rows)),
            }
        )

    # Washington enforcement/investigation prevalence, corroborated vs. uncorroborated
    wa_rows = [r for r in detailed if r["state"] == "Washington"]
    for status_label, matcher in [
        ("Corroborated", lambda r: r["corroboration_result"] == "Corroborated"),
        ("Uncorroborated", lambda r: r["corroboration_result"] == "Uncorroborated"),
    ]:
        subset = [r for r in wa_rows if matcher(r)]
        if not subset:
            continue
        n_with_enforcement = sum(1 for r in subset if int(r["total_enforcement"] or 0) > 0)
        n_with_investigations = sum(1 for r in subset if int(r["total_investigations"] or 0) > 0)
        summary_rows.append(
            {
                "metric": "WA enforcement/investigation prevalence by corroboration status",
                "state": "Washington",
                "corroboration_status": status_label,
                "n_clusters": len(subset),
                "n_with_enforcement": n_with_enforcement,
                "pct_with_enforcement": pct(n_with_enforcement, len(subset)),
                "n_with_investigations": n_with_investigations,
                "pct_with_investigations": pct(n_with_investigations, len(subset)),
            }
        )

    summary_path = os.path.join(BASE, "anonymized_data/corroboration_analysis_summary.csv")
    all_keys = []
    for row in summary_rows:
        for k in row:
            if k not in all_keys:
                all_keys.append(k)
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Wrote {len(summary_rows)} rows to {summary_path}")

    print()
    print("NOTE: Oregon's evidence-class distinction (openly-affiliated brand vs.")
    print("registry-corroborated-but-not-name-evident vs. same-legal-entity vs.")
    print("address-only) is NOT available for Washington - WA's original corroboration")
    print("protocol did not assess facility-name brand-openness. This is stated here")
    print("explicitly rather than papered over with an invented WA equivalent.")


if __name__ == "__main__":
    main()
