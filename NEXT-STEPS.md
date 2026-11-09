# Next steps: E00 RF-Score reproduction

## Complete

- [x] Acquire original PDBbind v2020 refined and general-minus-refined archives.
- [x] Confirm all 10,522 selected protein–ligand pairs are present; record file checksums.
- [x] Check that all selected structures have supported atoms and finite coordinates.
- [x] Audit released metadata, identify p-affinity labels, and document the kcal/mol comparison issue.

## Before the full run

1. [ ] Confirm the intended paper/supplement version and reconcile Table 1, author notebook settings, and repetition count. Until then label arXiv v3 targets provisional.
2. [ ] Document assay semantics and the energy conversion, including temperature and sign; report native p-affinity metrics and explicitly labeled energy conversions.
3. [ ] Create and verify an isolated environment from the recorded platform-specific package list; record actual versions.
4. [ ] Finish the derived RF-Score implementation and source-to-derived change log. Fail on missing samples, preserve identifiers, and select model settings using validation only.
5. [ ] Generate full-cohort descriptors, check feature shape and the training-only mask against the paper's 36 retained features, and investigate discrepancies.
6. [ ] Complete an end-to-end smoke run; freeze configuration, seed list, and validation selection rule before any test evaluation.
7. [ ] Train and report per-seed predictions, metrics, models, manifests, and resource use. Compare to version-matched paper results.
8. [ ] Audit BDB2020+ and evaluate the frozen model on that independent benchmark. Review discrepancies before starting E01–E09.

Structure-pair presence and parser checks do not prove that the downloaded coordinates match the exact preparations used by the authors. Track that uncertainty during reproduction. The licensed archives and generated per-file audits remain local; regenerate the latter using the scripts and metadata from the pinned upstream source.
