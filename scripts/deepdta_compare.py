"""Compare saved RF predictions on precisely the DeepDTA-eligible complexes."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from affinity_units import rmse_to_energy_equivalent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deepdta',type=Path,required=True)
    parser.add_argument('--rf',type=Path,required=True)
    parser.add_argument('--cohort',required=True,choices=['test','val','BDB2020+'])
    args=parser.parse_args()
    target=pd.read_csv(args.deepdta)
    target['id']=target.id.str.upper()
    if target.id.duplicated().any(): raise ValueError('Duplicate DeepDTA identifier')
    results={}
    for seed in range(3):
        name=f'predictions-seed-{seed}.csv' if args.cohort=='BDB2020+' else f'{args.cohort}-seed-{seed}.csv'
        frame=pd.read_csv(args.rf/name)
        frame['id']=frame.id.str.upper()
        pair=target.merge(frame,on='id',validate='one_to_one')
        if len(pair)!=len(target): raise ValueError('RF does not contain every DeepDTA identifier')
        if not np.allclose(pair.label_p_affinity_x,pair.label_p_affinity_y,rtol=0,atol=1e-8):
            raise ValueError('Labels differ between models')
        y=pair.label_p_affinity_x.to_numpy(); pred=pair.prediction_p_affinity.to_numpy()
        rmse=float(np.sqrt(np.mean((y-pred)**2)))
        results[str(seed)]={'n':len(pair),'rmse_p':rmse,'energy_equivalent_rmse':rmse_to_energy_equivalent(rmse),'pearson':float(pearsonr(y,pred).statistic),'spearman':float(spearmanr(y,pred).statistic)}
    print(json.dumps(results,indent=2,sort_keys=True))

if __name__=='__main__':main()
