"""
Created on 18.07.2022

@author: wf
"""
from tests.basetest import Basetest


class ScheduleTest(Basetest):
    """
    base class for Schedule Tests
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    def getScheduleExamples(self):
        """
        get schedule examples
        """
        s1 = "w_2(x) w_1(z) r_2(y) r_1(x) r_3(z) w_3(x) w_1(y) c_1 c_2 c_3"
        s2 = "r_2(z) w_1(y) r_3(z) r_2(y) r_1(x) w_2(y) w_3(x) c_1 c_2 c_3"
        s3 = "r_1(x) w_2(z) w_3(y) w_2(x) r_3(z) r_1(y) r_2(y) c_1 c_2 c_3"

        examples = [
            {
                "index": 1,
                "schedule": s1,
                "check": "C2PL",
                "correct": True,
                "result": """wl_2(x) rl_2(y) w_2(x) wu_2(x) r_2(y) ru_2(y) c_2 
wl_1(z) rl_1(x) wl_1(y) w_1(z) wu_1(z) r_1(x) ru_1(x) rl_3(z) wl_3(x) r_3(z) ru_3(z) w_3(x) wu_3(x) c_3 
w_1(y) wu_1(y) c_1""",
            },
            {
                "index": 2,
                "schedule": s2,
                "check": "S2PL",
                "correct": True,
                "result": "rl_2(z) r_2(z) wl_1(y) w_1(y) rl_3(z) r_3(z) rl_1(x) r_1(x) wu_1(y) ru_1(x) c_1 rl_2(y) r_2(y) wl_2(y) ru_2(z) ru_2(y) w_2(y) wu_2(y) c_2 wl_3(x) ru_3(z) w_3(x) wu_3(x) c_3",
            },
            {
                "index": 3,
                "schedule": s3,
                "check": "SS2PL",  # not possible because of deadlock, this locking is incorrect
                "correct": False,
                "result": "rl_1(x) r_1(x) wl_2(z) w_2(z)  wl_3(y) w_3(y) wl_2(x) w_2(x) rl_3(z) r_3(z) wu_3(y) ru_3(z) rl_1(y) r_1(y) ru_1(x) ru_1(y) rl_2(y) r_2(y) wu_2(z) wu_2(x) ru_2(y) c_1 c_2 c_3",
            },
        ]
        return examples
