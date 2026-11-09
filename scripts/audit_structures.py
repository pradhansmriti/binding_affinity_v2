"""Audit selected LP-PDBBind structure files; never silently drop samples."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('manifest', type=Path, help='Output of audit_metadata.py')
p.add_argument('roots', type=Path, nargs='+', help='Directories containing <id>/<id>_protein.pdb and <id>_ligand.sdf')
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
manifest = json.loads(a.manifest.read_text())
results = {}
for split, ids in manifest['identifiers'].items():
    entries = []
    for identifier in ids:
        candidates = [root / identifier for root in a.roots]
        complete = [d for d in candidates if (d / f'{identifier}_protein.pdb').is_file() and (d / f'{identifier}_ligand.sdf').is_file()]
        if len(complete) != 1:
            entries.append({'id': identifier, 'status': 'missing' if not complete else 'ambiguous', 'candidates': [str(d) for d in complete]})
            continue
        d = complete[0]
        files = [d / f'{identifier}_protein.pdb', d / f'{identifier}_ligand.sdf']
        entries.append({'id': identifier, 'status': 'ok', 'files': [{'path': str(f.resolve()), 'size': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]})
    results[split] = entries
summary = {s: {status: sum(e['status'] == status for e in entries) for status in ('ok', 'missing', 'ambiguous')} for s, entries in results.items()}
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps({'metadata_sha256': manifest['metadata_sha256'], 'roots': [str(r.resolve()) for r in a.roots], 'summary': summary, 'entries': results}, indent=2) + '\n')
print(json.dumps(summary, indent=2))
if any(v['missing'] or v['ambiguous'] for v in summary.values()):
    raise SystemExit(1)
