"""Check RF-Score atom readers across a complete structure manifest."""
import argparse
import json
import math
from pathlib import Path
from rfscore_descriptor import read_ligand, read_protein

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('manifest', type=Path)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
manifest = json.loads(a.manifest.read_text())
summary = {}
failures = []
for split, entries in manifest['entries'].items():
    passed = 0
    for entry in entries:
        if entry['status'] != 'ok':
            failures.append({'id': entry['id'], 'split': split, 'error': 'missing or ambiguous pair'})
            continue
        try:
            paths = [Path(item['path']) for item in entry['files']]
            for name, atoms in [('protein', list(read_protein(paths[0]))), ('ligand', list(read_ligand(paths[1])))]:
                if not atoms or not all(math.isfinite(x) for _, xyz in atoms for x in xyz):
                    raise ValueError(f'{name}: no supported atoms or nonfinite coordinates')
            passed += 1
        except (ValueError, IndexError, OSError, UnicodeError) as exc:
            failures.append({'id': entry['id'], 'split': split, 'error': str(exc)})
    summary[split] = {'checked': len(entries), 'passed': passed, 'failed': len(entries) - passed}
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps({'metadata_sha256': manifest['metadata_sha256'], 'summary': summary, 'failures': failures}, indent=2) + '\n')
print(json.dumps({'summary': summary, 'failures': failures[:10]}, indent=2))
if failures:
    raise SystemExit(1)
