# InteractionGraphNet: reproduction and model comparison

Status: **checkpoint and one graph smoke-tested; benchmark evaluation not completed.** No independently reproduced IGN RMSE or correlation is available yet. The selected journal article is [Li et al. (2026)](https://doi.org/10.1021/acs.jpcb.5c08598); [arXiv v3](https://arxiv.org/html/2308.09639v3) is separately accessible and includes an IGN supplement. The paper reports that 6,378 training complexes were retained after molecule preparation failures; these are not necessarily identical to the RF training population.

## Model and comparison with RF-Score

IGN is a graph neural network that represents a ligand and protein pocket using atom and bond features and spatial interactions, then applies learned graph operations to predict affinity. It can represent chemical connectivity and aspects of geometry that the current RF-Score v1 descriptor discards. RF-Score uses counts of atom-element pairs within 12 Å as inputs to a random forest; it is compact and fast but loses detailed bond, spatial and positional information.

IGN's richer representation is a possible advantage, not a guarantee of better performance or mechanistic explanation. It requires accurate protein/ligand structures, molecule sanitization, graph generation and compatible software. Its predictions can depend strongly on pose and preprocessing and it is more expensive to build and evaluate. RF-Score has simpler features and a small CPU footprint, but cannot distinguish different arrangements with the same contact counts.

## Published values and our RF baseline

These are **paper IGN results**, not our reproduction. Values use the paper's stated kcal/mol; our RF RMSE values are explicitly 298.15 K energy-equivalent, with an unconfirmed author conversion. RF entries are mean ± population SD over our three fixed seeds.

| Cohort | Paper IGN retrained | Our frozen RF-Score |
|---|---|---|
| Internal test | RMSE 2.16 ± 0.13 | RMSE 2.117 ± 0.010 |
| BDB2020+ | RMSE 1.38 ± 0.09; Pearson 0.54 ± 0.04 | RMSE 1.649 ± 0.028; Pearson 0.490 ± 0.009 |
| Mpro | RMSE 1.44; Pearson 0.61; Spearman 0.65 | RMSE 1.251 ± 0.035; Pearson 0.687 ± 0.019; Spearman 0.732 ± 0.005, provisional `pKa_reliable` |
| EGFR | RMSE 0.96; Pearson 0.65; Spearman 0.62 | RMSE 1.028 ± 0.024; Pearson 0.404 ± 0.060; Spearman 0.358 ± 0.076 |

Paper target values use its best BDB2020+ model; ours average all three seeds. Author cohort inclusion and structure preparation are not confirmed equivalent. These differences, different model seeds and small target samples mean this is a descriptive comparison rather than a paired model comparison.

## What was verified

- LP-PDBBind source commit `cc363f80a6a696d562f290a87aa20173e60f6c52` provides IGN checkpoint `2023-06-23_00_36_38_49161.pth`, SHA-256 `26b456632556201131a6505f2fc8d116735abd2333759cb48dbec3d5b17fe1cd`, and links to the separate [InteractionGraphNet repository](https://github.com/zjujdj/InteractionGraphNet/tree/ed0263fed7790d5e7a2d754daaea9308a25a8fe4). Its source is on `master`; the default `main` branch contains only a README. Master was inspected at `ed0263fed7790d5e7a2d754daaea9308a25a8fe4`. Historical identity of this revision to the authors' training code remains unconfirmed.
- All checkpoint parameters loaded strictly into the published prediction architecture. With an upstream-prepared example pickle, graph construction and CPU inference completed, giving finite score 4.3048248291. This is an unlabeled example and **not a benchmark metric**.
- The test used Python 3.10, PyTorch 2.13.0, DGL 1.1.3 and DGLLife 0.3.2, with compatibility aliases for changed DGL APIs. The published IGN environment specifies Python 3.7.12, PyTorch 1.13.1 and CUDA DGL 1.0.2; numerical and preprocessing equivalence is unverified. The compatibility shim is explicit in [the smoke script](scripts/ign_smoke.py).
- An exploratory attempt to form a 10 Å residue pocket from Mpro 7VTH using an independent atom-distance selection required bypassing RDKit sanitization. Although it generated a graph, it is not validated against the paper's Chimera-prepared pocket and its output is not interpreted as a reproduction. A source-provided serialized graph cache also failed to deserialize with newer DGL; regenerating from the supplied example molecule pickle succeeded.

## Remaining work

Recreate or obtain the paper's Chimera 1.17.3 10 Å residue-selected pocket and RDKit inputs and determine model-specific sample membership and errors. Verify graph features and predicted values against an author example under the original environment before running internal test, BDB2020+, Mpro and EGFR. Save per-record preprocessing failures and report a matched-sample RF comparison, plus full eligible-set coverage. The released checkpoint appears to be one run; it cannot by itself reproduce the paper's three-initialization mean and SD. Seek the other two checkpoints, exact sample IDs, preprocessing inputs, and selection metric from the authors if they can provide them.

Recreate the smoke test by making the pinned source and LP-PDBBind checkpoint available locally, installing DGL and DGLLife in an isolated environment, then running:

```sh
PYTHONPATH=/path/to/ign-deps DGLBACKEND=pytorch OMP_NUM_THREADS=1 python scripts/ign_smoke.py \
  --source /path/to/InteractionGraphNet --checkpoint /path/to/2023-06-23_00_36_38_49161.pth \
  --example /path/to/InteractionGraphNet/examples/ign_input/smi_total_3_2_replica-1_2
```

Only load pickled inputs and checkpoints from trusted source repositories. This command is a compatibility smoke test, not a scientific benchmark.
