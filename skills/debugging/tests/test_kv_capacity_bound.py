import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('kv_capacity_bound', Path(__file__).resolve().parents[1]/'scripts/kv_capacity_bound.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CapacityTest(unittest.TestCase):
    def document(self):
        return dict(block_bytes=1024, independent_allocations=True, pool_blocks=9,
                    groups=[dict(name='full', block_tokens=4),
                            dict(name='window', block_tokens=4, window_tokens=4)],
                    checks=[dict(label='before reclaim', requests=[dict(id='a', allocation_end=16, reclaim_frontier=8)]),
                            dict(label='after reclaim', requests=[dict(id='a', allocation_end=16, reclaim_frontier=16)])])

    def test_reclamation_and_guard_reserves(self):
        doc = self.document()
        doc['checks'][0]['reserved_blocks'] = 2
        result = module.evaluate(doc)
        # Before: full4 + window3 + null1 + reserve2 =10; after:4+1+1=6.
        self.assertEqual([r['required_blocks'] for r in result['checks']], [10, 6])
        self.assertEqual(result['peak']['margin_blocks'], -1)

    def test_rejects_unsupported_or_inconsistent_states(self):
        doc = self.document()
        doc['independent_allocations'] = False
        with self.assertRaises(ValueError):
            module.evaluate(doc)
        doc = self.document()
        doc['checks'][0]['requests'][0]['reclaim_frontier'] = 17
        with self.assertRaises(ValueError):
            module.evaluate(doc)

    def test_cli_example_from_reference(self):
        reference = Path(__file__).resolve().parents[1]/'references/kv-admission-and-lifecycle.md'
        text = reference.read_text(encoding='utf-8')
        example = text.split('```json\n', 1)[1].split('\n```', 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'case.json'
            path.write_text(example, encoding='utf-8')
            run = subprocess.run([sys.executable, str(Path(module.__file__).resolve()), str(path)],
                                 cwd=directory, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(result['peak']['required_blocks'], 10)
            self.assertEqual(result['peak']['margin_blocks'], -1)


if __name__ == '__main__':
    unittest.main()
