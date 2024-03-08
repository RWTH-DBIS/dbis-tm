"""
Created on 2022-07-06

@author: Lara
@author: Marc
@author: wf

"""
import re
from dbis_tm import Schedule
from dbis_tm.TMSolver import Scheduling, Recovery, Serializability
from dbis_tm.Solution_generator import Perform_conflictgraph
from typing import Union
from excmanager.scorer import Scorer, SetScorer


class ScheduleCheck:
    """
    check the schedule
    """

    @classmethod
    def check(cls, index, schedule, result) -> str:
        """
        check the given schedule against the given result
        """
        msg = None
        s_parsed, s_problem = Schedule.parse_schedule(schedule)
        result_parsed, result_problem = Schedule.parse_schedule(result)
        problems = Scheduling.check_operations_same(s_parsed, result_parsed)
        if not len(problems) == 0:
            msg = f"schedule_{index} enthält unterschiedliche oder nicht alle Operationen aus s{index}"
        return msg

    @classmethod
    def feedback(cls, msg: str, positive: bool):
        """
        give positive or negative feedback with the given message

        Args:
            msg(str): the message to print
            positive(bool): if True add a ✅ marker else ❌
        """
        marker = "✅" if positive else "❌"
        print(f"{msg} {marker}")

    @classmethod
    def check_same(
        self, original: Schedule, schedule: Schedule, schedule_str: str
    ) -> bool:
        """
        Checks whether the _schedule_ has the same operations (without locks) as _original_
            and whether _schedule_str_ can be parsed without errors

        Returns:
            True if no errors occur
        """
        sameProblemCount = 0
        problems = Schedule.is_operations_same(original, schedule)
        if not problems:
            self.feedback(
                f"schedule has not the same operations as the original.", False
            )
            sameProblemCount += 1
        else:
            self.feedback("schedule covers all operations", True)

        s_parsed, error_parse = Schedule.parse_schedule(schedule_str)
        if error_parse:
            ScheduleCheck.feedback(
                f"Could not parse schedule due to '{error_parse}'", False
            )
            sameProblemCount += 1
        else:
            ScheduleCheck.feedback("parse schedule ok", True)
        return sameProblemCount == 0


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
    def check_schedule_syntax(cls, schedule: str) -> str:
        """
        check the syntax of the given schedule

        Args:
            schedule(str): the schedule to check

        Returns:
            msg: None if ok else the problem message
        """
        schedule = Schedule.sanitize(schedule)
        syntax_pattern = "([rw][lu]?[1-3][(][a-z][)]|[c][1-3])?"
        p_count = re.findall(syntax_pattern, schedule).count("")
        msg = None
        if schedule == "":
            msg = "Leerer Schedule kann keine Lösung sein"
        if p_count > 1:
            msg = f"Schedule '{schedule}' hat keine korrekte Syntax"
        return msg

    @classmethod
    def check_conf_set_syntax(cls, conf_set: list[tuple[str, str]]) -> str:
        """
        Check syntax of strings in tuple that denotes conflicting operations.

        Returns:
            None if input is formatted according to pattern
            or an error message in case a tuple is formatted incorrectly
        """
        tuple_pattern = "[rw][1-3][(][a-z][)]|[rw]_[1-3][(][a-z][)]"
        if not isinstance(conf_set, list):
            return f"{conf_set} ist keine Liste"
        for t in conf_set:
            if not len(t) == 2:
                return f"Das Tupel {t} von {conf_set} ist kein Paar"
            for s in sorted(list(t)):
                if not re.match(tuple_pattern, s):
                    return f"Das Tupel {t} von {conf_set} hat keine korrekte Syntax"
        return None


class ScheduleScorer(Scorer):
    """
    Class to score scheduling
    """

    def __init__(self, debug: bool = False):
        """
        Constructor

        Args:
            debug(bool): if True show debug information
        """
        Scorer.__init__(self, debug=debug)

    def check_schedule(self, parsed: Schedule, check: str) -> list[str]:
        """
        Checks whether the schedule given (parsed) is in the correct form(check)

        Returns:
         array of errors
            or empty array
        """
        if check == "C2PL":
            _presult, errors = Scheduling.is_C2PL(parsed)

        elif check == "S2PL":
            _presult, errors = Scheduling.is_S2PL(parsed)

        elif check == "SS2PL":
            _presult, errors = Scheduling.is_SS2PL(parsed)
        else:
            errors = []

        return errors

    def getScore(
        self, original: str, schedule: str, check_scheduling: str, max_points: int
    ) -> int:
        """
        - Run syntax check for schedule
        - Check schedule for _check_scheduling_
        - Add points

        Returns:
            points
        """
        original_p, original_error = Schedule.parse_schedule(original)
        schedule_p, schedule_error = Schedule.parse_schedule(schedule)
        checkSame = ScheduleCheck.check_same(original_p, schedule_p, schedule)
        if checkSame:
            check = f"checking '{check_scheduling}' of schedule '{schedule}'"
            errors = self.check_schedule(schedule_p, check_scheduling)
            if errors:
                for error in errors:
                    # just for feedback
                    self.addScore(max_points, check, problem=f"'{error}'")
            else:
                self.addScore(max_points, check, problem=None)
        return self.score


class ConflictSetScorer:
    """
    scorer for conflict sets
    """

    def removeBlanks(self, result):
        """
        remove blanks and underscores
        """
        resultNoBlanks = {
            (str1.replace(" ", ""), str2.replace(" ", "")) for (str1, str2) in result
        }
        resultNoBlanks = {
            (str1.replace("_", ""), str2.replace("_", "")) for (str1, str2) in result
        }
        return resultNoBlanks

    def score_conflictSet(self, result1, result2, schedule1, schedule2, max_points):
        """
        score the given result sets against the given solutions
        """
        result1 = self.removeBlanks(result1)
        solution1 = Perform_conflictgraph.compute_conflict_quantity(schedule1)
        setScorer1 = SetScorer()
        setScorer1.evaluate_set(result1, solution1, max_points=max_points / 2)
        result2 = self.removeBlanks(result2)
        solution2 = Perform_conflictgraph.compute_conflict_quantity(schedule2)
        setScorer2 = SetScorer()
        setScorer2.evaluate_set(result2, solution2, max_points=max_points / 2)
        score = setScorer1.score + setScorer2.score
        return round(score, 2)


class ConflictSerializationScorer(Scorer):
    """
    a scorer for conflict serialization tasks
    """

    def score_conflictSerialization(
        self, name, cgresult, serializableResult, schedule, max_points
    ):
        """
        score a conflict serialization answer
        """
        points_seri = 0.5
        points_graph = max_points - points_seri
        if points_graph <= 0:
            points_seri = max_points / 2
            points_graph = max_points / 2
        serializable = Serializability.is_serializable(schedule)
        cgsolution = Perform_conflictgraph.compute_conflictgraph(serializable[1])

        serializableCheck = f"check that your result for serializable of {name} {serializableResult} = correct solution serializable {serializable[0]}"
        serializableProblem = None
        if serializableResult != serializable[0]:
            serializableProblem = ""
        self.addScore(points_seri, serializableCheck, serializableProblem)
        expectedGraph = str(cgsolution.digraph)
        conflictGraphCheck = f"check that conflictGraph is '''{expectedGraph}'''"
        conflictGraphProblem = None
        if cgresult != cgsolution:
            conflictGraphProblem = f"{str(cgresult.digraph)} is different"
        self.addScore(points_graph, conflictGraphCheck, conflictGraphProblem)
        return self.score


class RecoveryScorer(Scorer):
    """
    a scorer for recovery
    """

    def removeBlanksAndUnderScores(self, proof):
        """
        sanitize the given proof set

        Args:
            proof(set): the set to sanitize
        Return:
            set: set with no _ or blank in notation
        """
        proofResult = set()
        # loop over the tuples
        for t in list(proof):
            tlist = list(t)
            rtuple = ()
            for telement in tlist:
                if isinstance(telement, str):
                    for charToRemove in [" ", "_"]:
                        telement = telement.replace(charToRemove, "")
                rtuple += (telement,)
            proofResult.add(rtuple)
        return proofResult

    def setString(self, aSet):
        if aSet == set():
            return "{}"
        else:
            return str(aSet)

    def score_proof(
        self, name, proofName, isClass, proofClass, isClassSolution, proofClassSolution
    ):
        """
        score a proof

        Args:
            name(str): the name of the schedule
            proofName(str): the name of the proof/Class e.g. RC/ACA/ST
            isClass(bool): result if the schedule is in the class
            proofClass(set): the set to prove with
            isClassSolution(bool): True if the schedule is in the given class as the sample solution
            proofClassSolution(set): the set which proves to be in the class
        """
        negativeProof = False
        problem = None
        proofClass = self.removeBlanksAndUnderScores(proofClass)
        # positive Proof
        if isClassSolution:
            check = f"{name} is {proofName} with expected proof {proofClassSolution}"
            # check sets:
            errors1 = []
            errors2 = []
            for i in proofClassSolution:
                if i not in proofClass:
                    errors1.append(i)
            for j in proofClass:
                if j not in proofClassSolution:
                    errors2.append(j)
            if isClassSolution == isClass and len(errors1) == 0 == len(errors2):
                pass
            else:
                problem = f"Missing tuples: {errors1},wrong tuples: {errors2}"
            self.addScore(self.points_per_class, check, problem)
        else:
            check = (
                f"{name} is not {proofName} with expected proof {proofClassSolution}"
            )
            if isClassSolution == isClass:
                # get first element of set
                if len(proofClassSolution) == 0 and len(proofClass) == 0:
                    negativeProof = True
                else:
                    if len(proofClass) > 0:
                        proofClassItem = tuple(proofClass)[0]
                        negativeProof = (
                            len(proofClass) > 0 and proofClassItem in proofClassSolution
                        )
            if not negativeProof:
                problem = (
                    f"your proof {self.setString(proofClass)} is not the expected one"
                )
            self.addScore(self.points_per_class, check, problem)
        return negativeProof

    def score_recovery(
        self, name: str, schedule: Union[Schedule, str], result, max_score
    ) -> int:
        """
        We grade each class.

        RC needs a proof. For ACA and ST we can use the subset relationship to avoid giving a counterexample.

        That is, we either give a counterexample
        or we simply leave the proof empty but set the bool to the correct value. In that case it is necessary to
        show the class we are relying on for the subset relationship. That is, if a schedule is not ST, we can use the
        subset relationship IF it was shown that the schedule is not ACA.
        """
        self.points_per_class = max_score * (1 / 3)
        is_in_class, proof = result
        is_rc, is_aca, is_st = is_in_class
        proof_rc, proof_aca, proof_st = proof
        # RC
        is_rc_solution, proof_rc_solution = Recovery.is_recoverable(schedule)
        showed_not_rc = self.score_proof(
            name, "RC", is_rc, proof_rc, is_rc_solution, proof_rc_solution
        )

        # ACA
        is_aca_solution, proof_aca_solution = Recovery.avoids_cascading_aborts(schedule)
        if showed_not_rc:
            proof_aca_solution = {}
        showed_not_aca = self.score_proof(
            name, "ACA", is_aca, proof_aca, is_aca_solution, proof_aca_solution
        )

        # ST
        is_st_solution, proof_st_solution = Recovery.is_strict(schedule)
        if showed_not_aca:
            proof_st_solution = {}
        self.score_proof(name, "ST", is_st, proof_st, is_st_solution, proof_st_solution)
        return self.score
