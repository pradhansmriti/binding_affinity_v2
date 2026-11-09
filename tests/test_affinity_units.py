import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from affinity_units import energy_factor, p_to_energy_equivalent, rmse_to_energy_equivalent


class AffinityUnitsTest(unittest.TestCase):
    def test_ten_nanomolar_binding_and_rmse(self):
        self.assertAlmostEqual(energy_factor(), 1.364247, places=5)
        self.assertAlmostEqual(p_to_energy_equivalent(8), -8 * energy_factor())
        self.assertAlmostEqual(rmse_to_energy_equivalent(1), energy_factor())

    def test_energy_error_matches_transformed_predictions(self):
        y, pred = [6., 8., 9.], [7., 7., 11.]
        p_rmse = math.sqrt(sum((a-b)**2 for a,b in zip(y,pred))/len(y))
        e_rmse = math.sqrt(sum((p_to_energy_equivalent(a)-p_to_energy_equivalent(b))**2 for a,b in zip(y,pred))/len(y))
        self.assertAlmostEqual(e_rmse, rmse_to_energy_equivalent(p_rmse))

    def test_invalid_inputs(self):
        for value in [0, -1, float('nan')]:
            with self.assertRaises(ValueError): energy_factor(value)
        with self.assertRaises(ValueError): rmse_to_energy_equivalent(-1)

if __name__ == '__main__': unittest.main()
