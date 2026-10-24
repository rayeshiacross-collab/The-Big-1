import socket, subprocess, sys, tempfile, unittest
from pathlib import Path
from src import worker_runtime as worker


class WorkerRuntimeTests(unittest.TestCase):
    def test_model_command_meets_hermes_context_floor(self):
        runtime = dict(model_server='server', model_path='weights', model='fixture', context_tokens=65536)
        argv = worker.model_command(runtime, 23456)
        self.assertEqual(argv[argv.index('-c')+1], '65536')
        self.assertEqual(argv[argv.index('--port')+1], '23456')
        self.assertEqual(argv[argv.index('-ctk')+1], 'q8_0')
        runtime['context_tokens'] = 16384
        with self.assertRaisesRegex(worker.WorkerError, '64000'):
            worker.model_command(runtime, 23456)

    def test_gateway_stop_is_scoped_and_failure_blocks(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool = root/'hermes-fixture'
            tool.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$HOME/args"\nexit "${FIXTURE_EXIT:-0}"\n')
            tool.chmod(0o700)
            env = {'HOME': str(root), 'PATH': os.environ['PATH']}
            worker.stop_gateway(str(tool), env, root/'stop.log')
            self.assertEqual((root/'args').read_text().splitlines(), ['--profile', 'default', 'gateway', 'stop', '--yes'])
            env['FIXTURE_EXIT'] = '1'
            with self.assertRaisesRegex(worker.WorkerError, 'shutdown failed'):
                worker.stop_gateway(str(tool), env, root/'stop.log')

    def test_worker_selects_an_unused_loopback_port(self):
        port = worker.free_loopback_port()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', port))

    def test_model_readiness_path_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'v1').mkdir()
            (root/'v1/models').write_text('{"data": []}')
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            argv = [sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1', '--directory', str(root)]
            with worker.managed_service(argv, f'http://127.0.0.1:{port}/v1/models', root/'server.log', timeout=5) as process:
                self.assertIsNone(process.poll())

    def test_body_network_failure_is_not_swallowed(self):
        import requests
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            argv = [sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1']
            with self.assertRaisesRegex(requests.ConnectionError, 'body failed'):
                with worker.managed_service(argv, f'http://127.0.0.1:{port}/', root/'server.log', timeout=5):
                    raise requests.ConnectionError('body failed')

    def test_managed_service_becomes_ready_and_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            argv = [sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1', '--directory', str(root)]
            with worker.managed_service(argv, f'http://127.0.0.1:{port}/', root/'server.log', timeout=5) as process:
                self.assertIsNone(process.poll())
            self.assertIsNotNone(process.poll())

    def test_early_process_failure_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(worker.WorkerError, 'exited'):
                with worker.managed_service([sys.executable, '-c', 'raise SystemExit(7)'], 'http://127.0.0.1:1/', Path(tmp)/'log', timeout=2):
                    self.fail('Unready service must never yield')

    def test_startup_timeout_stops_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pid = root/'pid'
            argv = [sys.executable, '-c', f'import os,time;open({str(pid)!r},"w").write(str(os.getpid()));time.sleep(10)']
            with self.assertRaisesRegex(worker.WorkerError, 'ready'):
                with worker.managed_service(argv, 'http://127.0.0.1:1/', root/'log', timeout=.5):
                    self.fail('Unready service must never yield')
            if pid.exists():
                import os
                with self.assertRaises(ProcessLookupError):
                    os.kill(int(pid.read_text()), 0)

    def test_tool_proof_rejects_claim_without_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            proof = Path(tmp)/'proof.txt'
            with self.assertRaisesRegex(worker.WorkerError, 'tool-use'):
                worker.require_tool_proof(proof, 'nonce')
            proof.write_text('wrong')
            with self.assertRaises(worker.WorkerError):
                worker.require_tool_proof(proof, 'nonce')
            proof.write_text('nonce')
            worker.require_tool_proof(proof, 'nonce')
