from dbis_tm import Schedule, ConflictGraph, ConflictGraphNode
from tests.scheduletest import ScheduleTest


class Test_TM(ScheduleTest):
    # A tuple denotes: (schedule, is_well_formed, is_serializable)
    unparsed_schedule_tests = [
        ("w1(x)w1(y)r2(u)w2(x)r2(y)r3(x)w2(z)a2r1(z)c1c3", True, True),
        # well-formed, serializable
        ("R1(x)W1(x)r2(x)A1w2(x)C2", True, True),
        # well-formed, serializable
        ("w1(Y)w4(W)w3(Z)w2(X)r1(Z)r1(X)r4(Z)", True, True),
        # well-formed, serializable
        (
            "r1(x)w2(y)r1(x)w3(z)w3(x)r1(y)w1(y)w2(z)w1(z)w3(y)r2(x)c3r2(y)c2w1(y)a1",
            True,
            False,
        ),
        # well-formed, not serializable
        (
            "r1(x)w2(y)r1(x)w3(z)w3(x)r1(y)w1(y)w2(z)w1(z)w3(y)c3r2(y)c2w1(y)c1",
            True,
            False,
        ),
        # well-formed, not serializable
        (
            "r1(x)w2(y)r1(x)w3(z)w3(x)r1(y)w1y)w2(z)w1(z)w3(y)c3r2(y)c2w1(y)c1",
            False,
            False,
        ),
        # malformed
        (
            "r1(x)w2(y)r1(x)w3(z)w3(x)r1(y)w(y)w2(z)w1(z)w3(y)c3r2(y)c2w1(y)c1",
            False,
            False,
        ),
        # malformed
        (
            "r1(x)w2(y)r1(x)w3(z)w3(x)r1(y)w1(yw2(z)w1(z)w3(y)c3r2(y)c2w1(y)c1",
            False,
            False,
        ),
        # malformed
        (
            "r1(x)w2(y)r1(x)w3(z)w3(x)r1(y)1(y)w2(z)w1(z)w3(y)c3r2(y)c2w1(y)c1",
            False,
            False,
        )
        # malformed
    ]

    # A tuple denotes: (schedule, schedule_mod, compare_schedules)
    compare_schedules_test = [
        (
            "w1(x)r2(e)r1(y)",
            "rl2(e)wl1(x)w1(x)r2(e)rl1(y)r1(y)ru1(y)wu1(x)ru2(e)",
            True,
        ),
        (
            "r2(y)w3(x)w1(z)w3(y)r1(x)r2(z)r3(z)c1c2c3",
            "rl2(y)r2(y)wl3(x)w3(x)wl1(z)w1(z)wl3(y)w3(y)rl1(x)r1(x)wu1(z)ru1(x)rl2(z)r2(z)ru2(z)ru2(y)"
            "rl3(z)r3(z)wu3(x)wu3(y)ru3(z)c1c2c3",
            True,
        ),
    ]

    def test_schedule_parsing(self):
        """
        tests parse_schedule(unparsed_schedule)
        """
        for (schedule, is_well_formed, _), i in zip(
            self.unparsed_schedule_tests, range(0, len(self.unparsed_schedule_tests))
        ):
            _, msg = Schedule.parse_schedule(schedule)
            self.assertEqual(is_well_formed, msg == "", f"Schedule {i}:")

    def test_compare_schedules(self):
        """
        tests check_schedule(schedule, schedule_mod)
        """
        for (schedule, schedule_mod, result), _i in zip(
            self.compare_schedules_test, range(len(self.compare_schedules_test))
        ):
            parsed, msg = Schedule.parse_schedule(schedule)
            parsed_mod, msg_mod = Schedule.parse_schedule(schedule_mod)
            returned = Schedule.is_operations_same(parsed, parsed_mod)
            # returned =len(problems)==0
            self.assertEqual(returned, result)

    def testEdgeLessConflictGraph(self):
        """
        test the content of an empty graph
        """
        g_1 = ConflictGraph()
        t1 = ConflictGraphNode(1)
        t2 = ConflictGraphNode(2)
        self.assertTrue(g_1.isEmpty())
        gvMarkup = g_1.get_graphviz_graph()
        debug = False
        if debug:
            print(gvMarkup)
        self.assertTrue(
            """{
	graph [label="Konfliktgraph "]
}"""
            in str(gvMarkup)
        )
        g_1.add_edge(t1, t2)
        gvMarkup = g_1.get_graphviz_graph()
        if debug:
            print(gvMarkup)
        self.assertTrue("t1 -> t2" in str(gvMarkup))
