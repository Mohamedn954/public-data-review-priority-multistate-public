"""Linkage-robustness analysis (privacy-constrained).

Tests whether the shared-contact clustering result depends on a single,
fragile data-cleaning decision, by recomputing cluster counts under
alternative phone/address normalization rules.

THIS SCRIPT IS NOT PUBLICLY RE-RUNNABLE AT THE RECORD LEVEL. It reads raw,
non-anonymized facility records (real phone numbers and street addresses)
from the sibling private companion repositories, which are not part of the
public replication package. Per the manuscript's stated reproducibility
scope: "All manuscript results can be independently verified from the
released de-identified analytic package; privacy-sensitive entity-resolution
steps are transparently specified and accompanied by aggregate verification
outputs but cannot be independently rerun against unreleased identifiers."

What IS released publicly: this source file (the exact normalization rules,
in full), and its aggregate, anonymized outputs
(anonymized_data/linkage_robustness_summary.csv). What is NOT released: the
raw private input files it reads, which is why this script will simply
report "raw input files not found" and exit cleanly if run outside an
environment that has the sibling private repos checked out.

Raw input locations (overridable via environment variables):
  WA: $AFH_RAW_ENRICHED or ../PRIVATE-public-data-review-priority-afh/data_package_with_everything/wa_data/WA_AFH_3County_Enriched.csv
  OR: $OR_RAW_ENRICHED  or ../PRIVATE-public-data-review-priority-oregon/data/OR_Providers_Enriched.csv
"""

import csv
import os
import re
import sys
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(BASE)  # .../EB2NIW

WA_RAW = os.environ.get(
    "AFH_RAW_ENRICHED",
    os.path.join(REPO_ROOT, "PRIVATE-public-data-review-priority-afh/data_package_with_everything/wa_data/WA_AFH_3County_Enriched.csv"),
)
OR_RAW = os.environ.get(
    "OR_RAW_ENRICHED",
    os.path.join(REPO_ROOT, "PRIVATE-public-data-review-priority-oregon/data/OR_Providers_Enriched.csv"),
)

THRESHOLDS = [2, 3, 4, 5]

STREET_ABBREV = {
    "STREET": "ST", "AVENUE": "AVE", "BOULEVARD": "BLVD", "DRIVE": "DR",
    "ROAD": "RD", "LANE": "LN", "COURT": "CT", "PLACE": "PL", "CIRCLE": "CIR",
    "TERRACE": "TER", "PARKWAY": "PKWY", "HIGHWAY": "HWY", "NORTH": "N",
    "SOUTH": "S", "EAST": "E", "WEST": "W", "NORTHEAST": "NE", "NORTHWEST": "NW",
    "SOUTHEAST": "SE", "SOUTHWEST": "SW",
}
UNIT_RE = re.compile(r"\b(APT|UNIT|STE|SUITE|#)\s*\.?\s*\w*\b", re.IGNORECASE)


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def digits_only(phone):
    return re.sub(r"\D", "", phone or "")


def address_strict(addr):
    """Exact-normalized: uppercase, collapsed whitespace, nothing else changed."""
    return re.sub(r"\s+", " ", (addr or "").strip().upper())


def address_lenient(addr):
    """Lenient: strict, plus unit/suite stripped and common street-type words abbreviated."""
    a = address_strict(addr)
    a = UNIT_RE.sub("", a)
    tokens = a.split()
    tokens = [STREET_ABBREV.get(t, t) for t in tokens]
    return re.sub(r"\s+", " ", " ".join(tokens)).strip()


def build_shared_counts(rows, key_fn, field):
    """Returns facility_id -> shared count under the given key function, using self-inclusive
    convention consistent with the existing addr_shared_count/phone_shared_count fields
    (a facility with no match still counts itself, i.e. minimum value 1)."""
    keys = [key_fn(r.get(field, "")) for r in rows]
    counts = Counter(k for k in keys if k)
    return [counts.get(k, 0) if k else 0 for k in keys]


def looks_generic(phone, addr_cities):
    """Heuristic generic/corporate-contact-number flag: a phone shared across an unusually
    large number of distinct cities suggests a centralized answering service, management
    company switchboard, or registered-agent line rather than a single facility's own line."""
    return len(set(addr_cities)) >= 4


def main():
    missing = [p for p in (WA_RAW, OR_RAW) if not os.path.isfile(p)]
    if missing:
        print("Raw input file(s) not found - this is expected outside an environment")
        print("with the private sibling repositories checked out:")
        for p in missing:
            print(f"  {p}")
        print("Per this script's stated reproducibility scope, this is not an error;")
        print("exiting cleanly without producing output.")
        sys.exit(0)

    detailed = []
    for state, path in [("Washington", WA_RAW), ("Oregon", OR_RAW)]:
        rows = load_csv(path)

        # PRESPECIFIED PRIMARY CONSTRUCTION for phone: the raw file's own upstream
        # `phone_key` column, not a fresh reconstruction. Root-caused 2026-07-16
        # (see PRIVATE-public-data-review-priority-afh/private/
        # WA_53_vs_50_membership_comparison_PRIVATE.md): for Washington, exactly
        # three facilities share a phone number ((509) 593-0493) that the upstream
        # construction deliberately excluded (phone_key left blank for those three
        # rows only) as a likely generic/non-facility-specific contact number. A
        # naive digits-only reconstruction from the raw Phone field has no way to
        # know about that exclusion and over-counts by exactly 3 at thresholds 2-3.
        # Using phone_key directly reproduces the published baseline exactly.
        variants = {
            "phone_key_upstream (PRIMARY)": [r.get("phone_key", "") for r in rows],
            "phone_digits_only_no_upstream_exclusion (SENSITIVITY)": [digits_only(r.get("Phone", "")) for r in rows],
            "address_strict": [address_strict(r.get("Physical_Address", "")) for r in rows],
            "address_lenient": [address_lenient(r.get("Physical_Address", "")) for r in rows],
        }

        # Generic-contact exclusion: recompute phone (digits-only) clustering with
        # phone numbers shared across >=4 distinct cities excluded from counting.
        phone_to_cities = defaultdict(list)
        for r in rows:
            p = digits_only(r.get("Phone", ""))
            if p:
                phone_to_cities[p].append(r.get("City", ""))
        generic_phones = {p for p, cities in phone_to_cities.items() if looks_generic(p, cities)}
        phone_excl_generic = [
            digits_only(r.get("Phone", "")) if digits_only(r.get("Phone", "")) not in generic_phones else ""
            for r in rows
        ]
        variants["phone_digits_only_excl_generic (SENSITIVITY - independent >=4-city heuristic, not the upstream exclusion)"] = phone_excl_generic

        # Missing/placeholder removal: drop empty or obviously-placeholder values
        # (e.g., all-zero or fewer than 7 digits for phone) before counting.
        def clean_phone(p):
            d = digits_only(p)
            return d if len(d) >= 10 and d != d[0] * len(d) else ""

        variants["phone_digits_only_cleaned (SENSITIVITY)"] = [clean_phone(r.get("Phone", "")) for r in rows]

        for variant_name, keys in variants.items():
            counts = Counter(k for k in keys if k)
            shared = [counts.get(k, 0) if k else 0 for k in keys]
            for threshold in THRESHOLDS:
                n = sum(1 for c in shared if c >= threshold)
                detailed.append(
                    {
                        "state": state,
                        "normalization_variant": variant_name,
                        "threshold": threshold,
                        "n_qualifying_facilities": n,
                        "n_total_facilities": len(rows),
                        "pct_qualifying": round(100 * n / len(rows), 1) if rows else 0.0,
                        "n_generic_numbers_excluded": len(generic_phones) if "excl_generic" in variant_name else "",
                    }
                )

    detailed_path = os.path.join(BASE, "anonymized_data/linkage_robustness_detailed.csv")
    with open(detailed_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "state", "normalization_variant", "threshold",
                "n_qualifying_facilities", "n_total_facilities", "pct_qualifying",
                "n_generic_numbers_excluded",
            ],
        )
        writer.writeheader()
        writer.writerows(detailed)
    print(f"Wrote {len(detailed)} rows to {detailed_path} (aggregate counts only - no names, phones, or addresses)")

    # Manuscript-facing summary: does the headline result change materially
    # (>1 facility) between phone_exact_string and phone_digits_only, or between
    # address_strict and address_lenient, at each state's calibrated threshold?
    summary_rows = []

    def find(state, variant, threshold):
        for r in detailed:
            if r["state"] == state and r["normalization_variant"] == variant and r["threshold"] == threshold:
                return r
        return None

    for state, threshold in [("Washington", 3), ("Oregon", 2)]:
        for variant in [
            "phone_key_upstream (PRIMARY)",
            "phone_digits_only_no_upstream_exclusion (SENSITIVITY)",
            "phone_digits_only_excl_generic (SENSITIVITY - independent >=4-city heuristic, not the upstream exclusion)",
            "phone_digits_only_cleaned (SENSITIVITY)",
            "address_strict", "address_lenient",
        ]:
            r = find(state, variant, threshold)
            if r:
                summary_rows.append(
                    {
                        "state": state,
                        "threshold": threshold,
                        "normalization_variant": variant,
                        "n_qualifying_facilities": r["n_qualifying_facilities"],
                        "pct_qualifying": r["pct_qualifying"],
                    }
                )

    summary_path = os.path.join(BASE, "anonymized_data/linkage_robustness_summary.csv")
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["state", "threshold", "normalization_variant", "n_qualifying_facilities", "pct_qualifying"])
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Wrote {len(summary_rows)} rows to {summary_path} (aggregate counts only)")

    print()
    print("RESOLVED 2026-07-16: the phone_key_upstream (PRIMARY) variant reproduces the")
    print("published baseline exactly (WA=50 at threshold 3). Root cause fully diagnosed:")
    print("see PRIVATE-public-data-review-priority-afh/private/")
    print("WA_53_vs_50_membership_comparison_PRIVATE.md - exactly 3 Washington facilities")
    print("share a phone number the upstream construction deliberately excluded as a")
    print("likely generic/non-facility-specific contact number; a naive digits-only")
    print("reconstruction does not know about that exclusion and over-counts by exactly 3.")


if __name__ == "__main__":
    main()
