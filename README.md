# Public-Data Review-Priority Analytics for Medicaid Long-Term Care Oversight: Washington and Oregon

This is the self-contained replication package for the manuscript *"Public-Data Review-Priority Analytics for Medicaid Long-Term Care Oversight: Washington and Oregon"* (Mohamed Noor Hussein), prepared for submission to Health Affairs Scholar.

This manuscript synthesizes three things into one accounting: how the underlying 20-indicator typology was developed from Minnesota's public Medicaid audit and enforcement record, how it was piloted at scale in Washington's Adult Family Home sector, and how it held up as a cross-state portability test in Oregon, evaluated for technical, construct, and threshold portability. It adds two pieces of Washington-specific evidence not present in the original Washington working paper (a 2024 federal compliance audit and a March 2026 congressional program-integrity inquiry naming Washington directly), and situates the combined two-state record against the 2026 CMS Medicaid funding-deferral controversy, in which CMS deferred $350 million from Minnesota and $1.3 billion from California, the California amount resting in part on a partly undisclosed "statistical outlier" methodology that California's own published response has criticized as opaque.

## Relationship to the companion studies

This draws directly on one prior working paper, *A Public-Data Review-Priority Framework for Medicaid Residential Care Oversight: Evidence from Washington State Adult Family Homes* (Hussein, 2026a), posted on SSRN. The Oregon cross-state portability analysis is reported here directly, citing its own primary sources; it does not depend on a separate Oregon manuscript being posted to SSRN. Every Oregon fact this manuscript relies on is cited to its own primary source (Oregon DOJ and U.S. Attorney press releases, Oregon DHS's state-commissioned evaluations, the Oregon licensing portal) or is independently reproducible from this repository's own data via `scripts/verify_multistate_numbers.py`. A fuller, non-peer-reviewed companion account of the Oregon analysis, including the complete eight-tier evidentiary matrix, is maintained separately at [`public-data-review-priority-oregon-public`](https://github.com/Mohamedn954/public-data-review-priority-oregon-public), but this manuscript does not depend on it.

Unlike the Washington working paper, this manuscript introduces no new facility-level computation of its own beyond the combined evidentiary classification described below. What is new here: the Oregon analysis reported directly with its own primary sources, two new Washington-specific sources, the two-state synthesis and portability test, and the framing against the 2026 CMS deferral controversy.

## What's included

- `Hussein_Multistate_Manuscript.md` / `.docx` / `.pdf` — the manuscript (working-paper version, with the preprint disclosure in the Author Note), structured under Health Affairs Scholar's required Research Article headings (Introduction, Data and Methods, Results, Discussion, Conclusion), with two figures and no embedded tables.
- `Hussein_Multistate_Manuscript_Supplementary.md` / `.docx` / `.pdf` — the six supplementary appendices (A–F), submitted alongside the manuscript as Supplementary Material per journal instructions. Holds all three tables and the fuller evidentiary and methodological detail the main text references but does not have room for.
- `Hussein_Multistate_Manuscript_HAS_Submission.md` / `.docx` / `.pdf` — an identical copy prepared for actual journal submission, with the working-paper/not-yet-peer-reviewed sentence removed from the Author Note. Not part of the public replication package.
- `anonymized_data/washington/` — Washington's de-identified facility-level data, copied unmodified from the companion Washington repository.
- `anonymized_data/oregon/` — Oregon's de-identified facility-level data, copied unmodified from the companion Oregon repository.
- `anonymized_data/combined_evidence_matrix.csv` — **new to this repository**: each of the 20 indicators' Washington and Oregon evidentiary status, plus a Combined Evidentiary Classification into one of seven categories (from strongest to weakest evidentiary reach: Directly Operationalized, System-Level Evidence, Case-Level Evidence, Partially Operationalized, Contextually Assessed, Publicly Testable Not Completed, Internal Data Required), audited against what each state's analysis actually computed, not derived from the WA/OR testability labels alone.
- `scripts/build_combined_matrix.py` — generates `combined_evidence_matrix.csv` from the two states' evidentiary status columns and documents the audit rationale for every row.
- `scripts/build_figure1.py`, `scripts/build_figure2.py` — generate the manuscript's two figures programmatically; rerun either to regenerate that figure from source.
- `scripts/verify_multistate_numbers.py` — independently recomputes every facility-level headline number and the combined evidentiary classification counts in the manuscript from this repository's own `anonymized_data/`, and fails loudly on any mismatch.
- `figures/` — the two generated figures (`Fig1_Conceptual_Overview.png`, `Fig2_Framework_Architecture.png`).
- `CODEBOOK.md`, `PROVENANCE_MAP.md`, `SOURCE_MANIFEST.md` — field definitions, a claim-by-claim provenance table, and every external (non-facility-level) source cited, with access dates.

## How to verify the headline numbers

```bash
python3 scripts/verify_multistate_numbers.py
```

This checks Washington's facility count, enforcement prevalence, and cluster counts; Oregon's facility count and RF-03/RF-08 counts; and every category count in the combined evidentiary classification, all directly against the CSVs in `anonymized_data/`. It does not and cannot verify the federal-audit or congressional-letter citations, since those are documents, not facility-level data; see `SOURCE_MANIFEST.md` for those.

## Guardrails, in brief

- This is a methods-transparency and evidentiary-boundary study, not a fraud score, a validated predictive model, or an enforcement tool.
- No facility or operator is named anywhere in this repository.
- This study takes no position on the merits of the specific Medicaid expenditures under review in the 2026 CMS deferral actions against Minnesota or California; it uses that controversy only to situate why a disclosed, publicly reproducible alternative construction is a live national policy question.

## License and citation

This repository is licensed under [CC BY 4.0](LICENSE). See `CITATION.cff` for the preferred citation.
