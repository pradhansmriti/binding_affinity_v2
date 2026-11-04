# LP-PDBBind reproduction project

Created 2026-11-03. Status: source inspection and metadata audit complete; baseline execution pending inputs and notebook repairs. No extension experiments started.

## Scope and provenance

Reproduce published scoring results before exploring new hypotheses. Official upstream: https://github.com/THGLab/LP-PDBBind . For a portable checkout, clone upstream into `vendor/LP-PDBBind` (ignored by Git). Inspected commit: `cc363f80a6a696d562f290a87aa20173e60f6c52`. Keep this checkout unmodified; make repairs in a separate derived implementation and record its diff.

The uploaded PDF was not accessible in this chat. The referenced conversation returned only five turns, assistant content-reference placeholders, and no attachments. The exact uploaded paper version remains unresolved. The nine extension descriptions were subsequently recovered from the user and are preserved in `DEFERRED-EXTENSIONS.md`. This project does not claim to have inspected that attachment.

Inspected public paper: https://arxiv.org/html/2308.09639v3 (10 January 2026), including methods, results Table 1, and supplement outline. Earlier preprint: https://pmc.ncbi.nlm.nih.gov/articles/PMC10462179.1/ . Journal version: https://doi.org/10.1021/acs.jpcb.5c08598 . Do not mix numerical targets from versions. Confirm the user's PDF before declaring reproduction success.

## Paper benchmark contract (provisional v3)

Train on CL1 noncovalent complexes; validate and test on CL2 noncovalent complexes. Table 1 reports binding-energy RMSE in kcal/mol over three initializations. Its retrained RF-Score target is train 0.68 ± 0.003, validation 2.14 ± 0.01, test 2.10 ± 0.003. These are provisional reference values, not pass/fail tolerances.

The split controls protein and ligand similarity, rather than relying on time alone. Independent BDB2020+ and target-specific Mpro/EGFR evaluations follow the internal benchmark. Docked-pose evaluation is a separate later reproduction stage.

## Located official materials

All paths below are relative to the upstream checkout.

| Material | Location | Access/status |
|---|---|---|
| Metadata, labels, split and clean flags | `dataset/LP_PDBBind.csv` | Downloaded and audited |
| LP-PDBBind protein/ligand structures | https://www.pdbbind.org.cn | Separate PDBBind v2020 acquisition required; repository has metadata only |
| Independent benchmark structures/metadata | `dataset/BDB2020+.tgz` | Downloaded; not yet extracted/audited |
| Target benchmarks | `dataset/mpro.tgz`, `dataset/EGFR.tgz` | Downloaded; deferred reproduction stages |
| Split generation and similarity calculation | `dataset_creation/create_splitting.ipynb`, `calc_similarities.ipynb` | Located; retain released split for first run |
| Cleaning and dataset construction | `dataset_creation/CL_filters.ipynb`, `prepare_BDB2020+_dataset.ipynb` | Located |
| RF-Score implementation | `model_retraining/RFScore/RF_Score.ipynb` | Source inspected; repairs required |
| Vina implementation | `model_retraining/vina/` | README requires Vina, Meeko, ADFR and configurable paths |
| IGN instructions/environment/checkpoint | `model_retraining/IGN/` | Training scripts live in upstream https://github.com/zjujdj/InteractionGraphNet.git ; pin separately before using |
| DeepDTA scripts and checkpoint | `model_retraining/deepdta/` | README documents environment and input schema |

The repository README is an entry point, not a complete executable workflow. No training environment has been installed.

## Completed metadata audit

`metadata-audit.json` records the CSV SHA-256, exact sorted sample identifiers, and counts. It was produced using `scripts/audit_metadata.py`, which uses only Python's standard library.

| Population | Train | Validation | Test | Unassigned |
|---|---:|---:|---:|---:|
| Raw metadata split | 11,513 | 2,422 | 4,860 | 648 |
| First-run population: CL1 train / CL2 evaluation, noncovalent | 7,393 | 958 | 2,171 | excluded |

All 19,443 metadata identifiers are unique. Selected split identifier sets are disjoint. This does not verify sequence/chemical similarity or availability of structure files.

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

1. Obtain the exact uploaded PDF/supplement and prepared PDBBind v2020 structures. Audit all 10,522 selected complexes against the expected filenames and checksums.
2. Create an isolated CPU environment with numpy, pandas, scipy, scikit-learn and a notebook reader if needed. Resolve and record exact versions before training; RF-Score README supplies no version lock. Record OS, architecture, Python, CPU and available memory.
3. Implement the narrow repairs above, retaining a source-to-derived change log. Verify descriptors manually on a few complexes, then smoke-test end-to-end on a small training subset. Smoke metrics are not benchmark results.
4. Freeze `configs/first-baseline.json`; use three explicit project seeds (0, 1, 2). These are new reproducibility controls, not recovered author seeds.
5. Generate descriptors for the full official population, with no missing samples. Fit using train only; select settings using validation only. Keep test sealed until the configuration and selection rule are recorded.
6. Report per-seed train/validation/test RMSE and mean/std; add Pearson/Spearman as diagnostics. Export predictions with identifiers, labels and units, plus environment, run command, timings, feature mask, model and config hashes.
7. Compare to version-matched paper numbers. Investigate differences in population, energy conversion, parsing, versions and model selection before expanding scope. Then reproduce BDB2020+ using the frozen model.

Units are a blocking check: inspect `value` provenance and conversion in the preparation notebooks; confirm sign and kcal/mol conventions against the PDF. Do not infer conversion from column names or convert twice.

## Reproducibility checklist

- [x] Locate author-owned repository and record exact commit.
- [x] Inspect RF-Score source and model README instructions.
- [x] Hash metadata; export selected identifiers and count populations.
- [x] Verify identifier uniqueness and split disjointness.
- [ ] Recover uploaded PDF and supplement; hash and identify version.
- [ ] Reconcile target table, reported repetition count, source loop and hyperparameters.
- [ ] Acquire PDBBind v2020 prepared structures and verify complete coverage.
- [ ] Verify affinity units, assay handling and parser behavior.
- [ ] Pin environment and save derived source diff.
- [ ] Validate feature shapes and training-only preprocessing.
- [ ] Complete smoke run, then frozen full baseline.
- [ ] Save predictions, models, metrics, manifests and resource use.
- [ ] Reproduce independent benchmark with frozen model.
- [ ] Review discrepancies before releasing extension backlog.

## Next input needed

Reattach the original paper (and supplement if available) to confirm version-specific targets. The nine earlier experiments have been restored from the user’s supplied backlog in `DEFERRED-EXTENSIONS.md`; all remain deferred. Work completed here remains usable while the paper is recovered.
