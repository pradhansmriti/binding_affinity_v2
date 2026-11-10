# RF-Score source-to-derived implementation

The baseline derives from `model_retraining/RFScore/RF_Score.ipynb` at upstream commit `cc363f80a6a696d562f290a87aa20173e60f6c52`. The journal article and its supporting information are the comparison target. The source notebook's fixed 100 trees and `max_features=3` are starting settings, not confirmed paper settings.

- Use the released metadata's explicit CL1 noncovalent train and CL2 noncovalent validation/test identifiers, and require exact membership and descriptor checksums instead of silently dropping missing files.
- Use the separately audited 81-element flat descriptor order and strict `< 12 Å` source cutoff. Compute the nonzero feature mask from training only; require agreement with the audited 36 indices.
- Fit the fixed 100/3 configuration with explicit project seeds 0, 1 and 2; save all models and do not select a seed or tune against test. The source final loop uses ten unseeded fits and saves by test correlation.
- Save train/validation results and hashes in `frozen.json` before the separate test command can load test descriptors or labels. Evaluation verifies the frozen inputs and models, and reports every seed.
- Fit native metadata p-affinity; report native RMSE and a separate 298.15 K energy-equivalent RMSE. The journal's actual conversion and temperature are not established and mixed-assay labels are not all exact thermodynamic free energies.
- Preserve identifiers and original assay records in prediction CSVs. Record package versions, timings, peak process RSS and hashes. Serialized models must only be loaded from trusted run directories.

Run in the recorded isolated environment:

```sh
.conda-isolated/bin/python scripts/run_baseline.py train --run runs/rfscore-fixed-100-3
.conda-isolated/bin/python scripts/run_baseline.py evaluate --run runs/rfscore-fixed-100-3
```

The run directory must not exist before training; test evaluation refuses to overwrite existing results. The paper reports three initializations but the project seeds and this selection policy are not recovered author settings. Runs are ignored by Git and must be retained or archived separately.
