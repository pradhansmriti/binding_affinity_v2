import json, os
from pathlib import Path
import numpy as np
from scipy.spatial import distance_matrix
n=json.loads(Path('data/source/RF_Score.ipynb').read_text())
env={'np':np,'os':os,'distance_matrix':distance_matrix}
for i in (5,6,7): exec(''.join(n['cells'][i]['source']),env)
a=np.load('outputs/descriptors/train.npz'); ids=a['ids']; counts=a['counts']
manifest=json.loads(Path('outputs/structure-audit.json').read_text())
entries={e['id']:e for e in manifest['entries']['train']}
selected=[0,1,2,3,4,len(ids)//4,len(ids)//2,3*len(ids)//4,len(ids)-2,len(ids)-1]
for i in selected:
 identifier=str(ids[i]); directory=Path(entries[identifier]['files'][0]['path']).parent.parent
 reference=env['RF_descriptor']([identifier],str(directory))[identifier].reshape(-1)
 if not np.array_equal(reference,counts[i]): raise SystemExit('Mismatch: '+identifier)
print('Verified 81 features against author notebook for',len(selected),'train complexes:',', '.join(str(ids[i]) for i in selected))
