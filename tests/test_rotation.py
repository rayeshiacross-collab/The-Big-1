"""Contract fixtures only: no fixture proves real research, Drive storage or Hermes review."""
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from src import drive_storage


class DriveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / 'report.txt'; self.file.write_text('preserve this evidence')
        self.digest = hashlib.sha256(self.file.read_bytes()).hexdigest()
        self.meta = dict(id='remote1', name='report.txt', parents=['folder1'],
                         appProperties=dict(reboot_identity='batch1', sha256=self.digest))
        self.session = Mock()
        self.session.get.side_effect = [Mock(status_code=200, json=lambda: {'files':[self.meta]}),
                                       Mock(status_code=200, content=self.file.read_bytes())]

    def test_matching_upload_is_reused_and_read_back(self):
        client = drive_storage.DriveVerifier('folder1', 'token', session=self.session)
        self.assertTrue(client('batch1', [self.file]))
        self.session.post.assert_not_called()
        self.assertFalse(self.session.trust_env)

    def test_stale_remote_content_blocks_completion(self):
        self.session.get.side_effect = [Mock(status_code=200,json=lambda:{'files':[self.meta]}),
                                       Mock(status_code=200,content=b'different')]
        with self.assertRaisesRegex(RuntimeError, 'readback'):
            drive_storage.DriveVerifier('folder1','token',session=self.session)('batch1',[self.file])

    def test_wrong_parent_or_conflicting_identity_is_rejected(self):
        self.meta['parents'] = ['other-folder']
        with self.assertRaisesRegex(RuntimeError, 'identity'):
            drive_storage.DriveVerifier('folder1','token',session=self.session)('batch1',[self.file])

    def test_missing_credentials_fail_before_network(self):
        with self.assertRaises(RuntimeError):
            drive_storage.DriveVerifier('folder1','',session=self.session)
        self.session.get.assert_not_called()

    def test_new_file_upload_uses_related_multipart_and_readback(self):
        self.session.get.side_effect = [Mock(status_code=200,json=lambda:{'files':[]}),Mock(status_code=200,content=self.file.read_bytes())]
        self.session.post.return_value=Mock(status_code=200,json=lambda:self.meta)
        self.assertTrue(drive_storage.DriveVerifier('folder1','token',session=self.session)('batch1',[self.file]))
        call=self.session.post.call_args
        self.assertTrue(call.kwargs['headers']['Content-Type'].startswith('multipart/related; boundary='))
        self.assertIn(self.file.read_bytes(),call.kwargs['data'])
        self.assertFalse(call.kwargs['allow_redirects'])

    def test_duplicate_remote_objects_block_without_overwrite(self):
        self.session.get.side_effect=[Mock(status_code=200,json=lambda:{'files':[self.meta,self.meta]})]
        with self.assertRaisesRegex(RuntimeError,'Ambiguous'):
            drive_storage.DriveVerifier('folder1','token',session=self.session)('batch1',[self.file])
        self.session.post.assert_not_called()


class RotationTests(unittest.TestCase):
    def setUp(self):
        from src import config, handoff, ledger, runner
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for mod,name,value in [(config,'OUTPUT_PATH','out'),(drive_storage,'OUTPUT_PATH','out'),(runner,'OUTPUT_PATH','out'),(config,'HANDOFF_PATH','handoffs'),(handoff,'HANDOFF_PATH','handoffs'),(config,'LEDGER_PATH','ledgers'),(ledger,'LEDGER_PATH','ledgers')]:
            p=patch.object(mod,name,self.root/value); p.start(); self.addCleanup(p.stop)
        p=patch.dict(os.environ,MACHINE_LEDGER_PATH=str(self.root/'usage.jsonl'));p.start();self.addCleanup(p.stop)
        self.source=self.root/'source.txt'; self.source.write_text('A primary source snapshot with a checked quotation and context. '*5)
        self.packet=self.root/'sources.json'
        self.packet.write_text(json.dumps(dict(edition_date='2026-10-24',sources=[dict(id='s1',url='https://example.org/paper',published_at='2026-10-23',observed_at='2026-10-24T00:00:00-05:00',claim_limitation='Fixture only, not real research',text_path='source.txt',sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())])))
        self.catalog=self.root/'catalog.txt';self.catalog.write_text('Existing catalog for synthetic tests only. No published items in this fixture.')
        self.tools=self.root/'tools.json';self.tools.write_text(json.dumps(dict(hermes_executable='missing-hermes',model='fixture',model_base_url='http://127.0.0.1:11434/v1',local_tools=[],timeout_seconds=30)))
        self.rid='20261024-0600-central'

    def report(self):
        from src.text_rotation import CANDIDATE_FIELDS
        rows=[]
        for rank in range(1,11):
            row={k:'Concrete fixture explanation' for k in CANDIDATE_FIELDS}
            row.update(rank=rank,score=8,source_ids=['s1'],subject=f'Distinct fixture subject {rank}');rows.append(row)
        return dict(source_checks={'s1':{'quote':'checked quotation','limitation':'Synthetic snapshot only'}},signals=[dict(claim='Fixture claim',why_it_matters='Fixture audience relevance',generational_angle='both',source_ids=['s1'])],top10=rows,catalog_comparison='Fixture catalog comparison and distinguishing angle. '*4,market_white_space='Fixture competitive uncertainty explicitly identified. '*4,assignments=[dict(content_id=f'{prefix}-20261024-test',target_lane=lane,selected_angle='One bounded fixture angle',source_ids=['s1'],similar_episodes=[],distinguishing_angle='A different fixture treatment') for prefix,lane in [('psych','psychology'),('glitch','system-glitch')]])

    def test_source_hash_mismatch_blocks(self):
        from src.text_rotation import freeze_inputs
        self.source.write_text('changed')
        with self.assertRaisesRegex(ValueError,'hash'):
            freeze_inputs(self.rid,self.packet,self.catalog)

    def test_edition_date_mismatch_blocks(self):
        from src.text_rotation import freeze_inputs
        with self.assertRaisesRegex(ValueError,'date'):
            freeze_inputs('20261025-0600-central',self.packet,self.catalog)

    def test_text_doctor_does_not_require_video_tools(self):
        from src import text_rotation as rotation
        session=Mock();session.__enter__=Mock(return_value=session);session.__exit__=Mock(return_value=False)
        session.get.return_value=Mock(status_code=200,json=lambda:{'data':[{'id':'fixture'}]})
        with patch.object(rotation.shutil,'which',return_value='/bin/hermes'),patch.object(rotation.subprocess,'run',return_value=Mock(returncode=0,stdout='--safe-mode --query-file --base-url --oneshot')),patch.object(rotation.requests,'Session',return_value=session):
            exe,url=rotation.doctor(self.tools)
            self.assertEqual(exe,'/bin/hermes');self.assertTrue(url.endswith('/v1'))
        self.assertFalse(session.trust_env)

    def test_missing_hermes_fails_real_preflight(self):
        from src import text_rotation as rotation
        with patch.object(rotation.shutil,'which',return_value=None):
            with self.assertRaisesRegex(RuntimeError,'Hermes'):
                rotation.doctor(self.tools)

    def test_research_saves_before_handoff_and_retries_without_agent(self):
        from src import text_rotation as rotation, handoff, ledger
        def invoke(exe,url,tools,prompt,folder):
            (folder/'report.json').write_text(json.dumps(self.report()))
        verifier=Mock(return_value=True)
        def verify(identity,files):
            self.assertFalse((self.root/'handoffs'/'psych-20261024-test.json').exists())
            return True
        verifier.side_effect=verify
        with patch.object(rotation,'doctor',return_value=('hermes','http://127.0.0.1/v1')),patch.object(rotation,'invoke',side_effect=invoke) as agent,patch.object(rotation,'drive_client',return_value=verifier):
            result=rotation.research(self.rid,self.packet,self.catalog,self.tools)
            verifier.side_effect=None
            self.assertEqual(rotation.research(self.rid,self.packet,self.catalog,self.tools),result)
            self.assertEqual(agent.call_count,1)
        self.assertEqual(ledger.last_status(self.rid,'psych-20261024-test'),'RESEARCH_COMPLETE')
        self.assertEqual(handoff.Handoff.load('glitch-20261024-test').target_lane,'system-glitch')

    def test_failed_drive_does_not_publish_handoffs(self):
        from src import text_rotation as rotation
        def invoke(exe,url,tools,prompt,folder): (folder/'report.json').write_text(json.dumps(self.report()))
        with patch.object(rotation,'doctor',return_value=('hermes','local')),patch.object(rotation,'invoke',side_effect=invoke),patch.object(rotation,'drive_client',return_value=Mock(side_effect=RuntimeError('offline'))):
            with self.assertRaisesRegex(RuntimeError,'offline'): rotation.research(self.rid,self.packet,self.catalog,self.tools)
        self.assertFalse((self.root/'handoffs'/'psych-20261024-test.json').exists())

    def test_wrong_lane_claim_is_rejected_without_agent(self):
        from src import text_rotation as rotation,handoff
        handoff.Handoff(self.rid,'psych-20261024-test','psychology','Fixture angle',required_assets=['flagship.txt']).save()
        with patch.object(rotation,'invoke') as agent:
            with self.assertRaises(PermissionError): rotation.write_assignment('system-glitch','psych-20261024-test',self.tools)
            agent.assert_not_called()

    def prepare_edition(self):
        from src import text_rotation as rotation
        def invoke(exe,url,tools,prompt,folder): (folder/'report.json').write_text(json.dumps(self.report()))
        with patch.object(rotation,'doctor',return_value=('hermes','local')),patch.object(rotation,'invoke',side_effect=invoke),patch.object(rotation,'drive_client',return_value=Mock(return_value=True)):
            rotation.research(self.rid,self.packet,self.catalog,self.tools)

    def write_fixture(self,exe,url,tools,prompt,folder):
        from src import text_rotation as rotation
        from src.self_qa import WRITING_CHECKS
        cid='glitch-20261024-test'
        content={'script.txt':'word '*70,
                 'scene_plan.txt':json.dumps(dict(beats={k:'A concrete action revealing the relevant system contradiction in this fixture.' for k in ('recognition','tension','explanation','payoff')},captions=['A synthetic fixture caption with sufficient context.'])),
                 'packaging.json':json.dumps(dict(titles=['Fixture title'],description='A complete synthetic fixture description with no real publication.',thumbnail='A concrete thumbnail fixture concept')),
                 'claims.json':json.dumps([dict(claim='Synthetic factual claim for contract tests only.',source_ids=['s1'])]),
                 'timing.json':json.dumps(dict(words_per_minute=150,estimated_seconds=28.0),indent=2)}
        for name,text in content.items(): (folder/name).write_text(text)
        qa=dict(reviewer='Hermes',content_id=cid,stage='writing',verdict='PASS',reviewed_at='2026-10-24T06:30:00-05:00',unresolved_issues=[],artifact_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in content},checks={key:dict(status='PASS',evidence='Synthetic test fixture, no actual review') for key in WRITING_CHECKS})
        (folder/'self_qa.json').write_text(json.dumps(qa))

    def test_glitch_writes_complete_package_and_reuses_completed_assignment(self):
        from src import text_rotation as rotation,ledger
        self.prepare_edition()
        with patch.object(rotation,'doctor',return_value=('hermes','local')),patch.object(rotation,'invoke',side_effect=self.write_fixture) as agent,patch.object(rotation,'drive_client',return_value=Mock(return_value=True)):
            result=rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools)
            self.assertEqual(result['status'],'WRITING_COMPLETE')
            self.assertTrue(rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools)['reused'])
            self.assertEqual(agent.call_count,1)
        self.assertEqual(ledger.last_status(self.rid,'glitch-20261024-test'),'WRITING_COMPLETE')

    def test_glitch_storage_failure_requires_explicit_resume_without_regeneration(self):
        from src import text_rotation as rotation,ledger
        self.prepare_edition()
        verifier=Mock(side_effect=RuntimeError('upload offline'))
        with patch.object(rotation,'doctor',return_value=('hermes','local')),patch.object(rotation,'invoke',side_effect=self.write_fixture) as agent,patch.object(rotation,'drive_client',return_value=verifier):
            with self.assertRaisesRegex(RuntimeError,'upload offline'): rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools)
            self.assertEqual(ledger.last_status(self.rid,'glitch-20261024-test'),'WRITING_IN_PROGRESS')
            verifier.side_effect=None;verifier.return_value=True
            with self.assertRaises(FileExistsError): rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools)
            rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools,resume=True)
            self.assertEqual(agent.call_count,1)

    def test_invalid_review_does_not_upload_or_complete(self):
        from src import text_rotation as rotation,ledger
        self.prepare_edition()
        def invalid(*args):
            self.write_fixture(*args)
            (args[-1]/'self_qa.json').write_text('{}')
        verifier=Mock(return_value=True)
        with patch.object(rotation,'doctor',return_value=('hermes','local')),patch.object(rotation,'invoke',side_effect=invalid),patch.object(rotation,'drive_client',return_value=verifier):
            with self.assertRaises(Exception): rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools)
        verifier.assert_not_called()
        self.assertEqual(ledger.last_status(self.rid,'glitch-20261024-test'),'WRITING_IN_PROGRESS')

    def test_research_retry_rejects_changed_catalog(self):
        from src import text_rotation as rotation
        self.prepare_edition();self.catalog.write_text('A later batch catalog must not replace the original.')
        with patch.object(rotation,'invoke') as agent:
            with self.assertRaises(FileExistsError): rotation.research(self.rid,self.packet,self.catalog,self.tools)
            agent.assert_not_called()

    def test_late_central_observation_stays_in_same_edition(self):
        from src.text_rotation import freeze_inputs
        packet=json.loads(self.packet.read_text());packet['sources'][0]['observed_at']='2026-10-24T23:30:00-05:00';self.packet.write_text(json.dumps(packet))
        self.assertEqual(freeze_inputs(self.rid,self.packet,self.catalog)['edition_date'],'2026-10-24')

    def test_changed_frozen_source_is_rejected_before_writing(self):
        from src import text_rotation as rotation
        self.prepare_edition()
        evidence=self.root/'out'/'research'/self.rid/'evidence.json';data=json.loads(evidence.read_text());data['sources'][0]['text']+=' changed';evidence.write_text(json.dumps(data))
        with patch.object(rotation,'invoke') as agent:
            with self.assertRaisesRegex(ValueError,'hash'): rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools)
            agent.assert_not_called()

    def test_sunday_requires_separate_analysis_and_cannot_reuse_daily_edition(self):
        from src import text_rotation as rotation
        self.prepare_edition()
        with self.assertRaises(FileExistsError):
            rotation.research(self.rid,self.packet,self.catalog,self.tools,sunday=True)

    def test_duplicate_top_ten_subjects_are_rejected(self):
        from src import text_rotation as rotation
        report=self.report();report['top10'][1]['subject']=report['top10'][0]['subject']
        with self.assertRaisesRegex(ValueError,'distinct'):
            rotation.validate_report(report,rotation.freeze_inputs(self.rid,self.packet,self.catalog))

    def test_edited_catalog_is_blocked_by_recorded_edition_digest(self):
        from src import text_rotation as rotation
        self.prepare_edition()
        evidence=self.root/'out/research'/self.rid/'evidence.json';value=json.loads(evidence.read_text());value['catalog']='A changed catalog';evidence.write_text(json.dumps(value))
        with patch.object(rotation,'invoke') as agent,patch.object(rotation,'doctor',return_value=('hermes','local')),patch.object(rotation,'drive_client',return_value=Mock(return_value=True)):
            with self.assertRaisesRegex(ValueError,'edition'): rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools)
            agent.assert_not_called()

    def test_edited_report_angle_is_blocked_before_claim(self):
        from src import text_rotation as rotation,handoff
        self.prepare_edition()
        report=self.root/'out/research'/self.rid/'report.json';value=json.loads(report.read_text());value['assignments'][1]['selected_angle']='An altered assignment';report.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError,'edition'): rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools)
        self.assertFalse(handoff.claim_file('glitch-20261024-test').exists())

    def test_partial_asset_promotion_resumes_same_validated_attempt(self):
        from src import text_rotation as rotation
        self.prepare_edition();real_save=rotation.save_text;calls=0
        def interrupted(*args):
            nonlocal calls
            calls+=1
            if calls==2: raise OSError('interrupted promotion')
            return real_save(*args)
        with patch.object(rotation,'doctor',return_value=('hermes','local')),patch.object(rotation,'invoke',side_effect=self.write_fixture) as agent,patch.object(rotation,'drive_client',return_value=Mock(return_value=True)):
            with patch.object(rotation,'save_text',side_effect=interrupted):
                with self.assertRaisesRegex(OSError,'interrupted promotion'): rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools)
            rotation.write_assignment('system-glitch','glitch-20261024-test',self.tools,resume=True)
            self.assertEqual(agent.call_count,1)

    def test_psychology_assignment_produces_all_written_material(self):
        from src import text_rotation as rotation
        from src.self_qa import WRITING_CHECKS
        self.prepare_edition()
        def psychology_fixture(exe,url,tools,prompt,folder):
            cid='psych-20261024-test'
            values={'flagship.txt':'word '*1350,'short1.txt':'first '*60,'short2.txt':'second '*60,'short3.txt':'third '*60,'companion.txt':'article '*1000,
                    'titles.json':json.dumps([dict(title='A complete fixture title for the package',thumbnail='A concrete fixture thumbnail concept')])}
            for name in rotation.ASSETS['psychology']:
                (folder/name).write_text(values.get(name,'Complete fixture content with sufficient concrete context for contract validation. '*3))
            qa=dict(reviewer='Hermes',content_id=cid,stage='writing',verdict='PASS',reviewed_at='2026-10-24T06:30:00-05:00',unresolved_issues=[],artifact_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in rotation.ASSETS['psychology']},checks={key:dict(status='PASS',evidence='Synthetic fixture only, no actual review') for key in WRITING_CHECKS})
            (folder/'self_qa.json').write_text(json.dumps(qa))
        verifier=Mock(return_value=True)
        with patch.object(rotation,'doctor',return_value=('hermes','local')),patch.object(rotation,'invoke',side_effect=psychology_fixture),patch.object(rotation,'drive_client',return_value=verifier):
            result=rotation.write_assignment('psychology','psych-20261024-test',self.tools)
        self.assertEqual(result['status'],'WRITING_COMPLETE')
        self.assertEqual({p.name for p in verifier.call_args.args[1]},set(rotation.ASSETS['psychology'])|{'self_qa.json','evidence.json'})
