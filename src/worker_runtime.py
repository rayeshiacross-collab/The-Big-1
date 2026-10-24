"""Own a local model's lifetime and execute real Hermes acceptance/production."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import uuid
from urllib.parse import urlsplit, urlunsplit

import requests

from . import autonomous_video as av


class WorkerError(RuntimeError):
    pass


@contextmanager
def managed_service(argv, url, log_path, *, timeout=60, env=None):
    """Wait for HTTP readiness; reap the process on every exit path."""
    parsed = urlsplit(url)
    if parsed.query or parsed.fragment:
        raise WorkerError('Readiness URL must not contain a query or fragment')
    av.endpoint(urlunsplit((parsed.scheme, parsed.netloc, '', '', '')))
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open('w', encoding='utf-8') as log:
        process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, env=env)
        try:
            with requests.Session() as session:
                session.trust_env = False
                deadline = time.monotonic() + timeout
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        raise WorkerError(f'Local service exited with code {process.returncode}; see {log_path}')
                    try:
                        response = session.get(url, timeout=min(1, max(.05, deadline-time.monotonic())), allow_redirects=False)
                    except requests.RequestException:
                        response = None
                    if response is not None and response.status_code == 200:
                        yield process
                        return
                    time.sleep(.1)
                raise WorkerError(f'Local service did not become ready; see {log_path}')
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
            else:
                process.wait()


def require_tool_proof(path, nonce):
    if not path.is_file() or path.read_text(encoding='utf-8').strip() != nonce:
        raise WorkerError('Hermes did not produce the required live tool-use proof')


def socket_check():
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM):
            pass
    except OSError as exc:
        raise WorkerError('Hermes requires Unix-domain sockets; this host denies them') from exc


def free_loopback_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def model_command(runtime, port):
    context = runtime.get('context_tokens', 0)
    if type(context) is not int or context < 64000:
        raise WorkerError('Hermes requires at least 64000 model context tokens')
    return [runtime['model_server'], '-m', runtime['model_path'], '--alias', runtime['model'],
            '--host', '127.0.0.1', '--port', str(port), '--jinja', '--reasoning', 'off',
            '-c', str(context), '-b', '256', '-ub', '128', '-t', '4', '--parallel', '1',
            '--flash-attn', 'on', '-ctk', 'q8_0', '-ctv', 'q8_0']


def stop_gateway(executable, env, log_path):
    with log_path.open('w', encoding='utf-8') as log:
        result = subprocess.run([executable, '--profile', 'default', 'gateway', 'stop', '--yes'],
                                env=env, stdout=log, stderr=subprocess.STDOUT, timeout=60)
    if result.returncode:
        raise WorkerError('Isolated Hermes gateway shutdown failed; see '+str(log_path))


def stop_production_gateways(executable, output):
    root = (output/'production').resolve()
    if not root.exists():
        return
    for home in root.glob('*/*/attempt_*/isolated-home'):
        if home.is_symlink() or not home.resolve().is_relative_to(root):
            raise WorkerError('Refusing a production gateway home outside this job')
        stop_gateway(executable, av.isolated_env(home), home.parent/'gateway-stop.log')


def runtime_check(runtime, url, output):
    """Require a real model-backed tool call, not a model's verbal claim."""
    socket_check()
    nonce = uuid.uuid4().hex
    proof = output/'tool-proof.txt'
    query = output/'runtime-request.txt'
    query.write_text(
        'Use your terminal or file tool to create the UTF-8 file '+str(proof)+
        ' containing exactly '+nonce+'. Then read it with a tool and report its contents. '
        'This is a runtime acceptance test, not a media-production pass.', encoding='utf-8')
    cmd = [runtime['hermes_executable'], 'chat', '--safe-mode', '--provider', 'custom',
           '--base-url', url, '--api-key', 'local-no-secret', '--model', runtime['model'],
           '--toolsets', 'terminal,file', '--oneshot', '--quiet', '--max-turns', '6',
           '--query-file', str(query)]
    env = av.isolated_env(output/'hermes-home')
    with (output/'hermes-runtime.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen(cmd, cwd=output, env=env,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=600)
        finally:
            # Hermes may launch a gateway; it belongs to this bounded job too.
            try:
                import signal
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            if process.poll() is None:
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=10)
            # The official gateway detaches from the CLI's process group.
            stop_gateway(runtime['hermes_executable'], env, output/'gateway-stop.log')
    if code:
        raise WorkerError(f'Hermes runtime check exited {code}; see hermes-runtime.log')
    require_tool_proof(proof, nonce)


def run(runtime_path, output, *, script=None, policy=None, tools_path=None, content_id=None):
    runtime = json.loads(Path(runtime_path).read_text(encoding='utf-8'))
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {'status': 'STARTING', 'published': False, 'production_video_complete': False}
    report_path = output/'worker_status.json'
    av.save_json(report_path, report)
    try:
        socket_check()
        port = free_loopback_port()
        url = f'http://127.0.0.1:{port}/v1'
        argv = model_command(runtime, port)
        with managed_service(argv, url+'/models', output/'model-server.log',
                             env=av.isolated_env(output/'model-home')):
            with requests.Session() as session:
                session.trust_env = False
                response = session.get(url+'/models', timeout=10, allow_redirects=False)
                response.raise_for_status()
                if runtime['model'] not in {m['id'] for m in response.json()['data']}:
                    raise WorkerError('New model service did not advertise the configured model')
            runtime_check(runtime, url, output)
            report.update(status='RUNTIME_READY', live_tool_use=True)
            av.save_json(report_path, report)
            if script is not None:
                if not all((policy, tools_path, content_id)):
                    raise WorkerError('Production requires script, policy, tools and content ID')
                tools = av.config(tools_path, av.TOOL_KEYS)
                tools.update(hermes_executable=runtime['hermes_executable'],
                             model=runtime['model'], model_base_url=url)
                configured = output/'local_tools.json'
                av.save_json(configured, tools)
                try:
                    report['production'] = av.produce(content_id, script, policy, configured, output=output/'production')
                finally:
                    stop_production_gateways(runtime['hermes_executable'], output)
                report.update(status=report['production']['status'], production_video_complete=True)
        return report
    except Exception as exc:
        report.update(status='BLOCKED_OR_FAILED', error_type=type(exc).__name__, reason=str(exc))
        raise
    finally:
        av.save_json(report_path, report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--script', type=Path)
    parser.add_argument('--policy', type=Path)
    parser.add_argument('--tools', type=Path)
    parser.add_argument('--content-id')
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.runtime, args.output, script=args.script, policy=args.policy,
                             tools_path=args.tools, content_id=args.content_id), indent=2))
    except (WorkerError, av.ProductionError) as exc:
        parser.exit(2, str(exc)+'\n')


if __name__ == '__main__':
    main()
