import subprocess, tempfile, unittest
from pathlib import Path


class CheckoutTests(unittest.TestCase):
    def test_fresh_checkout_retry_and_dirty_preservation(self):
        helper = Path('scripts/worker_checkout.sh').resolve()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'source'
            subprocess.run(['git', 'init', '-q', str(source)], check=True)
            (source/'content.txt').write_text('original')
            subprocess.run(['git', '-C', str(source), 'add', 'content.txt'], check=True)
            subprocess.run(['git', '-C', str(source), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                            'commit', '-qm', 'fixture'], check=True)
            commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
            dest = root/'checkout'
            cmd = ['bash', '-c', 'set -e; source "$1"; worker_checkout "$2" "$3" "$4"',
                   'checkout-test', str(helper), source.as_uri(), str(dest), commit]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual((dest/'content.txt').read_text(), 'original')
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            (dest/'content.txt').write_text('preserve my work')
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('Refusing to overwrite', result.stderr)
            self.assertEqual((dest/'content.txt').read_text(), 'preserve my work')
