"""Extract protein-major RF-Score atom-pair counts from prepared PDB/SDF files."""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cdist


# Order and protein atom-name rules from the pinned upstream notebook.
ELEMENTS = ("C", "O", "N", "F", "P", "S", "Cl", "Br", "I")
PROTEIN_NAMES = (
    "C CA CB CD CD1 CD2 CE CE1 CE2 CE3 CG CG1 CG2 CH2 CZ CZ2 CZ3",
    "O OD1 OD2 OE1 OE1A OE1B OE2 OG OG1 OH OXT",
    "N NE NE1 NE2 NE2A NE2B ND1 ND2 NH1 NH2 NZ",
    "F", "P", "S SD SG", "Cl CL", "Br BR", "I",
)
PROTEIN_TYPES = {
    name: index for index, names in enumerate(PROTEIN_NAMES) for name in names.split()
}
LIGAND_TYPES = {symbol: index for index, symbol in enumerate(ELEMENTS)}


def read_protein(path):
    for line in path.read_text().splitlines():
        if line.startswith("ATOM  ") and line[76:78].strip() != "H":
            name = line[12:16].strip()
            if name in PROTEIN_TYPES:
                yield PROTEIN_TYPES[name], [float(line[i:i + 8]) for i in (30, 38, 46)]


def read_ligand(path):
    lines = path.read_text().splitlines()
    if len(lines) < 4 or not lines[3].rstrip().endswith("V2000"):
        raise ValueError(f"Expected V2000 SDF: {path}")
    atom_count = int(lines[3][:3])
    if atom_count <= 0 or len(lines) < 4 + atom_count:
        raise ValueError(f"Invalid atom count: {path}")
    for line in lines[4:4 + atom_count]:
        element = line[31:34].strip()
        if element in LIGAND_TYPES:
            yield LIGAND_TYPES[element], [float(line[i:i + 10]) for i in (0, 10, 20)]


def descriptor(protein, ligand):
    protein_atoms = list(read_protein(protein))
    ligand_atoms = list(read_ligand(ligand))
    if not protein_atoms or not ligand_atoms:
        raise ValueError("Protein and ligand must both contain supported atoms")
    p_types, p_xyz = map(np.asarray, zip(*protein_atoms))
    l_types, l_xyz = map(np.asarray, zip(*ligand_atoms))
    if not np.isfinite(p_xyz).all() or not np.isfinite(l_xyz).all():
        raise ValueError("Nonfinite coordinates")
    counts = np.zeros(81, dtype=np.int64)
    for start in range(0, len(p_types), 512):
        p_idx, l_idx = np.where(cdist(p_xyz[start:start + 512], l_xyz, "sqeuclidean") < 144)
        counts += np.bincount(9 * p_types[start + p_idx] + l_types[l_idx], minlength=81)
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protein", type=Path)
    parser.add_argument("ligand", type=Path)
    args = parser.parse_args()
    counts = descriptor(args.protein, args.ligand)
    print(json.dumps({"elements": ELEMENTS, "cutoff_angstrom": 12,
                      "counts_protein_major": counts.tolist(),
                      "total_contacts": int(counts.sum())}, indent=2))


if __name__ == "__main__":
    main()
