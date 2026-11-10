import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from run_baseline import load_split, metrics, sha


class BaselineChecks(unittest.TestCase):
    def test_descriptor_identity_and_checksum_are_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'train.npz'
            np.savez(path, ids=np.array(['a', 'b']), counts=np.ones((2, 81), dtype=int))
            summary = {'descriptor_files_sha256': {'train': sha(path)}}
            metadata = {i: {'new_split': 'train', 'CL1': 'True', 'covalent': 'False', 'value': str(v)} for i, v in [('a', 5), ('b', 7)]}
            ids, _, labels = load_split('train', metadata, summary, root, 2)
            self.assertEqual(ids, ['a', 'b'])
            np.testing.assert_array_equal(labels, [5, 7])
            metadata['b']['CL1'] = 'False'
            with self.assertRaisesRegex(ValueError, 'official cohort'):
                load_split('train', metadata, summary, root, 2)
            path.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                load_split('train', metadata, summary, root, 2)

    def test_metrics_keep_native_and_converted_scales(self):
        result = metrics(np.array([1., 2., 3.]), np.array([2., 3., 4.]))
        self.assertAlmostEqual(result['rmse_p_affinity'], 1.)
        self.assertAlmostEqual(result['rmse_energy_equivalent_kcal_mol'], 1.36425, places=4)
        self.assertAlmostEqual(result['pearson'], 1.)


if __name__ == '__main__':
    unittest.main()
