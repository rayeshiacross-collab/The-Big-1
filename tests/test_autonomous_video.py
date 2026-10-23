"""Synthetic orchestration/media fixtures. No Hermes perception or production claimed."""
import hashlib,json,os,shutil,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from src import autonomous_video as av
from src.self_qa import VIDEO_CHECKS

CID='psych-20261022-autonomous-fixture'
SCRIPT='One clear sentence.'
POLICY=dict(brand='Fixture',visual_style='Test only',format='short',dimensions=[320,568],voice=dict(engine='fixture',voice_id='fixture'),language='en')
REGISTRY=[dict(name='video-fixture',capability='video_review'),dict(name='audio-fixture',capability='audio_review')]

def dump(path,value): path.write_text(json.dumps(value))
def fixture(folder,static=False):
    """Create real test media plus deliberately synthetic review attestations."""
    folder.mkdir(parents=True,exist_ok=True)
    source='color=c=black:s=320x568:r=24' if static else 'testsrc2=size=320x568:rate=24'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',source,'-f','lavfi','-i','sine=frequency=440:sample_rate=24000','-t','2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(folder/'final.mp4')],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=440:sample_rate=24000','-t','2',str(folder/'narration.wav')],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=red:s=320x568','-frames:v','1',str(folder/'thumbnail.jpg')],check=True)
    (folder/'captions.srt').write_text('1\n00:00:00,000 --> 00:00:02,000\nOne clear sentence.\n')
    (folder/'narration.txt').write_text(SCRIPT)
    digest=hashlib.sha256(SCRIPT.encode()).hexdigest()
    dump(folder/'hermes_plan.json',dict(creator='Hermes',source_sha256=digest,voice=POLICY['voice'],scenes=[dict(id='s1',narration=SCRIPT,action='Synthetic fixture motion',prompt='Synthetic test pattern')]))
    dump(folder/'youtube.json',dict(title='Fixture',description='Synthetic fixture, not a real video',tags=['fixture'],hashtags=['fixture'],audience='NOT_MADE_FOR_KIDS',synthetic_media=True,paid_promotion=False))
    mapping=dict(video='final.mp4',audio='narration.wav',captions='captions.srt',thumbnail='thumbnail.jpg',metadata='youtube.json',plan='hermes_plan.json',narration='narration.txt')
    dump(folder/'production_manifest.json',dict(content_id=CID,source_sha256=digest,files=mapping))
    perception=[]
    for modality in ('video','audio'):
        name=modality+'_tool_receipt.json'
        dump(folder/name,dict(artifact_sha256=av.sha(folder/mapping[modality]),duration_seconds=2,reviewed_seconds=2,coverage=[[0,2]],fixture=True))
        perception.append(dict(path=name,sha256=av.sha(folder/name),tool=modality+'-fixture',modality=modality))
    dump(folder/'self_qa.json',dict(reviewer='Hermes',content_id=CID,stage='video',reviewed_at='2026-10-22T23:30:00-05:00',verdict='PASS',unresolved_issues=[],watched_full_video=True,listened_full_audio=True,artifact_sha256={v:av.sha(folder/v) for v in mapping.values()},checks={k:dict(status='PASS',evidence='Synthetic test fixture only') for k in VIDEO_CHECKS},perception_evidence=perception))

class ContractTests(unittest.TestCase):
    def test_no_scene_suggestions_in_initial_request(self):
        p=av.request_text(CID,'digest',POLICY,{'local_tools':[]})
        self.assertIn('Creative input is input_script.txt ONLY',p)
        for old in ('hourglass','phone face down','empty chair','loyalty test'):
            self.assertNotIn(old,p)
    def test_remote_endpoints_rejected(self):
        for url in ('http://example.com','https://127.0.0.1','http://127.0.0.1@evil.test','http://127.0.0.1/?x=1'):
            with self.assertRaises(av.ProductionError): av.endpoint(url)
    def test_coverage_and_caption_source(self):
        self.assertFalse(av.coverage([[0,1],[1.5,2]],2));self.assertTrue(av.coverage([[0,1],[1,2]],2))
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.srt';p.write_text('1\n00:00:00,000 --> 00:00:02,000\nWrong words.\n')
            with self.assertRaises(av.ProductionError): av.check_captions(p,SCRIPT,2)
    def test_credentials_not_in_worker_environment(self):
        with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,OPENAI_API_KEY='secret',ANTHROPIC_API_KEY='secret',HTTP_PROXY='proxy'):
            env=av.isolated_env(Path(t))
            self.assertNotIn('OPENAI_API_KEY',env);self.assertNotIn('HTTP_PROXY',env)
            self.assertEqual(env['ALLOW_PAID_APIS'],'0')
    def test_no_legacy_plan_input(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'policy.json';dump(p,{**POLICY,'scenes':['operator idea']})
            with self.assertRaises(av.ProductionError): av.config(p,av.POLICY_KEYS)
    def test_absent_hermes_stops_and_records_machine_use(self):
        with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,MACHINE_LEDGER_PATH=str(Path(t)/'usage.jsonl')):
            root=Path(t);(root/'s.txt').write_text(SCRIPT);dump(root/'policy.json',POLICY);dump(root/'tools.json',dict(model='local',model_base_url='http://127.0.0.1:11434',hermes_executable='nonexistent-hermes-fixture'))
            with self.assertRaises(av.ProductionError): av.produce(CID,root/'s.txt',root/'policy.json',root/'tools.json',output=root/'out')
            status=json.loads(next((root/'out').rglob('run_status.json')).read_text())
            self.assertEqual(status['status'],'BLOCKED_OR_FAILED');self.assertFalse(status['published'])
            self.assertIn('FAILED',(root/'usage.jsonl').read_text())

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required for real fixture decoding')
class MediaTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
        fixture(self.root)
    def test_real_fixture_package_and_all_artifacts(self):
        r=av.validate_package(self.root,CID,SCRIPT,POLICY,REGISTRY)
        self.assertEqual(r['status'],'READY_FOR_OWNER_INSPECTION');self.assertFalse(r['published'])
    def test_missing_full_audio_perception_rejected(self):
        q=json.loads((self.root/'self_qa.json').read_text());q['perception_evidence']=q['perception_evidence'][:1];dump(self.root/'self_qa.json',q)
        with self.assertRaises(av.ProductionError): av.validate_package(self.root,CID,SCRIPT,POLICY,REGISTRY)
    def test_static_rejected(self):
        fixture(self.root,static=True)
        with self.assertRaisesRegex(av.ProductionError,'Static'): av.validate_package(self.root,CID,SCRIPT,POLICY,REGISTRY)
    def test_repair_loop_is_real_orchestration_not_a_completed_hermes_run(self):
        cfg=self.root/'cfg';cfg.mkdir();(cfg/'script.txt').write_text(SCRIPT);dump(cfg/'policy.json',POLICY);dump(cfg/'tools.json',dict(model='fixture',model_base_url='http://127.0.0.1:11434',local_tools=REGISTRY,max_repair_attempts=1))
        calls=[]
        def fake_agent(exe,url,tools,prompt,folder):
            calls.append(prompt);fixture(folder,static=len(calls)==1)
        with patch.dict(os.environ,MACHINE_LEDGER_PATH=str(cfg/'machine.jsonl')),patch.object(av,'doctor',return_value=('fixture','http://127.0.0.1/v1')),patch.object(av,'invoke',side_effect=fake_agent):
            r=av.produce(CID,cfg/'script.txt',cfg/'policy.json',cfg/'tools.json',output=cfg/'out')
        self.assertEqual(len(calls),2);self.assertIn('Static/near-static',calls[1]);self.assertEqual(r['status'],'READY_FOR_OWNER_INSPECTION')
        self.assertTrue(list((cfg/'out').rglob('validation_failure.json')))

if __name__=='__main__': unittest.main()
