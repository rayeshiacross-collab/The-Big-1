import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
from concurrent.futures import ProcessPoolExecutor
from src import config, handoff, ledger, drive_storage, runner, local_model, validators
from src.safety import confined

CID = 'psych-20261022-test'
RID = '20261022-0600-central'
def attempt_claim(args):
    root, = args
    config.LEDGER_PATH = ledger.LEDGER_PATH = Path(root)/'ledger'
    config.HANDOFF_PATH = handoff.HANDOFF_PATH = Path(root)/'handoff'
    config.OUTPUT_PATH = drive_storage.OUTPUT_PATH = runner.OUTPUT_PATH = Path(root)/'output'
    try: handoff.claim(CID, 'psychology'); return True
    except FileExistsError: return False

class HubTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for mod, name, val in [(config,'LEDGER_PATH','ledger'),(ledger,'LEDGER_PATH','ledger'),(config,'HANDOFF_PATH','handoff'),(handoff,'HANDOFF_PATH','handoff'),(config,'OUTPUT_PATH','output'),(drive_storage,'OUTPUT_PATH','output'),(runner,'OUTPUT_PATH','output')]:
            p=patch.object(mod,name,self.root/val);p.start();self.addCleanup(p.stop)
        self.h = handoff.Handoff(RID,CID,'psychology','Test angle',required_assets=['flagship.txt','short1.txt','short2.txt','short3.txt','companion.txt']);self.h.save()
    def test_claim_race_processes(self):
        with ProcessPoolExecutor(4) as pool:
            self.assertEqual(sum(pool.map(attempt_claim, [(str(self.root),)]*8)), 1)
        self.assertEqual(len(ledger.read_events(RID)),1)
    def test_wrong_lane_no_mutation(self):
        with self.assertRaises(PermissionError): handoff.claim(CID,'omni')
        self.assertEqual(ledger.read_events(RID),[])
    def test_approved_reclaim_preserves_ledger(self):
        p=ledger.ledger_file(RID);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(dict(content_id=CID,status='RELEASE_APPROVED'))+'\n'); before=p.read_bytes()
        with self.assertRaises(RuntimeError): handoff.claim(CID,'psychology')
        self.assertEqual(p.read_bytes(),before)
    def test_ids_and_paths(self):
        for v in ['../../x','/tmp/x','psych-20260230-bad','psych-20261022-x/../../y']:
            with self.assertRaises(ValueError): drive_storage.save_text(v,'script.txt','hello')
            with self.assertRaises(ValueError): handoff.Handoff(RID,v,'psychology','angle').save()
        with self.assertRaises(ValueError): ledger.append_event('../../x',content_id=CID,lane='psychology',status='WRITING_IN_PROGRESS')
        for name in ['../../x','/tmp/x','a\\b']:
            with self.assertRaises(ValueError): drive_storage.save_text(CID,name,'hello')
        outside=self.root/'outside';outside.mkdir(); link=self.root/'output'/CID;link.parent.mkdir(exist_ok=True);link.rmdir();link.symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError): drive_storage.save_text(CID,'x','hello')
    def test_generator_and_labels(self):
        with self.assertRaises(validators.QualityGateError): validators.require_files(p for p in [self.root/'missing'])
        with self.assertRaises(validators.QualityGateError): validators.require_files([self.root/'missing'],[])
        with self.assertRaises(validators.QualityGateError): validators.require_files([])
    def test_unknown_status_and_release(self):
        for s, err in [('BOGUS',ValueError),('RELEASE_APPROVED',PermissionError),('VIDEO_QA_PASSED',PermissionError)]:
            with self.assertRaises(err): ledger.append_event(RID,content_id=CID,lane='psychology',status=s)
    def test_recovery_requires_token(self):
        h=handoff.claim(CID,'psychology')
        with self.assertRaises(PermissionError): handoff.abandon_claim(CID,'psychology','wrong')
        handoff.abandon_claim(CID,'psychology',h.claim_token)
        handoff.claim(CID,'psychology');self.assertEqual(len(ledger.read_events(RID)),1)
    def package(self):
        return [drive_storage.save_text(CID,name,text) for name,text in [('flagship.txt','word '*1300),('short1.txt','one '*40),('short2.txt','two '*40),('short3.txt','three '*40),('companion.txt','article '*130)]]
    def test_completion_gates_and_drive_required(self):
        h=handoff.claim(CID,'psychology');files=self.package()
        with self.assertRaises(RuntimeError): runner.mark_complete(RID,CID,'psychology',files,claim_token=h.claim_token)
        self.assertEqual(ledger.last_status(RID,CID),'WRITING_IN_PROGRESS')
        files[0].write_text('word '*340)
        with self.assertRaises(validators.QualityGateError): runner.mark_complete(RID,CID,'psychology',files,claim_token=h.claim_token,drive_verifier=lambda *_:True)
        files[0].write_text('word '*1300+' [VERIFY]')
        with self.assertRaises(validators.QualityGateError): runner.mark_complete(RID,CID,'psychology',files,claim_token=h.claim_token,drive_verifier=lambda *_:True)
        files[0].write_text('word '*1300)
        runner.mark_complete(RID,CID,'psychology',files,claim_token=h.claim_token,drive_verifier=lambda *_:True)
        self.assertEqual(ledger.last_status(RID,CID),'WRITING_COMPLETE')
        with self.assertRaises(RuntimeError): handoff.claim(CID,'psychology')
    def test_banned_and_duplicate(self):
        files=self.package()
        with patch.dict(config.CONFIG['quality'],banned_terms=['article']):
            with self.assertRaises(validators.QualityGateError): validators.require_non_empty(files[-1])
        files[2].write_text(files[1].read_text())
        with self.assertRaises(validators.QualityGateError): validators.psychology_gate(flagship=files[0],short1=files[1],short2=files[2],short3=files[3],companion=files[4])
    def test_no_remote_endpoint_or_paid_override(self):
        for url in ['http://example.com:11434','https://127.0.0.1','http://127.0.0.1@evil.com','http://127.0.0.1/?x=1']:
            with patch.object(config,'LOCAL_MODEL_BASE_URL',url):
                with self.assertRaises(RuntimeError): config.assert_open_stack()
        with patch.object(config,'ALLOW_PAID_APIS','1'):
            with self.assertRaises(RuntimeError): config.assert_open_stack()
    def test_doctor_exact(self):
        with patch.object(local_model,'chat',return_value='BOOKS TOKEN'):
            self.assertFalse(local_model.doctor_check()['ok'])
        with patch.object(runner,'doctor_check',return_value=dict(reachable=True,ok=False)):
            with self.assertRaises(SystemExit): runner.doctor()
    def test_model_retry_no_redirect_or_fallback(self):
        session=Mock();session.__enter__=Mock(return_value=session);session.__exit__=Mock(return_value=False)
        session.post.side_effect=[Mock(status_code=503),Mock(status_code=200,json=lambda:{'message':{'content':'OK'}})]
        with patch.object(local_model.requests,'Session',return_value=session),patch.object(local_model.time,'sleep'):
            self.assertEqual(local_model.chat([]),'OK');self.assertEqual(session.post.call_count,2)
        self.assertFalse(session.trust_env);self.assertFalse(session.post.call_args.kwargs['allow_redirects'])
        session.post.side_effect=None;session.post.return_value=Mock(status_code=302)
        with patch.object(local_model.requests,'Session',return_value=session):
            with self.assertRaises(local_model.LocalModelError): local_model.chat([])
    def test_output_retry_preserves_source(self):
        p=drive_storage.save_text(CID,'stable.txt','original')
        self.assertEqual(drive_storage.save_text(CID,'stable.txt','original'),p)
        with self.assertRaises(FileExistsError): drive_storage.save_text(CID,'stable.txt','replacement')
        self.assertEqual(p.read_text(),'original')
    def test_openai_protocol_and_bad_reply(self):
        session=Mock();session.__enter__=Mock(return_value=session);session.__exit__=Mock(return_value=False)
        session.post.return_value=Mock(status_code=200,json=lambda:{'choices':[{'message':{'content':'local answer'}}]})
        with patch.object(local_model.requests,'Session',return_value=session),patch.object(local_model,'LOCAL_MODEL_PROTOCOL','openai'):
            self.assertEqual(local_model.chat([]),'local answer')
            self.assertTrue(session.post.call_args.args[0].endswith('/v1/chat/completions'))
            session.post.return_value=Mock(status_code=200,json=lambda:{})
            with self.assertRaises(local_model.LocalModelError): local_model.chat([])
    def test_workflow_no_input_shell_interpolation(self):
        text=(config.ROOT/'.github/workflows/manual-run.yml').read_text()
        self.assertIn('contents: read',text);self.assertIn('concurrency:',text)
        self.assertNotIn('secrets.',text)
        self.assertNotIn('${{',text.split('run: |')[-1])

if __name__=='__main__': unittest.main()
