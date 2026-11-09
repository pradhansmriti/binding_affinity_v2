"""Generate audited RF-Score counts for the fixed cohort; never read labels or fit models."""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

from rfscore_descriptor import ELEMENTS, descriptor

EXPECTED = {'train': 7393, 'val': 958, 'test': 2171}


def file_sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def extract(entry):
    identifier = entry['id']
    try:
        if entry['status'] != 'ok' or len(entry['files']) != 2:
            raise ValueError('Missing or ambiguous protein/ligand pair')
        files = [Path(item['path']) for item in entry['files']]
        for path, info in zip(files, entry['files']):
            if not path.is_file() or file_sha256(path) != info['sha256']:
                raise ValueError(f'File missing or SHA-256 mismatch: {path.name}')
        result = descriptor(*files)
        if result.shape != (81,) or np.any(result < 0):
            raise ValueError('Invalid descriptor')
        return identifier, result
    except Exception as exc:
        raise RuntimeError(f'{identifier}: {type(exc).__name__}: {exc}') from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', type=Path, default=Path('data/source/LP_PDBBind.csv'))
    parser.add_argument('--manifest', type=Path, default=Path('outputs/structure-audit.json'))
    parser.add_argument('--output-dir', type=Path, default=Path('outputs/descriptors'))
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    manifest = json.loads(args.manifest.read_text())
    if file_sha256(args.metadata) != manifest['metadata_sha256']:
        raise ValueError('Metadata does not match the structure audit')
    with args.metadata.open(newline='') as f:
        rows = list(csv.DictReader(f))
    id_key = next(iter(rows[0]))
    if len({r[id_key] for r in rows}) != len(rows):
        raise ValueError('Duplicate metadata identifiers')
    by_split = {}
    for split, count in EXPECTED.items():
        expected_ids = {r[id_key] for r in rows if r['new_split'] == split and r['CL1' if split == 'train' else 'CL2'] == 'True' and r['covalent'] == 'False'}
        entries = sorted(manifest['entries'][split], key=lambda x: x['id'])
        actual_ids = [e['id'] for e in entries]
        if len(entries) != count or len(set(actual_ids)) != count or set(actual_ids) != expected_ids:
            raise ValueError(f'{split}: audited IDs do not match the full official selection')
        by_split[split] = entries
    masks, matrices = {}, {}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for split, entries in by_split.items():
            ids, vectors = [], []
            for i, (identifier, vector) in enumerate(pool.map(extract, entries, chunksize=8), 1):
                ids.append(identifier)
                vectors.append(vector)
                if i % 500 == 0 or i == len(entries):
                    print(f'{split}: {i}/{len(entries)}', file=sys.stderr, flush=True)
            matrix = np.stack(vectors)
            matrices[split] = (ids, matrix)
    train_mask = np.any(matrices['train'][1] != 0, axis=0)
    indices = np.flatnonzero(train_mask).tolist()
    # Notebook's commented mask (cell 15) can be compared with the computed mask.
    source_indices = [1, 2, 6, 10, 11, 15, 19, 20, 24, 28, 29, 33, 37, 38, 42, 46, 47, 51, 55, 56, 60, 64, 65, 69, 73, 74, 78]
    for split, (ids, matrix) in matrices.items():
        dest = args.output_dir / f'{split}.npz'
        temp = args.output_dir / f'{split}.tmp.npz'
        np.savez_compressed(temp, ids=np.array(ids), counts=matrix)
        os.replace(temp, dest)
    summary = {'metadata_sha256': manifest['metadata_sha256'], 'structure_manifest_sha256': file_sha256(args.manifest),
               'counts': {split: len(values[0]) for split, values in matrices.items()},
               'feature_shape': 81, 'feature_order': list(ELEMENTS), 'cutoff_angstrom': 12, 'cutoff_operator': '<',
               'training_mask_indices': indices, 'training_nonzero_features': len(indices),
               'paper_reported_nonzero_features': 36,
               'matches_paper_feature_count': len(indices) == 36,
               'notebook_commented_mask_indices': source_indices,
               'matches_notebook_commented_mask': indices == source_indices,
               'descriptor_files_sha256': {split: file_sha256(args.output_dir / f'{split}.npz') for split in EXPECTED},
               'versions': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
               'note': 'Counts only; no affinity labels, training, validation selection, or test metrics.'}
    (args.output_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
