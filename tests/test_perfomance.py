from dbis_tm import Schedule, OperationType, Operation
from dbis_tm.TMSolver import Scheduling
from src.dbis_tm.Solution_generator import Perform_scheduling, Perform_conflictgraph
from unittest import TestCase


class TestPerformer(TestCase):
    test_cases_scheduling = [
        (0, "w_1(z) w_3(y) r_1(x) r_3(z) r_2(y) w_2(z) w_3(x) c_1 c_2 c_3", "", ""),
        (1, "r_1(x) w_3(z) r_2(x) r_1(z) r_3(y) w_1(z) w_2(y) c_1 c_2 c_3", "", ""),
        (
            2,
            "r_1(x) w_3(z) r_2(x) r_1(z) r_3(y) w_1(z) w_2(y) r1(x) r1(x) c_1 c_2 c_3",
            "",
            "",
        ),
        (
            3,
            "w2(x) r3(x) r1(y) r1(z) w3(y) w1(x) c3 w1(y) c1 r2(x) c2 ",
            "Deadlock occurred",
            "Deadlock occurred",
        ),
        (
            4,
            "w2(a) w1(a) w3(c) r1(c) r3(a) c2 w1(c) c1 a3",
            "Deadlock occurred",
            "Deadlock occurred",
        ),
        (5, "w1(a) a1 r2(r) w3(e) c3 r2(a) w2(r) c2", "", ""),
        (6, "w1(a) a1 r2(r) w3(e) a3 r2(a) w2(r) a2", "", ""),
        # No example of s2pl'', 'Deadlock occurred' SS2pl bc
        # - a deadlock with reads needs to happen (r1(a) r2(b) w1(b) w2(a))
        # - but no locks can be acquired after first unlock :(
    ]

    def test_scheduling_performer(self):
        for (
            number,
            schedule_str,
            errors_s2pl,
            errors_ss2pl,
        ) in self.test_cases_scheduling:
            parsed_schedule = Schedule.parse_schedule(schedule_str)[0]
            s2pl, s2pl_msg = Perform_scheduling.perform_S2PL(schedule_str)
            self.assertEqual(
                s2pl_msg,
                errors_s2pl,
                f"{number} S2PL incorrect error message {schedule_str, Schedule.parse_string(s2pl)[0]}",
            )
            self.check_same(number, parsed_schedule, s2pl, bool(errors_s2pl))
            if not errors_s2pl:
                self.assertTrue(
                    Scheduling.is_S2PL(s2pl)[0],
                    f"{number} SS2PL computed schedule not in S2PL {s2pl}",
                )

            ss2pl, ss2pl_msg = Perform_scheduling.perform_SS2PL(schedule_str)
            self.assertEqual(
                ss2pl_msg,
                errors_ss2pl,
                f"{number} SS2PL incorrect error message {schedule_str, ss2pl}",
            )
            self.check_same(number, parsed_schedule, ss2pl, bool(errors_s2pl))
            if not errors_ss2pl:
                self.assertTrue(
                    Scheduling.is_SS2PL(ss2pl)[0],
                    f"{number} SS2PL computed schedule not in SS2PL {ss2pl}",
                )

            c2pl = Perform_scheduling.perform_C2PL(schedule_str)
            self.check_same(number, parsed_schedule, c2pl, False)
            self.assertTrue(
                Scheduling.is_C2PL(c2pl),
                f"{number} computed schedule not in SS2PL {c2pl}",
            )

    def check_same(
        self, number: int, original: Schedule, schedule: Schedule, deadlock: bool
    ) -> bool:
        """Helper to check wether the computed schedules without locks have the same order in the actions
        and the same operations"""
        locking = [
            OperationType.READ_LOCK,
            OperationType.READ_UNLOCK,
            OperationType.WRITE_LOCK,
            OperationType.WRITE_UNLOCK,
        ]
        helper = [op for op in schedule.operations if op.op_type not in locking]
        cleaned = Schedule(
            helper,
            schedule.resources,
            schedule.tx_count,
            schedule.aborts,
            schedule.commits,
        )
        if not deadlock:
            self.assertEqual(
                original.tx_count,
                cleaned.tx_count,
                f"{number} The schedules differ in the transactions{original.tx_count,cleaned.tx_count}",
            )
            self.assertEqual(
                original.resources,
                cleaned.resources,
                f"{number} The schedules differ in the resources{original.resources,cleaned.resources}",
            )

            self.assertEqual(
                [],
                [op for op in original.operations if op not in cleaned.operations],
                f"{number} The schedules differ in the operations{original.operations,cleaned.operations}",
            )
            self.assertEqual(
                [],
                [op for op in cleaned.operations if op not in cleaned.operations],
                f"{number} The schedules differ in the operations{original.operations,cleaned.operations}",
            )
            self.assertEqual(
                len(cleaned.operations),
                len(original.operations),
                f"{number} The schedules differ in the operation amount{original.operations,cleaned.operations}",
            )

            self.assertEqual(
                original.commits.keys(),
                cleaned.commits.keys(),
                f"{number} The schedules differ in the commits{original.commits.keys(),cleaned.commits.keys()}",
            )
            self.assertEqual(
                original.aborts.keys(),
                cleaned.aborts.keys(),
                f"{number} The schedules differ in the aborts{original.aborts.keys(),cleaned.aborts.keys()}",
            )

        for i in range(1, original.tx_count + 1):
            op_new = [op for op in cleaned.operations if op.tx_number == i]
            op_orig = [op for op in original.operations if op.tx_number == i]
            if deadlock:
                op_orig = op_orig[: len(op_new) - 1]
            for k, l in zip(op_orig, op_new):
                self.assertTrue(Operation.__eq__(k, l))

    def test_compute_conflictset(self):
        # A tuple denotes: (schedule, conflictset)
        conflict_schedules = [
            (
                "w1(x)r2(y)r1(x)r2(x)c1w2(x)c2",
                {("w1(x)", "r2(x)"), ("w1(x)", "w2(x)"), ("r1(x)", "w2(x)")},
            ),
            ("w1(x)r2(y)r1(x)r2(x)c1w2(x)a2", set()),
            ("w1(x)r2(y)r1(x)r2(x)a1w2(x)c2", set()),
            ("w1(x)r2(y)r1(x)r2(x)a1w2(x)a2", set()),
            ("w1(a) w3(c) r2(a) a2 r1(c) r3(a) a1 a3", set()),
            (
                "w1(a) w3(c) r2(a) c2 r1(c) r3(a) c1 c3",
                {("w1(a)", "r2(a)"), ("w1(a)", "r3(a)"), ("w3(c)", "r1(c)")},
            ),
        ]
        for schedule, cset in conflict_schedules:
            solution = Perform_conflictgraph.compute_conflict_quantity(
                Schedule.parse_schedule(schedule)[0]
            )
            self.assertEqual(
                cset, solution, f"Wrong conflict set returned{schedule, solution}"
            )
