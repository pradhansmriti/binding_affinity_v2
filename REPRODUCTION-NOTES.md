# LP-PDBBind reproduction project

Created 2026-11-03. Status updated 2026-11-13: metadata and label-unit audits completed; a structure-coverage audit and environment snapshot are available. Both v2020 structure archives have since been acquired; all 10,522 selected pairs are present and pass basic parsing. Author-setting reconciliation remains pending; the fixed internal and independent benchmarks have run. No extension experiments started. See [prerequisite findings](PREREQUISITES.md).

## Scope and provenance

Reproduce published scoring results before exploring new hypotheses. Official upstream: https://github.com/THGLab/LP-PDBBind . For a portable checkout, clone upstream into `vendor/LP-PDBBind` (ignored by Git). Inspected commit: `cc363f80a6a696d562f290a87aa20173e60f6c52`. Keep this checkout unmodified; make repairs in a separate derived implementation and record its diff.

The uploaded PDF was not accessible in this chat. The referenced conversation returned only five turns, assistant content-reference placeholders, and no attachments. The exact uploaded paper version remains unresolved, but the user selected the peer-reviewed journal article as the target. The nine extension descriptions were subsequently recovered from the user and are preserved in `DEFERRED-EXTENSIONS.md`. This project does not claim to have inspected that attachment.

Inspected public paper: https://arxiv.org/html/2308.09639v3 (10 January 2026), including methods, results Table 1, and supplement outline. Earlier preprint: https://pmc.ncbi.nlm.nih.gov/articles/PMC10462179.1/ . Journal version: https://doi.org/10.1021/acs.jpcb.5c08598 . The peer-reviewed journal article is the selected comparison target. Its accessible [PMC text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13430955/) is an author manuscript; the publisher supporting information was independently reviewed; do not mix unverified details across versions.

## Paper benchmark contract (peer-reviewed journal article)

Train on CL1 noncovalent complexes; validate and test on CL2 noncovalent complexes. Table 1 reports binding-energy RMSE in kcal/mol over three initializations. Its retrained RF-Score target is train 0.68 ± 0.003, validation 2.14 ± 0.01, test 2.10 ± 0.003. These values also appear in the PMC author manuscript; they are reference values, not pass/fail tolerances.

The split controls protein and ligand similarity, rather than relying on time alone. Independent BDB2020+ and target-specific Mpro/EGFR evaluations follow the internal benchmark. Docked-pose evaluation is a separate later reproduction stage.

## Located official materials

All paths below are relative to the upstream checkout.

| Material | Location | Access/status |
|---|---|---|
| Metadata, labels, split and clean flags | `dataset/LP_PDBBind.csv` | Downloaded and audited |
| LP-PDBBind protein/ligand structures | https://www.pdbbind.org.cn | Separate PDBBind v2020 acquisition required; repository has metadata only |
| Independent benchmark structures/metadata | `dataset/BDB2020+.tgz` | Downloaded, extracted, and evaluated; see [baseline results](BASELINE-RESULTS.md) |
| Target benchmarks | `dataset/mpro.tgz`, `dataset/EGFR.tgz` | Downloaded; deferred reproduction stages |
| Split generation and similarity calculation | `dataset_creation/create_splitting.ipynb`, `calc_similarities.ipynb` | Located; retain released split for first run |
| Cleaning and dataset construction | `dataset_creation/CL_filters.ipynb`, `prepare_BDB2020+_dataset.ipynb` | Located |
| RF-Score implementation | `model_retraining/RFScore/RF_Score.ipynb` | Source inspected; repairs required |
| Vina implementation | `model_retraining/vina/` | README requires Vina, Meeko, ADFR and configurable paths |
| IGN instructions/environment/checkpoint | `model_retraining/IGN/` | Training scripts live in upstream https://github.com/zjujdj/InteractionGraphNet.git ; pin separately before using |
| DeepDTA scripts and checkpoint | `model_retraining/deepdta/` | README documents environment and input schema |

The upstream README is an entry point, not a complete executable workflow. A separate project environment has been recreated and smoke-tested; the authors’ original environment is not recovered.

## Completed metadata audit

`metadata-audit.json` records the CSV SHA-256, exact sorted sample identifiers, and counts. It was produced using `scripts/audit_metadata.py`, which uses only Python's standard library.

| Population | Train | Validation | Test | Unassigned |
|---|---:|---:|---:|---:|
| Raw metadata split | 11,513 | 2,422 | 4,860 | 648 |
| First-run population: CL1 train / CL2 evaluation, noncovalent | 7,393 | 958 | 2,171 | excluded |

All 19,443 metadata identifiers are unique. Selected split identifier sets are disjoint. This does not verify sequence/chemical similarity. Subsequent structure and parsing audits cover all selected identifiers.

Set up upstream and re-run from this repository root:

```sh
git clone https://github.com/THGLab/LP-PDBBind.git vendor/LP-PDBBind
git -C vendor/LP-PDBBind checkout cc363f80a6a696d562f290a87aa20173e60f6c52
python3 scripts/audit_metadata.py vendor/LP-PDBBind/dataset/LP_PDBBind.csv --output metadata-audit.json
```

## First baseline: RF-Score v1

Choice: RF-Score has a compact CPU implementation and avoids needing a neural-network GPU environment. This is a project choice, not an author-recommended reproduction order.

Source-observed settings: 12 Å strict distance cutoff (`d < 12`); nine atom types C/O/N/F/P/S/Cl/Br/I on each side, forming 81 pair counts before removing training-all-zero columns. The source reads ligand SDF and protein PDB ATOM records. Its validation grid uses 100–500 trees in steps of 50 and `max_features` 2–10, with `random_state=24`. A separate final loop instead hardcodes 100 trees and `max_features=3`, trains ten models without explicit estimator seeds, and saves according to test Pearson correlation.

### Required repairs before the first run

1. Replace obsolete `UCBSplit.csv`, structure paths, and `BindingDB_test` references with explicit inputs. The CSV identifier is the unnamed index column, not an existing `pdbid` column; load with `index_col=0` and explicitly name/copy identifiers.
2. Flatten descriptor arrays to `(N, 81)` before applying the column mask. Source indexing applies a flat mask to an unflattened array.
3. Fail on missing protein/ligand files; record parse failures. Do not silently shrink the official population.
4. Freeze atom parsing, cutoff, column ordering and the training-derived feature mask; save mask and per-complex descriptors.
5. Separate validation selection from test reporting. Never choose a saved model using test correlation. Save every scheduled seed, with validation-selected configuration frozen before test evaluation.
6. Keep the source's fixed 100-tree/3-feature configuration and validation-grid configuration as explicitly labeled alternatives until paper/supplement reconciliation identifies the intended reported run. Do not silently claim either exactly reproduces the paper.

### Run sequence

1. Check the journal supporting information against the earlier arXiv supplement (done). Coverage and checksums for all 10,522 selected structure pairs are complete.
2. Create an isolated CPU environment with numpy, pandas, scipy, scikit-learn and a notebook reader if needed. Resolve and record exact versions before training; RF-Score README supplies no version lock. Record OS, architecture, Python, CPU and available memory.
3. Implement the narrow repairs above, retaining a source-to-derived change log. Verify descriptors manually on a few complexes, then smoke-test end-to-end on a small training subset. Smoke metrics are not benchmark results.
4. Freeze `configs/first-baseline.json`; use three explicit project seeds (0, 1, 2). These are new reproducibility controls, not recovered author seeds.
5. Generate descriptors for the full official population, with no missing samples. Fit using train only; select settings using validation only. Keep test sealed until the configuration and selection rule are recorded.
6. Report per-seed train/validation/test RMSE and mean/std; add Pearson/Spearman as diagnostics. Export predictions with identifiers, labels and units, plus environment, run command, timings, feature mask, model and config hashes.
7. Compare to version-matched paper numbers and investigate differences in population, energy conversion, parsing, versions and model selection. The frozen models have now been evaluated on BDB2020+; independent experiments may proceed alongside remaining reproduction work.

Units are a blocking check: inspect `value` provenance and conversion in the preparation notebooks; confirm sign and kcal/mol conventions against the PDF. Do not infer conversion from column names or convert twice.

## Reproducibility checklist

### Completed

- [x] Locate the authors’ repository and pin commit `cc363f80a6a696d562f290a87aa20173e60f6c52`; inspect the RF-Score notebook and README.
- [x] Hash released metadata, export selected IDs, count the cohorts, and verify ID uniqueness and split disjointness.
- [x] Inspect public arXiv v3 and its embedded supplement; document Table 1 targets, the notebook’s settings, and discrepancies in [paper–code reconciliation](PAPER-CODE-RECONCILIATION.md).
- [x] Acquire original PDBbind v2020 structures and verify complete file coverage and basic parsing for all 10,522 selected complexes. Identity with the authors’ prepared structures remains unverified.
- [x] Establish that the released `value` column matches the refined index’s p-affinity values for all 5,316 overlapping IDs; document the selected cohorts’ assay labels and the authors’ CL1/CL2 rationale.
- [x] Implement and test the explicitly labeled 298.15 K p-affinity-to-energy-equivalent conversion. The authors’ exact conversion convention remains unconfirmed.
- [x] Compare author and derived atom-reader outputs for all 10,522 selected protein and ligand pairs.
- [x] Recreate and verify the project’s recorded environment and run a small end-to-end train/validation smoke test inside it. This is not a recovered author environment or a benchmark result.
- [x] Generate 81 descriptors for every selected complex and derive a training-only mask of 36 features, matching the paper’s count. For ten training complexes, all 81 counts match the executable notebook. The notebook’s inactive 27-index comment differs; its historical computed mask indices are unavailable.

- [x] Review the publisher journal supporting information against the earlier arXiv RF-Score and cleaning notes; provenance and findings are in [paper–code reconciliation](PAPER-CODE-RECONCILIATION.md).

- [x] Implement the fixed internal training/evaluation pipeline and [source-to-derived change log](RF-SCORE-IMPLEMENTATION.md); require exact IDs.





### Still open

- [ ] Recover or reconcile the authors’ actual Table 1 settings, repetition count, software versions, temperature, and unit conversion. The released notebook’s ten unseeded fits and fixed settings do not establish what generated the reported three-run results.
- [ ] Verify the identity of the downloaded coordinates against the authors’ prepared structures where possible, and investigate the inactive commented mask if further evidence becomes available.
- [x] Audit and evaluate the independent BDB2020+ benchmark using the frozen models, then review material discrepancies; see [baseline results](BASELINE-RESULTS.md). Similarity and assay provenance remain open.

## Next input needed

The peer-reviewed journal article and its supporting information are the selected references; author settings and conversion remain unresolved. The independent benchmark has been evaluated locally; author-setting and coordinate discrepancies remain open. Independent experiments may proceed alongside remaining paper evaluations; see the plan in `DEFERRED-EXTENSIONS.md`.
