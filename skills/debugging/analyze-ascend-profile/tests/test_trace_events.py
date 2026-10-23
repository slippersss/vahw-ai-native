import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('trace_events', Path(__file__).resolve().parents[1]/'scripts/trace_events.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TraceTest(unittest.TestCase):
    def test_boundaries_wrappers_and_gzip(self):
        expected = [{'name': '核函数]\\"', 'args': {'shape': [12, 345], 'text': 'x'*100}},
                    {'name': 'synchronize', 'ts': 1.25e12, 'dur': 0}]
        documents = [expected, {'metadata': {'traceEvents': 'not the array'},
                                'traceEvents': expected, 'tail': 12345}]
        with tempfile.TemporaryDirectory() as directory:
            for compressed in (False, True):
                for document in documents:
                    path = Path(directory)/('trace.json.gz' if compressed else 'trace.json')
                    payload = json.dumps(document, ensure_ascii=False)
                    if compressed:
                        with gzip.open(path, 'wt', encoding='utf-8') as handle:
                            handle.write(payload)
                    else:
                        path.write_text('\ufeff'+payload, encoding='utf-8')
                    for size in (1, 7, 64, 1024):
                        self.assertEqual(list(module.events(path, size)), expected)

    def test_rejects_truncation_and_wrong_structure(self):
        invalid = ['[{"name":"x"}', '[{},]', '{"traceEvents":[]',
                   '{"metadata":[]}', '{"traceEvents":[],"traceEvents":[]}',
                   '[1]', '[] []', '{"traceEvents":[],"tail":12oops}']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.json'
            for payload in invalid:
                path.write_text(payload, encoding='utf-8')
                with self.subTest(payload=payload), self.assertRaises(ValueError):
                    list(module.events(path, 3))

    def test_cli_keeps_source_index_when_filtering(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'trace.json'
            path.write_text(json.dumps({'traceEvents': [{'name': 'other'}, {'name': 'synchronize'}]}), encoding='utf-8')
            run = subprocess.run([sys.executable, str(Path(module.__file__).resolve()),
                                  str(path), '--contains', 'synchronize', '--limit', '1'],
                                 cwd=directory, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            record = json.loads(run.stdout)
            self.assertEqual(record['event_index'], 1)
            self.assertEqual(record['source'], str(path))


if __name__ == '__main__':
    unittest.main()
