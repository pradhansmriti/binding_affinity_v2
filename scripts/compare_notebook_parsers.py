import sys,json,collections
from pathlib import Path
import numpy as np
from scipy.spatial import distance_matrix
sys.path.insert(0,'scripts')
from rfscore_descriptor import read_protein,read_ligand
n=json.loads(Path('data/source/RF_Score.ipynb').read_text())
env={'np':np,'distance_matrix':distance_matrix}
for i in (5,6): exec(''.join(n['cells'][i]['source']),env)
manifest=json.loads(Path('outputs/structure-audit.json').read_text())
counts=collections.Counter(); examples=collections.defaultdict(list)
for split, rows in manifest['entries'].items():
 for row in rows:
  p,l=(Path(x['path']) for x in row['files'])
  for kind, path, source, derived in [('protein',p,env['read_pdb_file'],read_protein),('ligand',l,env['read_ligand_sdf'],read_ligand)]:
   try:
    old_types,old_xyz=source(path); atoms=list(derived(path)); new_types=np.array([ (6,8,7,9,15,16,17,35,53)[t] for t,c in atoms]); new_xyz=np.array([c for t,c in atoms]);
    if not np.array_equal(old_types,new_types) or not np.array_equal(old_xyz,new_xyz):
     key=kind+'_mismatch'; counts[key]+=1
     if len(examples[key])<10: examples[key].append(row['id'])
    else: counts[kind+'_match']+=1
   except Exception as e:
    key=kind+'_error';counts[key]+=1
    if len(examples[key])<10:examples[key].append([row['id'],type(e).__name__,str(e)])
result={'summary':dict(counts),'examples':dict(examples),'note':'Comparison to pinned notebook readers, not validation of atom types or chemical correctness.'}
Path('outputs/parser-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
