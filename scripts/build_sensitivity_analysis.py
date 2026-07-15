"""Threshold-sensitivity sweep for the shared-contact clustering method (RF-03/RF-08).

Replaces the single static Oregon-only, phone-only, AFH-vs-all-types table in
Supplementary Appendix A with a reproducible sweep computed directly from
phone_shared_count and addr_shared_count in this repository's own
anonymized_data/, generated for both states, all thresholds {2,3,4,5}, both
linkage types (phone, address) plus a combined (either) view, and stratified
by county and facility type where the underlying data supports it.

Washington's population is single-facility-type (Adult Family Homes), so its
facility-type stratification is trivial (one row) and reported for symmetry,
not because it reveals anything WA-specific. Oregon's four facility types
(via OR_Facility_Type_Crosswalk.csv) are where the facility-type stratification
does real work, consistent with the manuscript's population-validity framing
(Section 3.3 / Discussion): Oregon's mixed population is the reason the
3+-license threshold calibrated on Washington needed recalibration in the
first place.

Outputs:
  anonymized_data/sensitivity_analysis_detailed.csv   (appendix-ready, full stratification)
  anonymized_data/sensitivity_analysis_summary.csv     (manuscript-facing, decisive findings only)
"""

import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THRESHOLDS = [2, 3, 4, 5]
LINKAGE_TYPES = ["phone", "address", "combined"]


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def linkage_count(row, linkage_type):
    phone = float(row.get("phone_shared_count") or 0)
    addr = float(row.get("addr_shared_count") or 0)
    if linkage_type == "phone":
        return phone
    if linkage_type == "address":
        return addr
    return max(phone, addr)  # combined: qualifies via either linkage


def qualifies(row, threshold, linkage_type):
    return linkage_count(row, linkage_type) >= threshold


def build_type_map(crosswalk_path):
    """Maps a facility's raw Specialty value to its base facility type."""
    rows = load_csv(crosswalk_path)
    return {r["Raw_Specialty"]: r["Base_Facility_Type"] for r in rows}


def facility_type(row, type_map):
    return type_map.get(row.get("Specialty", ""), row.get("Specialty", "UNKNOWN"))


def sweep(state_label, rows, type_map=None):
    """Yields detailed rows: state, threshold, linkage_type, county, facility_type, n, total, pct."""
    detailed = []

    def emit(county, ftype, subset):
        total = len(subset)
        if total == 0:
            return
        for threshold in THRESHOLDS:
            for linkage_type in LINKAGE_TYPES:
                n = sum(1 for r in subset if qualifies(r, threshold, linkage_type))
                detailed.append(
                    {
                        "state": state_label,
                        "threshold": threshold,
                        "linkage_type": linkage_type,
                        "county": county,
                        "facility_type": ftype,
                        "n_qualifying_facilities": n,
                        "n_total_facilities_in_stratum": total,
                        "pct_qualifying": round(100 * n / total, 1),
                    }
                )

    # Overview: all counties, all facility types
    emit("ALL", "ALL", rows)

    # By county (facility type pooled)
    counties = sorted({r["County"] for r in rows if r.get("County")})
    for county in counties:
        emit(county, "ALL", [r for r in rows if r["County"] == county])

    # By facility type (county pooled) - trivial for WA (single type), real for OR
    if type_map is not None:
        types = sorted({facility_type(r, type_map) for r in rows})
        for ftype in types:
            emit("ALL", ftype, [r for r in rows if facility_type(r, type_map) == ftype])
    else:
        emit("ALL", "AFH (single type)", rows)

    return detailed


def main():
    wa = load_csv(os.path.join(BASE, "anonymized_data/washington/WA_AFH_3County_Enriched_ANON.csv"))
    orr = load_csv(os.path.join(BASE, "anonymized_data/oregon/OR_Providers_Enriched_ANON.csv"))
    or_type_map = build_type_map(os.path.join(BASE, "anonymized_data/oregon/OR_Facility_Type_Crosswalk.csv"))

    detailed = []
    detailed += sweep("Washington", wa, type_map=None)
    detailed += sweep("Oregon", orr, type_map=or_type_map)

    detailed_path = os.path.join(BASE, "anonymized_data/sensitivity_analysis_detailed.csv")
    with open(detailed_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "state",
                "threshold",
                "linkage_type",
                "county",
                "facility_type",
                "n_qualifying_facilities",
                "n_total_facilities_in_stratum",
                "pct_qualifying",
            ],
        )
        writer.writeheader()
        writer.writerows(detailed)
    print(f"Wrote {len(detailed)} rows to {detailed_path}")

    # Manuscript-facing summary: decisive findings only.
    # (1) State-level phone-linkage sweep, all thresholds - the direct successor to
    #     Appendix A's original table, now generated for both states.
    # (2) Oregon facility-type breakdown at the calibrated threshold (3) and the
    #     recalibrated threshold (2), phone linkage - the population-validity finding.
    # (3) Phone-vs-address-vs-combined comparison at each state's headline threshold.
    summary_rows = []

    def find(state, threshold, linkage_type, county="ALL", ftype="ALL"):
        for r in detailed:
            if (
                r["state"] == state
                and r["threshold"] == threshold
                and r["linkage_type"] == linkage_type
                and r["county"] == county
                and r["facility_type"] == ftype
            ):
                return r
        return None

    summary_rows.append({"section": "State-level phone-linkage sweep (successor to Appendix A)"})
    for state in ["Washington", "Oregon"]:
        for threshold in THRESHOLDS:
            r = find(state, threshold, "phone")
            summary_rows.append(
                {
                    "section": "",
                    "state": state,
                    "threshold": threshold,
                    "linkage_type": "phone",
                    "n_qualifying_facilities": r["n_qualifying_facilities"],
                    "n_total_facilities_in_stratum": r["n_total_facilities_in_stratum"],
                    "pct_qualifying": r["pct_qualifying"],
                }
            )

    summary_rows.append({"section": "Oregon facility-type breakdown at threshold 2 vs 3 (phone linkage) - population-validity finding"})
    for ftype in sorted({facility_type(r, or_type_map) for r in orr}):
        for threshold in [2, 3]:
            r = find("Oregon", threshold, "phone", county="ALL", ftype=ftype)
            if r:
                summary_rows.append(
                    {
                        "section": "",
                        "state": "Oregon",
                        "threshold": threshold,
                        "linkage_type": "phone",
                        "facility_type": ftype,
                        "n_qualifying_facilities": r["n_qualifying_facilities"],
                        "n_total_facilities_in_stratum": r["n_total_facilities_in_stratum"],
                        "pct_qualifying": r["pct_qualifying"],
                    }
                )

    summary_rows.append({"section": "Linkage-type comparison at each state's calibrated threshold (WA=3, OR-recalibrated=2)"})
    for state, threshold in [("Washington", 3), ("Oregon", 2)]:
        for linkage_type in LINKAGE_TYPES:
            r = find(state, threshold, linkage_type)
            summary_rows.append(
                {
                    "section": "",
                    "state": state,
                    "threshold": threshold,
                    "linkage_type": linkage_type,
                    "n_qualifying_facilities": r["n_qualifying_facilities"],
                    "n_total_facilities_in_stratum": r["n_total_facilities_in_stratum"],
                    "pct_qualifying": r["pct_qualifying"],
                }
            )

    summary_path = os.path.join(BASE, "anonymized_data/sensitivity_analysis_summary.csv")
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


if __name__ == "__main__":
    main()
