from dbis_tm import Schedule, ConflictGraph, ConflictGraphNode, SyntaxCheck
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

    def testConfSyntaxCheck(self):
        """
        test the SyntaxCheck functionality for Conflicts
        """
        s1_conf = {("w_2(x)", "r_1(x)"), ("w_1(z)", "w_2(z)")}
        s2_conf = {
            ("r_2(x)", "w_3(x)"),
            ("w_1(y)", "r_2(y)"),
            ("w_1(y)", "w_2(y)"),
            ("w_1(y)", "w_3(y)"),
            ("w_3(z)", "w_1(z)"),
            ("w_3(z)", "w_2(z)"),
            ("r_2(y)", "w_3(y)"),
            ("w_2(y)", "w_3(y)"),
            ("w_2(y)", "r_1(y)"),
            ("w_1(z)", "w_2(z)"),
            ("w_3(y)", "r_1(y)"),
            ("w_3(y)", "w_2(y)"),
            ("r_1(y)", "w_2(y)"),
        }
        conf_err1 = []
        conf_err2 = {}
        conf_err3 = "Garbage"
        conf_err4 = {("a"), ("b", "c", "e")}
        conf_err5 = {("a_3(x)", "b")}
        debug = False
        expectedList = [
            None,
            None,
            "[] ist kein Set",
            None,
            "Garbage ist kein Set",
            (
                "Das Tupel ('b', 'c', 'e') von {('b', 'c', 'e'), 'a'} ist kein Paar",
                "Das Tupel a von {'a', ('b', 'c', 'e')} ist kein Paar",
            ),
            "Das Tupel ('a_3(x)', 'b') von {('a_3(x)', 'b')} hat keine korrekte Syntax",
        ]
        for i, conf in enumerate(
            [s1_conf, s2_conf, conf_err1, conf_err2, conf_err3, conf_err4, conf_err5]
        ):
            msg = SyntaxCheck.check_conf_set_syntax(conf)
            if debug:
                print(f"{i}:{msg}", "test")
            expected = expectedList[i]
            if isinstance(expected, tuple):
                expected1, expected2 = expected
                self.assertTrue(expected1 == msg or expected2 == msg)
            else:
                self.assertEqual(expected, msg)

    def testScheduleSyntaxCheck(self):
        """
        test the SyntaxCheck functionality for Schedules
        """
        schedule_1 = "w_2(x) w_1(z) r_2(y) r_1(x) r_3(z) w_3(x) w_1(y) c_1 c_2 c_3"
        schedule_2 = "r_2(z) w_1(y) r_3(z) r_2(y) r_1(x) w_2(y) w_3(x) c_1 c_2 c_3"
        schedule_3 = "r_1(x) w_2(z) w_3(y) w_2(x) r_3(z) r_1(y) r_2(y) c_1 c_2 c_3"
        schedule_4 = "w2(x)"
        schedule_5 = "rl_1(x) r_1(x) wl_2(z) w_2(z)  wl_3(y) w_3(y) wl_2(x) w_2(x) rl_3(z) r_3(z) wu_3(y) ru_3(z) rl_1(y) r_1(y) ru_1(x) ru_1(y) rl_2(y) r_2(y) wu_2(z) wu_2(x) ru_2(y) c_1 c_2 c_3"
        schedule_6 = "wl_2(x) rl_2(y) w_2(x) wu_2(x) r_2(y) ru_2(y) c_2 wl_1(z) rl_1(x) wl_1(y) w_1(z) wu_1(z) r_1(x) ru_1(x) rl_3(z) wl_3(x) r_3(z) ru_3(z) w_3(x) wu_3(x) c_3 w_1(y) wu_1(y) c_1"
        schedule_err2 = ""
        expected = [
            None,
            None,
            None,
            None,
            None,
            None,
            "Leerer Schedule kann keine Lösung sein",
        ]
        debug = False
        for i, schedule in enumerate(
            [
                schedule_1,
                schedule_2,
                schedule_3,
                schedule_4,
                schedule_5,
                schedule_6,
                schedule_err2,
            ]
        ):
            msg = SyntaxCheck.check_schedule_syntax(schedule)
            if debug:
                print(msg)
            self.assertEqual(expected[i], msg)
