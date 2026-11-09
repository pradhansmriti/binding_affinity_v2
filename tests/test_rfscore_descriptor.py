import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import rfscore_descriptor as rf


class RFScoreDescriptorTest(unittest.TestCase):
    def test_pair_order_and_strict_cutoff(self):
        protein = [(0, [0., 0., 0.]), (1, [12., 0., 0.])]
        ligand = [(2, [0., 0., 0.])]
        with patch.object(rf, 'read_protein', return_value=iter(protein)), patch.object(rf, 'read_ligand', return_value=iter(ligand)):
            result = rf.descriptor(Path('protein'), Path('ligand'))
        self.assertEqual(result.shape, (81,))
        self.assertEqual(result[0 * 9 + 2], 1)
        self.assertEqual(result[1 * 9 + 2], 0)
        self.assertEqual(result.sum(), 1)

    def test_rejects_nonfinite_coordinates(self):
        with patch.object(rf, 'read_protein', return_value=iter([(0, [np.nan, 0., 0.])])), patch.object(rf, 'read_ligand', return_value=iter([(0, [0., 0., 0.])])):
            with self.assertRaises(ValueError):
                rf.descriptor(Path('protein'), Path('ligand'))

if __name__ == '__main__':
    unittest.main()
