"""Port invariants; synthetic file fixtures are not independent-agent evidence."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import bracket as B

class Port(unittest.TestCase):
    def test_malformed_scores_cannot_override_scoring(self):
        for invalid in [float('nan'), float('inf'), 10**1000, -1, 11, True, '8', None]:
            a={k:8 for k,_ in B.WEIGHTS}
            a['correctness']=invalid
            v={'scores':{'a':a,'b':{k:7 for k,_ in B.WEIGHTS}},'winner':'a'}
            with self.assertRaises(B.ArenaError):
                B.decide(v,'a','b')

    def cli(self,*args):
        r=subprocess.run([sys.executable,B.SELF,*map(str,args)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        return r.stdout

    def test_restore_and_dispatch_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            old=Path(tmp)/'old';new=Path(tmp)/'new'
            self.cli('init','--agents',2,'--seed',7,'--task','Solve {{literal}}','--dir',old)
            self.cli('prompts','spawn','--dir',old)
            self.cli('dispatch','spawn','a001.spawn','actual-tool-id-1','--dir',old)
            r=subprocess.run([sys.executable,B.SELF,'dispatch','spawn','a002.spawn','actual-tool-id-1','--dir',str(old)],capture_output=True)
            self.assertEqual(r.returncode,2)
            (old/'r0/a001.md').write_text('completed fixture')
            before=(old/'task.md').read_bytes()
            shutil.move(old,new)
            self.cli('relocate','--dir',new)
            self.assertIn('1 of 2 job(s)',self.cli('next','--dir',new))
            state=json.loads((new/'arena.json').read_text())
            self.assertEqual(state['agents']['a001']['solution'],str(new/'r0/a001.md'))
            self.assertEqual(state['dispatches'][0]['agent_id'],'actual-tool-id-1')
            self.assertEqual(before,(new/'task.md').read_bytes())
            self.cli('prompts','spawn','--dir',new)
            self.assertNotIn(str(old),(new/'prompts/r0/a002.spawn.md').read_text())

    def test_rubric_templates_and_cards_frozen_for_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.cli('init','--agents',2,'--task','t','--dir',tmp)
            self.assertEqual((Path(tmp)/'prompt-templates.md').read_text(),Path(B.SKILL_PATH).read_text())
            self.assertEqual((Path(tmp)/'rubric.md').read_text(),Path(B.RUBRIC_PATH).read_text())
            self.assertEqual(B.DEFAULT_WAVE,1)
            self.cli('prompts','spawn','--dir',tmp)

    def test_explicit_directory_in_continuation_commands(self):
        with tempfile.TemporaryDirectory(prefix="arena space ") as tmp:
            self.cli('init','--agents',2,'--task','t','--dir',tmp)
            output=self.cli('next','--dir',tmp)
            self.assertIn('--dir',output)
            self.assertIn(tmp,output)

    def test_bad_verdict_retries_keep_raw_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.json'
            p.write_text('first');B.quarantine(str(p))
            p.write_text('second');B.quarantine(str(p))
            self.assertEqual(Path(str(p)+'.unreadable').read_text(),'first')
            self.assertEqual(Path(str(p)+'.unreadable.2').read_text(),'second')

    def test_baseline_snapshot_is_verbatim(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'baseline.txt'
            raw=b'    indented code\r\n\r\n'
            base.write_bytes(raw)
            run=Path(tmp)/'run'
            self.cli('init','--agents',1,'--task','t','--baseline-file',base,'--dir',run)
            self.assertEqual((run/'baseline.md').read_bytes(),base.read_bytes())
            (run/'r0').mkdir(exist_ok=True)
            (run/'r0/a001.md').write_text('synthetic unit fixture')
            self.cli('prompts','final','--dir',run)
            copies=[(run/'final'/f'{side}.md') for side in ('X','Y')]
            self.assertIn(base.read_bytes(),[p.read_bytes() for p in copies])

    def test_fatal_and_match_tie_fields_are_required(self):
        score={k:7 for k,_ in B.WEIGHTS}
        with self.assertRaises(B.ArenaError):
            B.decide({'scores':{'a':score,'b':score}},'a','b')
        score=dict(score,fatal=False)
        verdict={'scores':{'a':score,'b':score},'winner':'a','reason':'same scores'}
        with self.assertRaises(B.ArenaError):
            B.decide(verdict,'a','b')
        verdict['standing']={'a':[],'b':[]}
        verdict['reason']=''
        with self.assertRaises(B.ArenaError):
            B.decide(verdict,'a','b')
        verdict['reason']='a is easier to use'
        self.assertEqual(B.decide(verdict,'a','b')[0],'a')
        self.assertEqual(B.decide(verdict,'a','b',final=True)[0],'a')

    def test_wrong_winner_does_not_inherit_losers_evidence(self):
        v={'survived':['claim about the wrong candidate'],'reason':'wrong candidate is better'}
        reason, claims=B.winner_evidence(v,'b','scores override pick')
        self.assertEqual(claims,[])
        self.assertEqual(reason,'scores override pick')
        v['survived_by']={'a':['wrong'],'b':['correct']}
        self.assertEqual(B.winner_evidence(v,'b','scores override pick')[1],['correct'])

    def test_collected_verdict_requires_match_lists_and_reason(self):
        for v in [{}, {'reason':'ok'}, {'reason':'ok','match':'m','standing':{'a':[],'b':'invalid'}}]:
            with self.assertRaises(B.ArenaError):
                B.validate_collected_verdict(v,('a','b'),match='m')
        B.validate_collected_verdict({'reason':'ok','winner':'a','match':'m','standing':{'a':[],'b':[]}},('a','b'),match='m')

    def test_plan_rejects_zero_wave(self):
        r=subprocess.run([sys.executable,B.SELF,'plan','--wave','0'],capture_output=True)
        self.assertEqual(r.returncode,2)

if __name__=='__main__':
    unittest.main()
