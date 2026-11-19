"""Evaluate frozen RF-Score models on the pinned target-specific archives."""
import argparse
import csv
import json
from pathlib import Path
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sklearn
from rfscore_descriptor import descriptor
from run_baseline import metrics, sha, write_json


def evaluate(target, root, run, internal, out):
    lock_path = run / 'frozen.json'
    lock = json.loads(lock_path.read_text())
    if sklearn.__version__ != lock['versions']['scikit_learn']:
        raise ValueError('scikit-learn version differs from frozen run')
    for name, digest in lock['run_files_sha256'].items():
        if sha(run / name) != digest:
            raise ValueError('Frozen file mismatch: ' + name)
    ids_by_split = {}
    for split in ('train', 'val', 'test'):
        path = internal / (split + '.npz')
        if sha(path) != lock['descriptor_files_sha256'][split]:
            raise ValueError('Descriptor file mismatch: ' + split)
        with np.load(path, allow_pickle=False) as data:
            ids_by_split[split] = set(str(i).upper() for i in data['ids'])
    directory = root / target
    info = directory / 'info.csv'
    with info.open(newline='') as f:
        rows = list(csv.DictReader(f))
    id_key = 'pdbid' if target == 'mpro' else 'pdbids'
    ids = [r[id_key].upper() for r in rows]
    expected = 40 if target == 'mpro' else 23
    if len(ids) != expected or len(set(ids)) != expected:
        raise ValueError(f'{target}: unexpected membership')
    vectors, entries = [], []
    for identifier in ids:
        if target == 'mpro':
            protein, ligand = directory / identifier / 'protein.pdb', directory / identifier / 'ligand.sdf'
        else:
            protein, ligand = directory / 'protein' / (identifier + '.pdb'), directory / 'ligand' / (identifier + '.sdf')
        vec = descriptor(protein, ligand)
        if not np.isfinite(vec).all() or vec.sum() == 0:
            raise ValueError('Invalid contacts for ' + identifier)
        vectors.append(vec)
        entries.append({'id': identifier, 'protein_sha256': sha(protein), 'ligand_sha256': sha(ligand), 'contacts': int(vec.sum())})
    x = np.stack(vectors)[:, lock['training_mask_indices']]
    columns = ['pKa_reliable', 'pKa_full'] if target == 'mpro' else ['value']
    labels = {col: np.array([float(row[col]) for row in rows]) for col in columns}
    if any(not np.isfinite(values).all() for values in labels.values()):
        raise ValueError('Non-finite labels')
    preds = {int(seed): joblib.load(run / f'model-{seed}.joblib').predict(x) for seed in lock['seeds']}
    results = {column: {str(seed): metrics(y, pred) for seed, pred in preds.items()} for column, y in labels.items()}
    aggregate = {col: {key: {'mean': float(np.mean([results[col][str(s)][key] for s in preds])), 'std_population': float(np.std([results[col][str(s)][key] for s in preds]))} for key in next(iter(results[col].values()))} for col in columns}
    out.mkdir(parents=True, exist_ok=False)
    with (out / 'predictions.csv').open('w', newline='') as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(['id'] + columns + [f'prediction_seed_{s}' for s in preds])
        for i, identifier in enumerate(ids):
            writer.writerow([identifier] + [labels[c][i] for c in columns] + [preds[s][i] for s in preds])
    write_json(out / 'results.json', {'per_seed': results, 'aggregate': aggregate})
    write_json(out / 'audit.json', {'target': target, 'count': len(ids), 'ids': ids, 'label_columns': columns, 'metadata_sha256': sha(info), 'frozen_manifest_sha256': sha(lock_path), 'script_sha256': sha(Path(__file__)), 'archive_sha256': sha(root / (target + '.tgz')), 'internal_id_overlap': {s: sorted(set(ids) & members) for s, members in ids_by_split.items()}, 'entries': entries, 'sklearn_version': sklearn.__version__, 'output_sha256': {p.name: sha(p) for p in sorted(out.iterdir())}})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), constrained_layout=True)
    y = labels[columns[0]]
    mean = np.mean(list(preds.values()), axis=0)
    lo, hi = min(y.min(), mean.min()), max(y.max(), mean.max())
    axes[0].scatter(y, mean, s=28, alpha=.7)
    axes[0].plot([lo, hi], [lo, hi], '--', color='gray')
    axes[0].set(xlabel='Measured p-affinity', ylabel='Mean prediction', title=f'{target.upper()} (n={len(ids)})')
    order = np.argsort(y)
    axes[1].plot(np.arange(len(y)), y[order], '.', label='Measured')
    axes[1].plot(np.arange(len(y)), mean[order], '.', label='Mean prediction')
    axes[1].set(xlabel='Complex ordered by measured affinity', ylabel='p-affinity', title='Ranking by measured affinity')
    axes[1].legend(frameon=False)
    fig.savefig(out / 'predictions.png', dpi=170)
    plt.close(fig)
    print(target, json.dumps(aggregate, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--descriptors', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    for target in ('mpro', 'EGFR'):
        evaluate(target, args.root, args.run, args.descriptors, args.output / target)

if __name__ == '__main__':
    main()
