# Binding affinity v2 | LP-PDBBind reproduction and rebuttal

V1 was a simple affinity prediction example. Its split audit showed why a good
test score can be misleading when related proteins appear in training. That
experience motivates v2's question: how robust are the conclusions of LP-PDBBind
when we reproduce its benchmark and independently check its assumptions?

V2 starts with a reproduction of RF-Score, then tests specific limitations of
the benchmark and evaluates proposed fixes. The rebuttal will distinguish
confirmed findings, discrepancies, and hypotheses that remain open.

## E00 progress

- Pinned the released metadata and RF notebook at upstream commit
  `cc363f80a6a696d562f290a87aa20173e60f6c52`.
- Reran the official-cohort audit. The output matches the earlier audit byte for
  byte. The noncovalent CL1 training and CL2 evaluation filters give 7,393 train,
  958 validation, and 2,171 test complexes.
- Implemented the RF-Score descriptor extraction step with the source atom
  types, strict 12 Å cutoff, and an explicit flat feature order. On BDB2020+
  complex 7EJK, all 81 counts match the pinned notebook, totaling 5,620 contacts.
  This is a descriptor check on one structure, before model fitting.

The selected PDBbind v2020 structures have been acquired and audited for file
coverage and basic parsing. The 7EJK check used the separately released external
benchmark archive. The public arXiv v3 Table 1 is the provisional comparison target.
Reconcile affinity units, historical sample membership, and RF settings before
interpreting any numerical discrepancy.

## Prerequisite update — 2026-11-09

The released `value` column matches PDBbind p-affinity values for all 5,316
refined-index overlaps; the paper reports RMSE in kcal/mol, so units and the
conversion convention must be explicit. Both original PDBbind v2020 structure archives have been extracted: all
10,522 selected complexes have exactly one file pair and pass a basic atom and
coordinate parsing check. A structure-coverage and checksum audit and a
platform-specific snapshot of the existing working Python environment are now
available. See [prerequisite findings](PREREQUISITES.md) for evidence, commands,
and unresolved paper and source discrepancies. No full baseline has run.

The ordered [next steps](NEXT-STEPS.md) track the remaining baseline prerequisites.

## Reproduction and critique

1. **Reproduce.** Generate descriptors across the official cohort and verify
   the training-only mask against the paper's 36 retained
   features. Resolve the historical CSV name, label units, and differences between
   the notebook's validation grid and final fit. Freeze settings and seeds on
   validation, then report per-seed predictions and metrics. Use BDB2020+ as the
   external check with the fitted model frozen.
2. **Audit the claims.** Measure exact and near overlaps in proteins and ligands.
   Compare the released split with protein-disjoint, scaffold-disjoint, and
   jointly controlled alternatives. Report how error varies with distance to
   training and which complexes each threshold excludes. Compare training label
   policies with the evaluation cohort held fixed.
3. **Test improvements.** For each observed failure, run a matched comparison
   with the same RF-Score features and model. Candidate remedies include stricter
   similarity controls, clearer label policies, and a reproducible selection
   procedure. Report paired uncertainty and any loss of coverage alongside
   changes in error.
4. **Write the rebuttal.** For each claim, record the original result, our result,
   the evidence for any discrepancy, and the effect of the proposed remedy.
   Retain v1 as the motivating example and use simple controls where needed
   to interpret the paper's benchmark.

[Reproduction notes](REPRODUCTION-NOTES.md) and the
[E00–E09 backlog](DEFERRED-EXTENSIONS.md) contain the detailed protocol.
E01–E09 are follow-ups to E00.

The upstream metadata and structures are not included in this repository. To
restore the metadata used by the commands below, clone the pinned upstream
repository and copy `dataset/LP_PDBBind.csv` into `data/source/`; obtain the
original structure archives separately from PDBbind. Large per-file audit
manifests are generated locally and are not committed.

```sh
python3 scripts/audit_metadata.py data/source/LP_PDBBind.csv --output outputs/metadata-audit.json
python3 scripts/rfscore_descriptor.py /path/to/protein.pdb /path/to/ligand.sdf
```

The descriptor script uses NumPy and SciPy. Its ligand parser accepts V2000 SDF.
See the [public paper](https://arxiv.org/html/2308.09639v3) and
[pinned upstream source](https://github.com/THGLab/LP-PDBBind/tree/cc363f80a6a696d562f290a87aa20173e60f6c52).
