"""
Created 2022-05

@author: Lara
@author: Marc
@author: Wolfgang
"""
from dbis_tm import Schedule, ConflictGraph, ConflictGraphNode
from src.dbis_tm.TMSolver import Recovery, Scheduling, Serializability
from src.dbis_tm.TMCheck import SyntaxCheck
from tests.scheduletest import ScheduleTest


class TestTM(ScheduleTest):
    """
    tests and playground
    for https://git.rwth-aachen.de/i5/teaching/dbis-digi-2022/-/issues/35
    """

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

    # A tuple denotes: (schedule, (is_RC, proof/counterexample), (is_ACA, proof/counterexample), (is_ST, proof/counterexample))
    schedule_recoverability_tests = [
        (
            "w1(x)w3(x)a3r2(x)c1c2",
            (
                True,
                {
                    (1, "x", 2, False),
                    (1, "x", 3, False),
                    (2, "x", 1, True),
                    (2, "x", 3, False),
                    (3, "x", 1, False),
                    (3, "x", 2, False),
                },
            ),
            (False, {(2, "x", 1, True)}),
            (
                False,
                {("w1(x)", "w3(x)", False, False), ("w1(x)", "r2(x)", False, False)},
            ),
        ),
        # aborted w inbetween
        (
            "w1(x)w3(y)a3r2(x)c1a2",  # True,False,False),
            (
                True,
                {
                    (1, "x", 2, False),
                    (1, "x", 3, False),
                    (2, "x", 1, True),
                    (2, "x", 3, False),
                    (3, "x", 1, False),
                    (3, "x", 2, False),
                    (1, "y", 2, False),
                    (1, "y", 3, False),
                    (2, "y", 1, False),
                    (2, "y", 3, False),
                    (3, "y", 1, False),
                    (3, "y", 2, False),
                },
            ),
            (False, {(2, "x", 1, True)}),
            (False, {("w1(x)", "r2(x)", False, False)}),
        ),
        # reader aborted
        (
            "w1(x)w3(y)a1r2(x)c1c3",  # True,True,True),
            (
                True,
                {
                    (1, "x", 2, False),
                    (1, "x", 3, False),
                    (2, "x", 1, False),
                    (2, "x", 3, False),
                    (3, "x", 1, False),
                    (3, "x", 2, False),
                    (1, "y", 2, False),
                    (1, "y", 3, False),
                    (2, "y", 1, False),
                    (2, "y", 3, False),
                    (3, "y", 1, False),
                    (3, "y", 2, False),
                },
            ),
            (
                True,
                {
                    (1, "x", 2, False),
                    (1, "x", 3, False),
                    (2, "x", 1, False),
                    (2, "x", 3, False),
                    (3, "x", 1, False),
                    (3, "x", 2, False),
                    (1, "y", 2, False),
                    (1, "y", 3, False),
                    (2, "y", 1, False),
                    (2, "y", 3, False),
                    (3, "y", 1, False),
                    (3, "y", 2, False),
                },
            ),
            (True, {("w1(x)", "r2(x)", True, False)}),
        ),
        # no read because of abort before read
        (
            "w1(x)w3(y)a3r2(x)a1c2",  # False,False,False),
            (False, {(2, "x", 1, True)}),
            (False, {(2, "x", 1, True)}),
            (False, {("w1(x)", "r2(x)", False, False)}),
        ),
        # writer aborts at the end
        (
            "w1(x)r2(y)a1w2(x)r2(x)w2(y)c2",  # True,True,True),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (True, {("w1(x)", "w2(x)", True, False), ("w1(x)", "r2(x)", True, False)}),
        ),
        (
            "w1(x)r2(y)a1w2(x)r2(x)w2(y)a2",  # True,True,True),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (True, {("w1(x)", "w2(x)", True, False), ("w1(x)", "r2(x)", True, False)}),
        ),
        # strict with aborts
        (
            "w1(x)r2(y)r1(x)r2(x)c1w2(x)c2",  # True,False,False),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, True),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (False, {(2, "x", 1, True)}),
            (False, {("w1(x)", "r2(x)", False, False)}),
        ),
        (
            "w1(x)w2(y)r1(y)r2(x)c2w1(y)c1",  # False,False,False),
            (False, {(2, "x", 1, True)}),
            (False, {(2, "x", 1, True), (1, "y", 2, True)}),
            (
                False,
                {("w1(x)", "r2(x)", False, False), ("w2(y)", "r1(y)", False, False)},
            ),
        ),
        (
            "w1(x)r2(y)c1w2(x)r2(x)w2(y)c2",  # True,True,True),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (True, {("w1(x)", "w2(x)", False, True), ("w1(x)", "r2(x)", False, True)}),
        ),
        (
            "w2(x)r1(y)r2(x)r1(x)c2w1(y)c1",  # True,False,False),
            (
                True,
                {
                    (1, "x", 2, True),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (False, {(1, "x", 2, True)}),
            (False, {("w2(x)", "r1(x)", False, False)}),
        ),
        (
            "w1(x)w1(y)r2(u)w2(x)r2(y)w2(y)c2w1(z)c1",  # False, False, False),
            (False, {(2, "y", 1, True)}),
            (False, {(2, "y", 1, True)}),
            (
                False,
                {
                    ("w1(x)", "w2(x)", False, False),
                    ("w1(y)", "r2(y)", False, False),
                    ("w1(y)", "w2(y)", False, False),
                },
            ),
        ),
        (
            "w1(x)w1(y)r2(u)w2(x)r2(y)w2(y)w1(z)c1c2",  # True, False, False),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, True),
                    (1, "u", 2, False),
                    (2, "u", 1, False),
                    (1, "z", 2, False),
                    (2, "z", 1, False),
                },
            ),
            (False, {(2, "y", 1, True)}),
            (
                False,
                {
                    ("w1(x)", "w2(x)", False, False),
                    ("w1(y)", "r2(y)", False, False),
                    ("w1(y)", "w2(y)", False, False),
                },
            ),
        ),
        (
            "w1(x)w1(y)r2(u)w2(x)r2(y)r3(x)w2(z)a2r1(z)c1c3",  # False, False, False),
            (False, {(3, "x", 2, True)}),
            (False, {(2, "y", 1, True), (3, "x", 2, True)}),
            (
                False,
                {
                    ("w1(x)", "w2(x)", False, False),
                    ("w2(x)", "r3(x)", False, False),
                    ("w1(x)", "r3(x)", False, False),
                    ("w1(y)", "r2(y)", False, False),
                },
            ),
        ),
        (
            "r1(x)w2(y)r1(x)w3(z)w3(x)r1(y)w1(y)w2(z)w1(z)w3(y)r2(x)c3r2(y)c2w1(y)a1",  # True, False, False),
            (
                True,
                {
                    (1, "x", 2, False),
                    (1, "x", 3, False),
                    (2, "x", 1, False),
                    (2, "x", 3, True),
                    (3, "x", 1, False),
                    (3, "x", 2, False),
                    (1, "y", 2, True),
                    (1, "y", 3, False),
                    (2, "y", 1, False),
                    (2, "y", 3, True),
                    (3, "y", 1, False),
                    (3, "y", 2, False),
                    (1, "z", 2, False),
                    (1, "z", 3, False),
                    (2, "z", 1, False),
                    (2, "z", 3, False),
                    (3, "z", 1, False),
                    (3, "z", 2, False),
                },
            ),
            (False, {(2, "x", 3, True), (1, "y", 2, True)}),
            (
                False,
                {
                    ("w2(y)", "r1(y)", False, False),
                    ("w2(y)", "w1(y)", False, False),
                    ("w2(y)", "w3(y)", False, False),
                    ("w1(y)", "w3(y)", False, False),
                    ("w1(y)", "r2(y)", False, False),
                    ("w3(z)", "w2(z)", False, False),
                    ("w3(z)", "w1(z)", False, False),
                    ("w2(z)", "w1(z)", False, False),
                    ("w3(x)", "r2(x)", False, False),
                },
            ),
        ),
        (
            "w1(x)r2(y)r1(x)r2(x)c1w2(x)c2",  # True, False, False),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, True),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (False, {(2, "x", 1, True)}),
            (False, {("w1(x)", "r2(x)", False, False)}),
        ),
        (
            "w1(x)r2(y)c1w2(x)r2(x)w2(y)c2",  # True, True, True),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (True, {("w1(x)", "w2(x)", False, True), ("w1(x)", "r2(x)", False, True)}),
        ),
        (
            "w2(x)r1(y)r2(x)r1(x)c2w1(y)c1",  # True, False, False),
            (
                True,
                {
                    (1, "x", 2, True),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, False),
                },
            ),
            (False, {(1, "x", 2, True)}),
            (False, {("w2(x)", "r1(x)", False, False)}),
        ),
        (
            "w1(x)w1(y)r2(u)w2(x)r2(y)w2(y)w1(z)c1c2",  # True, False, False),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, True),
                    (1, "u", 2, False),
                    (2, "u", 1, False),
                    (1, "z", 2, False),
                    (2, "z", 1, False),
                },
            ),
            (False, {(2, "y", 1, True)}),
            (
                False,
                {
                    ("w1(x)", "w2(x)", False, False),
                    ("w1(y)", "r2(y)", False, False),
                    ("w1(y)", "w2(y)", False, False),
                },
            ),
        ),
        (
            "w1(x)w1(y)r2(u)w2(x)w1(z)c1r2(y)w2(y)c2",  # True, True, False),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, True),
                    (1, "u", 2, False),
                    (2, "u", 1, False),
                    (1, "z", 2, False),
                    (2, "z", 1, False),
                },
            ),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, True),
                    (1, "u", 2, False),
                    (2, "u", 1, False),
                    (1, "z", 2, False),
                    (2, "z", 1, False),
                },
            ),
            (False, {("w1(x)", "w2(x)", False, False)}),
        ),
        (
            "w1(x)w1(y)r2(u)w1(z)c1w2(x)r2(y)w2(y)c2",  # True, True, True)]
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, True),
                    (1, "u", 2, False),
                    (2, "u", 1, False),
                    (1, "z", 2, False),
                    (2, "z", 1, False),
                },
            ),
            (
                True,
                {
                    (1, "x", 2, False),
                    (2, "x", 1, False),
                    (1, "y", 2, False),
                    (2, "y", 1, True),
                    (1, "u", 2, False),
                    (2, "u", 1, False),
                    (1, "z", 2, False),
                    (2, "z", 1, False),
                },
            ),
            (
                True,
                {
                    ("w1(x)", "w2(x)", False, True),
                    ("w1(y)", "r2(y)", False, True),
                    ("w1(y)", "w2(y)", False, True),
                },
            ),
        ),
    ]

    # A tuple denotes: (schedule, (is_2PL,[errors]), (is_C2PL,[errors]), (is_S2PL,[errors]), (is_SS2PL,[errors]))
    scheduling_tests = [
        (
            "r1(y)rl1(y)ru1(y)",  # l1 broken
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
        ),
        (
            "rl1(y)ru1(y)r1(y)",  # l1 broken
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
        ),
        (
            "wl1(x)w1(x)r1(y)wu1(x)",  # l2 broken
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
            (False, ["L2: Nicht gesperrt vor Ausführung: r1(y)"]),
        ),
        (
            "wl1(x)rl1(y)w1(x)r1(y)ru1(y)ru1(y)wu1(x)",  # l3 broken
            (False, ["L3: Nicht gesperrt vor entsperren: ru1(y)"]),
            (False, ["L3: Nicht gesperrt vor entsperren: ru1(y)"]),
            (False, ["L3: Nicht gesperrt vor entsperren: ru1(y)"]),
            (False, ["L3: Nicht gesperrt vor entsperren: ru1(y)"]),
        ),
        (
            "wl1(x)rl1(y)w1(x)r1(y)ru1(y)ru1(z)wu1(x)",  # l3 broken
            (False, ["L3: Nicht gesperrt vor entsperren: ru1(z)"]),
            (False, ["L3: Nicht gesperrt vor entsperren: ru1(z)"]),
            (False, ["L3: Nicht gesperrt vor entsperren: ru1(z)"]),
            (False, ["L3: Nicht gesperrt vor entsperren: ru1(z)"]),
        ),
        (
            "wl1(x)rl2(x)r2(x)ru2(x)w1(x)wu1(x)",  # l4 broken
            (
                False,
                [
                    "L4: Schreibsperre inkompatibel mit allen andeden Sperren (rl2(x), [wl1(x)])"
                ],
            ),
            (
                False,
                [
                    "L4: Schreibsperre inkompatibel mit allen andeden Sperren (rl2(x), [wl1(x)])"
                ],
            ),
            (
                False,
                [
                    "L4: Schreibsperre inkompatibel mit allen andeden Sperren (rl2(x), [wl1(x)])"
                ],
            ),
            (
                False,
                [
                    "L4: Schreibsperre inkompatibel mit allen andeden Sperren (rl2(x), [wl1(x)])"
                ],
            ),
        ),
        (
            "rl1(x)wl2(x)r1(x)ru1(x)w2(x)wu2(x)",  # l4 broken
            (
                False,
                ["L4: Schreibsperre inkompatibel mit Lesesperren (wl2(x), [rl1(x)])"],
            ),
            (
                False,
                ["L4: Schreibsperre inkompatibel mit Lesesperren (wl2(x), [rl1(x)])"],
            ),
            (
                False,
                ["L4: Schreibsperre inkompatibel mit Lesesperren (wl2(x), [rl1(x)])"],
            ),
            (
                False,
                ["L4: Schreibsperre inkompatibel mit Lesesperren (wl2(x), [rl1(x)])"],
            ),
        ),
        (
            "wl1(x)w1(x)r2(e)wu1(x)rl1(y)r1(y)ru1(y)",  # 2PL verletzt
            (
                False,
                [
                    "2PL: Entsperren bevor alle anderen Sperren gesetzt sind: wu1(x)",
                    "L2: Nicht gesperrt vor Ausführung: r2(e)",
                ],
            ),
            (
                False,
                [
                    "2PL: Entsperren bevor alle anderen Sperren gesetzt sind: wu1(x)",
                    "L2: Nicht gesperrt vor Ausführung: r2(e)",
                ],
            ),
            (
                False,
                [
                    "2PL: Entsperren bevor alle anderen Sperren gesetzt sind: wu1(x)",
                    "L2: Nicht gesperrt vor Ausführung: r2(e)",
                ],
            ),
            (
                False,
                [
                    "2PL: Entsperren bevor alle anderen Sperren gesetzt sind: wu1(x)",
                    "L2: Nicht gesperrt vor Ausführung: r2(e)",
                ],
            ),
        ),
        (
            "rl2(y)r2(y)wl3(x)w3(x)wl1(z)w1(z)",
            (False, ["L1: Nicht alle Sperren aufgehoben: ['r2y', 'w3x', 'w1z']"]),
            (False, ["L1: Nicht alle Sperren aufgehoben: ['r2y', 'w3x', 'w1z']"]),
            (False, ["L1: Nicht alle Sperren aufgehoben: ['r2y', 'w3x', 'w1z']"]),
            (False, ["L1: Nicht alle Sperren aufgehoben: ['r2y', 'w3x', 'w1z']"]),
        ),
        (
            "rl2(e)wl1(x)w1(x)r2(e)rl1(y)r1(y)ru1(y)wu1(x)ru2(e)",
            (True, []),
            (
                False,
                ["C2PL: Sperren [rl1(y)] wurden nach der ersten r/w Operation gesetzt"],
            ),
            (
                False,
                [
                    "S2PL: Entsperren von [2] ist nicht direkt nach der letzten r/w Operation erfolgt"
                ],
            ),
            (
                False,
                [
                    "SS2PL: Entsperren von [2] ist nicht direkt nach der letzten r/w Operation erfolgt"
                ],
            ),
        ),
        (
            "rl1(x)r1(x)wl3(z)w3(z)rl2(x)r2(x)rl3(y)r3(y)wu3(z)ru3(y)"
            "c3rl1(z)r1(z)wl1(z)ru1(x)ru1(z)w1(z)wu1(z)c1wl2(y)ru2(x)"
            "w2(y)wu2(y)c2",
            (True, []),
            (
                False,
                [
                    "C2PL: Sperren [rl1(z), wl1(z), wl2(y), rl3(y)] wurden nach der ersten r/w Operation gesetzt"
                ],
            ),
            (True, []),
            (
                False,
                [
                    "SS2PL: [ru1(x), ru1(z), ru2(x)] wurde vor der letzten r/w Operation entsperrt"
                ],
            ),
        ),
        (
            "wl1(x)rl1(y)w1(x)wu1(x)r1(y)ru1(y)",
            (True, []),
            (True, []),
            (False, ["S2PL: [wu1(x)] wurden vor der letzten r/w Operation entsperrt"]),
            (False, ["SS2PL: [wu1(x)] wurde vor der letzten r/w Operation entsperrt"]),
        ),
        (
            "wl1(z)rl1(x)w1(z)wu1(z)r1(x)ru1(x)c1wl3(y)rl3(z)wl3(x)"
            "w3(y)wu3(y)r3(z)ru3(z)rl2(y)wl2(z)r2(y)ru2(y)w2(z)wu2(z)"
            "c2w3(x)wu3(x)c3",
            (True, []),
            (True, []),
            (
                False,
                [
                    "S2PL: [wu1(z), wu3(y)] wurden vor der letzten r/w Operation entsperrt"
                ],
            ),
            (
                False,
                [
                    "SS2PL: [wu1(z), ru2(y), wu3(y), ru3(z)] wurde vor der letzten r/w Operation entsperrt"
                ],
            ),
        ),
        (
            "wl1(x)w1(x)rl1(y)r1(y)ru1(y)wu1(x)",
            (True, []),
            (
                False,
                ["C2PL: Sperren [rl1(y)] wurden nach der ersten r/w Operation gesetzt"],
            ),
            (True, []),
            (True, []),
        ),
        (
            "wl1(x)rl1(y)r1(y)ru1(y)w1(x)wu1(x)",
            (True, []),
            (True, []),
            (True, []),
            (False, ["SS2PL: [ru1(y)] wurde vor der letzten r/w Operation entsperrt"]),
        ),
        (
            "wl1(x)rl1(y)w1(x)r1(y)ru1(y)wu1(x)",
            (True, []),
            (True, []),
            (True, []),
            (True, []),
        ),
        (
            "wl1(x)rl1(y)w1(x)r1(y)ru1(y)wu1(x)",
            (True, []),
            (True, []),
            (True, []),
            (True, []),
        ),
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

    def test_serializability(self):
        """
        tests is_serializable(parsed_schedule)
        """
        for (schedule, _, is_serializable), i in zip(
            self.unparsed_schedule_tests, range(len(self.unparsed_schedule_tests))
        ):
            parsed, msg = Schedule.parse_schedule(schedule)
            if msg == "":
                Serializability.remove_aborted_tx(parsed)
                actual, _ = Serializability.is_serializable(parsed)
                self.assertEqual(is_serializable, actual, f"Schedule {i}:")

    def test_removing_aborted_TM(self):
        """
        tests test_remove_aborted_TM(parsed_schedule)
        """
        unparsed_schedule = (
            "r1(x)w2(y)r1(x)w3(z)w3(x)r1(y)w1(y)w2(z)w1(z)w3(y)r2(x)c3r2(y)c2w1(y)a1"
        )
        expected = "w2(y)w3(z)w3(x)w2(z)w3(y)r2(x)r2(y)"

        parsed, msg = Schedule.parse_schedule(unparsed_schedule)
        self.assertEqual(msg, "")

        actual, _ = Serializability.is_serializable(parsed)
        self.assertFalse(actual)

        Serializability.remove_aborted_tx(parsed)
        expected, msg = Schedule.parse_schedule(expected)
        self.assertEqual(msg, "")
        actual, _ = Serializability.is_serializable(expected)
        self.assertFalse(actual)
        self.assertEqual(expected.operations, parsed.operations)

        actual, _ = Serializability.is_serializable(parsed)
        self.assertFalse(actual)

    def test_reads_from(self):
        """
        tests reads_from(parsed_schedule, tx1, resource, tx2)
        """
        unparsed_schedule = "w1(y)r2(y)a1c2"
        parsed1, msg = Schedule.parse_schedule(unparsed_schedule)
        self.assertEqual(msg, "")
        self.assertTrue(Recovery.reads_from(parsed1, 2, "y", 1)[0])

        unparsed_schedule = "w1(x)w1(y)r2(u)w2(x)r2(y)r3(x)w2(z)a2r1(z)c1c3"
        parsed2, msg = Schedule.parse_schedule(unparsed_schedule)
        self.assertEqual(msg, "")
        self.assertTrue(Recovery.reads_from(parsed2, 3, "x", 2)[0])
        self.assertFalse(Recovery.reads_from(parsed2, 3, "x", 1)[0])
        self.assertTrue(Recovery.reads_from(parsed2, 2, "y", 1)[0])
        self.assertFalse(Recovery.reads_from(parsed2, 1, "z", 2)[0])

        unparsed_schedule = "w1(y)a1r2(y)c2"
        parsed1, msg = Schedule.parse_schedule(unparsed_schedule)
        self.assertEqual(msg, "")
        self.assertFalse(Recovery.reads_from(parsed1, 2, "y", 1)[0])

        unparsed_schedule = "w3(y)w1(y)r2(y)c2a1c3"
        parsed1, msg = Schedule.parse_schedule(unparsed_schedule)
        self.assertEqual(msg, "")
        self.assertTrue(Recovery.reads_from(parsed1, 2, "y", 1)[0])
        self.assertFalse(Recovery.reads_from(parsed1, 2, "y", 3)[0])

        unparsed_schedule = "w3(y)w1(y)a1r2(y)c2c3"
        parsed1, msg = Schedule.parse_schedule(unparsed_schedule)
        self.assertEqual(msg, "")
        self.assertFalse(Recovery.reads_from(parsed1, 2, "y", 1)[0])
        self.assertTrue(Recovery.reads_from(parsed1, 2, "y", 3)[0])

    def test_is_recoverable(self):
        """
        tests is_recoverable(parsed_schedule)
        """
        for (schedule, (is_recoverable, proof), _, _), i in zip(
            self.schedule_recoverability_tests,
            range(len(self.schedule_recoverability_tests)),
        ):
            parsed, msg = Schedule.parse_schedule(schedule)
            self.assertEqual(msg, "")
            actual, result = Recovery.is_recoverable(parsed)
            self.assertEqual(proof, result, f"Schedule {i}: {schedule, result}")
            self.assertEqual(is_recoverable, actual, f"Schedule {i}: {schedule}")

    def test_avoids_cascading_aborts(self):
        """
        tests avoids_cascading_aborts(parsed_schedule)
        """
        for (schedule, _, (avoids_cascading_aborts, proof), _), i in zip(
            self.schedule_recoverability_tests,
            range(len(self.schedule_recoverability_tests)),
        ):
            parsed, msg = Schedule.parse_schedule(schedule)
            self.assertEqual(msg, "")
            actual, result = Recovery.avoids_cascading_aborts(parsed)
            self.assertEqual(proof, result, f"Schedule {i}: {schedule, result}")
            self.assertEqual(
                avoids_cascading_aborts, actual, f"Schedule {i}: {schedule}"
            )

    def test_is_strict(self):
        """
        tests is_strict(parsed_schedule)
        """
        for (schedule, _, _, (is_strict, proof)), i in zip(
            self.schedule_recoverability_tests,
            range(len(self.schedule_recoverability_tests)),
        ):
            parsed, msg = Schedule.parse_schedule(schedule)
            self.assertEqual(msg, "")
            actual, result = Recovery.is_strict(parsed)
            self.assertEqual(proof, result, f"Schedule {i}: {schedule, result}")
            self.assertEqual(is_strict, actual, f"Schedule {i}: {schedule}")

    def test_is_2PL(self):
        """
        tests is_2PL(parsed_schedule)
        """
        for (schedule, (is2PL, reason), _, _, _), i in zip(
            self.scheduling_tests, range(len(self.scheduling_tests))
        ):
            parsed, msg = Schedule.parse_schedule(schedule)
            self.assertEqual(msg, "")
            actual, errors = Scheduling.is_2PL(parsed)
            self.assertEqual(
                is2PL, actual, f"Schedule {i}: {schedule}\n Error: {errors}"
            )
            self.assertEqual(not errors, is2PL)
            self.assertEqual(
                reason, errors, f"Schedule {i}: {schedule}\n Error: {errors}"
            )

    def test_is_C2PL(self):
        """
        tests is_C2PL(parsed_schedule)
        """
        for (schedule, _, (isC2PL, reason), _, _), i in zip(
            self.scheduling_tests, range(len(self.scheduling_tests))
        ):
            parsed, msg = Schedule.parse_schedule(schedule)
            self.assertEqual(msg, "")
            actual, errors = Scheduling.is_C2PL(parsed)
            self.assertEqual(
                isC2PL, actual, f"Schedule {i}: {schedule}\n Error: {errors}"
            )
            self.assertEqual(not errors, isC2PL)
            self.assertEqual(
                reason, errors, f"Schedule {i}: {schedule}\n Error: {errors}"
            )

    def test_is_S2PL(self):
        """
        tests is_S2PL(parsed_schedule)
        """
        for (schedule, _, _, (isS2PL, reason), _), i in zip(
            self.scheduling_tests, range(len(self.scheduling_tests))
        ):
            parsed, msg = Schedule.parse_schedule(schedule)
            self.assertEqual(msg, "")
            actual, errors = Scheduling.is_S2PL(parsed)
            self.assertEqual(
                isS2PL, actual, f"Schedule {i}: {schedule}\n Error: {errors}"
            )
            self.assertEqual(not errors, isS2PL)
            self.assertEqual(
                reason, errors, f"Schedule {i}: {schedule}\n Error: {errors}"
            )

    def test_is_SS2PL(self):
        """
        tests is_SS2PL(parsed_schedule)
        """
        for (schedule, _, _, _, (isSS2PL, reason)), i in zip(
            self.scheduling_tests, range(len(self.scheduling_tests))
        ):
            parsed, msg = Schedule.parse_schedule(schedule)
            self.assertEqual(msg, "")
            actual, errors = Scheduling.is_SS2PL(parsed)
            self.assertEqual(
                isSS2PL, actual, f"Schedule {i}: {schedule}\n Error: {errors}"
            )
            self.assertEqual(not errors, isSS2PL)
            self.assertEqual(
                reason, errors, f"Schedule {i}: {schedule}\n Error: {errors}"
            )

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
