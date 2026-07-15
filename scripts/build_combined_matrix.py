"""Rebuilds anonymized_data/combined_evidence_matrix.csv from the Washington
and Oregon per-indicator evidentiary status columns already reported in
Appendix B.

The Combined_Status column is not derived from the WA/OR status labels alone
(labels like "Testable" describe whether public data could in principle
support an indicator, not whether this study actually computed or assessed
it). Instead, each row's category is audited directly against the
underlying Status_Notes (WA_RedFlag_Testability_Matrix_v2.csv) and Basis
(OR_RF_Evidence_Matrix.csv) text describing what was actually done, then
mapped to the stronger of the two states' audited categories. The audit
rationale for every row is recorded below so the mapping is checkable, not
asserted.
"""

import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "anonymized_data", "combined_evidence_matrix.csv")

CANONICAL_ORDER = [
    "Directly Operationalized",
    "System-Level Evidence",
    "Case-Level Evidence",
    "Partially Operationalized",
    "Contextually Assessed",
    "Publicly Testable, Not Completed",
    "Internal Data Required",
    "Not Established",
]
RANK = {name: i for i, name in enumerate(CANONICAL_ORDER)}

# RF_ID, Indicator, WA_Status (label), OR_Status (label), WA_Category (audited),
# OR_Category (audited), audit rationale.
ROWS = [
    ("RF-01", "Rapid provider/facility growth", "Testable (program/sector level)", "Publicly Testable, Not Completed",
     "Publicly Testable, Not Completed", "Publicly Testable, Not Completed",
     "WA notes: license-date field is testable over time, but this study's snapshot shows the current roster only; no growth series was constructed in either state."),
    ("RF-02", "Spending growth disconnected from beneficiary growth", "Testable (program level)", "Contextually Assessed",
     "Partially Operationalized", "Contextually Assessed",
     "WA reported an actual program-level spending-growth figure ($3.8B to $13.07B); Oregon had only statewide contextual figures, no facility- or county-level series in either state."),
    ("RF-03", "Multi-entity/multi-facility operator concentration", "Partially Testable", "Partially Operationalized",
     "Partially Operationalized", "Partially Operationalized",
     "Both states computed a shared-contact proxy for operator concentration; neither independently corroborated common operational control, the underlying construct."),
    ("RF-04", "Geographic concentration or out-of-state operator", "Partially Testable", "Publicly Testable, Not Completed",
     "Publicly Testable, Not Completed", "Publicly Testable, Not Completed",
     "WA notes this is not bulk-computable from the public interface (sample/manual only); Oregon's registry cross-check exists but was not performed. Neither state completed it."),
    ("RF-05", "Incomplete administrative or enrollment data", "Not Publicly Testable", "Partially Operationalized",
     "Internal Data Required", "Partially Operationalized",
     "WA's confidential enrollment-file completeness is internal-data-only; Oregon directly measured its own public-record field completeness (zero unexplained nulls)."),
    ("RF-06", "Excluded party involvement or linkage gap", "Partially Testable", "Publicly Testable, Not Completed",
     "Partially Operationalized", "Publicly Testable, Not Completed",
     "WA's exclusion-list cross-match was executed but remained inconclusive because facility and licensee names could not be linked reliably; Oregon's cross-match was not attempted."),
    ("RF-07", "Concealed or opaque ownership / related-party control", "Partially Testable", "Publicly Testable, Not Completed",
     "Publicly Testable, Not Completed", "Publicly Testable, Not Completed",
     "WA notes assessor-based cross-matching is manual and records-intensive and was not performed at scale; Oregon's ownership cross-check was not performed either."),
    ("RF-08", "Shared address, phone, or network (network-cluster threshold)", "Testable (proxy)", "Operationalized; recalibration required",
     "Directly Operationalized", "Directly Operationalized",
     "Both states directly computed shared-contact clusters at facility level across the full roster (72 WA clusters; 792 OR facilities screened)."),
    ("RF-09", "Phantom, mailbox, or questionable address", "Partially Testable", "Contextually Assessed",
     "Contextually Assessed", "Contextually Assessed",
     "WA notes the Adult Family Home model structurally limits this risk and the indicator was not computed for AFHs; Oregon reached the same structural conclusion contextually."),
    ("RF-10", "Impossible hours or overlapping services", "Not Publicly Testable", "Internal Data Required",
     "Internal Data Required", "Internal Data Required", "Requires claims data in both states."),
    ("RF-11", "Maximum-unit or implausible service-volume billing", "Not Publicly Testable", "Internal Data Required",
     "Internal Data Required", "Internal Data Required", "Requires claims data in both states."),
    ("RF-12", "Out-of-state or impossible-location billing", "Not Publicly Testable", "Case Supported",
     "Internal Data Required", "Case-Level Evidence",
     "Not publicly testable prospectively in Washington; established after the fact by an Oregon DOJ guilty plea and sentencing."),
    ("RF-13", "Billing after death, absence, discharge, or ineligibility", "Not Publicly Testable", "Internal Data Required",
     "Internal Data Required", "Internal Data Required", "Requires claims data in both states; no matter in either state's record establishes this construct."),
    ("RF-14", "Cloned, missing, or fabricated documentation", "Not Publicly Testable", "Case Supported",
     "Internal Data Required", "Case-Level Evidence",
     "Not systematically extracted from Washington's 586 investigation narratives in this study; established, at the allegation stage, by a pending Oregon federal indictment."),
    ("RF-15", "Stolen credentials or unauthorized professional IDs", "Not Publicly Testable", "Not Established",
     "Internal Data Required", "Not Established", "No dataset field in Washington; no Oregon case or public source identified."),
    ("RF-16", "Frontline referrals not acted upon or poorly triaged", "Partially Testable", "System Supported",
     "Contextually Assessed", "System-Level Evidence",
     "WA notes this is documented only qualitatively in SAO audits, not computed from a facility-level field; Oregon's SOQ evaluations document a system-level complaint-backlog finding directly."),
    ("RF-17", "Payment holds, restrictions, suspensions, enhanced oversight, sanctions, exclusions, or enforcement history", "Partially Testable", "Partially Operationalized",
     "Directly Operationalized", "Partially Operationalized",
     "WA's sanction/enforcement component was fully computed at facility level (165 facilities with enforcement, 18 stop-placements, reported in Section 3.1); Oregon computed regulatory-action and civil-fine counts but did not incorporate enhanced-oversight designations or the exclusion-list cross-match."),
    ("RF-18", "Reactive oversight and insufficient capacity", "Fully Testable", "System Supported",
     "System-Level Evidence", "System-Level Evidence",
     "Documented in both states by a state or federal audit/evaluation (Washington's SAO and HHS-OIG audits; Oregon's SOQ evaluations), not by a facility-level roster computation."),
    ("RF-19", "Program design vulnerability", "Testable (qualitative)", "Contextually Assessed",
     "Contextually Assessed", "Contextually Assessed",
     "Assessed via statutory/rule analysis in both states, not systematically operationalized from a data field."),
    ("RF-20", "Unresolved audit findings or weak corrective-action follow-through", "Fully Testable", "System Supported",
     "System-Level Evidence", "System-Level Evidence",
     "Documented in both states by an audit follow-up series (Washington's SAO recurring audits; Oregon's two-stage SOQ evaluation), not by a facility-level roster computation."),
]


def combined_status(wa_cat: str, or_cat: str) -> str:
    return wa_cat if RANK[wa_cat] <= RANK[or_cat] else or_cat


# Display-only refinement: RF-15 is Internal Data Required in Washington and
# Not Established in Oregon, two distinct weakest-tier conclusions rather
# than one. The combined category used for counting is still "Internal Data
# Required" (RANK's weakest-or-tied choice), but the printed label names
# both conclusions for clarity. This does not change any count.
DISPLAY_OVERRIDE = {"RF-15": "Internal Data Required; Not Established"}


def main():
    with open(OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["RF_ID", "Indicator", "WA_Status", "OR_Status", "Combined_Status"])
        for rf_id, indicator, wa_status, or_status, wa_cat, or_cat, _rationale in ROWS:
            label = DISPLAY_OVERRIDE.get(rf_id, combined_status(wa_cat, or_cat))
            writer.writerow([rf_id, indicator, wa_status, or_status, label])
    counts = {}
    for _, _, _, _, wa_cat, or_cat, _ in ROWS:
        c = combined_status(wa_cat, or_cat)
        counts[c] = counts.get(c, 0) + 1
    print(f"saved {OUT}")
    for cat in CANONICAL_ORDER:
        if cat in counts:
            print(f"  {cat}: {counts[cat]}")


if __name__ == "__main__":
    main()
