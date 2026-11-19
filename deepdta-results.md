# DeepDTA: released-checkpoint evaluation

This is a first evaluation of the authors' **one released checkpoint**, not independent retraining and not a three-initialization reproduction. We used their 8/8-kernel inference notebook, source model and dictionaries from pinned commit `cc363f80a6a696d562f290a87aa20173e60f6c52`; model and inputs are hashed in the [manifest](outputs/deepdta-evaluation/manifest.json). PyTorch 2.13.0 and RDKit 2026.03.6 differ from the README's listed PyTorch 2.1.0; original training and output units have not been independently verified. We interpret predictions as p-affinity and convert RMSE using the project's 298.15 K convention, so kcal/mol values are conditional energy-equivalent comparisons rather than verified physical binding energies.

DeepDTA uses two 1D convolution branches on a protein amino-acid sequence and a ligand SMILES string, then combines their representations for affinity regression. RF-Score counts 3D protein–ligand atom contacts and trains a random forest. DeepDTA can score sequence/SMILES pairs without a 3D pose and can learn sequence patterns, but it does not directly see binding geometry or distinguish poses from the same input strings. It also inherits sequence/SMILES preprocessing and vocabulary limitations. These are model characteristics, not a universal ranking of methods.

| Cohort / eligibility | n | DeepDTA RMSE p-units | DeepDTA energy-equivalent RMSE | DeepDTA Pearson | RF matched-ID energy-equivalent RMSE | Paper DeepDTA RMSE |
|---|---:|---:|---:|---:|---:|---:|
| Internal test, ≤2,000 protein / ≤200 canonical SMILES | 2,162 | 1.792 | 2.445 | 0.433 | 2.120 (three-seed mean) | 2.29 ± 0.04 |
| Validation, same limits | 956 | 1.662 | 2.268 | 0.463 | not calculated | 2.07 ± 0.02 |
| BDB2020+, same limits | 93 | 1.342 | 1.831 | 0.244 | 1.772 (three-seed mean) | 1.72 ± 0.10 |
| BDB2020+, notebook-style long sequences | 114 | 1.585 | 2.162 | 0.061 | 1.656 (three-seed mean) | 1.72 ± 0.10 |

The paper's values are three-initialization means and SDs; RF values are the mean of three independently computed per-seed RMSEs on the exact matching IDs. DeepDTA is one checkpoint, so no seed uncertainty or exact training provenance can be assessed. Paper BDB cohort membership and external sequence preprocessing are unconfirmed; differences in cohorts, canonicalization, software, model and units prevent attributing metric differences to any one cause. No target-specific DeepDTA comparison or new training is claimed.

The arXiv v3 supporting information section S1.8 says training excluded proteins longer than 2,000 and isomeric SMILES longer than 200, with 7,338/956/2,162 train/validation/test records. Our internal eligible counts match the latter two after canonicalizing released SMILES. Our journal supporting information review for this issue was not completed, so this is an arXiv supplement statement, not a verified journal supplement statement. The released prediction notebook performs per-record padding with Python lists, which does not truncate or reject sequences above its nominal length. Thus applying the training-length cutoff to external evaluation is a distinct, explicitly labeled policy, not proven author procedure. The second BDB result follows the notebook's single-case prediction behavior for long sequences. Invalid or out-of-vocabulary inputs are listed with IDs and reasons in each `results.json`. One BDB protein sequence (7NA3) begins with an unsupported space and was excluded from both evaluations; it was not silently cleaned.

Twenty-one of the 115 BDB records have sequences over 2,000 and are excluded in the first external comparison. Sequence construction matters: the released BDB sequence for 7M8M and 7S3K has 7,096 residues, while their extracted structures contain 301- and 306-residue peptide sequences that are exact substrings. The 21 longer cases have an energy-equivalent RMSE of 3.243 by themselves under notebook-style inference. Whether the authors used the released complete sequences, a target chain, or another representation is unknown; this material question should be added to the author draft. The 15 unseen-token losses mentioned in the arXiv supplement are not yet reconciled with our cohorts.

All metadata IDs and per-seed RF predictions are matched by identifier and labels verified in `scripts/deepdta_compare.py`. RF matched test RMSEs are 2.125, 2.105, 2.129; BDB 93 RMSEs 1.765, 1.813, 1.739; BDB 114 RMSEs 1.646, 1.693, 1.628. The `test` split excludes 1L5Q, 1L5R, 1L5S, 1L7X, 3A2C, 3KR4, 4R6T, 4R76 and 4R7M. BDB excluded IDs are enumerated in the saved results. The 93 shared BDB checkpoint predictions agree between batch and single-case inference within 4.8e-6 p-units. The [scatter plots](outputs/deepdta-evaluation/predictions.png) show the relationship for each cohort; the diagonal is equality. These checks do not validate scientific correctness of the checkpoint or identify the original training samples.

Re-run using the recorded isolated environment, a restored pinned upstream checkout, and a fresh output directory:

```sh
/path/to/python scripts/deepdta_evaluate.py --source /path/to/LP-PDBBind --baseline /path/to/binding_affinity_v2 --output /path/to/new-output --cohorts BDB2020+ test val
/path/to/python scripts/deepdta_overlength.py --source /path/to/LP-PDBBind --baseline /path/to/binding_affinity_v2 --output /path/to/new-output-long --cohorts BDB2020+
```

The metadata, checkpoint and dictionary hashes are recorded; these scripts do not download source or certify its origin. For reproducibility restore source at the stated pinned commit and verify the hashes. `scripts/deepdta_plot.py` regenerates the current fixed-path figure. Training and target-specific evaluations remain open.
