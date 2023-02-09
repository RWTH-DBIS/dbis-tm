'''
Created on 2022-07-06

@author: Lara
@author: Marc
@author: wf

'''
import re
from assets.TMBasic import Schedule
from assets.TMSolver import Scheduling, Recovery, Serializability
from typing import Union
from assets.Solution_generator import Perform_conflictgraph

class Scorer:
    """
    general scorer
    """

    def __init__(self, debug: bool = False):
        """
        constructor
        """
        self.score = 0
        self.debug = debug

    def addScore(self, amount: float, check: str, problem: str = None):
        """
        add the given amount to self.score if there is no problem
        increment self.max_score by 1

        Args:
            amount(float): the amount to add
            check(str): message text about what was checked
            problem(str): message text about a problem - if this is not none the score will not be increased
        """
        if problem is not None:
            if self.debug:
                print(f"no score for {check} due to {problem}❌")
            return
        else:
            self.score += amount
            if self.debug:
                print(f"adding {amount} to score for {check}✅")
                
class SyntaxCheck:
    """
    I am an interface for checking the syntax of inputs.
    You should not construct me because I am a stateless interface that merely provides static functions.

    Functions:
        check_conf_set_syntax (checks syntax of strings in tuple that denotes conflicting operations)
    """

    def __init__(self):
        raise TypeError("Cannot create 'SyntaxCheck' instances.")

    @classmethod
    def check_schedule_syntax(cls,schedule:str) -> str:
        '''
        check the syntax of the given schedule
        
        Args:
            schedule(str): the schedule to check
            
        Returns:
            msg: None if ok else the problem message
        '''
        schedule = schedule.replace(" ", "").replace("_", "")
        syntax_pattern = "([rw][lu]?[1-3][(][xyz][)]|[c][1-3])?"
        pcount=re.findall(syntax_pattern, schedule).count('')
        msg=None
        if pcount>1:
            msg=f"Schedule '{schedule}' hat keine korrekte Syntax"
        return msg
        
    @classmethod
    def check_conf_set_syntax(cls, conf_set: set[tuple[str, str]]) -> str:
        """
        Check syntax of strings in tuple that denotes conflicting operations.

        Returns:
            None if input is formatted according to pattern
            or an error message in case a tuple is formatted incorrectly
        """
        tuple_pattern = "[rw]_[1-3][(][xyz][)]"
        if not isinstance(conf_set,set):
            return f"{conf_set} ist kein Set"
        for t in conf_set:
            for s in t:
                if not re.match(tuple_pattern, s):
                    return f"Das Tupel {t} von {conf_set}  hat keine korrekte Syntax"
        return None
    
class ScoreSchedule(Scorer):
    """
    Class to score schedules
    """

    def __init__(self, debug: bool = False):
        """
        Constructor

        Args:
            debug(bool): if True show debug information
        """
        Scorer.__init__(self, debug)

    @classmethod
    def grade_schedule(cls, parsed: Schedule, check: str) -> list[str]:
        """
        Checks whether the schedule given (parsed) is in the correct form(check)

        Returns:
         array of errors
            or empty array
        """
        if check == "C2PL":
            errors = Scheduling.is_C2PL(parsed)[1]

        elif check == "S2PL":
            errors = Scheduling.is_S2PL(parsed)[1]

        elif check == "SS2PL":
            errors = Scheduling.is_SS2PL(parsed)[1]
        else:
            errors = []

        return errors

    def check_syntax(self, original: Schedule, schedule: Schedule, schedule_str: str) -> bool:
        """
        Checks whether the _schedule_ has the same operations (without locks) as _original_
            and whether _schedule_str_ can be parsed without errors

        Returns:
            True iff no errors occur
        """
        problem1 = None
        problem2 = None
        if not Scheduling.is_operations_same(original, schedule):
            problem1 = "Not done the original schedule."
        self.addScore(0, "right schedule", problem1)

        error_parse = Schedule.parse_schedule(schedule_str)[1]
        if error_parse:
            problem2 = f"Could not parse schedule due to '{error_parse}'"
        self.addScore(0, "parse schedule", problem2)
        if problem1 or problem2:
            return False
        return True

    def getScore(self, original: str, schedule: str, check_scheduling: str, max_points: int) -> int:
        """
        - Run syntax check for schedule
        - Check schedule for _check_scheduling_
        - Add points

        Returns:
            points
        """
        original_p = Schedule.parse_schedule(original)[0]
        schedule_p = Schedule.parse_schedule(schedule)[0]
        syntax = self.check_syntax(original_p, schedule_p, schedule)
        if syntax:
            check = f"checking '{schedule}' for '{check_scheduling}'"
            errors = self.grade_schedule(schedule_p, check_scheduling)
            problems = None
            if errors:
                for x in errors:
                    problems = f"'{x}'"
                    self.addScore(0.5, check, problems)
                    max_points -= 0.5
            else:
                self.addScore(max_points, check, problems)
        return self.score

    def getDifference(self, list1, list2, max_points):
        """
        Gets two lists and the possible points.
        Calculates the differences between those two.
        Adds score.
        """
        not_in = []
        for i in list1:
            if i not in list2:
                not_in.append(i)
        for j in list2:
            if j not in list1:
                not_in.append(j)
        check = f"Checking '{list2}' for correct answers."
        problems = None
        if not_in:
            problems = f"'{not_in}'"
        self.addScore(max_points, check, problems)
        return self.score
    
    
class Grading:
    """
    I am an interface for grading solutions.
    You should not construct me because I am a stateless interface that merely provides static functions.

    Functions:
        grade_recovery (grade relationship of RC, ACA, ST regarding a given schedule)
    """

    def __init__(self):
        raise TypeError("Cannot create 'Grading' instances.")

    @classmethod
    def grade_schedule(cls, org_schedule, schedule, check, max_score):
        """
        Class to grade the Scheduling. Compute whether the given solution is vaild
        scheduled. If so give points, otherwise for each error -1 point.
        """
        if not Scheduling.is_operations_same(org_schedule, schedule):
            return 0, ["Not done the original schedule."]

        parsed, error_parse = Schedule.parse_schedule(schedule)
        if not error_parse:
            return 0, error_parse  # should not occur

        if check == "C2PL":
            result, errors = Scheduling.is_C2PL(parsed)

        elif check == "S2PL":
            result, errors = Scheduling.is_S2PL(parsed)

        elif check == "SS2PL":
            result, errors = Scheduling.is_SS2PL(parsed)
        score = max_score
        if not result:
            for x in errors:
                score -= 1
                if score == 0:
                    return 0, errors

        return score, errors

    @classmethod
    def grade_recovery(cls, schedule: Union[Schedule, str], is_in_class, proof, max_score) -> int:
        """
        We grade each class.
        RC needs a proof. For ACA and ST we can use the subset relationship to avoid giving a counterexample.
        That is, we either give a counterexample
        or we simply leave the proof empty but set the bool to the correct value. In that case the it is necessary to
        show the class we are relying on for the subset relationship. That is, if a schedule is not ST, we can use the
        subset relationship IF it was shown that the schedule is not ACA.
        """
        score = 0
        points_per_class = max_score * (1 / 3)

        # RC
        showed_rc = False
        is_rc, proof_solution = Recovery.is_recoverable(schedule)
        if is_rc:
            if is_rc == is_in_class[0] and proof[0] == proof_solution:
                score += points_per_class
                showed_rc = True
        else:
            if is_rc == is_in_class[0] and len(proof[0]) > 0 and tuple(proof[0])[0] in proof_solution:
                score += points_per_class
                showed_rc = True

        # ACA
        showed_aca = False
        is_aca, proof_solution = Recovery.avoids_cascading_aborts(schedule)
        if is_aca:
            if is_aca == is_in_class[1] and proof[1] == proof_solution:
                score += points_per_class
                showed_aca = True
        else:
            if (is_rc == is_aca and is_aca == is_in_class[1] and proof[1] == {} and showed_rc) \
                    or (is_aca == is_in_class[1] and len(proof[1]) > 0 and tuple(proof[1])[0] in proof_solution):
                score += points_per_class
                showed_aca = True

        # ST
        is_st, proof_solution = Recovery.is_strict(schedule)
        if is_st:
            if is_st == is_in_class[2] and proof[2] == proof_solution:
                score += points_per_class
        else:
            if (is_aca == is_st and is_st == is_in_class[2] and proof[2] == {} and showed_aca) \
                    or (is_st == is_in_class[2] and len(proof[2]) > 0 and tuple(proof[2])[0] in proof_solution):
                score += points_per_class

        return score
        
    @classmethod
    def grade_conflictsets(cls, schedule: Union[Schedule, str], solution, max_score)-> int:
        """
        Grading the conflict set task. Compute conflictset from original schedule.
        Check whether the conflict sets are the same. For each wrong entry -0.5 points.
        """
        score = 0
        error = 0
        if isinstance(schedule, str):
            schedule = Schedule.parse_schedule(schedule)
            assert not schedule[1]
            schedule = schedule[0]
        conflictset = Perform_conflictgraph.compute_conflict_quantity(schedule)
        add = max_score /len(conflictset)
        for i in conflictset:
            if i in solution:
                score += add
            else:
                score -= add
        if score < 0:
            score = 0
        score = 0
        return score
    
    @classmethod
    def grade_conflictgraph(cls,  schedule: Union[Schedule, str], conflictgraph, is_serializable:bool, max_score)-> int:
        """
        Grading the conflict graph task. Compute serilizability from original schedule.
        If right value 0.6 points.
        Then compute conflict graph and check for equality of both. If equal points,
        otherwise none.
        """
        score = 0
        error = 0
        if isinstance(schedule, str):
            schedule = Schedule.parse_schedule(schedule)
            assert not schedule[1]
            schedule = schedule[0]

        solution = Serializability.is_serializable(schedule)
        if is_serializable == solution[0]:
            score += 0.5
        graph_solution = Perform_conflictgraph.compute_conflictgraph(solution[1])
        if conflictgraph.__eq__(graph_solution):
            score += max_score-0.5
        return score
