# Transparent Public-Data Prioritization for Medicaid Long-Term-Care Oversight: Evidence From Two States

This is the self-contained replication package for the manuscript *"Transparent Public-Data Prioritization for Medicaid Long-Term-Care Oversight: Evidence From Two States"* (Mohamed Noor Hussein), prepared for submission to Health Affairs Scholar.

This manuscript tests one narrow claim: a disclosed public-data method can provide a reproducible first layer of Medicaid long-term-care review prioritization, but its constructs, measurements, and thresholds must be evaluated separately and recalibrated across regulatory settings. It reports four things in sequence: (1) what was derived — an initial 20-indicator taxonomy generated from two Minnesota documentary lineages (the Office of the Legislative Auditor's 2009 and 2017 evaluations, and a May 2026 Minnesota health-care-fraud federal enforcement action), each indicator's anchor support disclosed rather than presumed uniform; (2) what was independently corroborated — a prespecified, dated external search testing whether each indicator recurs in authoritative federal and state records outside its Minnesota source; (3) what was operationalized — indicators measured in Washington's Adult Family Homes (n = 3,457) and Oregon's four licensed long-term-care types (n = 792); and (4) what was learned from cross-state transfer — the measurement pipeline reproduced technically in Oregon, but the same rule produced a different result across a differently composed population, a population-validity finding distinct from a threshold-calibration finding. All results are evaluated across six explicit validity dimensions: source, content, measurement, population, threshold, and predictive — predictive validity is stated as untested throughout.

## Relationship to the companion studies

This draws directly on one prior working paper, *A Public-Data Review-Priority Framework for Medicaid Residential Care Oversight: Evidence from Washington State Adult Family Homes* (Hussein, 2026a), posted on SSRN. The Oregon cross-state transfer analysis is reported here directly, citing its own primary sources; it does not depend on a separate Oregon manuscript being posted to SSRN. Every Oregon fact this manuscript relies on is cited to its own primary source (Oregon DOJ and U.S. Attorney press releases, Oregon DHS's state-commissioned evaluations, the Oregon licensing portal) or is independently reproducible from this repository's own data via `scripts/verify_multistate_numbers.py`. A fuller, non-peer-reviewed companion account of the Oregon analysis is maintained separately at [`public-data-review-priority-oregon-public`](https://github.com/Mohamedn954/public-data-review-priority-oregon-public), but this manuscript does not depend on it.

## What's included

- `Hussein_Multistate_Manuscript.md` / `.docx` / `.pdf` — the manuscript (working-paper version, with the preprint disclosure in the Author Note), structured under Health Affairs Scholar's required Research Article headings, with three figures and one main-text table.
- `Hussein_Multistate_Manuscript_Supplementary.md` / `.docx` / `.pdf` — eight supplementary appendices (A–H), submitted alongside the manuscript as Supplementary Material. Holds the full RF specification registry, the federal/external corroboration crosswalk, and the fuller evidentiary and methodological detail the main text summarizes but does not have room for.
- `anonymized_data/washington/` — Washington's de-identified facility-level data, copied unmodified from the companion Washington repository.
- `anonymized_data/oregon/` — Oregon's de-identified facility-level data, copied unmodified from the companion Oregon repository, plus `A5_OR_Cluster_Corroboration_ANON.csv` (new to this repository — Oregon's 49-cluster shared-contact corroboration classification; see reproducibility tiers below).
- `anonymized_data/combined_evidence_matrix.csv` — each of the 20 original indicators' Washington and Oregon evidentiary status, plus a Combined Evidentiary Classification into one of seven categories, audited against what each state's analysis actually computed.
- `anonymized_data/sensitivity_analysis_detailed.csv` / `_summary.csv` — threshold {2,3,4,5} × linkage-type × county × facility-type sweep of the shared-contact clustering rule, both states.
- `anonymized_data/corroboration_analysis_detailed.csv` / `_summary.csv` — cross-state cluster-corroboration summary (Washington + Oregon combined).
- `anonymized_data/observability_analysis_detailed.csv` / `_summary.csv` — multi-dimensional public-record observability (any record / inspections / investigations / enforcement), both states.
- `anonymized_data/linkage_robustness_detailed.csv` / `_summary.csv` — aggregate-only output of the privacy-constrained phone/address normalization robustness check (see reproducibility tiers below).
- `scripts/build_combined_matrix.py` — generates `combined_evidence_matrix.csv`.
- `scripts/build_sensitivity_analysis.py` — generates the threshold-sensitivity sweep. Fully publicly reproducible.
- `scripts/build_corroboration_analysis.py` — generates the cross-state cluster-corroboration summary. Fully publicly reproducible.
- `scripts/build_observability_analysis.py` — generates the observability summary. Fully publicly reproducible.
- `scripts/build_cluster_enforcement_exploratory.py` — generates the exploratory, hypothesis-generating comparison of enforcement/investigation prevalence between clustered and nonclustered facilities (crude and Mantel-Haenszel-adjusted). Fully publicly reproducible. Explicitly not a predictive-validity claim.
- `scripts/build_linkage_robustness.py` — generates the linkage-robustness aggregate output. **Privacy-constrained**: reads raw, non-anonymized facility files from sibling private repositories and cannot be rerun against the public package alone; see below.
- `scripts/build_figure1.py`, `scripts/build_figure2.py`, `scripts/build_figure3.py` — generate the manuscript's three figures programmatically.
- `scripts/verify_multistate_numbers.py` — independently recomputes every facility-level headline number, cluster/corroboration count, threshold-sensitivity result, observability count, and Table 1/Appendix B/Appendix G reconciliation in the manuscript from this repository's own `anonymized_data/` and manuscript source files, and fails loudly on any mismatch. Full list of checks below.
- `figures/` — the three generated figures (`Fig1_Conceptual_Overview.png`, `Fig2_Framework_Architecture.png`, `Fig3_Population_Analytic_Flow.png`).
- `CODEBOOK.md`, `PROVENANCE_MAP.md`, `SOURCE_MANIFEST.md` — field definitions, a claim-by-claim provenance table (with an explicit reproducibility tier per claim), and every external (non-facility-level) source cited, with access dates.
- `checksums.sha256` — SHA-256 checksums for every released `.md` document, script, and `anonymized_data/`/`figures/` file (verify with `shasum -a 256 -c checksums.sha256`), so a cloner can confirm the *released* files they downloaded are byte-identical to the ones that produced the submitted manuscript — i.e., an integrity check on the package as distributed. This is a different claim from cross-environment build reproducibility: regenerating a figure from `scripts/build_figure*.py` under any `requirements.txt`-compatible matplotlib version produces visually (pixel-)identical output, but the PNG file itself embeds the exact matplotlib version in its metadata, so its SHA-256 hash can differ from the committed file even when the image is indistinguishable. Data and script outputs (CSVs, the verification script's checks) do not have this issue — those are exact-byte reproducible from any compatible environment.
- `requirements.txt` — pinned Python dependencies for every script in this repository.
- `REPRODUCIBILITY_LOG.md` — a dated record of the actual verification commands run against this repository (headline-number checks, checksum self-check, PII sweep of the public data package) and their results, so the reproducibility claims above are not taken on faith.

## Submission-only files not included in this public repository

These files exist in the author's private working repository but are deliberately absent from this public archive:

- `Hussein_Multistate_Manuscript_HAS_Submission.md` / `.docx` / `.pdf` — an identical copy of the manuscript prepared for actual journal submission (working-paper/not-yet-peer-reviewed sentence removed from the Author Note; full residential correspondence address retained, as Health Affairs Scholar requires on the title page). Not released here because a full mailing address has no reason to be public.
- `HAS_Cover_Letter.md` — the submission cover letter to the journal editors.
- `derivation_audit/` — the private research log behind the derivation audit and external-corroboration search (dated query library, session log, source-screening log, corpus adjudication). Retained privately because it constitutes the manual-research process itself, not facility-level data requiring independent reproduction.
- The raw, non-anonymized Washington/Oregon facility files that `scripts/build_linkage_robustness.py` reads from sibling private repositories. Retained privately because they contain identifiable facility/operator information.

What each of these contributed to the manuscript is fully summarized in Supplementary Appendices G and H, which are public. The final Phase F submission-package audit (cover letter, HAS-submission copy, address handling) is conducted separately in the private working repository and is out of scope for this public archive.

## Public vs. privacy-constrained reproducibility, summarized

This package supports three distinct reproducibility tiers, and the manuscript, `PROVENANCE_MAP.md`, and this README are consistent about which claim falls in which tier:

1. **Fully publicly reproducible** — every facility-level count, the combined evidentiary classification, the threshold-sensitivity sweep, the cross-state cluster-corroboration summary, the observability analysis, and all three figures. Rerun any script in `scripts/` against the released `anonymized_data/` and get identical output.
2. **Aggregate-verifiable, privacy-constrained** — the phone/address linkage-robustness check and Oregon's cluster-level entity-resolution corroboration. The processing code, normalization rules, and aggregate outputs are released and independently checkable against the manuscript's reported figures, but the underlying raw identifiers (unredacted phone/address fields, Oregon business-registry lookups) are not part of the public package and the record-level step cannot be independently rerun without them.
3. **Not part of the public package by design** — the derivation audit and external-corroboration search process itself (`derivation_audit/`), because it is a documented manual research log, not facility-level data. Its conclusions are fully reported in Supplementary Appendices G and H.

The exact phrasing used throughout this repository for tier 2: *"All quantitative results derived from the released de-identified analytic data can be independently recomputed. Privacy-sensitive entity-resolution outputs are accompanied by aggregate verification files and disclosed construction rules but cannot be independently regenerated without the unreleased identifiers."* This is deliberately narrower than "all manuscript results": it covers the facility-level quantitative claims this package's data supports, not the external documentary findings (federal audits, court records, press releases) reported in Appendix H, which are citations to sources outside this repository, not computations over it.

## Verification script extension (how to verify the headline numbers)

```bash
pip install -r requirements.txt
python3 scripts/verify_multistate_numbers.py
```

This single script checks, against this repository's own `anonymized_data/` and manuscript source files:

- **Washington**: total facility count (3,457); facilities with ≥1 and ≥2 enforcement actions; stop-placement-order count; facilities with ≥1 complaint investigation; distinct operator-cluster count (72) and facilities in shared-contact clusters (164).
- **Oregon**: total facility count (792); Clackamas and Washington County facility counts; RF-03 (phone_shared_count≥2) and RF-08 (phone_shared_count≥3) counts; distinct operator-cluster count (49).
- **Combined evidentiary accounting**: all seven Combined Evidentiary Classification category counts in `combined_evidence_matrix.csv`.
- **Oregon corroboration (Phase A5)**: the 36/8/2/1/1/1 evidence-class distribution and the 47/1/1 corroborated/not-corroborated/indeterminate breakdown across all 49 clusters.
- **Cross-state cluster corroboration**: Washington's 72-cluster/70-corroborated and Oregon's 49-cluster/47-corroborated summary rows.
- **Threshold-sensitivity sweep**: Washington's facility counts at thresholds 2/3/4/5 (164/50/20/0); Oregon's all-type threshold-2 count (101) and the Residential Care Facility vs. Adult Foster Home threshold-3 split (5 of 81 vs. 0 of 629) that the Oregon population-validity finding rests on.
- **Public-record observability**: the "no public record at all" count for each state (Washington 1,287; Oregon 118) and each state's enforcement- and investigation-record counts.
- **Table 1 / Appendix G / Appendix B reconciliation**: parses the manuscript's Table 1 directly and checks its six evidentiary-role category counts (3/4/5/5/1/3, summing to 21) and separately confirms Supplementary Appendix B's 22 RF rows exactly match Supplementary Appendix G's Table G1 22 RF rows.
- **Figures**: confirms all three figure files exist and are non-trivial PNGs.
- **Exploratory cluster-enforcement comparison**: Oregon's crude enforcement risk ratio (2.10) and facility-type-adjusted risk ratio (0.66), plus clustered/nonclustered facility counts.

It does not and cannot verify the federal-audit, congressional-letter, or external-corroboration-source citations, since those are documents, not facility-level data; see `SOURCE_MANIFEST.md` for those, and Supplementary Appendix H for how each was tiered and what remains to fully verify any source still marked "candidate."

## Guardrails, in brief

- This is a methods-transparency and evidentiary-boundary study, not a fraud score, a validated predictive model, or an enforcement tool. Predictive validity is explicitly untested.
- No facility or operator is named anywhere in this repository.
- This study takes no position on the merits of the specific Medicaid expenditures under review in the 2026 CMS deferral actions against Minnesota or California; it uses that controversy only to situate why a disclosed, publicly reproducible alternative construction is a live national policy question.
- The evidence was allowed to change the framework: this audit retired one indicator (contradicted by its own source), split two into distinct subconstructs, and flagged two more for retirement or redefinition after a completed search found no qualifying evidence. This is disclosed in Supplementary Appendix G, not smoothed over.

## License and citation

This repository is licensed under [CC BY 4.0](LICENSE). See `CITATION.cff` for the preferred citation.
