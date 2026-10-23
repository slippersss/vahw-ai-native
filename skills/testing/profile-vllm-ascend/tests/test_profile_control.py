import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

spec = importlib.util.spec_from_file_location('profile_control', Path(__file__).resolve().parents[1]/'scripts/profile_control.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Handler(BaseHTTPRequestHandler):
    calls = []

    def do_POST(self):
        self.calls.append(self.path)
        self.send_response(200 if self.path == '/start_profile' else 503)
        self.end_headers()
        self.wfile.write(b'profiler response')

    def log_message(self, *args):
        pass


class ControlTest(unittest.TestCase):
    def test_success_and_failure_are_recorded_without_retry(self):
        Handler.calls = []
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            root = f'http://127.0.0.1:{server.server_port}'
            start = module.control(root, 'start_profile', 2)
            stop = module.control(root, 'stop_profile', 2)
            self.assertTrue(start['ok'])
            self.assertEqual(stop['status'], 503)
            self.assertFalse(stop['ok'])
            self.assertIn('profiler response', stop['body'])
            self.assertEqual(Handler.calls, ['/start_profile', '/stop_profile'])
            self.assertGreaterEqual(start['finished_wall_ns'], start['started_wall_ns'])
        finally:
            server.shutdown()
            server.server_close()
            worker.join()
        failed = module.control(root, 'start_profile', .2)
        self.assertFalse(failed['ok'])
        self.assertEqual(failed['completion'], 'unknown')

    def test_cli_from_another_directory_and_existing_output_does_not_send(self):
        Handler.calls = []
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            root = f'http://127.0.0.1:{server.server_port}'
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory)/'start.json'
                command = [sys.executable, str(Path(module.__file__).resolve()),
                           '--base-url', root, '--action', 'start_profile', '--output', str(output)]
                first = subprocess.run(command, cwd=directory, capture_output=True)
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertTrue(json.loads(output.read_text(encoding='utf-8'))['ok'])
                second = subprocess.run(command, cwd=directory, capture_output=True)
                self.assertNotEqual(second.returncode, 0)
                self.assertEqual(Handler.calls, ['/start_profile'])
        finally:
            server.shutdown()
            server.server_close()
            worker.join()


if __name__ == '__main__':
    unittest.main()
