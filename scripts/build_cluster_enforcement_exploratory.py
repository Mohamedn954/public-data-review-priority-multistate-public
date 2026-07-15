"""Exploratory analysis: does public enforcement/investigation prevalence differ
between facilities in a shared-contact cluster and facilities not in one?

This is NOT a predictive-validity test and is not presented as one anywhere in
this manuscript (Section 2.6 states predictive validity as untested throughout).
Shared-contact clustering is designed and reported as an entity-resolution proxy
for concealed-ownership concern (RF-08), not a fraud predictor. This script asks
a narrower, descriptive question: do clustered facilities show a different
observed public-oversight history than nonclustered facilities, once the
confound this manuscript's own population-validity finding (Section 3.4)
already identified is accounted for -- county in Washington, facility type in
Oregon?

Method: 2x2 tables (clustered vs. not) x (has >=1 enforcement action / has >=1
investigation) computed both crude and Mantel-Haenszel-adjusted (stratified by
County for Washington, Base_Facility_Type for Oregon). Reports, for every
comparison: exact stratum-level 2x2 denominators, absolute risk difference with
a 95% CI, risk ratio with a 95% CI, and odds ratio with a 95% CI. Every
comparison is run twice: once on the full population, and once restricted to
facilities with n_docs_total > 0 (excluding facilities with no observable
public record at all, since a facility with zero documents cannot by
definition show a positive outcome and could otherwise bias the crude
comparison mechanically rather than substantively).

Every association is reported regardless of direction (positive, null, or
reversed) -- this script does not search for a particular finding and applies
identical logic to both states and both outcomes.

Outputs:
  anonymized_data/cluster_enforcement_exploratory_detailed.csv  (every stratum, every comparison)
  anonymized_data/cluster_enforcement_exploratory_summary.csv   (crude + MH-adjusted summary rows only)
"""

import csv
import math
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Z = 1.959963984540054  # 95% two-sided standard normal critical value


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def is_clustered(row):
    return bool((row.get("cluster_id") or "").strip())


def has_event(row, field):
    val = row.get(field)
    try:
        return int(val or 0) >= 1
    except ValueError:
        return False


def has_public_record(row):
    try:
        return int(row.get("n_docs_total") or 0) > 0
    except ValueError:
        return False


def two_by_two(rows, event_field):
    """a=clustered+event, b=clustered+no event, c=nonclustered+event, d=nonclustered+no event."""
    a = b = c = d = 0
    for r in rows:
        clustered = is_clustered(r)
        event = has_event(r, event_field)
        if clustered and event:
            a += 1
        elif clustered and not event:
            b += 1
        elif not clustered and event:
            c += 1
        else:
            d += 1
    return a, b, c, d


def risk_difference(a, b, c, d):
    n1, n0 = a + b, c + d
    if n1 == 0 or n0 == 0:
        return None
    p1, p0 = a / n1, c / n0
    rd = p1 - p0
    se = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    return {"estimate": rd, "lo": rd - Z * se, "hi": rd + Z * se, "p1": p1, "p0": p0, "n1": n1, "n0": n0}


def risk_ratio(a, b, c, d):
    n1, n0 = a + b, c + d
    if a == 0 or c == 0 or n1 == 0 or n0 == 0:
        return None
    rr = (a / n1) / (c / n0)
    se_log = math.sqrt(1 / a - 1 / n1 + 1 / c - 1 / n0)
    log_rr = math.log(rr)
    return {"estimate": rr, "lo": math.exp(log_rr - Z * se_log), "hi": math.exp(log_rr + Z * se_log)}


def odds_ratio(a, b, c, d):
    if a == 0 or b == 0 or c == 0 or d == 0:
        return None
    orr = (a * d) / (b * c)
    se_log = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    log_or = math.log(orr)
    return {"estimate": orr, "lo": math.exp(log_or - Z * se_log), "hi": math.exp(log_or + Z * se_log)}


def mh_odds_ratio(tables):
    """Mantel-Haenszel-adjusted OR with Robins-Breslow-Greenland (1986) variance."""
    tables = [(a, b, c, d) for (a, b, c, d) in tables if (a + b + c + d) > 0]
    if not tables:
        return None
    R = [a * d / (a + b + c + d) for (a, b, c, d) in tables]
    S = [b * c / (a + b + c + d) for (a, b, c, d) in tables]
    sum_R, sum_S = sum(R), sum(S)
    if sum_S == 0:
        return None
    orr_mh = sum_R / sum_S
    P = [(a + d) / (a + b + c + d) for (a, b, c, d) in tables]
    Q = [(b + c) / (a + b + c + d) for (a, b, c, d) in tables]
    term1 = sum(p * r for p, r in zip(P, R)) / (2 * sum_R ** 2)
    term2 = sum(p * s + q * r for p, s, q, r in zip(P, S, Q, R)) / (2 * sum_R * sum_S)
    term3 = sum(q * s for q, s in zip(Q, S)) / (2 * sum_S ** 2)
    var_log = term1 + term2 + term3
    if var_log <= 0:
        return {"estimate": orr_mh, "lo": None, "hi": None, "n_strata": len(tables)}
    se_log = math.sqrt(var_log)
    log_or = math.log(orr_mh)
    return {"estimate": orr_mh, "lo": math.exp(log_or - Z * se_log), "hi": math.exp(log_or + Z * se_log), "n_strata": len(tables)}


def mh_risk_ratio(tables):
    """Mantel-Haenszel-adjusted RR with Greenland-Robins (1985) variance."""
    tables = [(a, b, c, d) for (a, b, c, d) in tables if (a + b + c + d) > 0]
    if not tables:
        return None
    num = sum(a * (c + d) / (a + b + c + d) for (a, b, c, d) in tables)
    den = sum(c * (a + b) / (a + b + c + d) for (a, b, c, d) in tables)
    if den == 0:
        return None
    rr_mh = num / den
    var_num = 0.0
    for (a, b, c, d) in tables:
        n = a + b + c + d
        n1, n0 = a + b, c + d
        var_num += (n1 * n0 * (a + c) - a * c * n) / (n ** 2)
    denom_a = sum(a * n0 / (a + b + c + d) for (a, b, c, d) in tables for n0 in [c + d])
    denom_c = sum(c * n1 / (a + b + c + d) for (a, b, c, d) in tables for n1 in [a + b])
    if denom_a == 0 or denom_c == 0:
        return {"estimate": rr_mh, "lo": None, "hi": None, "n_strata": len(tables)}
    var_log = var_num / (denom_a * denom_c)
    if var_log <= 0:
        return {"estimate": rr_mh, "lo": None, "hi": None, "n_strata": len(tables)}
    se_log = math.sqrt(var_log)
    log_rr = math.log(rr_mh)
    return {"estimate": rr_mh, "lo": math.exp(log_rr - Z * se_log), "hi": math.exp(log_rr + Z * se_log), "n_strata": len(tables)}


def fmt(x, nd=3):
    return "NA" if x is None else round(x, nd)


def run_comparison(rows, strata_field, state_label, event_field, record_filter_label, detailed_out, summary_out):
    a, b, c, d = two_by_two(rows, event_field)
    n_clustered, n_nonclustered = a + b, c + d
    rd = risk_difference(a, b, c, d)
    rr = risk_ratio(a, b, c, d)
    orr = odds_ratio(a, b, c, d)

    detailed_out.append({
        "state": state_label, "outcome": event_field, "record_filter": record_filter_label,
        "stratum": "CRUDE (all strata pooled)", "a_clustered_event": a, "b_clustered_noevent": b,
        "c_nonclustered_event": c, "d_nonclustered_noevent": d, "n_clustered": n_clustered, "n_nonclustered": n_nonclustered,
    })

    strata_values = sorted({r.get(strata_field, "") for r in rows if r.get(strata_field)})
    stratum_tables = []
    for stratum in strata_values:
        stratum_rows = [r for r in rows if r.get(strata_field) == stratum]
        sa, sb, sc, sd = two_by_two(stratum_rows, event_field)
        stratum_tables.append((sa, sb, sc, sd))
        detailed_out.append({
            "state": state_label, "outcome": event_field, "record_filter": record_filter_label,
            "stratum": stratum, "a_clustered_event": sa, "b_clustered_noevent": sb,
            "c_nonclustered_event": sc, "d_nonclustered_noevent": sd, "n_clustered": sa + sb, "n_nonclustered": sc + sd,
        })

    mh_or = mh_odds_ratio(stratum_tables)
    mh_rr = mh_risk_ratio(stratum_tables)

    summary_out.append({
        "state": state_label, "outcome": event_field, "record_filter": record_filter_label,
        "adjustment": strata_field,
        "n_clustered": n_clustered, "n_nonclustered": n_nonclustered,
        "pct_clustered_with_event": fmt(100 * a / n_clustered, 1) if n_clustered else "NA",
        "pct_nonclustered_with_event": fmt(100 * c / n_nonclustered, 1) if n_nonclustered else "NA",
        "crude_risk_difference": fmt(rd["estimate"]) if rd else "NA",
        "crude_rd_95ci_lo": fmt(rd["lo"]) if rd else "NA",
        "crude_rd_95ci_hi": fmt(rd["hi"]) if rd else "NA",
        "crude_risk_ratio": fmt(rr["estimate"]) if rr else "NA (zero cell)",
        "crude_rr_95ci_lo": fmt(rr["lo"]) if rr else "NA",
        "crude_rr_95ci_hi": fmt(rr["hi"]) if rr else "NA",
        "crude_odds_ratio": fmt(orr["estimate"]) if orr else "NA (zero cell)",
        "crude_or_95ci_lo": fmt(orr["lo"]) if orr else "NA",
        "crude_or_95ci_hi": fmt(orr["hi"]) if orr else "NA",
        "mh_adjusted_risk_ratio": fmt(mh_rr["estimate"]) if mh_rr else "NA",
        "mh_rr_95ci_lo": fmt(mh_rr["lo"]) if mh_rr and mh_rr.get("lo") else "NA",
        "mh_rr_95ci_hi": fmt(mh_rr["hi"]) if mh_rr and mh_rr.get("hi") else "NA",
        "mh_adjusted_odds_ratio": fmt(mh_or["estimate"]) if mh_or else "NA",
        "mh_or_95ci_lo": fmt(mh_or["lo"]) if mh_or and mh_or.get("lo") else "NA",
        "mh_or_95ci_hi": fmt(mh_or["hi"]) if mh_or and mh_or.get("hi") else "NA",
        "n_strata": mh_or["n_strata"] if mh_or else len(strata_values),
    })


def main():
    wa = load_csv(os.path.join(BASE, "anonymized_data/washington/WA_AFH_3County_Enriched_ANON.csv"))
    orr_raw = load_csv(os.path.join(BASE, "anonymized_data/oregon/OR_Providers_Enriched_ANON.csv"))
    crosswalk = load_csv(os.path.join(BASE, "anonymized_data/oregon/OR_Facility_Type_Crosswalk.csv"))
    specialty_to_type = {r["Raw_Specialty"]: r["Base_Facility_Type"] for r in crosswalk}
    for r in orr_raw:
        r["Base_Facility_Type"] = specialty_to_type.get(r.get("Specialty", ""), "Unknown")

    detailed, summary = [], []

    for record_filter_label, wa_rows, or_rows in [
        ("All facilities", wa, orr_raw),
        ("Excl. facilities with no public record (n_docs_total>0)",
         [r for r in wa if has_public_record(r)], [r for r in orr_raw if has_public_record(r)]),
    ]:
        for outcome in ("n_enforcement", "n_investigations"):
            run_comparison(wa_rows, "County", "Washington", outcome, record_filter_label, detailed, summary)
            run_comparison(or_rows, "Base_Facility_Type", "Oregon", outcome, record_filter_label, detailed, summary)

    detailed_path = os.path.join(BASE, "anonymized_data/cluster_enforcement_exploratory_detailed.csv")
    summary_path = os.path.join(BASE, "anonymized_data/cluster_enforcement_exploratory_summary.csv")

    with open(detailed_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(detailed[0].keys()))
        w.writeheader()
        w.writerows(detailed)

    with open(summary_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    print(f"wrote {detailed_path} ({len(detailed)} rows)")
    print(f"wrote {summary_path} ({len(summary)} rows)")
    print()
    print("=== Summary (MH-adjusted) ===")
    for row in summary:
        print(f"{row['state']:12s} {row['outcome']:16s} {row['record_filter'][:40]:40s} "
              f"MH-RR={row['mh_adjusted_risk_ratio']} ({row['mh_rr_95ci_lo']}-{row['mh_rr_95ci_hi']})  "
              f"MH-OR={row['mh_adjusted_odds_ratio']} ({row['mh_or_95ci_lo']}-{row['mh_or_95ci_hi']})")


if __name__ == "__main__":
    main()
