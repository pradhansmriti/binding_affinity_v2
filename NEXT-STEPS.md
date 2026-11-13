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

- [x] Review the peer-reviewed journal supporting information against the earlier RF-Score and cleaning notes.
- [x] Plot internal-cohort label and prediction distributions and measured-versus-predicted affinities; see [baseline results](BASELINE-RESULTS.md).

## Baseline follow-up

1. [ ] If possible, recover the authors’ actual Table 1 settings, repetitions, and unit convention. The journal supporting information has been reviewed; it does not resolve the forest settings or temperature, and its printed energy formula leaves the meaning of K unclear.
2. [x] Report native p-affinity metrics and the separately labeled 298.15 K energy-equivalent conversion, preserving assay limitations. The authors’ exact conversion remains unconfirmed.
3. [x] Recreate and verify the isolated environment from the recorded osx-arm64 package list; core package versions and smoke output match the earlier run.
4. [x] Implement the fixed RF-Score baseline and [source-to-derived change log](RF-SCORE-IMPLEMENTATION.md), requiring exact sample membership and preserving identifiers.
5. [x] Generate full-cohort descriptors and verify the training-only mask retains the paper’s 36 features. The notebook's inactive 27-index comment differs; its computed 36-feature output agrees in count, but does not expose the historical indices.
6. [x] Freeze the fixed configuration, seeds and no-selection rule before test evaluation.
7. [x] Train and report per-seed predictions, metrics, models, manifests, and resource use; see [baseline results](BASELINE-RESULTS.md) for the limited journal comparison.
8. [ ] Audit BDB2020+ and evaluate the frozen models on that independent benchmark. Plot the resulting distributions and predictions, and review discrepancies before starting E01–E09.

Structure-pair presence and parser checks do not prove that the downloaded coordinates match the exact preparations used by the authors. Track that uncertainty during reproduction. The licensed archives and generated per-file audits remain local; regenerate the latter using the scripts and metadata from the pinned upstream source.

The publisher supporting information supplied by the user was reviewed on 2026-11-10; its SHA-256 and findings are recorded in [paper–code reconciliation](PAPER-CODE-RECONCILIATION.md).
