import importlib.util, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('media_assembly',Path(__file__).parents[1]/'scripts/media_assembly.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AssemblyHelpers(unittest.TestCase):
    def test_caption_phrases_preserve_every_word_and_fit_two_lines(self):
        text=Path('examples/dark-psychology/narration.txt').read_text()
        phrases=m.caption_phrases(text)
        self.assertEqual(' '.join(phrases).split(),text.split())
        for phrase in phrases:
            lines=m.caption_lines(phrase)
            self.assertLessEqual(len(lines),2)
            self.assertTrue(all(len(x)<=55 for x in lines))
    def test_timestamp_carries_milliseconds(self):
        self.assertEqual(m.stamp(59.9997),'00:01:00,000')

class EncodeFixture(unittest.TestCase):
    def test_real_encoding_creates_no_review_attestation(self):
        import tempfile,os,json
        from unittest.mock import patch
        from tests.test_autonomous_video import fixture,POLICY,CID
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root)
            (root/'self_qa.json').unlink()
            (root/'final.mp4').rename(root/'visual.mp4')
            (root/'standing_policy.json').write_text(json.dumps(POLICY))
            previous=Path.cwd()
            try:
                os.chdir(root);m.encode(Path('visual.mp4'),.5,CID)
            finally:os.chdir(previous)
            self.assertTrue((root/'final.mp4').stat().st_size>1000)
            self.assertFalse((root/'self_qa.json').exists())
            self.assertFalse((root/'verified_delivery.json').exists())
            self.assertIn('PlayResX: 320',(root/'captions.ass').read_text())
