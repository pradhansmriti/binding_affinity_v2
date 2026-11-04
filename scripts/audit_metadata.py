"""Audit the official metadata without third-party dependencies or training."""
import argparse, collections, csv, hashlib, json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('csv', type=Path)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
rows = list(csv.DictReader(a.csv.open()))
id_key = next(iter(rows[0]))
ids = [r[id_key] for r in rows]
assert len(ids) == len(set(ids)), 'Duplicate complex identifiers'
def selected(split, level):
    return sorted(r[id_key] for r in rows if r['new_split'] == split and r[level] == 'True' and r['covalent'] == 'False')
manifests = {s: selected(s, 'CL1' if s == 'train' else 'CL2') for s in ['train', 'val', 'test']}
for s, ids_s in manifests.items():
    assert ids_s, f'Empty {s}'
    assert all(not(set(ids_s) & set(v)) for k,v in manifests.items() if k != s)
result = {'metadata_sha256': hashlib.sha256(a.csv.read_bytes()).hexdigest(), 'rows': len(rows),
          'raw_split_counts': dict(collections.Counter(r['new_split'] or 'unassigned' for r in rows)),
          'filter': 'noncovalent; CL1 train; CL2 validation/test',
          'counts': {s:len(v) for s,v in manifests.items()}, 'identifiers': manifests}
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k != 'identifiers'}, indent=2))
