"""Public-record observability analysis.

Generalizes the manuscript's existing single Washington figure (the 37.2%
no-public-record rate) into a multi-dimensional observability table for both
states: what proportion of facilities have any public record at all,
inspection records, investigation/complaint records, enforcement records,
usable access dates, and a documented multi-year presence - all computed
from fields already in this repository's own anonymized_data/, no new data
required.

Outputs:
  anonymized_data/observability_analysis_detailed.csv   (appendix-ready, per-state dimension table)
  anonymized_data/observability_analysis_summary.csv    (manuscript-facing, decisive findings only)
"""

import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def pct(n, total):
    return round(100 * n / total, 1) if total else 0.0


def has_public_reports(row):
    # Has_Public_Reports is not populated in the anonymized enriched files
    # (empty for every row in both states' _ANON.csv). The manuscript's
    # existing 37.2% WA figure (Appendix F) is computed from n_docs_total==0,
    # so that is the field this script uses too, for consistency with
    # already-published numbers rather than a different, untested field.
    return int_field(row, "n_docs_total") > 0


def int_field(row, key):
    try:
        return int(float(row.get(key) or 0))
    except ValueError:
        return 0


def dimension_rows(state, enriched, reports_by_id):
    total = len(enriched)
    rows = []

    def emit(label, n):
        rows.append(
            {
                "state": state,
                "dimension": label,
                "n_facilities": n,
                "n_total": total,
                "pct": pct(n, total),
            }
        )

    n_any_record = sum(1 for r in enriched if has_public_reports(r))
    emit("Any public record (Has_Public_Reports)", n_any_record)

    n_inspections = sum(1 for r in enriched if int_field(r, "n_inspections") > 0)
    emit("Has inspection record(s)", n_inspections)

    n_investigations = sum(1 for r in enriched if int_field(r, "n_investigations") > 0)
    emit("Has complaint/investigation record(s)", n_investigations)

    n_enforcement = sum(1 for r in enriched if int_field(r, "n_enforcement") > 0)
    emit("Has enforcement record(s)", n_enforcement)

    n_civil_fines = sum(1 for r in enriched if int_field(r, "n_civil_fines") > 0)
    emit("Has civil-fine record(s)", n_civil_fines)

    n_usable_date = sum(1 for r in enriched if (r.get("DateAccessed") or "").strip())
    emit("Has a usable access date", n_usable_date)

    n_latest_year = sum(1 for r in enriched if (r.get("latest_year") or "").strip())
    emit("Has a usable latest-activity year", n_latest_year)

    # Record-window: multi-year presence, from the companion Reports file where available
    multi_year = 0
    checked = 0
    for r in enriched:
        rep = reports_by_id.get(r["facility_id"])
        if rep is None:
            continue
        checked += 1
        years_present = (rep.get("years_present") or "").strip()
        # years_present is stored as a delimited list or count depending on source; count entries if delimited
        if years_present and len(years_present.replace(" ", "").split(";")) > 1 or years_present.replace(" ", "").isdigit() and int(years_present) > 1:
            multi_year += 1
    if checked:
        rows.append(
            {
                "state": state,
                "dimension": "Has a multi-year documented record window",
                "n_facilities": multi_year,
                "n_total": checked,
                "pct": pct(multi_year, checked),
            }
        )

    return rows


def main():
    wa = load_csv(os.path.join(BASE, "anonymized_data/washington/WA_AFH_3County_Enriched_ANON.csv"))
    orr = load_csv(os.path.join(BASE, "anonymized_data/oregon/OR_Providers_Enriched_ANON.csv"))
    wa_reports = load_csv(os.path.join(BASE, "anonymized_data/washington/WA_AFH_3County_Reports_ANON.csv"))
    or_reports = load_csv(os.path.join(BASE, "anonymized_data/oregon/OR_Reports_ANON.csv"))

    wa_reports_by_id = {r["facility_id"]: r for r in wa_reports}
    or_reports_by_id = {r["facility_id"]: r for r in or_reports}

    detailed = []
    detailed += dimension_rows("Washington", wa, wa_reports_by_id)
    detailed += dimension_rows("Oregon", orr, or_reports_by_id)

    detailed_path = os.path.join(BASE, "anonymized_data/observability_analysis_detailed.csv")
    with open(detailed_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["state", "dimension", "n_facilities", "n_total", "pct"])
        writer.writeheader()
        writer.writerows(detailed)
    print(f"Wrote {len(detailed)} rows to {detailed_path}")

    # Manuscript-facing summary: the headline "no public record" figure for both
    # states (generalizing the existing WA-only 37.2% figure), plus the
    # inspection/investigation/enforcement observability gap.
    summary_rows = []
    for state, enriched in [("Washington", wa), ("Oregon", orr)]:
        total = len(enriched)
        n_no_record = sum(1 for r in enriched if not has_public_reports(r))
        summary_rows.append(
            {
                "metric": "No public record at all (external analyst cannot observe this facility)",
                "state": state,
                "n_facilities": n_no_record,
                "n_total": total,
                "pct": pct(n_no_record, total),
            }
        )

    for row in detailed:
        if row["dimension"] in (
            "Has inspection record(s)",
            "Has complaint/investigation record(s)",
            "Has enforcement record(s)",
        ):
            summary_rows.append(
                {
                    "metric": row["dimension"],
                    "state": row["state"],
                    "n_facilities": row["n_facilities"],
                    "n_total": row["n_total"],
                    "pct": row["pct"],
                }
            )

    summary_path = os.path.join(BASE, "anonymized_data/observability_analysis_summary.csv")
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "state", "n_facilities", "n_total", "pct"])
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Wrote {len(summary_rows)} rows to {summary_path}")


if __name__ == "__main__":
    main()
