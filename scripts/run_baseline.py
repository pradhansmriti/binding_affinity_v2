"""Fit the fixed RF-Score baseline, then evaluate its frozen models on test.

Commands are separate to preserve a pre-test, immutable protocol and fitted models.
Never load serialized models from an untrusted run directory.
"""
import argparse
import csv
import hashlib
import json
import os
import platform
import resource
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import scipy
from scipy.stats import pearsonr, spearmanr
import sklearn
from sklearn.ensemble import RandomForestRegressor

from affinity_units import DEFAULT_TEMPERATURE_K, rmse_to_energy_equivalent
from rfscore_descriptor import ELEMENTS


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def load_metadata(path):
    with path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError('Empty metadata')
    key = next(iter(rows[0]))
    data = {row[key]: row for row in rows}
    if len(data) != len(rows) or '' in data:
        raise ValueError('Duplicate or empty metadata ID')
    return data


def load_split(split, metadata, summary, directory, expected_count):
    path = directory / (split + '.npz')
    if sha(path) != summary['descriptor_files_sha256'][split]:
        raise ValueError(f'{split}: descriptor checksum mismatch')
    with np.load(path, allow_pickle=False) as data:
        ids = data['ids'].tolist()
        counts = data['counts']
    expected = {k for k, row in metadata.items() if row['new_split'] == split
                and row['CL1' if split == 'train' else 'CL2'] == 'True'
                and row['covalent'] == 'False'}
    if len(ids) != expected_count or len(set(ids)) != len(ids) or set(ids) != expected:
        raise ValueError(f'{split}: descriptor IDs do not match official cohort')
    if counts.shape != (len(ids), 81) or not np.issubdtype(counts.dtype, np.number) or not np.isfinite(counts).all() or (counts < 0).any():
        raise ValueError(f'{split}: invalid descriptor matrix')
    labels = np.array([float(metadata[i]['value']) for i in ids])
    if not np.isfinite(labels).all():
        raise ValueError(f'{split}: nonfinite labels')
    return ids, counts, labels


def metrics(y, pred):
    rmse = float(np.sqrt(np.mean((pred - y) ** 2)))
    def corr(fn):
        result = float(fn(y, pred).statistic)
        return result if np.isfinite(result) else None
    return {'rmse_p_affinity': rmse,
            'rmse_energy_equivalent_kcal_mol': rmse_to_energy_equivalent(rmse),
            'pearson': corr(pearsonr), 'spearman': corr(spearmanr)}


def predictions(path, ids, y, pred, metadata):
    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'assay_record', 'label_p_affinity', 'prediction_p_affinity'])
        writer.writerows((i, metadata[i]['kd/ki'], float(a), float(b)) for i, a, b in zip(ids, y, pred))


def verify_inputs(args):
    config = json.loads(args.config.read_text())
    summary = json.loads((args.descriptors / 'summary.json').read_text())
    if sha(args.metadata) != summary['metadata_sha256']:
        raise ValueError('Metadata checksum mismatch')
    if summary['feature_order'] != list(ELEMENTS) or summary['cutoff_operator'] != '<' or summary['cutoff_angstrom'] != 12:
        raise ValueError('Descriptor protocol mismatch')
    if config['source_fixed_config'] != {'n_estimators': 100, 'max_features': 3} or config['proposed_seeds'] != [0, 1, 2]:
        raise ValueError('Unexpected fixed baseline configuration')
    return config, summary, load_metadata(args.metadata)


def train(args):
    config, summary, metadata = verify_inputs(args)
    data = {s: load_split(s, metadata, summary, args.descriptors, config['expected_counts'][s]) for s in ('train', 'val')}
    mask = np.any(data['train'][1] != 0, axis=0)
    indices = np.flatnonzero(mask).tolist()
    if indices != summary['training_mask_indices'] or len(indices) != 36:
        raise ValueError('Training-derived mask does not match audited mask')
    args.run.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    results = {}
    for seed in config['proposed_seeds']:
        model = RandomForestRegressor(**config['source_fixed_config'], random_state=seed, n_jobs=1)
        model.fit(data['train'][1][:, mask], data['train'][2])
        joblib.dump(model, args.run / f'model-{seed}.joblib')
        results[str(seed)] = {}
        for split, (ids, x, y) in data.items():
            pred = model.predict(x[:, mask])
            results[str(seed)][split] = metrics(y, pred)
            predictions(args.run / f'{split}-seed-{seed}.csv', ids, y, pred, metadata)
    write_json(args.run / 'train-validation-metrics.json', results)
    write_json(args.run / 'config.json', config)
    files = sorted(p for p in args.run.iterdir() if p.is_file())
    lock = {'purpose': 'Fixed 100/3; all three seeds retained, no test selection',
            'metadata_sha256': sha(args.metadata), 'training_script_sha256': sha(Path(__file__)), 'descriptor_summary_sha256': sha(args.descriptors / 'summary.json'),
            'descriptor_files_sha256': summary['descriptor_files_sha256'],
            'training_mask_indices': indices, 'seeds': config['proposed_seeds'],
            'run_files_sha256': {p.name: sha(p) for p in files},
            'versions': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__, 'scikit_learn': sklearn.__version__, 'joblib': joblib.__version__, 'platform': platform.platform()},
            'training_seconds': time.monotonic() - start,
            'peak_rss_platform_units': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'conversion_temperature_kelvin': DEFAULT_TEMPERATURE_K,
            'warning': 'Project protocol, not recovered author settings; mixed-assay energy values are comparison scale only.'}
    write_json(args.run / 'frozen.json', lock)
    print('Frozen train/validation run:', args.run)


def evaluate(args):
    start = time.monotonic()
    lock = json.loads((args.run / 'frozen.json').read_text())
    if (args.run / 'test-metrics.json').exists():
        raise ValueError('Test evaluation already exists; do not overwrite')
    if sha(args.metadata) != lock['metadata_sha256'] or sha(args.descriptors / 'summary.json') != lock['descriptor_summary_sha256']:
        raise ValueError('Frozen input checksum mismatch')
    for name, digest in lock['run_files_sha256'].items():
        if sha(args.run / name) != digest:
            raise ValueError(f'Frozen file changed: {name}')
    if sklearn.__version__ != lock['versions']['scikit_learn']:
        raise ValueError('scikit-learn version differs from training')
    config = json.loads((args.run / 'config.json').read_text())
    summary = json.loads((args.descriptors / 'summary.json').read_text())
    metadata = load_metadata(args.metadata)
    ids, x, y = load_split('test', metadata, summary, args.descriptors, config['expected_counts']['test'])
    mask = lock['training_mask_indices']
    results = {}
    for seed in lock['seeds']:
        model = joblib.load(args.run / f'model-{seed}.joblib')
        pred = model.predict(x[:, mask])
        results[str(seed)] = metrics(y, pred)
        predictions(args.run / f'test-seed-{seed}.csv', ids, y, pred, metadata)
    write_json(args.run / 'test-metrics.json', results)
    all_metrics = json.loads((args.run / 'train-validation-metrics.json').read_text())
    aggregates = {}
    for split in ('train', 'val', 'test'):
        aggregate = {}
        for metric in results[str(lock['seeds'][0])]:
            values = [results[str(seed)][metric] if split == 'test' else all_metrics[str(seed)][split][metric] for seed in lock['seeds']]
            aggregate[metric] = {'mean': float(np.mean(values)), 'std_population': float(np.std(values, ddof=0))} if all(v is not None for v in values) else None
        aggregates[split] = aggregate
    write_json(args.run / 'aggregate-metrics.json', aggregates)
    outputs = [args.run / f'test-seed-{seed}.csv' for seed in lock['seeds']] + [args.run / 'test-metrics.json', args.run / 'aggregate-metrics.json']
    write_json(args.run / 'evaluation-manifest.json', {'frozen_sha256': sha(args.run / 'frozen.json'), 'script_sha256': sha(Path(__file__)), 'outputs_sha256': {p.name: sha(p) for p in outputs}, 'evaluation_seconds': time.monotonic() - start, 'peak_rss_platform_units': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    print('Evaluated all frozen seeds:', args.run)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=['train', 'evaluate'])
    p.add_argument('--config', type=Path, default=Path('configs/first-baseline.json'))
    p.add_argument('--metadata', type=Path, default=Path('data/source/LP_PDBBind.csv'))
    p.add_argument('--descriptors', type=Path, default=Path('outputs/descriptors'))
    p.add_argument('--run', type=Path, required=True)
    args = p.parse_args()
    (train if args.stage == 'train' else evaluate)(args)


if __name__ == '__main__':
    main()
