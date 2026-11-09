"""Exercise the RF-Score pipeline on a small train/validation subset, never test."""
import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy
import sklearn
from sklearn.ensemble import RandomForestRegressor

from affinity_units import DEFAULT_TEMPERATURE_K, rmse_to_energy_equivalent
from rfscore_descriptor import descriptor


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata', type=Path, default=Path('data/source/LP_PDBBind.csv'))
    p.add_argument('--manifest', type=Path, default=Path('outputs/structure-audit.json'))
    p.add_argument('--output', type=Path, default=Path('outputs/smoke-baseline.json'))
    p.add_argument('--train-count', type=int, default=32)
    p.add_argument('--val-count', type=int, default=8)
    a = p.parse_args()
    if a.train_count < 2 or a.val_count < 1:
        p.error('Need at least two training and one validation sample')
    manifest = json.loads(a.manifest.read_text())
    digest = hashlib.sha256(a.metadata.read_bytes()).hexdigest()
    if digest != manifest['metadata_sha256']:
        raise ValueError('Metadata hash does not match structure audit')
    with a.metadata.open(newline='') as f:
        rows = list(csv.DictReader(f))
    id_key = next(iter(rows[0]))
    metadata = {r[id_key]: r for r in rows}
    if len(metadata) != len(rows):
        raise ValueError('Duplicate metadata identifiers')
    arrays, selected = {}, {}
    for split, count in [('train', a.train_count), ('val', a.val_count)]:
        entries = sorted(manifest['entries'][split], key=lambda x: x['id'])[:count]
        if len(entries) != count:
            raise ValueError(f'Insufficient {split} samples')
        X, y = [], []
        for entry in entries:
            if entry['status'] != 'ok':
                raise ValueError(f"Missing or ambiguous structure: {entry['id']}")
            row = metadata[entry['id']]
            if row['new_split'] != split or row['CL1' if split == 'train' else 'CL2'] != 'True' or row['covalent'] != 'False':
                raise ValueError(f"Filter mismatch: {entry['id']}")
            paths = [Path(item['path']) for item in entry['files']]
            X.append(descriptor(*paths))
            y.append(float(row['value']))
        arrays[split] = (np.asarray(X), np.asarray(y))
        selected[split] = [x['id'] for x in entries]
    train_x, train_y = arrays['train']
    val_x, val_y = arrays['val']
    mask = np.any(train_x != 0, axis=0)
    if int(mask.sum()) < 3:
        raise ValueError('Fewer than three nonzero training features')
    model = RandomForestRegressor(n_estimators=100, max_features=3, random_state=0, n_jobs=1)
    model.fit(train_x[:, mask], train_y)
    pred = model.predict(val_x[:, mask])
    rmse = float(np.sqrt(np.mean((pred - val_y)**2)))
    result = {'kind': 'smoke_only_not_benchmark', 'metadata_sha256': digest,
              'selected_ids': selected, 'feature_shape': [len(train_x), 81],
              'training_mask_indices': np.flatnonzero(mask).tolist(),
              'nonzero_features': int(mask.sum()), 'model': {'n_estimators': 100, 'max_features': 3, 'random_state': 0},
              'validation_rmse_p_units_smoke_only': rmse,
              'validation_rmse_energy_equivalent_kcal_mol_smoke_only': rmse_to_energy_equivalent(rmse),
              'conversion_temperature_kelvin': DEFAULT_TEMPERATURE_K,
              'versions': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__, 'scikit_learn': sklearn.__version__},
              'warning': 'Smoke test only; no test-set data, benchmark conclusions, or author energy convention verified.'}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('selected_ids', 'training_mask_indices')}, indent=2))


if __name__ == '__main__':
    main()
