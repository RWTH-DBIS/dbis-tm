from assets.TMBasic import Schedule
from assets.TMSolver import  Recovery, Scheduling
from assets.Generate import generate
from assets.Solution_generator import predict_deadlock, Perform_scheduling, Perform_conflictgraph
import unittest

class TestTMPerformance(unittest.TestCase):
    def test_generate_recovery(self):
        test_number = 1000
        for i in range(test_number):
            none = generate(3, ['a','b','c'],recovery="n")[0]
            self.assertFalse(Recovery.is_recoverable(none)[0], Schedule.parse_string(none))
            self.assertFalse(Recovery.avoids_cascading_aborts(none)[0],  Schedule.parse_string(none))
            self.assertFalse(Recovery.is_strict(none)[0], Schedule.parse_string(none))

            recovery = generate(3, ['a','b','c'],recovery="r")[0]
            self.assertTrue(Recovery.is_recoverable(recovery)[0], Schedule.parse_string(recovery))
            self.assertFalse(Recovery.avoids_cascading_aborts(recovery)[0], Schedule.parse_string(recovery))
            self.assertFalse(Recovery.is_strict(recovery)[0], Schedule.parse_string(recovery))

            aca = generate(3, ['a','b','c'],recovery='a')[0]
            self.assertTrue(Recovery.is_recoverable(aca)[0], Schedule.parse_string(aca))
            self.assertTrue(Recovery.avoids_cascading_aborts(aca)[0], Schedule.parse_string(aca))
            self.assertFalse(Recovery.is_strict(aca)[0], Schedule.parse_string(aca))

            st = generate(3, ['a','b','c'],recovery='s')[0]
            self.assertTrue(Recovery.is_recoverable(st)[0], Schedule.parse_string(st))
            self.assertTrue(Recovery.avoids_cascading_aborts(st)[0], Schedule.parse_string(st))
            self.assertTrue(Recovery.is_strict(st)[0], Schedule.parse_string(st))
        
        
    def test_generate_deadlock(self):
        no_deadlock = 0
        for i in range(1000):
            deadlock = generate(3, ['a','b','c'], True)[0]
            self.assertTrue(predict_deadlock(deadlock), Schedule.parse_string(deadlock))
            y = generate(3, ['a','b','c'], False)[0]
            if predict_deadlock(y):
                no_deadlock+=1 # cases in which it not worked
            

    def test_scheduling_performer(self):
        test_caces_scheduling = ["w_1(z) w_3(y) r_1(x) r_3(z) r_2(y) w_2(z) w_3(x) c_1 c_2 c_3",
                            "r_1(x) w_3(z) r_2(x) r_1(z) r_3(y) w_1(z) w_2(y) c_1 c_2 c_3",
                            "r_1(x) w_3(z) r_2(x) r_1(z) r_3(y) w_1(z) w_2(y) r1(x) r1(x) c_1 c_2 c_3",
                            "w2(x) r3(x) r1(y) r1(z) w3(y) w1(x) c3 w1(y) c1 r2(x) c2 "]
        for i in test_caces_scheduling:
            x = Schedule.parse_schedule(i)[0]
            self.assertTrue( Scheduling.is_S2PL(Perform_scheduling.perform_S2PL(x)[0]),"S2PL"+i )
            self.assertTrue( Scheduling.is_SS2PL(Perform_scheduling.perform_SS2PL(x)[0]),"SS2PL"+i )
            self.assertTrue( Scheduling.is_C2PL(Perform_scheduling.perform_C2PL(x)),"C2PL"+i )
            

    def test_compute_conflictset(self):
        # A tuple denotes: (schedule, conflictset)
        conflict_schedules =   [("w1(x)r2(y)r1(x)r2(x)c1w2(x)c2", [("w1(x)","r2(x)"),("w1(x)","w2(x)"), ("r1(x)","w2(x)")]),
                                ("w1(x)r2(y)r1(x)r2(x)c1w2(x)a2", []),
                                ("w1(x)r2(y)r1(x)r2(x)a1w2(x)c2", []),
                                ("w1(x)r2(y)r1(x)r2(x)a1w2(x)a2", [])
        ]
        for schedule, cset in conflict_schedules:
            solution = Perform_conflictgraph.compute_conflict_quantity( Schedule.parse_schedule(schedule)[0])
            self.assertEqual(cset, solution,schedule)

if __name__ == '__main__':
    unittest.main()
