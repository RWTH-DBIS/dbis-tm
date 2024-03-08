from dbis_tm import Schedule
from dbis_tm.TMSolver import Recovery
from dbis_tm.Generate import generate
from dbis_tm.Solution_generator import predict_deadlock
from unittest import TestCase
import random


class TestGenerator(TestCase):
    def valid_schedule(self, schedule: Schedule, transactions, resources):
        """Helper function to assert wether the schedule is valid."""
        self.assertEqual(
            schedule.tx_count,
            transactions,
            f"More transactions in schedule than should be.{schedule}",
        )
        self.assertEqual(
            schedule.resources, resources, f"Wrong resources in schedule.{schedule}"
        )
        concluded_trans = list(schedule.aborts.keys()) + list(schedule.commits.keys())
        self.assertEqual(
            list(range(1, transactions + 1)),
            sorted(concluded_trans),
            f"Not all transactions finished/ or to many.{schedule}",
        )
        self.assertEqual(
            Schedule.parse_string(schedule)[1],
            "",
            f"Schedule invalid because parsing failed.{schedule}",
        )

    def test_generate(self):
        test_runs = 1000
        res_list = ["a", "b", "c", "d", "e"]
        # trans = 1
        for i in range(test_runs):
            # random testing
            res = random.sample(res_list, random.randint(1, 5))
            trans = random.randint(1, 7)
            # structured
            # if i%(test_runs/5) == 0:
            #     trans +=1
            #     res = res_list[0:1]
            # elif i%(test_runs/20) == 0:
            #     res.append(res_list[int(i%(test_runs/5)/(test_runs/20))+1])

            schedule = generate(trans, res, None, None)[0]
            self.valid_schedule(schedule, trans, res)

    def test_generate_recovery(self):
        test_runs = 1000
        res_list = ["a", "b", "c", "d", "e"]
        # trans = 1
        for i in range(test_runs):
            # random
            res = random.sample(res_list, random.randint(1, 5))
            trans = random.randint(2, 6)
            # # structured
            # if i%(test_runs/5) == 0:
            #     trans +=1
            #     res = res_list[0:2]
            # elif i%(test_runs/20) == 0:
            #     res.append(res_list[int(i%(test_runs/5)/(test_runs/20))+1])
            none = generate(trans, res, recovery="n")[0]
            self.assertFalse(
                Recovery.is_recoverable(none)[0], Schedule.parse_string(none)
            )
            self.assertFalse(
                Recovery.avoids_cascading_aborts(none)[0], Schedule.parse_string(none)
            )
            self.assertFalse(Recovery.is_strict(none)[0], Schedule.parse_string(none))
            self.valid_schedule(none, trans, res)

            recovery = generate(trans, res, recovery="r")[0]
            self.assertTrue(
                Recovery.is_recoverable(recovery)[0], Schedule.parse_string(recovery)
            )
            self.assertFalse(
                Recovery.avoids_cascading_aborts(recovery)[0],
                Schedule.parse_string(recovery),
            )
            self.assertFalse(
                Recovery.is_strict(recovery)[0], Schedule.parse_string(recovery)
            )
            self.valid_schedule(recovery, trans, res)

            aca = generate(trans, res, recovery="a")[0]
            self.assertTrue(Recovery.is_recoverable(aca)[0], Schedule.parse_string(aca))
            self.assertTrue(
                Recovery.avoids_cascading_aborts(aca)[0], Schedule.parse_string(aca)
            )
            self.assertFalse(Recovery.is_strict(aca)[0], Schedule.parse_string(aca))
            self.valid_schedule(aca, trans, res)

            st = generate(trans, res, recovery="s")[0]
            self.assertTrue(Recovery.is_recoverable(st)[0], Schedule.parse_string(st))
            self.assertTrue(
                Recovery.avoids_cascading_aborts(st)[0], Schedule.parse_string(st)
            )
            self.assertTrue(Recovery.is_strict(st)[0], Schedule.parse_string(st))
            self.valid_schedule(st, trans, res)

    def test_generate_deadlock(self):
        test_runs = 1000
        res_list = ["a", "b", "c", "d", "e"]
        # trans = 1
        no_deadlock_count = 0
        for i in range(test_runs):
            # random
            res = random.sample(res_list, random.randint(2, 5))  # at least 2 res
            trans = random.randint(2, 6)  # at least 2 trans
            # # structured
            # if i%(test_runs/5) == 0:
            #     trans +=1
            #     res = res_list[0:2]
            # elif i%(test_runs/20) == 0:
            #     res.append(res_list[int(i%(test_runs/5)/(test_runs/20))+1])
            deadlock = generate(trans, res, True)[0]
            self.assertTrue(predict_deadlock(deadlock), Schedule.parse_string(deadlock))
            self.valid_schedule(deadlock, trans, res)
            no_deadlock = generate(trans, res, False)[0]
            self.valid_schedule(no_deadlock, trans, res)
            if predict_deadlock(no_deadlock):
                no_deadlock_count += 1
        print("No deadlock generation failed in ", no_deadlock_count, "/", test_runs)
