# Target-specific RF-Score evaluation

Evaluation date: 2026-11-18. Comparison: Li et al., [journal article](https://doi.org/10.1021/acs.jpcb.5c08598), Table 3; the [PMC author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC13430955/) describes 40 Mpro and 23 EGFR complexes. These are first results under our frozen baseline, not an exact rerun of the authors' selected model.

| Target and label | n | Native RMSE (p-affinity) | Energy-equivalent RMSE (kcal/mol) | Pearson | Spearman |
|---|---:|---:|---:|---:|---:|
| Mpro, `pKa_reliable` | 40 | 0.917 ± 0.026 | 1.251 ± 0.035 | 0.687 ± 0.019 | 0.732 ± 0.005 |
| Mpro, `pKa_full` sensitivity | 40 | 0.919 ± 0.021 | 1.254 ± 0.029 | 0.625 ± 0.020 | 0.690 ± 0.007 |
| Paper, Mpro RF-Score retrained | 40 | — | 1.64 | 0.52 | 0.58 |
| EGFR, `value` | 23 | 0.754 ± 0.018 | 1.028 ± 0.024 | 0.404 ± 0.060 | 0.358 ± 0.076 |
| Paper, EGFR RF-Score retrained | 23 | — | 0.97 | 0.52 | 0.45 |

Project values are means ± population SD across the three frozen seeds 0, 1, and 2; they describe seed variation, not uncertainty from sampling complexes. Per-seed values and predictions are in [Mpro](outputs/target-evaluation/mpro/results.json) and [EGFR](outputs/target-evaluation/EGFR/results.json). The project uses its 298.15 K conversion of native p-affinity RMSE to an energy-equivalent comparison scale; the authors' conversion convention is unconfirmed. Mixed Kd, Ki and IC50 labels are not uniformly thermodynamic free energies. EGFR results are in the same general range; Mpro error is ~0.39 kcal/mol lower than the paper and correlations higher. These differences are material enough to retain as unresolved, not as proof of better performance or an exact match.

## Exploratory comparison using the best BDB2020+ seed

The paper's best BDB2020+ model plausibly means its best trained initialization, analogous to choosing a seed; its exact selection criterion is not specified. Seed 2 has the lowest BDB2020+ RMSE and the highest Pearson and Spearman correlations among our three frozen models. The paper says it used the best BDB2020+ model for Table 3, but does not specify the selection metric. As a post hoc, illustrative comparison, retaining our seed 2 gives:

| Evaluation | Seed 2 energy-equivalent RMSE (kcal/mol) | Seed 2 Pearson | Seed 2 Spearman | Paper RMSE / Pearson / Spearman |
|---|---:|---:|---:|---|
| BDB2020+ | 1.621 | 0.502 | 0.414 | 1.61 ± 0.008 / 0.51 ± 0.008 / not reported in Table 2 |
| Mpro, `pKa_reliable` | 1.278 | 0.686 | 0.739 | 1.64 / 0.52 / 0.58 |
| Mpro, `pKa_full` | 1.275 | 0.625 | 0.700 | 1.64 / 0.52 / 0.58 |
| EGFR | 0.994 | 0.488 | 0.452 | 0.97 / 0.52 / 0.45 |

The BDB2020+ paper values are reported means ± SD for three initializations; the target Table 3 values describe one selected author model. Our seed 2 values are single-model results, so the BDB2020+ comparison is not a like-for-like mean comparison. This retrospective selection makes BDB2020+ a selection set for this analysis, so its selected-seed result is optimistic as an estimate of performance on new data. Both target results were already inspected before this comparison, and EGFR overlaps internal validation/test IDs; the target comparisons are exploratory. Retain the three-seed results as the primary analysis. Unknown selection rules and author seeds prevent claiming the chosen model matches the paper's model.

## Protocol and caveats

The released RF-Score baseline uses all three previously frozen models, the same 36-column training mask and no model selection or refitting. Table 3 instead reports one model chosen for best BDB2020+ performance; the paper does not establish which of our seeds corresponds to it. The published value is not a three-seed mean. Authors' exact settings, input provenance, labels, and energy conversion remain uncertain.

Both Mpro label columns are provided because the released CSV does not establish which was used for Table 3. Five entries differ; `pKa_reliable` and `pKa_full` both equal 6 − log10 of their corresponding numeric columns, consistent with micromolar values. The `reliable` label is used in the figure as a transparent provisional choice, not a verified paper convention; the `full` comparison is a sensitivity check. EGFR `value` is used as released p-affinity; the `affinity` strings contain mixed assay types and sometimes multiple measurements. No claim is made that each selected value is the correct assay for its structure.

All 40/23 metadata IDs are unique, all have supported readable structure pairs, finite labels and nonzero contacts; no row was excluded. All 81 descriptor counts were independently compared with the executable pinned notebook readers and distance calculation on every one of the 63 structure pairs, with exact agreement. This validates computation on the released files, not their chemical correctness or equivalence to historical prepared inputs. Seed-0 native RMSE, Pearson and Spearman were independently recalculated from the saved CSV using pandas and NumPy and matched. The seven existing unit tests passed.

There are no exact PDB ID overlaps with our frozen training set for either cohort. Mpro has no overlap with our validation or test IDs. EGFR overlaps validation for 2ITP, 2J6M and 2JIU and test for 1XKK, 2ITO, 2ITT, 2ITY, 2ITZ, 5EDQ, 5EM8 and 5UGB. These overlaps do not mean the frozen models were trained on those structures, but the target cohort is not independent of our internal evaluation data. Exact ID checks do not rule out protein or ligand similarity to training; the research similarity audit remains open. No historical sample identity or assay provenance is established by matching counts.

The [Mpro plot](outputs/target-evaluation/mpro/predictions.png) and [EGFR plot](outputs/target-evaluation/EGFR/predictions.png) show predictions averaged across seeds for visualization; metrics are calculated per seed. Mpro 7VTH has the largest absolute error with `pKa_reliable` (measured 5.07, mean predicted 7.37 p-units). EGFR 5X27 has the largest absolute error (measured 9.22, mean predicted 7.71). These are candidates for follow-up label and structure review, not established data errors.

## Provenance and reproduction

Archives came from pinned upstream commit `cc363f80a6a696d562f290a87aa20173e60f6c52`: `dataset/mpro.tgz` SHA-256 `09315d5424a25f01c83b6b215a57eb2ed6caafe7b5beb18b9b92762e9ef020d0`, and `dataset/EGFR.tgz` SHA-256 `d898de7455563dbe6f88c584d5d093ad6d7f00cd9bc5c03a96eb8358150c3b76`. The JSON audits record hashes of all evaluated files and the frozen manifest. The archive downloads and extraction currently reside under `/private/tmp/lp-targets`, which is temporary; restore the pinned archives and check these hashes before rerunning. The evaluator records the archive and extracted-file hashes but does not itself prove that the extracted files came from that archive.

```sh
MPLCONFIGDIR=/private/tmp/lp-mpl /path/to/.conda-isolated/bin/python scripts/evaluate_targets.py \
  --root /path/to/targets --run /path/to/runs/rfscore-fixed-100-3 \
  --descriptors /path/to/outputs/descriptors --output /path/to/new-output
```

The root must contain extracted `mpro/` and `EGFR/` directories and archives named `mpro.tgz` and `EGFR.tgz`. The output path must be new. The frozen run and descriptor files remain in the main checkout and are not committed. Verify the frozen model, descriptor and archive hashes on restoration. `scripts/evaluate_targets.py` requires the recorded scikit-learn version.
