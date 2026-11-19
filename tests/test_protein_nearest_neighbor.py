import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from scripts.protein_nearest_neighbor import aligner, identity, normalise

class ProteinNearestTests(unittest.TestCase):
    def test_identical_and_gap(self):
        a = aligner()
        self.assertEqual(identity(a, 'ACDE', 'ACDE'), (4, 4))
        self.assertEqual(identity(a, 'ACDE', 'ACD'), (3, 4))

    def test_explicit_delimiter_policy(self):
        self.assertEqual(normalise('AC:DE', 'reject'), (None, 'unresolved_chain_separator'))
        self.assertEqual(normalise('AC:DE', 'strip'), ('ACDE', 'ok'))
        self.assertEqual(normalise('AC?DE', 'strip'), (None, 'unsupported_residue'))

    def test_partial_maximum_and_cross_category(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with (root / 'meta.csv').open('w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=['', 'seq', 'type'])
                w.writeheader()
                w.writerows([{'':'a', 'seq':'ACDE', 'type':'x'},
                             {'':'b', 'seq':'AC:DE', 'type':'x'},
                             {'':'c', 'seq':'ACDE', 'type':'y'},
                             {'':'q', 'seq':'ACDE', 'type':'x'}])
            for name, values in [('train', ['a', 'b', 'c']), ('query', ['q'])]:
                with (root / (name + '.csv')).open('w', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=['id']); w.writeheader()
                    w.writerows({'id':v} for v in values)
            for policy, expected_ties, expected_status in [('reject', '1', 'partial'), ('strip', '2', 'ok')]:
                output = root / (policy + '.csv')
                subprocess.run([sys.executable, 'scripts/protein_nearest_neighbor.py',
                                '--metadata', str(root / 'meta.csv'), '--train', str(root / 'train.csv'),
                                '--query', str(root / 'query.csv'), '--chain-policy', policy,
                                '--output', str(output)], check=True)
                with output.open() as f:
                    row = next(csv.DictReader(f))
                self.assertEqual(row['similarity'], '1.0')
                self.assertEqual(row['tie_count'], expected_ties)
                self.assertEqual(row['status'], expected_status)

if __name__ == '__main__':
    unittest.main()
