"""Audit released BDB2020+ and evaluate every frozen RF model; never refit."""
import argparse
import csv
import json
from pathlib import Path

import joblib
import numpy as np
import sklearn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

from rfscore_descriptor import descriptor
from run_baseline import sha, metrics, write_json


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--benchmark', type=Path, required=True, help='Extracted BDB2020+ directory')
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--run', type=Path, default=Path('runs/rfscore-fixed-100-3'))
    p.add_argument('--output', type=Path, default=Path('runs/bdb2020-fixed-100-3'))
    p.add_argument('--plot', type=Path, default=Path('outputs/bdb2020-predictions.png'))
    args = p.parse_args()
    lock_path = args.run / 'frozen.json'
    lock = json.loads(lock_path.read_text())
    if sklearn.__version__ != lock['versions']['scikit_learn']:
        raise ValueError('scikit-learn differs from frozen training environment')
    for name, digest in lock['run_files_sha256'].items():
        if sha(args.run / name) != digest:
            raise ValueError(f'Frozen file changed: {name}')
    metadata = args.benchmark / 'BDB2020+.csv'
    with metadata.open(newline='') as f:
        rows = list(csv.DictReader(f))
    ids = [r['pdbid'] for r in rows]
    if len(ids) != 115 or len(set(ids)) != len(ids) or any(not i.isalnum() or len(i) != 4 for i in ids):
        raise ValueError('Unexpected benchmark membership')
    if any(r['accurate'] != 'True' for r in rows):
        raise ValueError('Unexpected inaccurate label')
    labels = np.array([float(r['pKa']) for r in rows])
    raw = np.array([float(r['value']) for r in rows])
    if not np.isfinite(labels).all() or not np.isfinite(raw).all() or (raw <= 0).any():
        raise ValueError('Invalid labels')
    if not np.allclose(labels, 9 - np.log10(raw), rtol=0, atol=1e-10):
        raise ValueError('pKa does not match -log10(value in nM)')
    internal = set()
    for split in ('train', 'val', 'test'):
        path = Path('outputs/descriptors') / f'{split}.npz'
        if sha(path) != lock['descriptor_files_sha256'][split]:
            raise ValueError(f'{split}: frozen descriptor checksum mismatch')
        with np.load(path, allow_pickle=False) as data:
            internal.update(i.upper() for i in data['ids'].tolist())
    entries, vectors = [], []
    for identifier in ids:
        folder = args.benchmark / 'dataset' / identifier
        protein, ligand = folder / 'protein.pdb', folder / 'ligand.sdf'
        vector = descriptor(protein, ligand)
        vectors.append(vector)
        entries.append({'id': identifier, 'protein_sha256': sha(protein), 'ligand_sha256': sha(ligand), 'contacts': int(vector.sum())})
    x = np.stack(vectors)
    mask = lock['training_mask_indices']
    predictions = {}
    results = {}
    for seed in lock['seeds']:
        model = joblib.load(args.run / f'model-{seed}.joblib')
        pred = model.predict(x[:, mask])
        predictions[seed] = pred
        results[str(seed)] = metrics(labels, pred)
    aggregate = {key: {'mean': float(np.mean([results[str(s)][key] for s in lock['seeds']])),
                       'std_population': float(np.std([results[str(s)][key] for s in lock['seeds']]))}
                 for key in results[str(lock['seeds'][0])]}
    args.output.mkdir(parents=True, exist_ok=False)
    for seed, pred in predictions.items():
        with (args.output / f'predictions-seed-{seed}.csv').open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'value_nM', 'label_p_affinity', 'prediction_p_affinity'])
            writer.writerows(zip(ids, raw, labels, pred))
    write_json(args.output / 'results.json', {'per_seed': results, 'aggregate': aggregate})
    write_json(args.output / 'audit.json', {'archive_sha256': sha(args.archive), 'metadata_sha256': sha(metadata),
        'frozen_manifest_sha256': sha(lock_path), 'script_sha256': sha(Path(__file__)),
        'count': len(ids), 'internal_id_overlap': sorted(set(ids) & internal), 'entries': entries,
        'label_note': 'CSV pKa equals 9 - log10(value); value interpreted as nM. Assay identity is not in this CSV.',
        'training_mask_indices': mask, 'seeds': lock['seeds'], 'sklearn_version': sklearn.__version__,
        'output_sha256': {p.name: sha(p) for p in sorted(args.output.iterdir()) if p.is_file()}})
    values = np.concatenate([labels] + list(predictions.values()))
    lo, hi = np.floor(values.min()), np.ceil(values.max())
    grid = np.linspace(lo, hi, 600)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), constrained_layout=True)
    for values, label, color in [(labels, 'Measured', '#687888')] + [(predictions[s], f'Seed {s}', c) for s, c in zip(lock['seeds'], ['#126782', '#db7d28', '#8b5ca6'])]:
        kde = gaussian_kde(values, bw_method=0.3 / np.std(values, ddof=1))
        density = kde(grid)
        if label == 'Measured':
            axes[0].fill_between(grid, density, color='#b9c4d1', alpha=0.65, label=label)
        else:
            axes[0].plot(grid, density, label=label, color=color)
    axes[0].set(xlabel='p-affinity', ylabel='Density', title=f'BDB2020+ (n={len(ids)})')
    axes[0].legend(frameon=False)
    axes[1].scatter(labels, np.mean(list(predictions.values()), axis=0), s=20, alpha=.6, color='#126782')
    axes[1].plot([lo, hi], [lo, hi], '--', color='#bd562e')
    axes[1].set(xlim=(lo, hi), ylim=(lo, hi), xlabel='Measured p-affinity', ylabel='Mean prediction', title='Mean of three seeds')
    axes[1].set_aspect('equal', adjustable='box')
    fig.suptitle('Frozen RF-Score: independent benchmark')
    fig.text(.5, -.02, 'Density bandwidth: 0.3 p-affinity; dashed line: perfect prediction.', ha='center', fontsize=9)
    args.plot.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.plot, dpi=180, bbox_inches='tight')
    plt.close(fig)
    print(json.dumps(aggregate, indent=2))


if __name__ == '__main__':
    main()
