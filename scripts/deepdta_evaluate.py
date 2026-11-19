"""Evaluate upstream DeepDTA checkpoint using released vocabulary and notebook encoding."""
import argparse
import csv
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from rdkit import Chem, rdBase
from scipy.stats import pearsonr, spearmanr
import torch


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--cohorts', nargs='+', default=['BDB2020+', 'test', 'val', 'train'], choices=['BDB2020+', 'test', 'val', 'train'])
    args = parser.parse_args()
    torch.set_num_threads(2)
    src = args.source / 'model_retraining/deepdta'
    spec = importlib.util.spec_from_file_location('upstream_deepdta_model', src/'model.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pdict = json.loads((src/'protein_dict.json').read_text())
    ldict = json.loads((src/'ligand_dict.json').read_text())
    model = module.DeepDTA(len(pdict)+1, len(ldict)+1, 32, 8, 8)
    model.load_state_dict(torch.load(src/'deepdta_retrain.pt', map_location='cpu', weights_only=True))
    model.eval()
    metadata = pd.read_csv(args.baseline/'data/source/LP_PDBBind.csv', index_col=0)
    metadata.index = metadata.index.str.upper()
    cohorts = {}
    for split in ('train', 'val', 'test'):
        path = args.baseline/'outputs/descriptors'/f'{split}.npz'
        ids = np.load(path, allow_pickle=False)['ids']
        df = metadata.loc[[str(x).upper() for x in ids]].copy()
        df['pdbid'] = df.index
        cohorts[split] = (df, 'seq', 'smiles', 'value')
    bdb = pd.read_csv(args.baseline/'data/structures/BDB2020+/BDB2020+.csv')
    bdb = bdb[bdb['accurate'] == True].copy()
    cohorts['BDB2020+'] = (bdb, 'seq', 'smiles', 'pKa')
    args.output.mkdir(parents=True, exist_ok=False)
    manifest={'source_commit':'cc363f80a6a696d562f290a87aa20173e60f6c52',
        'source_files_sha256': {p.name:sha(p) for p in [src/'model.py',src/'deepdta_retrain.pt',src/'protein_dict.json',src/'ligand_dict.json']},
        'input_sha256': {'metadata':sha(args.baseline/'data/source/LP_PDBBind.csv'), 'bdb':sha(args.baseline/'data/structures/BDB2020+/BDB2020+.csv'),
         **{f'{s}_descriptors':sha(args.baseline/'outputs/descriptors'/f'{s}.npz') for s in ('train','val','test')}},
        'script_sha256':sha(Path(__file__)), 'torch':torch.__version__, 'rdkit':rdBase.rdkitVersion, 'platform':platform.platform(),
        'notes':'Checkpoint inference only; no retraining. Notebook canonicalizes to isomeric SMILES. Sequences >2000 or SMILES >200 are excluded per arXiv S1.8; unknown tokens excluded. Output scale of checkpoint unconfirmed.'}
    allresults = {}
    for name in args.cohorts:
        frame, seqcol, smicol, labelcol = cohorts[name]
        if args.limit: frame=frame.iloc[:args.limit]
        included=[]; excluded=[]
        for _, row in frame.iterrows():
            identifier = str(row['pdbid']).upper(); reasons=[]
            seq = row[seqcol]; smiles=row[smicol]
            if not isinstance(seq,str) or not seq: reasons.append('missing sequence')
            if not isinstance(smiles,str) or not smiles: reasons.append('missing smiles'); canonical=''
            else:
                mol=Chem.MolFromSmiles(smiles)
                if mol is None: reasons.append('invalid smiles'); canonical=''
                else: canonical=Chem.MolToSmiles(mol, isomericSmiles=True)
            if isinstance(seq,str) and len(seq)>2000: reasons.append('sequence >2000')
            if len(canonical)>200: reasons.append('canonical isomeric smiles >200')
            if isinstance(seq,str) and set(seq)-pdict.keys(): reasons.append('unknown protein token: '+''.join(sorted(set(seq)-pdict.keys())))
            if set(canonical)-ldict.keys(): reasons.append('unknown ligand token: '+''.join(sorted(set(canonical)-ldict.keys())))
            if not np.isfinite(float(row[labelcol])): reasons.append('nonfinite label')
            if reasons: excluded.append({'id':identifier,'reasons':reasons}); continue
            included.append((identifier,seq,canonical,float(row[labelcol])))
        rows=[]
        with torch.inference_mode():
            for start in range(0,len(included),16):
                batch=included[start:start+16]
                proteins=torch.tensor([[pdict[c] for c in seq]+[pdict['dummy']]*(2000-len(seq)) for _,seq,_,_ in batch],dtype=torch.long)
                ligands=torch.tensor([[ldict[c] for c in smi]+[ldict['dummy']]*(200-len(smi)) for _,_,smi,_ in batch],dtype=torch.long)
                predictions=np.atleast_1d(model(proteins,ligands).numpy())
                rows.extend((id_,y,float(pred)) for (id_,seq,smi,y),pred in zip(batch,predictions))
        with (args.output/f'{name}-predictions.csv').open('w',newline='') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(['id','label_p_affinity','checkpoint_prediction_unconfirmed_scale']);w.writerows(rows)
        a=np.array([r[1] for r in rows]);b=np.array([r[2] for r in rows]); native=float(np.sqrt(np.mean((a-b)**2)))
        allresults[name]={'input_count':len(frame),'evaluated_count':len(rows),'excluded':excluded,'label_mean':float(np.mean(a)), 'prediction_mean':float(np.mean(b)),
            'rmse_assuming_prediction_p_affinity':native,'rmse_298k_energy_equivalent_if_p_affinity':native*1.364247013844294,
            'pearson':float(pearsonr(a,b).statistic),'spearman':float(spearmanr(a,b).statistic)}
        print(name, json.dumps(allresults[name]),flush=True)
    (args.output/'results.json').write_text(json.dumps(allresults,indent=2,sort_keys=True)+'\n')
    manifest['output_sha256']={p.name:sha(p) for p in sorted(args.output.iterdir())}
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True,default=str)+'\n')

if __name__=='__main__': main()
