''' 
Created on 2022-07-16

@author: wf
'''
from assets.TMCheck import ConflictSetScorer, ConflictSerializationScorer, RecoveryScorer, ScheduleScorer
from assets.TMBasic import ConflictGraph, ConflictGraphNode
from tests.scheduletest import ScheduleTest

class TestTMScorer(ScheduleTest):
    """
    tests for scorers of
    for https://git.rwth-aachen.de/i5/teaching/dbis-digi-2022/-/issues/35
    """
    
    def testConflictSetScorer(self):
        '''
        test the conflict set scorer
        '''
        examples=[ {
            "result1": {("w_2(x)","r_1(x)"),("w_1(z)","w_2(z)")},
            "result2": {
                ("r_2(x)","w_3(x)"),
                ("w_1(y)","r_2(y)"),
                ("w_1(y)","w_2(y)"),
                ("w_1(y)","w_3(y)"),
                ("w_3(z)","w_1(z)"),
                ("w_3(z)","w_2(z)"),
                ("r_2(y)","w_3(y)"), 
                ("w_2(y)","w_3(y)"),
                ("w_2(y)","r_1(y)"), 
                ("w_1(z)","w_2(z)"),
                ("w_3(y)","r_1(y)"),
                ("w_3(y)","w_2(y)"),
                ("r_1(y)","w_2(y)")
            },
            "expected":4.0
        }
        ]
        solution1 = {("w_2(x)", "r_1(x)"), ("w_1(z)", "w_2(z)")}
        solution2 = {("r_2(x)", "w_3(x)"), ("w_1(y)", "r_2(y)"), ("w_1(y)", "w_2(y)"), ("w_1(y)", "w_3(y)"), ("w_3(z)", "w_1(z)"), ("w_3(z)", "w_2(z)"), ("r_2(y)", "w_3(y)"), 
             ("w_2(y)", "w_3(y)"), ("w_2(y)", "r_1(y)"), ("w_1(z)", "w_2(z)"), ("w_3(y)", "r_1(y)"), ("w_3(y)", "w_2(y)"), ("r_1(y)", "w_2(y)")}
        max_points=4
        debug=False
        for i,example in enumerate(examples):
            result1=example["result1"]
            result2=example["result2"]
            expected=example["expected"]
            css=ConflictSetScorer()
            score=css.score_conflictSet(result1, result2, solution1, solution2, max_points)
            if debug:
                print(f"{i+1} score: {score} expected: {expected}")
            self.assertEquals(expected,score)
            
    def testConflictSerializationScorer(self):
        '''
        test conflict serialization scoring
        '''
        
        graphRight = ConflictGraph()
        graphLess = ConflictGraph()
        graphMuch = ConflictGraph()
        t1 = ConflictGraphNode(1)
        t2 = ConflictGraphNode(2)
        t3 = ConflictGraphNode(3)
        graphRight.add_edge(t1,t2)
        graphRight.add_edge(t3,t2)
        graphRight.add_edge(t2,t1)
        
        graphLess.add_edge(t1,t2)
        graphLess.add_edge(t2,t1)
        
        graphMuch.add_edge(t1,t2)
        graphMuch.add_edge(t3,t2)
        graphMuch.add_edge(t2,t1)
        graphMuch.add_edge(t3,t1)
        schedule = "r1(x) w2(x) r3(y) w2(y) w2(z) r1(x) c1 c2 c3"
        
        schedule1= "r1(x) w2(x) w3(x) w2(y) w3(y) r1(y) w3(z) r1(z) w2(z) c1 c2 c3"
        schedule2 = "w1(x) w3(x) w3(y) w1(y) c1 c2"
        t1 = ConflictGraphNode(1)
        t2 = ConflictGraphNode(2)
        t3 = ConflictGraphNode(3)
        
        graph1 = ConflictGraph()
        graph1.add_edge(t1, t2)
        graph1.add_edge(t1, t3)
        graph1.add_edge(t2, t1)
        graph1.add_edge(t2, t3)
        graph1.add_edge(t3, t1)
        graph1.add_edge(t3, t2)
        
        graph2 = ConflictGraph()
        graph2.add_edge(t1, t3)
        graph2.add_edge(t3, t1)
        
        conf_g3=ConflictGraph()
        conf_g3.add_edge(t1, t2)
        examples=[ {
            "name": "s3",
            "result": graph1,
            "serializable": False,
            "schedule": schedule1,
            "expected": 1.5
            },
            {
            "name": "s3",
            "result": conf_g3,
            "serializable": False,
            "schedule": schedule1,
            "expected": 0.5
            },
            {
            "name": "s4",
            "result": graph2,
            "schedule": schedule2,
            "serializable": False,
            "expected": 1.5
            }
        ]
        debug=False
        for i,example in enumerate(examples):
            name=example["name"]
            result=example["result"]
            cgsolution=example["schedule"]
            expected=example["expected"]
            
            css=ConflictSerializationScorer()
            score=css.score_conflictSerialization(name,result, serializableResult, cgsolution=cgsolution, serializable=False)
            print(score)
            if debug:
                print(f"{i+1} score: {score} expected: {expected}")
            self.assertEquals(expected,score)
            
    def testRecoveryScorer(self):
        '''
        test the recovery scorer
        '''
        # subtask2.setSolution(([s2_is_rc, s2_is_aca, s2_is_st], [s2_proof_rc, s2_proof_aca, s2_proof_st]))
        
        s1="w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1"
        s3="w_2(y) r_1(z) c_2 w_1(y) r_1(y) w_1(z) c_1"

      
        examples=[ 
            # No points -no result specified
            {
            "name": "s1",
            "schedule": s1,
            "expected": 0,
            "result": 
                (
                    (
                        None,  # is_rc
                        None, # is_aca
                        None  # is_st
                    )
                        ,
                    (
                        # proof_rc
                        {},
                        # proof_aca
                        {},
                        # proof_st
                        {}
                    )
                )
            },
            # No points, is in rc but no proof given
             {
            "name": "s1",
            "schedule": s1,
            "expected": 0,
            "result": 
                (
                    (
                        True,  # is_rc
                        False, # is_aca
                        False  # is_st
                    )
                        ,
                    (
                        # proof_rc
                        {},
                        # proof_aca
                        {},
                        # proof_st
                        {}
                    )
                )
            },
            # No points, is in rc but no proof given
             {
            "name": "s1",
            "schedule": s1,
            "expected": 0,
            "result": 
                (
                    (
                        True,  # is_rc
                        True, # is_aca
                        True  # is_st
                    )
                        ,
                    (
                        # proof_rc
                        {},
                        # proof_aca
                        {},
                        # proof_st
                        {}
                    )
                )
            },
            # correct answer and proof
            {
            "name": "s1",
            "schedule": s1,
            "expected": 2,
            "result": 
                (
                    (
                        True,  # is_rc
                        False, # is_aca
                        False  # is_st
                    )
                        ,
                    (
                        # proof_rc
                        {(1, "y", 2, True), (2, "y", 1, False), (1, "z", 2, False), (2, "z", 1, False)},
                        # proof_aca
                        {(1, "y", 2, True)},
                        # proof_st
                        {}
                    )
                )
            },
            {
            "name": "s1",
            "schedule": s1,
            "expected": 0,
            "result": 
                (
                    (
                        True,  # is_rc
                        False, # is_aca
                        False  # is_st
                    )
                        ,
                    (
                        # proof_rc
                        {},
                        # proof_aca
                        {},
                        # proof_st
                        {}
                    )
                )
            },
            {
            "name": "s3",
            "schedule": s3,
            "expected": 2,
            "result": 
                (
                    (
                        True,  # is_rc
                        True, # is_aca
                        True  # is_st
                    )
                        ,
                    (
                        # proof_rc
                        {(1, "y", 2, False), (2, "y", 1, False), (1, "z", 2, False), (2, "z", 1, False)},
                        # proof_aca
                         {(1, "y", 2, False), (2, "y", 1, False), (1, "z", 2, False), (2, "z", 1, False)},
                        # proof_st
                        {("w_2(y)", "w_1(y)", False, True), ("w_2(y)", "r_1(y)", False, True)}
                    )
                )
            },
        ]
        debug=False
        for i,example in enumerate(examples):
            name=example["name"]
            result=example["result"]
            schedule=example["schedule"]
            expected=example["expected"]
            rs=RecoveryScorer()
            score=rs.score_recovery(name,schedule,result, 2)
            
            if debug:
                print(f"{i+1} score: {score} expected: {expected}")
            self.assertEquals(expected,score)
      
    def testScheduleScorer(self):
        '''
        test the Schedule scorer
        '''
        examples=self.getScheduleExamples()
        debug=False
        for i,example in enumerate(examples):
            index=example["index"]
            schedule=example["schedule"]
            result=example["result"]
            check=example["check"]
            sScorer=ScheduleScorer()
            score=sScorer.getScore(schedule, result,check,max_points=1)
            if debug:
                print(f"{i+1}: score={score}")
            self.assertEqual(1,score)
    
    # def grade_recovery(self,schedule,isClassList,proofList,max_score):
    #     rs=RecoveryScorer()
    #     name="?"
    #     result=(tuple(isClassList),tuple(proofList))
    #     score=rs.score_proof(name,schedule,result, max_score)
    #     return score
        
            
    # def testGradeRecovery(self):
    #     """
    #     test Grade Recovery
    #     """
    #     # No points
    #     rc_proof = {}
    #     is_rc = None
    #     aca_proof = {}
    #     is_aca = None
    #     st_proof = {}
    #     is_st = None
    #     self.assertEqual(0,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # No points, is in rc but no proof given
    #     is_rc = True
    #     is_aca = None
    #     is_st = None
    #     self.assertEqual(0,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # No points, is in rc but no proof given
    #     is_rc = True
    #     is_aca = True
    #     is_st = True
    #     self.assertEqual(0,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # Gets 0 because is_aca was not shown although is_st == False is correct
    #     is_rc = True
    #     is_aca = False
    #     is_st = False
    #     self.assertEqual(0,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # Gets 0 because is_st is correct but is_aca was not shown
    #     is_rc = True
    #     is_aca = True
    #     is_st = False
    #     self.assertEqual(0,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # Gets 2 / 3 because is_aca (cex given)
    #     is_rc = None
    #     is_aca = False
    #     aca_proof = {(1, 'y', 2, True)}
    #     is_st = None
    #     self.assertEqual(2 / 3,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # Gets 2 * (2 / 3) because is_aca (cex given) and is_st is correct
    #     is_rc = True
    #     is_aca = False
    #     aca_proof = {(1, 'y', 2, True)}
    #     is_st = False
    #     self.assertEqual(4 / 3,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # Gets 0 points because is_aca (cex given) but bool is not set
    #     is_rc = None
    #     is_aca = None
    #     aca_proof = {(1, 'y', 2, True)}
    #     is_st = None
    #     self.assertEqual(0,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # Gets 2 / 3 points because is_aca (cex given) and bool is set
    #     is_rc = None
    #     is_aca = False
    #     aca_proof = {(1, 'y', 2, True)}
    #     is_st = None
    #     self.assertEqual(2 / 3,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # Gets 0 points because is_aca == False was not shown although is_st == False is correct
    #     is_rc = None
    #     is_aca = None
    #     aca_proof = {}
    #     is_st = False
    #     self.assertEqual(0,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))

    #     # Gets 2 points (correct solution)
    #     is_rc = True
    #     rc_proof = {(1, 'z', 2, False), (2, 'y', 1, False), (1, 'y', 2, True), (2, 'z', 1, False)}
    #     is_aca = False
    #     aca_proof = {(1, 'y', 2, True)}
    #     is_st = False
    #     st_proof = {}
    #     self.assertEqual(2,
    #                      self.grade_recovery("w_2(y) r_1(z) r_2(y) r_1(y) c_2 w_1(y) c_1", [is_rc, is_aca, is_st],
    #                                             [rc_proof, aca_proof, st_proof], 2))
