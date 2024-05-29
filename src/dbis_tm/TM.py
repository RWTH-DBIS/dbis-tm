"""
Created 2022-05

@author: Lara
@author: Marc
@author: Wolfgang
"""
from __future__ import annotations

import itertools
import sys, re
from enum import Enum, EnumMeta
from typing import Union
from graphviz import Digraph


class OperationTypeMeta(EnumMeta):
    """
    meta class for Operation type
    """

    def __contains__(self, item):
        """
        check that the item is contained in my member values
        """
        return item in [v.value for v in self.__members__.values()]


class OperationType(Enum, metaclass=OperationTypeMeta):
    """
    The kind / type of operation for an Operation
    """

    READ = "r"
    READ_LOCK = "rl"
    READ_UNLOCK = "ru"
    WRITE = "w"
    WRITE_LOCK = "wl"
    WRITE_UNLOCK = "wu"


# class Transaction:
# there is no Transaction class yet since we only need the
# transaction number
# feel free to add this later ...


class Operation:
    """
    I am a step of a transaction
    """

    def __init__(
        self, op_type: OperationType, tx_number: int, resource: str, index: int
    ):
        """
        Constructor

        Args:
            op_type(Operation): the kind of operation
            tx_number(int): link to my Transaction
            resource(str): link to my data object the operation will be applied on
            index(int): my position in the schedule
        """
        self.op_type = op_type
        self.tx_number = tx_number
        self.resource = resource
        self.index = index

    def __repr__(self):
        return f"{self.op_type.value}{self.tx_number}({self.resource})"

    def __eq__(self, obj):
        return (
            isinstance(obj, Operation)
            and self.op_type == obj.op_type
            and self.tx_number == obj.tx_number
            and self.resource == obj.resource
        )

    def __sr__(self, obj):
        """True if operations of same trans and on same resource"""
        return (
            isinstance(obj, Operation)
            and self.tx_number == obj.tx_number
            and self.resource == obj.resource
        )

    def __same__(self, obj):
        """Is the same operation"""
        return (
            isinstance(obj, Operation)
            and self.op_type == obj.op_type
            and self.tx_number == obj.tx_number
            and self.resource == obj.resource
            and self.index == obj.index
        )


class Schedule:
    """
    I am a container for
        a list of operations,
        a set of resources,
        a map of aborts and commits,
        and a count of transactions
    """

    def __init__(
        self,
        operations: list[Operation],
        resources: set[str],
        tx_count: int,
        aborts: dict,
        commits: dict,
    ):
        """
        Constructor:

        Args:
            operations(list[Operation]): the kind of operation
            resources(set[str]): link to my Transaction
            tx_count(int): link to my data object the operation will be applied on
            aborts(dict): my position in the schedule
            commits(dict): my position in the schedule
        """
        self.operations = operations
        self.resources = resources
        self.tx_count = tx_count
        self.aborts = aborts
        self.commits = commits

    def __repr__(self):
        return (
            f"Schedule[operations: {self.operations}, resources: {self.resources}, tx_count: {self.tx_count}, "
            f"aborts: {self.aborts}, commits: {self.commits}]"
        )

    def active(self) -> list[int]:
        """Returns the still active transactions."""
        return [
            i
            for i in range(1, self.tx_count + 1)
            if i not in self.aborts.keys() and i not in self.commits.keys()
        ]

    def next_index(self):
        """Returns the next unused index"""
        if self.operations:
            return (
                max(
                    [0]
                    + [self.operations[-1].index]
                    + list(self.aborts.values())
                    + list(self.commits.values())
                )
                + 1
            )
        else:
            return 1

    def op_trans(self, transaction: int) -> int:
        """Returns how many operations one transaction perfomed"""
        return max(
            0,
            len([op for op in self.operations if op.tx_number == transaction]),
        )

    @classmethod
    def sanitize(cls, schedule: str) -> str:
        """
        return a sanitized schedule

        Args:
            schedule(str): the plain input schedule using underscores and whitespaces

        Returns:
            str: the sanitized schedule with underscores and whitespaces removed
        """
        for removeChar in [" ", "_", "\t", "\n"]:
            schedule = schedule.replace(removeChar, "")
        return schedule

    @classmethod
    def parse_schedule(cls, schedule_str: str) -> tuple[Schedule, str]:
        """
        Parse the given string to a schedule.

        Returns:
            Created Schedule object
            In case of error, the unparseable part is returned. Else an empty string is returned
        """

        # Sanitize input
        schedule_str = Schedule.sanitize(schedule_str)

        parsed_schedule = Schedule([], set(), 0, {}, {})
        tx = set()
        index = 0
        i = 0
        while i < len(schedule_str):
            curr_char = schedule_str[i].lower()
            next_char = schedule_str[i + 1].lower()

            if curr_char + next_char in OperationType:
                operation_type = OperationType(curr_char + next_char)
                index += 1
                i += 2
            elif curr_char in OperationType:
                operation_type = OperationType(curr_char)
                index += 1
                i += 1
            elif curr_char == "c":
                index += 1
                parsed_schedule.commits[int(next_char)] = index

                i += 2
                continue
            elif curr_char == "a":
                index += 1
                parsed_schedule.aborts[int(next_char)] = index
                i += 2
                continue
            else:
                p1 = max(i - 2, 0)
                p2 = min(i + 5, len(schedule_str) - 1)
                return parsed_schedule, schedule_str[p1:p2]

            tx_number = schedule_str[i].lower()
            if not tx_number.isdigit():
                p1 = max(i - 2, 0)
                p2 = min(i + 5, len(schedule_str) - 1)
                return parsed_schedule, schedule_str[p1:p2]
            tx.add(tx_number)
            i += 2

            resource = schedule_str[i].lower()
            if not resource.isalpha():
                p1 = max(i - 2, 0)
                p2 = min(i + 5, len(schedule_str) - 1)
                return parsed_schedule, schedule_str[p1:p2]
            parsed_schedule.resources.add(resource)
            i += 2

            parsed_schedule.operations.append(
                Operation(operation_type, int(tx_number), resource, index)
            )

        parsed_schedule.tx_count = len(tx)
        return parsed_schedule, ""

    @classmethod
    def parse_string(cls, schedule: Schedule) -> tuple[str, str]:
        """
        Parse a given schedule into a string.
        Only works if each transaction is concluded.

        Returns:
            - Parsed string of this schedule,
            - And a error message if somethings wrong
        """
        schedule_str = ""
        abort = schedule.aborts
        commit = schedule.commits
        op_len = len(schedule.operations)
        op_counter = 0
        for i in range(1, op_len + schedule.tx_count + 1):
            if op_counter < op_len:
                operation = schedule.operations[op_counter]
            if op_counter < op_len and operation.index == i:
                op_counter += 1
                schedule_str += (
                    operation.op_type.value
                    + str(operation.tx_number)
                    + "("
                    + operation.resource
                    + ") "
                )
            else:
                trc = list(
                    filter(
                        lambda trans: commit.get(trans) == i,
                        range(1, schedule.tx_count + 1),
                    )
                )
                tra = list(
                    filter(
                        lambda trans: abort.get(trans) == i,
                        range(1, schedule.tx_count + 1),
                    )
                )
                if trc:
                    # get transaction if index from dict
                    schedule_str += "c" + str(trc[0]) + " "
                elif tra:
                    # get transaction of index from dict
                    schedule_str += "a" + str(tra[0]) + " "
                else:
                    return schedule_str, "The index: " + str(i) + "is not given."
        return schedule_str, ""

    @classmethod
    def is_operations_same(
        cls, schedule: Union[Schedule, str], mod_schedule: Union[Schedule, str]
    ) -> bool:
        """
        Checks whether the two  given schedules do have the same operations.

        Gets:
            schedule: 'original' schedule (without locks and unlocks)
            schedule_mod: modified schedule (with locks and unlocks)

        Returns:
           bool: True if no problems
        """

        problems = Schedule.check_operations_same(schedule, mod_schedule)
        return len(problems) == 0

    @classmethod
    def check_operations_same(
        cls, schedule: Union[Schedule, str], mod_schedule: Union[Schedule, str]
    ) -> list:
        """
        Checks whether the two  given schedules do have the same operations.

        Gets:
            schedule: 'original' schedule (without locks and unlocks)
            schedule_mod: modified schedule (with locks and unlocks)

        Returns:
           list of problems
        """
        if isinstance(schedule, str):
            schedule = Schedule.parse_schedule(schedule)
            assert not schedule[1]
            schedule = schedule[0]
        if isinstance(mod_schedule, str):
            mod_schedule = Schedule.parse_schedule(mod_schedule)
            assert not mod_schedule[1]
            mod_schedule = mod_schedule[0]
        problems = []
        org_operations = list(
            filter(
                lambda op: op.op_type in [OperationType.READ, OperationType.WRITE],
                mod_schedule.operations,
            )
        )
        for x in org_operations:
            if x in schedule.operations:
                continue
            else:
                problems.append(x)
        for y in schedule.operations:
            if y in org_operations:
                continue
            else:
                problems.append(y)
        for i in range(1, schedule.tx_count + 1):
            trans_op_mod = list(
                filter(
                    lambda op: op.op_type in [OperationType.READ, OperationType.WRITE]
                    and op.tx_number == i,
                    mod_schedule.operations,
                )
            )
            trans_op_org = list(
                filter(lambda op: op.tx_number == i, schedule.operations)
            )
            if not (trans_op_mod == trans_op_org):
                problems.append(f"{trans_op_mod} != {trans_op_org} at {i}")
        return problems


class ConflictGraph:
    """
    a conflict graph
    """

    def __init__(self, labelPostfix=""):
        """
        constructor

        Args:
            labelPostfix(str): the postfix for the label to be used
        """
        self.nodes = set()
        self.edges = set()
        cglabel = f"Konfliktgraph {labelPostfix}"
        self.digraph = Digraph(
            "Konfliktgraph",
            "generiert von DBIS VL UB 8 TM.ConflictGraph",
            graph_attr={"label": cglabel},
        )

    def isEmpty(self):
        return len(self.nodes) == 0

    def __eq__(self, obj):
        return (
            isinstance(obj, ConflictGraph)
            and self.nodes == obj.nodes
            and self.edges == obj.edges
        )

    def get_graphviz_graph(self):
        return self.digraph

    def add_edge(self, t1: ConflictGraphNode, t2: ConflictGraphNode) -> None:
        self.nodes.add(t1)
        self.nodes.add(t2)
        self.edges.add((t1, t2))
        self.digraph.edge(f"t{t1.tx_number}", f"t{t2.tx_number}")


class ConflictGraphNode:
    """ """

    def __init__(self, tx_number: int):
        self.tx_number = tx_number

    def __eq__(self, obj):
        return isinstance(obj, ConflictGraphNode) and self.tx_number == obj.tx_number

    def __hash__(self):
        return hash(self.tx_number)


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
    def check_conf_set_syntax(cls, conf_set: set[tuple[str, str]]) -> str:
        """
        Check syntax of strings in tuple that denotes conflicting operations.

        Returns:
            None if input is formatted according to pattern
            or an error message in case a tuple is formatted incorrectly
        """
        tuple_pattern = "[rw][1-3][(][a-z][)]|[rw]_[1-3][(][a-z][)]"
        if conf_set == {}:
            pass
        elif not isinstance(conf_set, set):
            return f"{conf_set} ist kein Set"
        for t in conf_set:
            if not len(t) == 2:
                return f"Das Tupel {t} von {conf_set} ist kein Paar"
            for s in sorted(list(t)):
                if not re.match(tuple_pattern, s):
                    return f"Das Tupel {t} von {conf_set} hat keine korrekte Syntax"
        return None

    @classmethod
    def check(cls, index, schedule, result) -> str:
        """
        check the given schedule against the given result
        """
        msg = None
        s_parsed, s_problem = Schedule.parse_schedule(schedule)
        result_parsed, result_problem = Schedule.parse_schedule(result)
        problems = Schedule.check_operations_same(s_parsed, result_parsed)
        if not len(problems) == 0:
            msg = f"schedule_{index} enthält unterschiedliche oder nicht alle Operationen aus s{index}"
        return msg
