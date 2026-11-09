# E00 prerequisite findings (2026-11-09)

## Structures

The required official noncovalent cohort is 10,522 complexes (7,393 train, 958 validation, 2,171 test). Both original v2020 archives have been acquired and audited; see the completed coverage and parsing results below. To repeat the audit, run:

```sh
/opt/homebrew/Caskroom/miniforge/base/envs/affinity/bin/python scripts/audit_structures.py outputs/metadata-audit.json /path/to/general-set /path/to/refined-set --output outputs/structure-audit.json
```

Each root must contain `<pdbid>/<pdbid>_protein.pdb` and `<pdbid>/<pdbid>_ligand.sdf`. The audit hashes complete pairs and fails if any pair is missing or duplicated across roots. This verifies presence and records provenance, not chemical correctness or that these are the authors' prepared coordinates. Follow it with parser validation across the entire cohort. If a dataset includes the same complex in both roots, curate a single unambiguous source per ID before running.

## Labels and comparison units

The released CSV `value` equals the PDBbind v2020 refined index's `-logKd/Ki` for all 5,316 IDs in their intersection (exact to the provided decimal precision). For example, 6r8o is 8.22 with `Kd=0.006uM`, consistent with -log10 molar affinity. The RF notebook fits `value` directly, with no conversion in its model cells. This is strong evidence that its native target is p-affinity, not kcal/mol; values including IC50 and inequalities require attention to source assay semantics and are not necessarily thermodynamic Kd values.

The public [arXiv v3 paper](https://arxiv.org/html/2308.09639v3) Table 1 labels RMSE as kcal/mol. For an explicit *illustrative convention* of standard binding free energy at 298.15 K, ΔG = -RT ln(10) × p-affinity, with R = 0.00198720425864083 kcal mol⁻¹ K⁻¹ (factor ≈ -1.36425 kcal/mol per p unit). RMSE scales by the absolute factor; correlations are unchanged when both predictions and labels are converted consistently; converting only one reverses their sign. The authors' actual conversion convention and temperature have not been verified. Report native p-unit results and separately labelled conversions; do not claim an exact paper comparison until this is reconciled.

## Settings and paper version

Public arXiv v3 supplement S1.6 specifies 81 possible contacts, a 12 Å cutoff, and 36 training-nonzero features; the released notebook uses a strict `< 12 Å` cutoff. The supplement does not specify tree count or `max_features`. The notebook grid selects by validation RMSE (100–500 trees, max_features 2–10, random_state 24), but its final loop instead uses 100 trees and 3 features, ten unseeded fits, and saves by test correlation. Table 1 reports three initializations. The provenance of the reported settings and whether those notebook versions generated the paper results are unresolved. Treat fixed settings and validation selection as separately identified protocols; do not use the test set to choose a model.

The public arXiv v3 and its embedded supporting information are available as the provisional reference. The originally mentioned uploaded paper and its version remain unidentified; they should be checked before claiming a version-matched reproduction.

## Environment

The existing local conda `affinity` environment successfully imports Python 3.10.21, NumPy 2.2.6, SciPy 1.15.2, pandas 2.3.3 and scikit-learn 1.7.2. Its full conda explicit package list is recorded in `environment/affinity-osx-arm64-explicit.txt`; it is platform-specific and captures the current environment, not the authors' environment. An offline recreation into `.conda-isolated` succeeded with `CONDA_REGISTER_ENVS=false`; Conda issued a nonfatal home-registry warning. Python 3.10.21, NumPy 2.2.6, SciPy 1.15.2, pandas 2.3.3 and scikit-learn 1.7.2 were verified in the new environment. Conversion tests passed, and the 32-train/8-validation smoke output exactly matched the prior environment. The full baseline has not run.

## General-set archive received (2026-11-09)

The user downloaded `PDBbind_v2020_other_PL.tar.gz`. Its full archive member stream was checked for unsafe paths and unsupported member types before extraction to `data/structures/v2020-other-PL`. Archive SHA-256 is recorded in `outputs/general-archive-sha256.txt`. A complete-pair and hash audit (`outputs/structure-audit-general.json`) finds 5,118 train, 406 validation and 830 test pairs. It reports 2,275 train, 552 validation and 1,341 test missing; this archive specifically excludes the refined set, at that stage; the refined archive was subsequently supplied and audited as described below. The audit checks file presence, not structure parsing or scientific equivalence.

## Complete structure coverage and parsing (2026-11-09)

The user subsequently supplied `PDBbind_v2020_refined.tar.gz`. After validating archive member paths and types, it was extracted to `data/structures/refined-set`; its archive SHA-256 is in `outputs/refined-archive-sha256.txt`. The combined audit `outputs/structure-audit.json` finds exactly one protein/ligand pair for every selected ID: 7,393 train, 958 validation, and 2,171 test. It records SHA-256 hashes for each file. `scripts/audit_parsing.py` checked each pair with the current RF-Score readers for nonempty supported atoms and finite coordinates; all 10,522 passed (`outputs/parsing-audit.json`). This does not establish identity with the structures used by the authors or validate all chemical details. Descriptor generation, the training-only feature mask, and model training remain to be run.
