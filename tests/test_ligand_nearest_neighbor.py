import unittest
from rdkit import DataStructs
from scripts.ligand_nearest_neighbor import corrected_score, make_molecule


class LigandSimilarityTests(unittest.TestCase):
    def test_identical_and_different_molecules(self):
        a = make_molecule('CCO')
        self.assertEqual(corrected_score(a, make_molecule('OCC')), (1.0, 10))
        score, radius = corrected_score(a, make_molecule('CCN'))
        self.assertEqual(radius, 2)
        self.assertGreaterEqual(score, 0)
        self.assertLess(score, 1)

    def test_bulk_and_scalar_dice_agree(self):
        query = make_molecule('CCO')
        ligands = [make_molecule(s) for s in ('CCO', 'CCN', 'c1ccccc1')]
        bulk = DataStructs.BulkDiceSimilarity(query[1][2], [x[1][2] for x in ligands])
        self.assertEqual(bulk, [corrected_score(query, x)[0] for x in ligands])

    def test_invalid_smiles(self):
        self.assertIsNone(make_molecule('not a molecule'))


if __name__ == '__main__':
    unittest.main()
