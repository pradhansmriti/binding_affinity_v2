import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np

spec = importlib.util.spec_from_file_location("interaction_nearest", Path(__file__).resolve().parents[1] / "scripts" / "interaction_nearest.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InteractionNearestTests(unittest.TestCase):
    def test_weighted_jaccard_and_ties(self):
        q = np.zeros(256, dtype=np.int32)
        q[:2] = [2, 1]
        a = q.copy()
        b = np.zeros(256, dtype=np.int32)
        b[:2] = [1, 2]
        self.assertEqual(module.nearest(q, np.array([b, a, a]), ["other", "z", "a"]), ("a", 3, 3, 2))
        self.assertEqual(module.nearest(q, np.array([b]), ["other"]), ("other", 2, 4, 1))

    def test_zero_pair_is_undefined(self):
        q = np.zeros(256, dtype=np.int32)
        with self.assertRaises(ValueError):
            module.nearest(q, np.array([q]), ["empty"])

    def test_exclusion_and_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vectors.csv"
            header = ",".join(["id", *module.FEATURES])
            zeros = ",".join(["0"] * 256)
            path.write_text(f"{header}\nempty,{zeros}\n", encoding="utf-8")
            ids, rows, failures = module.read_vectors(path)
            self.assertEqual(ids, [])
            self.assertEqual(rows.shape, (0, 256))
            self.assertEqual(failures[0]["reason"], "empty_fingerprint")
            path.write_text(f"{header}\nempty,{zeros}\nempty,{zeros}\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                module.read_vectors(path)


if __name__ == "__main__":
    unittest.main()
