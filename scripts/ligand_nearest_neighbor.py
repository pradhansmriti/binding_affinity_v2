#!/usr/bin/env python3
"""Audit nearest training ligands using the released LP-PDBBind notebook rule."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from rdkit import Chem, DataStructs, RDLogger, rdBase
from rdkit.Chem import AllChem

RDLogger.DisableLog('rdApp.warning')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_ids(path):
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f))
    ids = [row['id'] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f'duplicate cohort IDs in {path}')
    return ids

def make_molecule(smiles):
    mol = Chem.MolFromSmiles(smiles) if smiles else None
    if mol is None:
        return None
    fps = {r: AllChem.GetMorganFingerprintAsBitVect(mol, r, nBits=1024) for r in (2, 4, 10)}
    return (Chem.MolToSmiles(mol), fps)

def corrected_score(a, b, first=None):
    value = DataStructs.DiceSimilarity(a[1][2], b[1][2]) if first is None else first
    radius = 2
    if value == 1:
        radius = 4
        value = DataStructs.DiceSimilarity(a[1][4], b[1][4])
        if value == 1:
            radius = 10
            value = DataStructs.DiceSimilarity(a[1][10], b[1][10])
            if value == 1 and a[0] != b[0]:
                value = 0.99
    return value, radius

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--metadata', required=True)
    p.add_argument('--train', required=True)
    p.add_argument('--query', required=True)
    p.add_argument('--query-metadata', help='Separate BDB2020+ CSV with pdbid and smiles columns')
    p.add_argument('--output', required=True)
    a = p.parse_args()
    train_ids, query_ids = read_ids(a.train), read_ids(a.query)
    if set(train_ids) & set(query_ids):
        raise ValueError('training and query IDs overlap')
    with open(a.metadata, newline='') as f:
        records = list(csv.DictReader(f))
    meta = {}
    for row in records:
        key = row.get('', '')
        if key in meta:
            raise ValueError(f'duplicate metadata ID: {key}')
        meta[key] = row
    query_meta = meta
    if a.query_metadata:
        with open(a.query_metadata, newline='') as f:
            external_rows = list(csv.DictReader(f))
        query_meta = {row['pdbid']: row for row in external_rows}
        if len(query_meta) != len(external_rows):
            raise ValueError('duplicate query metadata ID')
    absent = sorted((set(train_ids) - meta.keys()) | (set(query_ids) - query_meta.keys()))
    if absent:
        raise ValueError(f'{len(absent)} cohort IDs absent from metadata, examples: {absent[:5]}')
    molecules = {i: make_molecule(meta[i].get('smiles', '')) for i in train_ids}
    molecules.update({i: make_molecule(query_meta[i].get('smiles', '')) for i in query_ids})
    valid_train = [i for i in sorted(train_ids) if molecules[i] is not None]
    if not valid_train:
        raise ValueError('no valid training molecules')
    with open(a.output, 'w', newline='') as f:
        fields = ['query_id', 'nearest_training_id', 'similarity', 'radius2_similarity', 'radius_used', 'tie_count', 'eligible_training', 'status']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        fps2 = [molecules[i][1][2] for i in valid_train]
        for query_id in sorted(query_ids):
            query = molecules[query_id]
            if query is None:
                writer.writerow({'query_id': query_id, 'eligible_training': len(valid_train), 'status': 'invalid_smiles'})
                continue
            raw = DataStructs.BulkDiceSimilarity(query[1][2], fps2)
            best = -1.0
            ties = 0
            chosen = None
            for training_id, score in zip(valid_train, raw):
                value, radius = corrected_score(query, molecules[training_id], score)
                if value > best:
                    best, ties = value, 1
                    chosen = (training_id, score, radius)
                elif value == best:
                    ties += 1
            writer.writerow(dict(query_id=query_id, nearest_training_id=chosen[0], similarity=best,
                radius2_similarity=chosen[1], radius_used=chosen[2], tie_count=ties,
                eligible_training=len(valid_train), status='ok'))
    audit = dict(method='radius-2/4/10 1024-bit Morgan and Dice, canonical SMILES collision correction',
                 rdkit=rdBase.rdkitVersion, source_metadata_sha256=digest(a.metadata),
                 train_ids_sha256=digest(a.train), query_ids_sha256=digest(a.query),
                 query_metadata_sha256=digest(a.query_metadata) if a.query_metadata else None,
                 output_sha256=digest(a.output), training_total=len(train_ids),
                 training_valid=len(valid_train), query_total=len(query_ids),
                 invalid_training=sorted(i for i in train_ids if molecules[i] is None),
                 invalid_query=sorted(i for i in query_ids if molecules[i] is None),
                 note='Paper-aligned audit; historical software and input provenance not established.')
    Path(a.output + '.audit.json').write_text(json.dumps(audit, indent=2) + '\n')

if __name__ == '__main__':
    main()
