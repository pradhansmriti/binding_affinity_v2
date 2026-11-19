import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
fig,axes=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
for ax,(path,title) in zip(axes,[('outputs/deepdta-evaluation/test-predictions.csv','Test: 2,162'),('outputs/deepdta-evaluation/BDB2020+-predictions.csv','BDB2020+: 93'),('outputs/deepdta-bdb-notebook/BDB2020+-predictions.csv','BDB2020+: 114')]):
 d=pd.read_csv(path);x=d.label_p_affinity;y=d.checkpoint_prediction_unconfirmed_scale;lo=min(x.min(),y.min());hi=max(x.max(),y.max());ax.scatter(x,y,s=13,alpha=.55);ax.plot([lo,hi],[lo,hi],'--',color='gray');ax.set(title=title,xlabel='Measured p-affinity',ylabel='Checkpoint prediction (scale assumed)')
fig.savefig('outputs/deepdta-evaluation/predictions.png',dpi=160)
