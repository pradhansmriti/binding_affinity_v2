# Next steps: E00 RF-Score reproduction

## Complete

- [x] Acquire original PDBbind v2020 refined and general-minus-refined archives.
- [x] Confirm all 10,522 selected protein–ligand pairs are present; record file checksums.
- [x] Check that all selected structures have supported atoms and finite coordinates.
- [x] Audit released metadata, identify p-affinity labels, and document the kcal/mol comparison issue.
- [x] Compare arXiv v3 and its supporting information with the pinned RF-Score notebook; document agreements and unresolved discrepancies in [paper–code reconciliation](PAPER-CODE-RECONCILIATION.md).
- [x] Compare source and project atom-reader outputs across all 10,522 selected structures.
- [x] Implement and test the documented p-affinity to 298.15 K energy-equivalent RMSE conversion.
- [x] Recreate the recorded environment in `.conda-isolated` and rerun conversion tests and the 32-train/8-validation smoke test; no test-set evaluation. Output matches the earlier run.
- [x] Generate all 10,522 81-feature descriptors and confirm the training-only mask retains 36 features, matching the paper. Compare all 81 counts with the executable notebook for ten train complexes.

## Before the full run

1. [ ] Confirm the originally intended paper/supplement version and, if possible, recover the authors’ actual Table 1 settings, repetitions, and unit convention. The documented source discrepancies remain unresolved; arXiv v3 targets are provisional.
2. [ ] Use the verified 298.15 K energy-equivalent conversion in the full run; report native p-affinity metrics alongside converted RMSE and preserve assay-type limitations. The authors’ exact conversion remains unconfirmed.
3. [x] Recreate and verify the isolated environment from the recorded osx-arm64 package list; core package versions and smoke output match the earlier run.
4. [ ] Finish the derived RF-Score implementation and source-to-derived change log. Fail on missing samples and preserve identifiers. Start with the authors’ notebook settings of 100 trees and 3 candidate features per split; these have not been independently validated. Any separate tuning uses validation only.
5. [x] Generate full-cohort descriptors and verify the training-only mask retains the paper’s 36 features. The notebook's inactive 27-index comment differs; its computed 36-feature output agrees in count, but does not expose the historical indices.
6. [ ] Freeze configuration, seed list, and validation selection rule before any test evaluation. The small smoke run has passed in the isolated environment.
7. [ ] Train and report per-seed predictions, metrics, models, manifests, and resource use. Compare to version-matched paper results.
8. [ ] Audit BDB2020+ and evaluate the frozen model on that independent benchmark. Review discrepancies before starting E01–E09.

Structure-pair presence and parser checks do not prove that the downloaded coordinates match the exact preparations used by the authors. Track that uncertainty during reproduction. The licensed archives and generated per-file audits remain local; regenerate the latter using the scripts and metadata from the pinned upstream source.
