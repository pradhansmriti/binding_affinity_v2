"""Smoke-test a released IGN checkpoint on one upstream-prepared example.

This evaluates no benchmark and is not a reproduction metric. Only load pickle
and checkpoint files from a trusted upstream checkout.
"""
import argparse
import json
import sys
import tempfile
import types
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True, help='InteractionGraphNet master checkout')
    p.add_argument('--checkpoint', type=Path, required=True, help='LP-PDBBind IGN checkpoint')
    p.add_argument('--example', type=Path, required=True, help='Trusted upstream ligand/pocket pickle')
    args = p.parse_args()
    import torch
    import dgl
    import dgl.function as fn
    import dgllife
    from dgllife.utils import BaseBondFeaturizer
    # Compatibility with the old upstream API, avoiding modification of source.
    fn.copy_edge = fn.copy_e
    fn.src_mul_edge = fn.u_mul_e
    shim = types.ModuleType('dgl.data.chem')
    shim.BaseBondFeaturizer = BaseBondFeaturizer
    sys.modules['dgl.data.chem'] = shim
    sys.path.insert(0, str(args.source / 'codes'))
    from graph_constructor import graphs_from_mol_mul
    from model import DTIPredictorV4_V2
    import pickle
    ligand, pocket = pickle.loads(args.example.read_bytes())
    with tempfile.TemporaryDirectory(prefix='ign-smoke-') as tmp:
        graphs_from_mol_mul(str(args.example), 'example', 0, tmp, 12, '/')
        graph_path = Path(tmp) / 'example'
        if not graph_path.exists():
            raise RuntimeError('Upstream graph generator failed silently')
        data = pickle.loads(graph_path.read_bytes())
        model = DTIPredictorV4_V2(node_feat_size=40, edge_feat_size=21,
            num_layers=2, graph_feat_size=128, outdim_g3=128,
            d_FC_layer=128, n_FC_layer=2, dropout=.15, n_tasks=1)
        checkpoint = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
        model.load_state_dict(checkpoint['model_state_dict'], strict=True)
        model.eval()
        with torch.no_grad():
            result = float(model(data['g'], data['g3']).item())
        print(json.dumps({'prediction': result, 'ligand_atoms': ligand.GetNumAtoms(),
            'pocket_atoms': pocket.GetNumAtoms(), 'torch': torch.__version__,
            'dgl': dgl.__version__, 'dgllife': dgllife.__version__}, indent=2))

if __name__ == '__main__':
    main()
