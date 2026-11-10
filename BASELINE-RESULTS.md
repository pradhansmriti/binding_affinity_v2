# Fixed RF-Score baseline: first internal evaluation

Run: 2026-11-10, `runs/rfscore-fixed-100-3`. Comparison target: Li et al., *J. Phys. Chem. B* 130 (2026), 730–740, DOI [10.1021/acs.jpcb.5c08598](https://doi.org/10.1021/acs.jpcb.5c08598), Table 1. These are first results, not a claim of exact reproduction.

Three independently seeded fixed 100-tree, 3-candidate-feature forests were trained on the 7,393 CL1 noncovalent training complexes. A training-only 36-feature mask and all models, settings, hashes and validation results were frozen before the 958 validation and 2,171 test cohort results were used for reporting; validation was predicted during training, and test was evaluated in a separate subsequent command. No test-based model selection was performed. Standard deviations below are population SD across project seeds 0, 1 and 2; the authors' SD convention and seeds are not known.

| Cohort | Native RMSE (p-affinity) | Energy-equivalent RMSE (kcal/mol) | Journal RMSE (kcal/mol) |
|---|---:|---:|---:|
| Train | 0.4996 ± 0.0017 | 0.6816 ± 0.0023 | 0.68 ± 0.003 |
| Validation | 1.5685 ± 0.0008 | 2.1399 ± 0.0011 | 2.14 ± 0.01 |
| Test | 1.5516 ± 0.0075 | 2.1167 ± 0.0102 | 2.10 ± 0.003 |

The test mean Pearson correlation is 0.5620 ± 0.0063 and Spearman is 0.5321 ± 0.0073. Energy-equivalent RMSE uses the stated 298.15 K project conversion, not a verified author convention. The training labels include IC50 and censored records, so the converted numbers are comparison-scale values and are not uniformly physical binding free energies. The means are close to the reported journal values, but settings, conversion, sample provenance and SD convention are not established; do not call this an exact reproduction.

`runs/rfscore-fixed-100-3/` contains all per-seed predictions, metrics, serialized models, configuration, frozen manifest, aggregate metrics and evaluation manifest. It is ignored by Git. The frozen manifest records hashes of models, inputs and train/validation outputs, but this first run did not record the training script hash; the evaluation manifest records the later script hash. Preserve the run directory and this limitation. Training took 3.34 seconds in the isolated environment; the process reported peak RSS 288,112,640 bytes on macOS. The BDB2020+ independent benchmark is not yet audited or evaluated.
